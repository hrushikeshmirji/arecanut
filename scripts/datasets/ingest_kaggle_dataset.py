"""
ArecaGuard - Kaggle Dataset Ingestion & Clean Multi-Class Setup
===============================================================
Maps verified classes from `sumanthsadiga/arecanut-plant-disease-dataset`
into `D:\arecanut_project\dataset_multiclass_clean\`:
  * `male koleroga` / `mahali koleroga` -> `fruit_rot`
  * `yellow leaf` -> `yellow_leaf`
  * `stem bleeding` -> `stem_bleeding`
  * `healthy nut` -> `healthy_nut`
  * `healthy leaf` -> `healthy_leaf`

Filters:
  * Remove files under 200x200 resolution.
  * Remove corrupted files.
  * Deduplicate via SHA-256 hash.
"""
from __future__ import annotations

import hashlib
import os
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Set

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)

import kagglehub
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CLEAN_DIR = PROJECT_ROOT / "dataset_multiclass_clean"

CLASS_MAP: Dict[str, List[str]] = {
    "fruit_rot":     ["koleroga", "mahali", "male koleroga"],
    "yellow_leaf":   ["yellow leaf"],
    "stem_bleeding": ["stem_bleeding", "stem bleeding"],
    "healthy_nut":   ["healthy_nut", "healthy nut"],
    "healthy_leaf":  ["healthy_leaf", "healthy leaf"],
}

MIN_DIM = 200


def get_class_for_file(filename: str) -> str | None:
    lower = filename.lower()
    for canonical, patterns in CLASS_MAP.items():
        for pat in patterns:
            if pat in lower:
                return canonical
    return None


def main():
    print("=" * 65)
    print("  ARECAGUARD KAGGLE DATASET INGESTION")
    print("=" * 65)

    print("\n[1] Resolving dataset via kagglehub...")
    dataset_path = kagglehub.dataset_download("sumanthsadiga/arecanut-plant-disease-dataset")
    dataset_path = Path(dataset_path)
    print(f"    Resolved at: {dataset_path}")

    # Recreate clean target directory
    if CLEAN_DIR.exists():
        shutil.rmtree(CLEAN_DIR)
    CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    for c in CLASS_MAP:
        (CLEAN_DIR / c).mkdir(parents=True, exist_ok=True)

    print("\n[2] Scanning and filtering images (>= 200x200)...")
    seen_hashes: Set[str] = set()
    counts: Dict[str, int] = {c: 0 for c in CLASS_MAP}
    corrupt_count = 0
    small_count = 0
    duplicate_count = 0

    extensions = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

    for f in sorted(dataset_path.rglob("*")):
        if not f.is_file() or f.suffix.lower() not in extensions:
            continue

        canonical_cls = get_class_for_file(f.name)
        if not canonical_cls:
            continue

        # Corruption & resolution check
        try:
            with Image.open(f) as img:
                img.verify()
            with Image.open(f) as img:
                img = img.convert("RGB")
                w, h = img.size
                if w < MIN_DIM or h < MIN_DIM:
                    small_count += 1
                    continue
                data = f.read_bytes()
                h_val = hashlib.sha256(data).hexdigest()
                if h_val in seen_hashes:
                    duplicate_count += 1
                    continue
                seen_hashes.add(h_val)

                dest = CLEAN_DIR / canonical_cls / f"{canonical_cls}_{counts[canonical_cls]:04d}.jpg"
                img.save(dest, "JPEG", quality=95)
                counts[canonical_cls] += 1
        except Exception:
            corrupt_count += 1
            continue

    print("\n[3] Ingestion & Quality Filter Report:")
    print(f"    Excluded (<200x200) : {small_count}")
    print(f"    Corrupted/Unreadable: {corrupt_count}")
    print(f"    Duplicate Copies    : {duplicate_count}")

    print("\n" + "=" * 65)
    print("  FINAL CLEAN DATASET SUMMARY")
    print("=" * 65)
    grand_total = 0
    for cls, cnt in counts.items():
        grand_total += cnt
        print(f"    {cls:<20s}: {cnt:>5d} verified images")
    print("  " + "-" * 50)
    print(f"    {'TOTAL':<20s}: {grand_total:>5d} images")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    main()
