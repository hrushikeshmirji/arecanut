"""
merge_and_partition_dataset.py
===============================
TASK 2: Dataset Merging & Stratified 80/20 Partitioning
-------------------------------------------------------
Merges:
  1. Active verified dataset (dataset_large_scale_verified: 1,878 images)
  2. Sanitized legacy dataset (dataset_legacy_sanitized: 1,269 images)
Into:
  D:/arecanut_project/dataset_unified_v3/
    ├── train/  (80% stratified)
    └── val/    (20% stratified)

Quality Guarantees:
  - Preserves original dataset_large_scale_verified intact (zero data loss)
  - MD5 hash deduplication across the entire combined corpus
  - Stratified 80/20 train/val split per canonical class (seed=42)
  - Strict verification of 0% cross-split leakage (train_hashes ∩ val_hashes == ∅)
  - Metadata manifest generation with full audit trail
"""

import os
import sys
import json
import shutil
import hashlib
from pathlib import Path
from typing import Dict, List, Set, Tuple
from PIL import Image
from sklearn.model_selection import train_test_split

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)

PROJECT_ROOT = Path("D:/arecanut_project").resolve()
ACTIVE_DIR = PROJECT_ROOT / "dataset_large_scale_verified"
SANITIZED_DIR = PROJECT_ROOT / "dataset_legacy_sanitized"
OUTPUT_DIR = PROJECT_ROOT / "dataset_unified_v3"
TRAIN_DIR = OUTPUT_DIR / "train"
VAL_DIR = OUTPUT_DIR / "val"

CANONICAL_CLASSES = [
    "bud_borer",
    "fruit_rot",
    "healthy_leaf",
    "healthy_nut",
    "healthy_trunk",
    "non_areca",
    "stem_bleeding",
    "stem_cracking",
    "yellow_leaf",
]

RANDOM_SEED = 42


def compute_md5(path: Path) -> str:
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def main():
    print("=" * 80)
    print("  TASK 2: DATASET MERGING & STRATIFIED 80/20 PARTITIONING")
    print("=" * 80)

    # 1. Verification of Sources
    if not ACTIVE_DIR.exists():
        print(f"Error: Active dataset directory not found at {ACTIVE_DIR}")
        sys.exit(1)
    if not SANITIZED_DIR.exists():
        print(f"Error: Sanitized legacy dataset directory not found at {SANITIZED_DIR}")
        sys.exit(1)

    print(f"[1] Source 1: Active verified dataset at {ACTIVE_DIR}")
    print(f"    Source 2: Sanitized legacy dataset at {SANITIZED_DIR}")
    print(f"    Target  : Unified v3 dataset at {OUTPUT_DIR}")

    # Prepare directories
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    TRAIN_DIR.mkdir(parents=True, exist_ok=True)
    VAL_DIR.mkdir(parents=True, exist_ok=True)

    for c in CANONICAL_CLASSES:
        (TRAIN_DIR / c).mkdir(parents=True, exist_ok=True)
        (VAL_DIR / c).mkdir(parents=True, exist_ok=True)

    # 2. Collect all candidate files per class with global MD5 deduplication
    print("\n[2] Indexing and de-duplicating all images across both sources...")
    corpus_by_class: Dict[str, List[Tuple[Path, str]]] = {c: [] for c in CANONICAL_CLASSES}
    global_hashes: Set[str] = set()
    total_duplicates = 0

    # Index Source 1: Active dataset (train + val)
    active_count = 0
    for split in ["train", "val"]:
        sdir = ACTIVE_DIR / split
        if not sdir.exists():
            continue
        for c in CANONICAL_CLASSES:
            cdir = sdir / c
            if not cdir.exists():
                continue
            for img_path in cdir.glob("*.*"):
                if img_path.is_file() and img_path.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp", ".webp"}:
                    h = compute_md5(img_path)
                    if h in global_hashes:
                        total_duplicates += 1
                        continue
                    global_hashes.add(h)
                    corpus_by_class[c].append((img_path, h))
                    active_count += 1

    print(f"    Indexed {active_count} unique images from active dataset.")

    # Index Source 2: Sanitized legacy dataset
    legacy_count = 0
    for c in CANONICAL_CLASSES:
        cdir = SANITIZED_DIR / c
        if not cdir.exists():
            continue
        for img_path in cdir.glob("*.*"):
            if img_path.is_file() and img_path.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp", ".webp"}:
                h = compute_md5(img_path)
                if h in global_hashes:
                    total_duplicates += 1
                    continue
                global_hashes.add(h)
                corpus_by_class[c].append((img_path, h))
                legacy_count += 1

    print(f"    Indexed {legacy_count} unique images from sanitized legacy dataset.")
    print(f"    Duplicates skipped: {total_duplicates}")
    total_unique = sum(len(v) for v in corpus_by_class.values())
    print(f"    Total combined unique corpus: {total_unique} images across 9 classes.")

    # 3. Stratified 80/20 Partitioning
    print("\n[3] Performing stratified 80% train / 20% validation split (seed=42)...")
    split_summary = {}
    manifest_records = []
    train_hashes: Set[str] = set()
    val_hashes: Set[str] = set()

    for c in CANONICAL_CLASSES:
        items = corpus_by_class[c]
        if not items:
            print(f"    Warning: No images found for class {c}")
            continue

        paths = [it[0] for it in items]
        hashes = [it[1] for it in items]

        # Stratified 80/20 split
        train_paths, val_paths, train_h, val_h = train_test_split(
            paths, hashes, test_size=0.20, random_state=RANDOM_SEED, shuffle=True
        )

        split_summary[c] = {
            "total": len(items),
            "train": len(train_paths),
            "val": len(val_paths),
            "train_pct": round(len(train_paths) / len(items) * 100.0, 1),
            "val_pct": round(len(val_paths) / len(items) * 100.0, 1),
        }

        # Copy to Train folder
        for idx, (p, h) in enumerate(zip(train_paths, train_h)):
            dest_name = f"{c}_train_{idx+1:04d}{p.suffix.lower()}"
            dest_path = TRAIN_DIR / c / dest_name
            shutil.copy2(p, dest_path)
            train_hashes.add(h)
            manifest_records.append({
                "split": "train",
                "class": c,
                "filename": dest_name,
                "source_path": str(p),
                "md5": h
            })

        # Copy to Val folder
        for idx, (p, h) in enumerate(zip(val_paths, val_h)):
            dest_name = f"{c}_val_{idx+1:04d}{p.suffix.lower()}"
            dest_path = VAL_DIR / c / dest_name
            shutil.copy2(p, dest_path)
            val_hashes.add(h)
            manifest_records.append({
                "split": "val",
                "class": c,
                "filename": dest_name,
                "source_path": str(p),
                "md5": h
            })

    # 4. Strict Leakage Verification Audit
    print("\n[4] Running cryptographic verification audit...")
    leakage = train_hashes.intersection(val_hashes)
    if leakage:
        print(f"FATAL ERROR: Detected {len(leakage)} hash leakages between train and val!")
        sys.exit(1)
    else:
        print("    PASSED: 0% data leakage! train_hashes and val_hashes are cryptographically disjoint (empty intersection).")

    # 5. Image Integrity Audit
    print("\n[5] Auditing image readability across all partitioned files...")
    corrupted_count = 0
    total_copied = 0
    for split_dir in [TRAIN_DIR, VAL_DIR]:
        for img_file in split_dir.rglob("*.*"):
            if img_file.is_file() and img_file.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp", ".webp"}:
                total_copied += 1
                try:
                    with Image.open(img_file) as im:
                        im.verify()
                except Exception:
                    corrupted_count += 1

    print(f"    Total files verified in dataset_unified_v3: {total_copied}")
    print(f"    Corrupted files: {corrupted_count}")

    # 6. Save Manifest & Summary
    manifest_path = OUTPUT_DIR / "dataset_manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump({
            "total_images": total_copied,
            "train_images": len(train_hashes),
            "val_images": len(val_hashes),
            "class_summary": split_summary,
            "manifest": manifest_records
        }, f, indent=2)

    # 7. Print Final Table
    print("\n" + "=" * 80)
    print("  DATASET UNIFIED V3 - FINAL PARTITIONING SUMMARY")
    print("=" * 80)
    print(f"{'Canonical Class':<22} | {'Total':<8} | {'Train (80%)':<12} | {'Val (20%)':<10}")
    print("-" * 60)
    grand_total = 0
    grand_train = 0
    grand_val = 0
    for c, stat in sorted(split_summary.items()):
        grand_total += stat["total"]
        grand_train += stat["train"]
        grand_val += stat["val"]
        print(f"{c:<22} | {stat['total']:<8} | {stat['train']:<12} | {stat['val']:<10}")
    print("-" * 60)
    print(f"{'GRAND TOTAL':<22} | {grand_total:<8} | {grand_train:<12} | {grand_val:<10}")
    print("=" * 80)
    print(f"Manifest written to: {manifest_path}")


if __name__ == "__main__":
    main()
