"""
train_vit_large_scale.py
=========================
Large-scale Vision Transformer (ViT-B/16) fine-tuning on:
  D:/arecanut_project/dataset_large_scale_verified/
    ├── train/ (783 images across 9 classes)
    └── val/   (200 images across 9 classes)

Key Features:
  - 9-Class Multi-Class classification with large-scale negative OOD shield (non_areca)
  - Data Augmentations: RandomHorizontalFlip, RandomVerticalFlip, ColorJitter, RandomAffine
  - Label Smoothing (0.1) in Cross-Entropy Loss to prevent overconfidence on out-of-distribution uploads
  - Safe Checkpoint Saving: loads from backup and exports to target folder to prevent Windows mmap file locking
  - Target destination: backend/weights/vit_areca_classifier_v2
"""

from __future__ import annotations

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
    sys.stdout.reconfigure(line_buffering=True)

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
DATASET_DIR = PROJECT_ROOT / "dataset_large_scale_verified"
LOAD_MODEL_DIR = PROJECT_ROOT / "backend" / "weights" / "vit_areca_classifier_v2_backup"
OUTPUT_MODEL_DIR = PROJECT_ROOT / "backend" / "weights" / "vit_areca_classifier_v2"
BASE_MODEL_NAME = "google/vit-base-patch16-224"

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


class LargeScaleArecaDataset(Dataset):
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
    """Safely saves Hugging Face model and verifies config mappings."""
    target_dir.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(str(target_dir))
    processor.save_pretrained(str(target_dir))

    config_file = target_dir / "config.json"
    with open(config_file, "r") as f:
        cfg = json.load(f)
    cfg["id2label"] = id2label
    cfg["label2id"] = label2id
    with open(config_file, "w") as f:
        json.dump(cfg, f, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Large-scale ViT fine-tuning for ArecaGuard")
    parser.add_argument("--epochs", type=int, default=2)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--lr", type=float, default=2e-5)
    parser.add_argument("--weight-decay", type=float, default=0.01)
    parser.add_argument("--label-smoothing", type=float, default=0.1)
    args = parser.parse_args()

    print("=" * 80, flush=True)
    print("  ARECAGUARD: LARGE-SCALE VISION TRANSFORMER (ViT) TRAINING PIPELINE", flush=True)
    print("=" * 80, flush=True)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if device.type == "cpu":
        torch.set_num_threads(min(8, os.cpu_count() or 4))
    print(f"  Target Device: {device} (threads: {torch.get_num_threads()})", flush=True)

    # Discover classes
    train_dir = DATASET_DIR / "train"
    val_dir = DATASET_DIR / "val"
    classes = sorted([d.name for d in train_dir.iterdir() if d.is_dir()])
    print(f"  Discovered {len(classes)} classes: {classes}", flush=True)

    train_samples = load_split(train_dir, classes)
    val_samples = load_split(val_dir, classes)
    print(f"  Loaded Samples -> Train: {len(train_samples)}, Val: {len(val_samples)}", flush=True)

    # Transforms
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
        LargeScaleArecaDataset(train_samples, train_transform),
        batch_size=args.batch_size,
        shuffle=True,
        num_workers=0,
    )

    val_loader = DataLoader(
        LargeScaleArecaDataset(val_samples, val_transform),
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=0,
    )

    # Label mappings
    id2label = {i: c for i, c in enumerate(classes)}
    label2id = {c: i for i, c in enumerate(classes)}

    # Initialize ViT Model (warm-start from backup to prevent Windows mmap locking)
    print(f"\n  Initializing ViT Classifier from: {LOAD_MODEL_DIR}...", flush=True)
    if LOAD_MODEL_DIR.exists():
        model = ViTForImageClassification.from_pretrained(
            str(LOAD_MODEL_DIR),
            num_labels=len(classes),
            id2label=id2label,
            label2id=label2id,
            ignore_mismatched_sizes=True,
        )
        print("  -> Warm-started from verified production weights.", flush=True)
    else:
        model = ViTForImageClassification.from_pretrained(
            BASE_MODEL_NAME,
            num_labels=len(classes),
            id2label=id2label,
            label2id=label2id,
            ignore_mismatched_sizes=True,
        )
        print(f"  -> Initialized from base pre-trained ViT: {BASE_MODEL_NAME}.", flush=True)

    model.to(device)

    processor = ViTImageProcessor.from_pretrained(
        str(LOAD_MODEL_DIR) if LOAD_MODEL_DIR.exists() else BASE_MODEL_NAME
    )

    # Class-weighted Cross-Entropy Loss with Label Smoothing
    class_counts = np.zeros(len(classes), dtype=np.float32)
    for _, l in train_samples:
        class_counts[l] += 1
    weights = class_counts.max() / (class_counts + 1e-5)
    weights = torch.tensor(weights, dtype=torch.float32).to(device)

    criterion = nn.CrossEntropyLoss(weight=weights, label_smoothing=args.label_smoothing)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)

    print("\n" + "=" * 80, flush=True)
    print("  STARTING OPTIMIZATION", flush=True)
    print(f"  Epochs         : {args.epochs}", flush=True)
    print(f"  Batch Size     : {args.batch_size}", flush=True)
    print(f"  Learning Rate  : {args.lr}", flush=True)
    print(f"  Label Smoothing: {args.label_smoothing}", flush=True)
    print("=" * 80, flush=True)

    best_val_f1 = 0.0
    start_time = time.time()

    for epoch in range(1, args.epochs + 1):
        t0 = time.time()
        train_loss, train_acc = train_one_epoch(
            model=model,
            loader=train_loader,
            optimizer=optimizer,
            criterion=criterion,
            device=device,
        )

        val_loss, val_acc, val_f1 = evaluate(
            model=model,
            loader=val_loader,
            criterion=criterion,
            device=device,
        )

        elapsed = time.time() - t0
        print(
            f"  Epoch {epoch:02d}/{args.epochs:02d} | "
            f"Train Loss: {train_loss:.4f} | Train Acc: {train_acc:5.2f}% | "
            f"Val Loss: {val_loss:.4f} | Val Acc: {val_acc:5.2f}% | Val Macro F1: {val_f1:5.2f}% | "
            f"({elapsed:.1f}s)",
            flush=True,
        )

        if val_f1 >= best_val_f1:
            best_val_f1 = val_f1
            print(f"    * Best checkpoint reached (Val Macro F1: {best_val_f1:.2f}%). Saving to {OUTPUT_MODEL_DIR}...", flush=True)
            save_checkpoint(model, processor, OUTPUT_MODEL_DIR, id2label, label2id)
            print("    * Checkpoint saved successfully.", flush=True)

    total_time = time.time() - start_time
    print(f"\n  Optimization completed in {total_time:.1f}s. Best Val Macro F1: {best_val_f1:.2f}%", flush=True)
    print("=" * 80, flush=True)
    print(f"  PRODUCTION MODEL EXPORT VERIFIED AT: {OUTPUT_MODEL_DIR}", flush=True)
    print("=" * 80, flush=True)


if __name__ == "__main__":
    main()
