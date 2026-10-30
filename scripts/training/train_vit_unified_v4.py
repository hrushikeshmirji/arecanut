"""
train_vit_unified_v4.py
========================
Fine-tunes the 9-class Vision Transformer (ViT-B/16) on the newly expanded
dataset_unified_v4 (4,151 images: 3,317 train, 834 validation).

Features:
- Warmstarts from vit_areca_classifier_v3
- Cosine Annealing learning rate schedule
- Label smoothing (0.1) for confidence calibration
- Robust data augmentations
- Checkpoints saved to backend/weights/vit_areca_classifier_v4/
- Backward-compatible synchronization to vit_areca_classifier_v3/ and vit_areca_classifier_v2/
"""

import argparse
import copy
import json
import logging
import os
import random
import shutil
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)

import numpy as np
import torch
import torch.nn as nn
from PIL import Image
from sklearn.metrics import f1_score, precision_recall_fscore_support
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms
from transformers import ViTForImageClassification, ViTImageProcessor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path("D:/arecanut_project").resolve()
DATASET_DIR = PROJECT_ROOT / "dataset_unified_v4"
WARMSTART_DIR = PROJECT_ROOT / "backend" / "weights" / "vit_areca_classifier_v3"
if not WARMSTART_DIR.exists():
    WARMSTART_DIR = PROJECT_ROOT / "backend" / "weights" / "vit_areca_classifier_v2"
OUTPUT_V4_DIR = PROJECT_ROOT / "backend" / "weights" / "vit_areca_classifier_v4"
OUTPUT_V3_DIR = PROJECT_ROOT / "backend" / "weights" / "vit_areca_classifier_v3"
OUTPUT_V2_DIR = PROJECT_ROOT / "backend" / "weights" / "vit_areca_classifier_v2"

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

class ArecaUnifiedDataset(Dataset):
    def __init__(self, samples: List[Tuple[Path, int]], transform: transforms.Compose):
        self.samples = samples
        self.transform = transform

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int]:
        img_path, label = self.samples[idx]
        with Image.open(img_path) as img:
            img = img.convert("RGB")
            tensor = self.transform(img)
        return tensor, label

def load_split(split_dir: Path, classes: List[str]) -> List[Tuple[Path, int]]:
    samples: List[Tuple[Path, int]] = []
    class_to_idx = {c: i for i, c in enumerate(classes)}

    for class_name in classes:
        folder = split_dir / class_name
        if not folder.exists():
            continue
        c_idx = class_to_idx[class_name]
        files = [
            f for f in sorted(folder.iterdir())
            if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS
        ]
        samples.extend((f, c_idx) for f in files)

    random.shuffle(samples)
    return samples

def train_one_epoch(
    model: nn.Module,
    loader: DataLoader,
    optimizer: torch.optim.Optimizer,
    criterion: nn.Module,
    device: torch.device,
) -> Tuple[float, float]:
    model.train()
    total_loss = 0.0
    correct = 0
    total = 0

    for step, (images, labels) in enumerate(loader):
        images = images.to(device)
        labels = labels.to(device)

        optimizer.zero_grad()
        outputs = model(images)
        logits = outputs.logits
        loss = criterion(logits, labels)
        loss.backward()
        optimizer.step()

        total_loss += loss.item() * images.size(0)
        preds = logits.argmax(dim=-1)
        correct += (preds == labels).sum().item()
        total += labels.size(0)

        if (step + 1) % 25 == 0 or (step + 1) == len(loader):
            print(f"      Step [{step+1}/{len(loader)}] - Batch Loss: {loss.item():.4f} - Running Acc: {(correct/total)*100:.2f}%", flush=True)

    return total_loss / total, (correct / total) * 100.0

def evaluate(
    model: nn.Module,
    loader: DataLoader,
    criterion: nn.Module,
    device: torch.device,
) -> Tuple[float, float, float]:
    model.eval()
    total_loss = 0.0
    all_preds: List[int] = []
    all_labels: List[int] = []

    with torch.no_grad():
        for images, labels in loader:
            images = images.to(device)
            labels = labels.to(device)

            outputs = model(images)
            logits = outputs.logits
            loss = criterion(logits, labels)

            total_loss += loss.item() * images.size(0)
            preds = logits.argmax(dim=-1)

            all_preds.extend(preds.cpu().tolist())
            all_labels.extend(labels.cpu().tolist())

    total = len(all_labels)
    acc = (sum(p == y for p, y in zip(all_preds, all_labels)) / total) * 100.0
    macro_f1 = f1_score(all_labels, all_preds, average="macro", zero_division=0) * 100.0
    return total_loss / total, acc, macro_f1

def save_checkpoint(model: nn.Module, processor: ViTImageProcessor, target_dir: Path, id2label: Dict[int, str], label2id: Dict[str, int]):
    target_dir.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(str(target_dir))
    processor.save_pretrained(str(target_dir))

    config_file = target_dir / "config.json"
    with open(config_file, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    cfg["id2label"] = id2label
    cfg["label2id"] = label2id
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)

def main():
    parser = argparse.ArgumentParser(description="Unified v4 ViT fine-tuning for ArecaGuard")
    parser.add_argument("--epochs", type=int, default=2)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--lr", type=float, default=2e-5)
    parser.add_argument("--weight-decay", type=float, default=0.01)
    parser.add_argument("--label-smoothing", type=float, default=0.1)
    args = parser.parse_args()

    print("=" * 80, flush=True)
    print("  ARECAGUARD: VISION TRANSFORMER (ViT-B/16) RETRAINING PIPELINE (V4)", flush=True)
    print("=" * 80, flush=True)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if device.type == "cpu":
        torch.set_num_threads(min(8, os.cpu_count() or 4))
    print(f"  Target Device: {device} (threads: {torch.get_num_threads()})", flush=True)

    train_dir = DATASET_DIR / "train"
    val_dir = DATASET_DIR / "val"
    classes = sorted([d.name for d in train_dir.iterdir() if d.is_dir()])
    print(f"  Canonical Classes ({len(classes)}): {classes}", flush=True)

    id2label = {i: c for i, c in enumerate(classes)}
    label2id = {c: i for i, c in enumerate(classes)}

    train_samples = load_split(train_dir, classes)
    val_samples = load_split(val_dir, classes)
    print(f"  Dataset Partition: {len(train_samples)} Train, {len(val_samples)} Validation", flush=True)

    # Transforms with data augmentations
    train_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomVerticalFlip(p=0.5),
        transforms.RandomRotation(degrees=15),
        transforms.ColorJitter(brightness=0.15, contrast=0.15, saturation=0.15),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    val_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    train_dataset = ArecaUnifiedDataset(train_samples, train_transform)
    val_dataset = ArecaUnifiedDataset(val_samples, val_transform)

    train_loader = DataLoader(
        train_dataset,
        batch_size=args.batch_size,
        shuffle=True,
        num_workers=0,
        pin_memory=False,
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=0,
        pin_memory=False,
    )

    print(f"\n[1] Warm-starting ViT architecture from: {WARMSTART_DIR}", flush=True)
    processor = ViTImageProcessor.from_pretrained(str(WARMSTART_DIR))
    model = ViTForImageClassification.from_pretrained(
        str(WARMSTART_DIR),
        num_labels=len(classes),
        id2label=id2label,
        label2id=label2id,
        ignore_mismatched_sizes=True,
    )
    model.to(device)

    criterion = nn.CrossEntropyLoss(label_smoothing=args.label_smoothing)
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=args.lr,
        weight_decay=args.weight_decay,
    )
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
        optimizer,
        T_max=args.epochs * len(train_loader),
        eta_min=1e-6,
    )

    print("\n[2] Pre-training Baseline Evaluation...", flush=True)
    t0 = time.time()
    pre_loss, pre_acc, pre_f1 = evaluate(model, val_loader, criterion, device)
    print(f"    Pre-eval: Val Loss: {pre_loss:.4f} | Val Acc: {pre_acc:.2f}% | Val Macro F1: {pre_f1:.2f}% ({time.time()-t0:.1f}s)", flush=True)

    best_acc = pre_acc
    best_weights = copy.deepcopy(model.state_dict())

    print(f"\n[3] Commencing Fine-Tuning ({args.epochs} Epochs)...", flush=True)
    for epoch in range(1, args.epochs + 1):
        print(f"\n  ---> Epoch {epoch}/{args.epochs}", flush=True)
        t_epoch = time.time()

        train_loss, train_acc = train_one_epoch(model, train_loader, optimizer, criterion, device)
        val_loss, val_acc, val_f1 = evaluate(model, val_loader, criterion, device)
        scheduler.step()

        elapsed = time.time() - t_epoch
        print(f"    Epoch {epoch} Result ({elapsed:.1f}s):", flush=True)
        print(f"      Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.2f}%", flush=True)
        print(f"      Val Loss:   {val_loss:.4f} | Val Acc:   {val_acc:.2f}% | Val Macro F1: {val_f1:.2f}%", flush=True)

        if val_acc >= best_acc:
            best_acc = val_acc
            best_weights = copy.deepcopy(model.state_dict())
            print(f"      [*] New best validation accuracy achieved: {best_acc:.2f}%", flush=True)

    print("\n[4] Restoring optimal checkpoint...", flush=True)
    model.load_state_dict(best_weights)

    # Final evaluation
    final_loss, final_acc, final_f1 = evaluate(model, val_loader, criterion, device)
    print("\n" + "=" * 80, flush=True)
    print(f"  FINAL MODEL BENCHMARK (dataset_unified_v4):", flush=True)
    print(f"    Validation Accuracy : {final_acc:.2f}%", flush=True)
    print(f"    Validation Macro F1: {final_f1:.2f}%", flush=True)
    print(f"    Validation Loss    : {final_loss:.4f}", flush=True)
    print("=" * 80, flush=True)

    # Save checkpoints
    print(f"\n[5] Saving checkpoint to {OUTPUT_V4_DIR}...", flush=True)
    save_checkpoint(model, processor, OUTPUT_V4_DIR, id2label, label2id)
    print(f"    [OK] Saved primary v4 weights.")

    # Synchronize to v3 and v2 for live inference
    print(f"    Synchronizing weights to {OUTPUT_V3_DIR}...", flush=True)
    save_checkpoint(model, processor, OUTPUT_V3_DIR, id2label, label2id)
    print(f"    Synchronizing weights to {OUTPUT_V2_DIR}...", flush=True)
    save_checkpoint(model, processor, OUTPUT_V2_DIR, id2label, label2id)
    print("    [OK] Synchronized weights for runtime compatibility.")

    # Export training metrics metadata
    meta = {
        "dataset": "dataset_unified_v4",
        "train_samples": len(train_samples),
        "val_samples": len(val_samples),
        "total_samples": len(train_samples) + len(val_samples),
        "classes": classes,
        "epochs": args.epochs,
        "batch_size": args.batch_size,
        "learning_rate": args.lr,
        "val_accuracy": round(final_acc, 2),
        "val_macro_f1": round(final_f1, 2),
        "val_loss": round(final_loss, 4),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    with open(OUTPUT_V4_DIR / "training_summary.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    print(f"    Saved training summary to {OUTPUT_V4_DIR / 'training_summary.json'}")

if __name__ == "__main__":
    main()
