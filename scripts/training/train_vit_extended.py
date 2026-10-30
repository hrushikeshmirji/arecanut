"""
ArecaGuard - Extended Vision Transformer (ViT) Fine-Tuning Pipeline
===================================================================
Fine-tunes a Vision Transformer on the clean verified dataset:
  - fruit_rot (from male koleroga / Mahali Koleroga)
  - yellow_leaf (Yellow Leaf Disease / Phytoplasma)
  - stem_bleeding (Thielaviopsis paradoxa)
  - bud_borer (Inflorescence & bud borer)
  - stem_cracking (Stem cracking)
  - healthy_nut (Healthy nut bunches)
  - healthy_leaf (Healthy foliage)
  - healthy_trunk (Healthy trunk / foot)

Saves best fine-tuned checkpoint to `backend/weights/vit_areca_classifier_v2`.
"""

from __future__ import annotations

import argparse
import copy
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
from sklearn.metrics import f1_score
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms
from transformers import ViTForImageClassification, ViTImageProcessor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# -- Paths --------------------------------------------------------------------
PROJECT_ROOT = Path("D:/arecanut_project").resolve()
DEFAULT_DATASET_DIR = PROJECT_ROOT / "dataset_clean_verified"
BASE_MODEL_DIR = PROJECT_ROOT / "backend" / "weights" / "vit_areca_classifier"
OUTPUT_MODEL_DIR = PROJECT_ROOT / "backend" / "weights" / "vit_areca_classifier_v2"

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


# -- Dataset Definition -------------------------------------------------------
class PatchClassificationDataset(Dataset):
    """Dataset with on-the-fly torchvision transforms."""

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


def load_dataset_split(
    split_dir: Path,
    classes: List[str],
) -> List[Tuple[Path, int]]:
    """Load samples for a given pre-split directory (train or val)."""
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


def discover_classes(data_dir: Path) -> List[str]:
    """Inspect subdirectories inside train split or data_dir."""
    train_dir = data_dir / "train"
    target = train_dir if train_dir.exists() else data_dir

    classes = []
    for entry in sorted(target.iterdir()):
        if entry.is_dir():
            has_images = any(
                f.suffix.lower() in IMAGE_EXTENSIONS for f in entry.iterdir() if f.is_file()
            )
            if has_images:
                classes.append(entry.name)

    if not classes:
        raise ValueError(f"No valid image classes found inside {target}")

    return sorted(classes)


# -- Training & Validation Loops ----------------------------------------------
def train_one_epoch(
    model: nn.Module,
    loader: DataLoader,
    optimizer: torch.optim.Optimizer,
    criterion: nn.Module,
    device: torch.device,
    use_amp: bool = False,
) -> Tuple[float, float]:
    """Train for one epoch, returning average loss and accuracy percentage."""
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0

    for step, (images, labels) in enumerate(loader, start=1):
        images = images.to(device)
        labels = labels.to(device)

        optimizer.zero_grad()

        if use_amp:
            with torch.amp.autocast("cpu", dtype=torch.bfloat16):
                outputs = model(images)
                logits = outputs.logits
                loss = criterion(logits, labels)
        else:
            outputs = model(images)
            logits = outputs.logits
            loss = criterion(logits, labels)

        loss.backward()

        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()

        running_loss += loss.item() * images.size(0)
        preds = torch.argmax(logits, dim=-1)
        correct += (preds == labels).sum().item()
        total += labels.size(0)

        if step % 5 == 0 or step == len(loader):
            step_loss = running_loss / max(1, total)
            step_acc = (correct / max(1, total)) * 100.0
            print(
                f"\r    Step [{step:>2d}/{len(loader):>2d}] "
                f"Loss: {step_loss:.4f} | Acc: {step_acc:5.2f}%",
                end="",
                flush=True,
            )

    epoch_loss = running_loss / max(1, total)
    epoch_acc = (correct / max(1, total)) * 100.0
    print()
    return epoch_loss, epoch_acc


def evaluate(
    model: nn.Module,
    loader: DataLoader,
    criterion: nn.Module,
    device: torch.device,
    use_amp: bool = False,
) -> Tuple[float, float, float]:
    """Evaluate model on validation loader, returning average loss, accuracy, and macro F1."""
    model.eval()
    running_loss = 0.0
    all_preds: List[int] = []
    all_labels: List[int] = []

    with torch.no_grad():
        for images, labels in loader:
            images = images.to(device)
            labels = labels.to(device)

            if use_amp:
                with torch.amp.autocast("cpu", dtype=torch.bfloat16):
                    outputs = model(images)
                    logits = outputs.logits
                    loss = criterion(logits, labels)
            else:
                outputs = model(images)
                logits = outputs.logits
                loss = criterion(logits, labels)

            running_loss += loss.item() * images.size(0)
            preds = torch.argmax(logits, dim=-1)
            all_preds.extend(preds.cpu().tolist())
            all_labels.extend(labels.cpu().tolist())

    val_loss = running_loss / max(1, len(all_labels))
    val_acc = (np.array(all_preds) == np.array(all_labels)).mean() * 100.0
    val_f1 = f1_score(all_labels, all_preds, average="macro", zero_division=0) * 100.0
    return val_loss, val_acc, val_f1


def save_checkpoint(model: nn.Module, processor: ViTImageProcessor, out_dir: Path):
    """Safely save model checkpoint and processor."""
    out_dir.mkdir(parents=True, exist_ok=True)
    safetensor_path = out_dir / "model.safetensors"
    if safetensor_path.exists():
        try:
            safetensor_path.unlink()
        except Exception as e:
            logger.warning("Could not unlink existing safetensors: %s", e)

    model.save_pretrained(str(out_dir))
    processor.save_pretrained(str(out_dir))
    logger.info("Saved best model weights to %s", out_dir)


# -- Main Training Pipeline ---------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Fine-tune ViT for ArecaGuard Multi-Class")
    parser.add_argument("--epochs", type=int, default=6, help="Number of training epochs (default: 6)")
    parser.add_argument("--batch_size", type=int, default=16, help="Batch size (default: 16)")
    parser.add_argument("--lr", type=float, default=2e-5, help="Learning rate (default: 2e-5)")
    parser.add_argument("--weight_decay", type=float, default=0.01, help="Weight decay (default: 0.01)")
    parser.add_argument(
        "--dataset_dir",
        type=str,
        default=str(DEFAULT_DATASET_DIR),
        help="Path to clean verified dataset",
    )
    args = parser.parse_args()

    data_dir = Path(args.dataset_dir)

    # Setup device & CPU threads
    use_amp = False
    if torch.cuda.is_available():
        device = torch.device("cuda")
        logger.info("Using GPU: %s", torch.cuda.get_device_name(0))
    else:
        device = torch.device("cpu")
        num_threads = min(10, max(1, os.cpu_count() or 4))
        torch.set_num_threads(num_threads)
        use_amp = True
        logger.info("Using CPU with %d threads and bfloat16 AMP acceleration", num_threads)

    # 1. Discover all active classes
    classes = discover_classes(data_dir)
    num_labels = len(classes)
    id2label = {i: c for i, c in enumerate(classes)}
    label2id = {c: i for i, c in enumerate(classes)}

    print("=" * 65)
    print("  ARECAGUARD ViT MULTI-CLASS FINE-TUNING")
    print("=" * 65)
    print(f"Registered {num_labels} classes: {classes}")

    # 2. Load Base ViT Model & Processor
    if not BASE_MODEL_DIR.exists():
        logger.warning(
            "Base checkpoint %s not found. Falling back to google/vit-base-patch16-224",
            BASE_MODEL_DIR,
        )
        model_source = "google/vit-base-patch16-224"
    else:
        model_source = str(BASE_MODEL_DIR)

    logger.info("Loading base processor from %s", model_source)
    processor = ViTImageProcessor.from_pretrained(model_source)

    logger.info(
        "Loading base ViT model from %s with num_labels=%d and ignore_mismatched_sizes=True",
        model_source,
        num_labels,
    )
    model = ViTForImageClassification.from_pretrained(
        model_source,
        num_labels=num_labels,
        id2label=id2label,
        label2id=label2id,
        ignore_mismatched_sizes=True,
    )
    # Enable eager attention for explainability compatibility
    if hasattr(model.config, "_attn_implementation"):
        model.config._attn_implementation = "eager"
    model.to(device)

    # 3. Setup Augmentations & Transforms
    image_mean = getattr(processor, "image_mean", [0.485, 0.456, 0.406])
    image_std = getattr(processor, "image_std", [0.229, 0.224, 0.225])

    train_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomRotation(degrees=15),
        transforms.ColorJitter(brightness=0.1, contrast=0.1),
        transforms.ToTensor(),
        transforms.Normalize(mean=image_mean, std=image_std),
    ])

    val_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=image_mean, std=image_std),
    ])

    # 4. Prepare DataLoaders
    train_dir = data_dir / "train"
    val_dir = data_dir / "val"
    if train_dir.exists() and val_dir.exists():
        train_samples = load_dataset_split(train_dir, classes)
        val_samples = load_dataset_split(val_dir, classes)
    else:
        raise FileNotFoundError(f"Missing train or val directory inside {data_dir}")

    print(f"Loaded {len(train_samples)} training samples, {len(val_samples)} validation samples.")

    train_dataset = PatchClassificationDataset(train_samples, transform=train_transform)
    val_dataset = PatchClassificationDataset(val_samples, transform=val_transform)

    train_loader = DataLoader(
        train_dataset,
        batch_size=args.batch_size,
        shuffle=True,
        num_workers=0,
        drop_last=False,
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=0,
        drop_last=False,
    )

    # 5. Optimizer and Criterion
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=args.lr,
        weight_decay=args.weight_decay,
    )

    print("\n" + "=" * 65)
    print("  STARTING OPTIMIZATION")
    print(f"  Epochs       : {args.epochs}")
    print(f"  Batch Size   : {args.batch_size}")
    print(f"  Learning Rate: {args.lr}")
    print(f"  Weight Decay : {args.weight_decay}")
    print("=" * 65)

    best_val_f1 = 0.0
    history: List[Dict[str, float]] = []
    total_start_time = time.time()

    for epoch in range(1, args.epochs + 1):
        t0 = time.time()
        print(f"\n>> Epoch {epoch}/{args.epochs}")

        train_loss, train_acc = train_one_epoch(
            model=model,
            loader=train_loader,
            optimizer=optimizer,
            criterion=criterion,
            device=device,
            use_amp=use_amp,
        )

        val_loss, val_acc, val_f1 = evaluate(
            model=model,
            loader=val_loader,
            criterion=criterion,
            device=device,
            use_amp=use_amp,
        )

        elapsed = time.time() - t0
        print(
            f"  Result -> Train Loss: {train_loss:.4f} | Train Acc: {train_acc:5.2f}% | "
            f"Val Loss: {val_loss:.4f} | Val Acc: {val_acc:5.2f}% | Val Macro F1: {val_f1:5.2f}% | Time: {elapsed:.1f}s"
        )

        history.append({
            "epoch": epoch,
            "train_loss": train_loss,
            "train_acc": train_acc,
            "val_loss": val_loss,
            "val_acc": val_acc,
            "val_f1": val_f1,
            "time_s": elapsed,
        })

        if val_f1 >= best_val_f1:
            best_val_f1 = val_f1
            save_checkpoint(model, processor, OUTPUT_MODEL_DIR)

    total_time = time.time() - total_start_time

    # Print Final Summary Table
    print("\n" + "=" * 75)
    print("  ViT FINE-TUNING COMPLETE - FINAL METRICS")
    print("=" * 75)
    print("  Epoch | Train Loss | Train Acc |  Val Loss  |  Val Acc  |  Macro F1  | Duration")
    print("  " + "-" * 70)
    for h in history:
        print(
            f"   {h['epoch']:>2d}   |   {h['train_loss']:.4f}   |  {h['train_acc']:5.2f}%   |   "
            f"{h['val_loss']:.4f}   |  {h['val_acc']:5.2f}%   |   {h['val_f1']:5.2f}%   |   {h['time_s']:.1f}s"
        )
    print("  " + "-" * 70)
    print(f"  Best Validation Macro F1 : {best_val_f1:.2f}%")
    print(f"  Total Training Duration  : {total_time:.1f}s ({total_time/60:.2f} min)")
    print(f"  Saved Checkpoint to      : {OUTPUT_MODEL_DIR}")
    print("=" * 75 + "\n")


if __name__ == "__main__":
    main()
