"""
ArecaGuard - Noise Filtering, Canonical Consolidation & Stratified Splitting
=============================================================================
Builds a verified, clean dataset in D:\arecanut_project\dataset_clean_verified\
Classes:
  - fruit_rot (from male koleroga / Mahali_Koleroga)
  - yellow_leaf (from yellow leaf disease)
  - stem_bleeding (from stem bleeding)
  - bud_borer (from bud borer)
  - stem_cracking (from stem cracking)
  - healthy_nut (from healthy nut)
  - healthy_leaf (from healthy leaf)
  - healthy_trunk (from healthy foot + healthy trunk)

Guarantees:
  - Verification with PIL Image.verify()
  - Filtering: resolution >= 224x224 px, aspect ratio between 0.33 and 3.0
  - Deduplication with MD5 hashing to prevent cross-split leakage
  - Stratified 80/20 train/validation split
"""

from __future__ import annotations

import hashlib
import os
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)

import kagglehub
from PIL import Image
from sklearn.model_selection import train_test_split

PROJECT_ROOT = Path("D:/arecanut_project").resolve()
OUTPUT_DIR = PROJECT_ROOT / "dataset_clean_verified"
TRAIN_DIR = OUTPUT_DIR / "train"
VAL_DIR = OUTPUT_DIR / "val"

# Mapping from folder numbers (0-8) and string identifiers to canonical classes
FOLDER_NUM_TO_CANONICAL = {
    "0": "bud_borer",
    "1": "healthy_trunk",  # healthy foot -> healthy trunk
    "2": "healthy_leaf",
    "3": "healthy_nut",
    "4": "healthy_trunk",  # healthy trunk -> healthy trunk
    "5": "fruit_rot",      # Mahali Koleroga
    "6": "stem_cracking",
    "7": "stem_bleeding",
    "8": "yellow_leaf",
}

CANONICAL_CLASSES = [
    "fruit_rot",
    "yellow_leaf",
    "stem_bleeding",
    "bud_borer",
    "stem_cracking",
    "healthy_nut",
    "healthy_leaf",
    "healthy_trunk",
]

MIN_RES = 224
MIN_ASPECT = 0.33
MAX_ASPECT = 3.0


def classify_file(file_path: Path) -> str | None:
    # Check parent directory name if it's 0-8
    parent_name = file_path.parent.name
    if parent_name in FOLDER_NUM_TO_CANONICAL:
        return FOLDER_NUM_TO_CANONICAL[parent_name]

    # Otherwise match filename patterns
    lower = file_path.name.lower()
    if any(k in lower for k in ["koleroga", "mahali", "fruit_rot", "fruit rot"]):
        return "fruit_rot"
    if any(k in lower for k in ["yellow leaf", "yellow_leaf", "yld"]):
        return "yellow_leaf"
    if any(k in lower for k in ["stem bleeding", "stem_bleeding"]):
        return "stem_bleeding"
    if any(k in lower for k in ["bud borer", "bud_borer"]):
        return "bud_borer"
    if any(k in lower for k in ["stem cracking", "stem_cracking"]):
        return "stem_cracking"
    if any(k in lower for k in ["healthy nut", "healthy_nut"]):
        return "healthy_nut"
    if any(k in lower for k in ["healthy leaf", "healthy_leaf"]):
        return "healthy_leaf"
    if any(k in lower for k in ["healthy trunk", "healthy_trunk", "healthy foot", "healthy_foot"]):
        return "healthy_trunk"

    return None


def main():
    print("=" * 70)
    print("  ARECAGUARD CLEAN DATASET PREPROCESSING & STRATIFIED SPLITTING")
    print("=" * 70)

    print("\n[Step 1] Resolving benchmark dataset via kagglehub...")
    dataset_path = kagglehub.dataset_download("sumanthsadiga/arecanut-plant-disease-dataset")
    dataset_path = Path(dataset_path)
    print(f"Dataset root: {dataset_path}")

    # Recreate output directories
    if OUTPUT_DIR.exists():
        print(f"Cleaning previous output directory: {OUTPUT_DIR}")
        shutil.rmtree(OUTPUT_DIR)

    TRAIN_DIR.mkdir(parents=True, exist_ok=True)
    VAL_DIR.mkdir(parents=True, exist_ok=True)
    for cls in CANONICAL_CLASSES:
        (TRAIN_DIR / cls).mkdir(parents=True, exist_ok=True)
        (VAL_DIR / cls).mkdir(parents=True, exist_ok=True)

    print("\n[Step 2] Scanning, validating, deduplicating, and filtering images...")
    seen_md5: Set[str] = set()
    class_valid_files: Dict[str, List[Path]] = {cls: [] for cls in CANONICAL_CLASSES}

    valid_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
    total_scanned = 0
    discarded_unreadable = 0
    discarded_low_res = 0
    discarded_aspect = 0
    discarded_duplicate = 0

    all_files = sorted(dataset_path.rglob("*"))
    for file_path in all_files:
        if not file_path.is_file() or file_path.suffix.lower() not in valid_extensions:
            continue

        total_scanned += 1
        target_cls = classify_file(file_path)
        if target_cls is None:
            continue

        # 1. PIL verification
        try:
            with Image.open(file_path) as img:
                img.verify()
        except Exception:
            discarded_unreadable += 1
            continue

        # 2. Resolution & Aspect ratio check
        try:
            with Image.open(file_path) as img:
                w, h = img.size
                if w < MIN_RES or h < MIN_RES:
                    discarded_low_res += 1
                    continue
                aspect = w / float(h)
                if aspect < MIN_ASPECT or aspect > MAX_ASPECT:
                    discarded_aspect += 1
                    continue
        except Exception:
            discarded_unreadable += 1
            continue

        # 3. MD5 Deduplication
        try:
            file_bytes = file_path.read_bytes()
            md5_hash = hashlib.md5(file_bytes).hexdigest()
            if md5_hash in seen_md5:
                discarded_duplicate += 1
                continue
            seen_md5.add(md5_hash)
        except Exception:
            discarded_unreadable += 1
            continue

        class_valid_files[target_cls].append(file_path)

    print(f"Scanned files: {total_scanned}")
    print(f"Discarded - Unreadable: {discarded_unreadable}")
    print(f"Discarded - Low resolution (<{MIN_RES}x{MIN_RES}): {discarded_low_res}")
    print(f"Discarded - Extreme aspect ratio: {discarded_aspect}")
    print(f"Discarded - Duplicate MD5 hashes: {discarded_duplicate}")

    print("\n[Step 3] Performing 80/20 stratified split per class...")
    summary_rows = []
    total_train = 0
    total_val = 0

    for cls in CANONICAL_CLASSES:
        files = class_valid_files[cls]
        n_total = len(files)
        if n_total == 0:
            print(f"Warning: No valid files found for {cls}!")
            summary_rows.append((cls, 0, 0, 0))
            continue

        if n_total == 1:
            train_files = files
            val_files = []
        else:
            train_files, val_files = train_test_split(
                files, test_size=0.20, random_state=42, shuffle=True
            )

        # Copy to train
        for i, src in enumerate(train_files):
            ext = src.suffix.lower()
            dst = TRAIN_DIR / cls / f"{cls}_train_{i+1:04d}{ext}"
            shutil.copy2(src, dst)

        # Copy to val
        for i, src in enumerate(val_files):
            ext = src.suffix.lower()
            dst = VAL_DIR / cls / f"{cls}_val_{i+1:04d}{ext}"
            shutil.copy2(src, dst)

        n_train = len(train_files)
        n_val = len(val_files)
        total_train += n_train
        total_val += n_val
        summary_rows.append((cls, n_train, n_val, n_total))

    # Print summary table
    print("\n" + "=" * 65)
    print(f"{'Class Name':<20} | {'Train Count':<12} | {'Val Count':<10} | {'Total':<8}")
    print("-" * 65)
    for cls, n_train, n_val, n_total in summary_rows:
        print(f"{cls:<20} | {n_train:<12} | {n_val:<10} | {n_total:<8}")
    print("-" * 65)
    print(f"{'TOTAL':<20} | {total_train:<12} | {total_val:<10} | {total_train + total_val:<8}")
    print("=" * 65)
    print(f"\n[DONE] Clean stratified dataset generated at: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
