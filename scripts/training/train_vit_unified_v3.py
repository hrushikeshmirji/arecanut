"""
train_vit_unified_v3.py
========================
TASK 3: Vision Transformer (ViT-B/16) Retraining on Unified Dataset v3
---------------------------------------------------------------------
Fine-tunes the 9-class ViT-B/16 model on the unified corpus:
  D:/arecanut_project/dataset_unified_v3/
    ├── train/ (2,514 images)
    └── val/   (633 images)

Hyperparameters & Architecture:
  - Base: google/vit-base-patch16-224 (warm-started from v2 checkpoint)
  - Classes: 9 canonical classes (all certified ICAR-CPCRI conditions + OOD negative shield)
  - Optimizer: AdamW (lr=2e-5, weight_decay=0.01)
  - Criterion: CrossEntropyLoss with Label Smoothing (0.1) for calibrated confidence
  - Augmentations: RandomHorizontalFlip, RandomVerticalFlip, ColorJitter, RandomAffine
  - Checkpoint targets:
      backend/weights/vit_areca_classifier_v3/
      backend/weights/vit_areca_classifier_v2/ (updated in-place for detector)
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
DATASET_DIR = PROJECT_ROOT / "dataset_unified_v3"
WARMSTART_DIR = PROJECT_ROOT / "backend" / "weights" / "vit_areca_classifier_v2_backup"
if not WARMSTART_DIR.exists():
    WARMSTART_DIR = PROJECT_ROOT / "backend" / "weights" / "vit_areca_classifier_v2"
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
    parser = argparse.ArgumentParser(description="Unified v3 ViT fine-tuning for ArecaGuard")
    parser.add_argument("--epochs", type=int, default=2)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--lr", type=float, default=2e-5)
    parser.add_argument("--weight-decay", type=float, default=0.01)
    parser.add_argument("--label-smoothing", type=float, default=0.1)
    args = parser.parse_args()

    print("=" * 80, flush=True)
    print("  ARECAGUARD: TASK 3 - VISION TRANSFORMER (ViT-B/16) RETRAINING PIPELINE", flush=True)
    print("=" * 80, flush=True)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if device.type == "cpu":
        torch.set_num_threads(min(8, os.cpu_count() or 4))
    print(f"  Target Device: {device} (threads: {torch.get_num_threads()})", flush=True)

    train_dir = DATASET_DIR / "train"
    val_dir = DATASET_DIR / "val"
    classes = sorted([d.name for d in train_dir.iterdir() if d.is_dir()])
    print(f"  Canonical Classes ({len(classes)}): {classes}", flush=True)

    train_samples = load_split(train_dir, classes)
    val_samples = load_split(val_dir, classes)
    print(f"  Loaded Samples -> Train: {len(train_samples)}, Val: {len(val_samples)}", flush=True)

    train_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomVerticalFlip(p=0.2),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.05),
        transforms.RandomAffine(degrees=10, translate=(0.05, 0.05), scale=(0.95, 1.05)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    val_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    train_loader = DataLoader(
        ArecaUnifiedDataset(train_samples, train_transform),
        batch_size=args.batch_size,
        shuffle=True,
        num_workers=0,
    )

    val_loader = DataLoader(
        ArecaUnifiedDataset(val_samples, val_transform),
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=0,
    )

    id2label = {i: c for i, c in enumerate(classes)}
    label2id = {c: i for i, c in enumerate(classes)}

    print(f"\n  Warm-starting ViT Classifier from: {WARMSTART_DIR}...", flush=True)
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
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)

    # Pre-training baseline
    print("\n  Evaluating pre-training baseline on validation set...", flush=True)
    init_loss, init_acc, init_f1 = evaluate(model, val_loader, criterion, device)
    print(f"  Baseline -> Val Loss: {init_loss:.4f}, Val Acc: {init_acc:.2f}%, Val Macro F1: {init_f1:.2f}%\n", flush=True)

    best_f1 = init_f1
    best_model_weights = copy.deepcopy(model.state_dict())

    total_training_start = time.time()

    for epoch in range(1, args.epochs + 1):
        print(f"\n  [EPOCH {epoch}/{args.epochs}] Starting training on {len(train_samples)} images...", flush=True)
        epoch_start = time.time()

        train_loss, train_acc = train_one_epoch(model, train_loader, optimizer, criterion, device)
        val_loss, val_acc, val_f1 = evaluate(model, val_loader, criterion, device)

        epoch_elapsed = time.time() - epoch_start
        print(f"  [EPOCH {epoch}/{args.epochs}] Completed in {epoch_elapsed:.1f}s", flush=True)
        print(f"      Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.2f}%", flush=True)
        print(f"      Val Loss  : {val_loss:.4f} | Val Acc  : {val_acc:.2f}% | Val Macro F1: {val_f1:.2f}%", flush=True)

        if val_f1 >= best_f1:
            best_f1 = val_f1
            best_model_weights = copy.deepcopy(model.state_dict())
            print(f"      *** NEW BEST MODEL SAVED (Macro F1: {val_f1:.2f}%) ***", flush=True)

    total_training_time = time.time() - total_training_start
    print(f"\n  Training completed in {total_training_time:.1f}s ({total_training_time/60:.2f} mins)", flush=True)

    # Load best weights
    model.load_state_dict(best_model_weights)

    # Save to vit_areca_classifier_v3
    print(f"\n  Saving best checkpoint to {OUTPUT_V3_DIR}...", flush=True)
    save_checkpoint(model, processor, OUTPUT_V3_DIR, id2label, label2id)

    # Save backup of v3
    v3_backup = PROJECT_ROOT / "backend" / "weights" / "vit_areca_classifier_v3_backup"
    if v3_backup.exists():
        shutil.rmtree(v3_backup)
    shutil.copytree(OUTPUT_V3_DIR, v3_backup)

    # Safely update vit_areca_classifier_v2 for immediate inference pipeline use
    print(f"  Updating live checkpoint at {OUTPUT_V2_DIR}...", flush=True)
    save_checkpoint(model, processor, OUTPUT_V2_DIR, id2label, label2id)

    print("\n" + "=" * 80, flush=True)
    print("  TASK 3 RETRAINING SUCCESSFULLY COMPLETED!", flush=True)
    print(f"  Final Model Performance: Val Macro F1 = {best_f1:.2f}%", flush=True)
    print(f"  Model saved to: {OUTPUT_V3_DIR} and {OUTPUT_V2_DIR}", flush=True)
    print("=" * 80, flush=True)


if __name__ == "__main__":
    main()
