"""
export_flat_dataset_by_disease.py
==================================
Exports all 4,151 images from dataset_unified_v4 into:
  D:/arecanut_dataset/<disease_name>/

Structure:
  D:/arecanut_dataset/
    ├── bud_borer/       (176 images)
    ├── fruit_rot/       (804 images)
    ├── healthy_leaf/    (308 images)
    ├── healthy_nut/     (808 images)
    ├── healthy_trunk/   (288 images)
    ├── non_areca/       (494 images)
    ├── stem_bleeding/   (198 images)
    ├── stem_cracking/   (192 images)
    └── yellow_leaf/     (883 images)

No 'train', 'val', or 'test' folders. Pure disease-named directories.
Filenames formatted cleanly as: <disease>_0001.jpg, <disease>_0002.jpg ...
"""

import os
import sys
import shutil
import hashlib
from pathlib import Path
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SOURCE_DIR = Path(r"D:\arecanut_project\dataset_unified_v4")
TARGET_DIR = Path(r"D:\arecanut_dataset")

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

def main():
    print("=" * 70)
    print("EXPORTING UNIFIED DATASET BY DISEASE NAME")
    print(f"Source: {SOURCE_DIR}")
    print(f"Target: {TARGET_DIR}")
    print("=" * 70)

    TARGET_DIR.mkdir(parents=True, exist_ok=True)

    # Collect images per class from both train and val
    class_files = defaultdict(list)
    seen_hashes = defaultdict(set)

    for split in ["train", "val"]:
        split_dir = SOURCE_DIR / split
        if not split_dir.exists():
            continue
        for cls_name in CANONICAL_CLASSES:
            cls_dir = split_dir / cls_name
            if not cls_dir.exists():
                continue
            for f in sorted(cls_dir.iterdir()):
                if f.is_file() and f.suffix.lower() in [".jpg", ".jpeg", ".png"]:
                    # MD5 check to ensure 100% uniqueness
                    with open(f, "rb") as fp:
                        h = hashlib.md5(fp.read()).hexdigest()
                    if h not in seen_hashes[cls_name]:
                        seen_hashes[cls_name].add(h)
                        class_files[cls_name].append((f, h))

    total_exported = 0

    print("\nCopying and indexing images into disease folders...")
    for cls_name in CANONICAL_CLASSES:
        out_cls_dir = TARGET_DIR / cls_name
        out_cls_dir.mkdir(parents=True, exist_ok=True)

        items = class_files[cls_name]
        for idx, (src_file, h) in enumerate(items, 1):
            ext = src_file.suffix.lower()
            dst_name = f"{cls_name}_{idx:04d}{ext}"
            dst_path = out_cls_dir / dst_name
            shutil.copy2(src_file, dst_path)

        total_exported += len(items)
        print(f"  {cls_name:<16}: {len(items):>5} images -> {out_cls_dir}")

    print("\n" + "=" * 70)
    print(f"EXPORT COMPLETED SUCCESSFULLY!")
    print(f"Total Unique Images Exported: {total_exported}")
    print(f"Destination: {TARGET_DIR}")
    print("=" * 70)

    # Write a handy README in the destination folder
    readme_path = TARGET_DIR / "README.txt"
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write("ArecaGuard AI Engine - Dataset Image Bank for Model Testing\n")
        f.write("============================================================\n\n")
        f.write("This directory contains all 4,151 authentic images used in the project,\n")
        f.write("organized strictly by disease name for testing model predictions.\n\n")
        f.write("Folder Breakdown:\n")
        for cls_name in CANONICAL_CLASSES:
            f.write(f"  - {cls_name:<16}: {len(class_files[cls_name])} images\n")
        f.write(f"\nTotal: {total_exported} images\n\n")
        f.write("Instructions:\n")
        f.write("1. Open any disease folder above.\n")
        f.write("2. Drag and drop any image into the ArecaGuard Web UI (http://localhost:5173).\n")
        f.write("3. Verify the AI model's diagnosis, confidence, and 5-stage explainability output.\n")

if __name__ == "__main__":
    main()
