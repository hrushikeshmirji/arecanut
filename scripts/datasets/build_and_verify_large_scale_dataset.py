"""
build_and_verify_large_scale_dataset.py
=========================================
Builds a large-scale, multi-verified dataset in:
  D:/arecanut_project/dataset_large_scale_verified/
    ├── train/  (80%)
    └── val/    (20%)

Canonical Classes (9 classes):
  1. fruit_rot       (Mahali Koleroga / Phytophthora meadii)
  2. yellow_leaf     (Yellow Leaf Disease / Phytoplasma)
  3. stem_bleeding   (Thielaviopsis paradoxa)
  4. bud_borer       (Inflorescence & bud borer / Carvalhoia arecae)
  5. stem_cracking   (Stem cracking / Sun scald)
  6. healthy_nut     (Healthy nut bunches)
  7. healthy_leaf    (Healthy leaf fronds)
  8. healthy_trunk   (Healthy palm trunk and foot)
  9. non_areca       (Out-of-Distribution / Lookalikes, fruits, furniture, humans, other plants)

Strict 5-Level Verification Gates:
  - Gate 1: Byte decodability & PIL.Image.verify()
  - Gate 2: Resolution check (>= 224x224 px) & Aspect ratio (0.33 <= w/h <= 3.0)
  - Gate 3: MD5 deduplication (zero cross-split leakage)
  - Gate 4: Pixel variance check (rejects solid/corrupted images)
  - Gate 5: Stratified 80/20 train/validation split
"""

from __future__ import annotations

import hashlib
import json
import os
import random
import shutil
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Set, Tuple

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)

import numpy as np
from PIL import Image
from sklearn.model_selection import train_test_split

PROJECT_ROOT = Path("D:/arecanut_project").resolve()
OUTPUT_DIR = PROJECT_ROOT / "dataset_large_scale_verified"
TRAIN_DIR = OUTPUT_DIR / "train"
VAL_DIR = OUTPUT_DIR / "val"

KAGGLE_CACHE_DIR = Path(
    r"C:\Users\Hrushikesh Mirji\.cache\kagglehub\datasets\sumanthsadiga\arecanut-plant-disease-dataset\versions\1\dataset"
)

# Canonical mapping for Kaggle folders (0-8)
KAGGLE_FOLDER_TO_CANONICAL = {
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

MIN_RES = 224
MIN_ASPECT = 0.33
MAX_ASPECT = 3.0
MIN_VARIANCE = 15.0  # std dev of pixel intensities to reject blank/solid images


def compute_md5(img_path: Path) -> str:
    with open(img_path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def compute_bytes_md5(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


def verify_image(img_path: Path) -> Tuple[bool, str]:
    """Applies Gate 1, 2, 4 checks on a file."""
    try:
        # Gate 1: Byte decodability & verification
        with Image.open(img_path) as im:
            im.verify()

        # Re-open for dimension and variance check
        with Image.open(img_path) as im:
            im = im.convert("RGB")
            w, h = im.size

            # Gate 2: Resolution & aspect ratio
            if w < MIN_RES or h < MIN_RES:
                return False, f"Resolution too low ({w}x{h} < {MIN_RES})"

            aspect = w / float(h)
            if aspect < MIN_ASPECT or aspect > MAX_ASPECT:
                return False, f"Aspect ratio extreme ({aspect:.2f})"

            # Gate 4: Variance sanity check
            arr = np.array(im, dtype=np.float32)
            std = float(arr.std())
            if std < MIN_VARIANCE:
                return False, f"Low pixel variance ({std:.1f} < {MIN_VARIANCE})"

        return True, "OK"
    except Exception as e:
        return False, f"Corrupted or unreadable: {e}"


def download_negative_sample(p_id: int, timeout: int = 6) -> Tuple[bytes | None, str | None]:
    """Download clean negative sample from Picsum / open public vision sources."""
    url = f"https://picsum.photos/id/{p_id}/320/320"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
        return data, compute_bytes_md5(data)
    except Exception:
        return None, None


def main():
    print("=" * 80)
    print("  ARECAGUARD: LARGE-SCALE DATASET INGESTION & 5-STAGE MULTI-VERIFICATION")
    print("=" * 80)

    # 1. Clean destination directories
    if OUTPUT_DIR.exists():
        print(f"[1] Cleaning existing {OUTPUT_DIR}...")
        shutil.rmtree(OUTPUT_DIR)

    TRAIN_DIR.mkdir(parents=True, exist_ok=True)
    VAL_DIR.mkdir(parents=True, exist_ok=True)
    for c in CANONICAL_CLASSES:
        (TRAIN_DIR / c).mkdir(parents=True, exist_ok=True)
        (VAL_DIR / c).mkdir(parents=True, exist_ok=True)

    # 2. Ingest from verified Kaggle benchmark (all train + test splits)
    print("\n[2] Ingesting & Verifying Arecanut Classes from Kaggle Benchmark...")
    raw_images_by_class: Dict[str, List[Path]] = {c: [] for c in CANONICAL_CLASSES if c != "non_areca"}
    global_seen_hashes: Set[str] = set()

    rejection_reasons: Dict[str, int] = {}
    verified_count = 0

    if not KAGGLE_CACHE_DIR.exists():
        raise FileNotFoundError(f"Kaggle cache not found at {KAGGLE_CACHE_DIR}")

    # Process all subfolders in train and test
    for split_folder in ["train", "test"]:
        split_path = KAGGLE_CACHE_DIR / split_folder
        if not split_path.exists():
            continue

        for folder_entry in sorted(split_path.iterdir()):
            if not folder_entry.is_dir():
                continue
            folder_key = folder_entry.name.strip()
            canonical_class = KAGGLE_FOLDER_TO_CANONICAL.get(folder_key)
            if not canonical_class:
                continue

            for img_file in sorted(folder_entry.glob("*.*")):
                if img_file.suffix.lower() not in {".jpg", ".jpeg", ".png", ".bmp", ".webp"}:
                    continue

                # Run Gate 1, 2, 4
                is_valid, reason = verify_image(img_file)
                if not is_valid:
                    rejection_reasons[reason] = rejection_reasons.get(reason, 0) + 1
                    continue

                # Gate 3: Deduplication
                h = compute_md5(img_file)
                if h in global_seen_hashes:
                    rejection_reasons["Duplicate MD5 hash"] = rejection_reasons.get("Duplicate MD5 hash", 0) + 1
                    continue

                global_seen_hashes.add(h)
                raw_images_by_class[canonical_class].append(img_file)
                verified_count += 1

    print(f"    Verified {verified_count} arecanut images across 8 classes.")
    if rejection_reasons:
        print("    Filter rejections:", rejection_reasons)

    # 3. Build & Verify Expanded Negative OOD Class (non_areca)
    print("\n[3] Ingesting & Verifying Non-Areca (OOD Negative) Samples...")
    non_areca_images: List[Tuple[bytes, str]] = []
    seen_negative_hashes: Set[str] = set()

    # Download high-diversity negative images across ids 1 to 350
    candidate_ids = list(range(1, 350))
    random.seed(42)
    random.shuffle(candidate_ids)

    print(f"    Fetching diverse negative images across {len(candidate_ids)} candidates...")
    with ThreadPoolExecutor(max_workers=12) as executor:
        futures = {executor.submit(download_negative_sample, pid): pid for pid in candidate_ids}
        for future in as_completed(futures):
            data, h = future.result()
            if data and h and h not in global_seen_hashes and h not in seen_negative_hashes:
                # Gate 1, 2, 4 on in-memory bytes
                try:
                    from io import BytesIO
                    with Image.open(BytesIO(data)) as im:
                        im.verify()
                    with Image.open(BytesIO(data)) as im:
                        im = im.convert("RGB")
                        w, h_dim = im.size
                        if w >= MIN_RES and h_dim >= MIN_RES:
                            arr = np.array(im, dtype=np.float32)
                            if float(arr.std()) >= MIN_VARIANCE:
                                non_areca_images.append((data, h))
                                seen_negative_hashes.add(h)
                                global_seen_hashes.add(h)
                                if len(non_areca_images) >= 200:
                                    break
                except Exception:
                    pass

    print(f"    Verified {len(non_areca_images)} high-diversity non-areca negative samples.")

    # 4. Stratified 80/20 Train/Validation Split for all 9 classes
    print("\n[4] Executing Stratified 80/20 Train/Validation Split...")
    final_stats: Dict[str, Dict[str, int]] = {}

    # Process 8 Arecanut Classes
    for cls_name, img_paths in raw_images_by_class.items():
        random.seed(42)
        random.shuffle(img_paths)

        # 80/20 split
        train_paths, val_paths = train_test_split(img_paths, test_size=0.20, random_state=42)

        # Copy to train
        for idx, src_p in enumerate(train_paths):
            dest_p = TRAIN_DIR / cls_name / f"{cls_name}_train_{idx+1:04d}.jpg"
            with Image.open(src_p) as im:
                im.convert("RGB").save(dest_p, "JPEG", quality=95)

        # Copy to val
        for idx, src_p in enumerate(val_paths):
            dest_p = VAL_DIR / cls_name / f"{cls_name}_val_{idx+1:04d}.jpg"
            with Image.open(src_p) as im:
                im.convert("RGB").save(dest_p, "JPEG", quality=95)

        final_stats[cls_name] = {
            "train": len(train_paths),
            "val": len(val_paths),
            "total": len(train_paths) + len(val_paths),
        }

    # Process non_areca class
    random.seed(42)
    random.shuffle(non_areca_images)
    n_train = int(len(non_areca_images) * 0.80)
    train_na = non_areca_images[:n_train]
    val_na = non_areca_images[n_train:]

    from io import BytesIO
    for idx, (data, _) in enumerate(train_na):
        dest_p = TRAIN_DIR / "non_areca" / f"non_areca_train_{idx+1:04d}.jpg"
        with Image.open(BytesIO(data)) as im:
            im.convert("RGB").save(dest_p, "JPEG", quality=95)

    for idx, (data, _) in enumerate(val_na):
        dest_p = VAL_DIR / "non_areca" / f"non_areca_val_{idx+1:04d}.jpg"
        with Image.open(BytesIO(data)) as im:
            im.convert("RGB").save(dest_p, "JPEG", quality=95)

    final_stats["non_areca"] = {
        "train": len(train_na),
        "val": len(val_na),
        "total": len(train_na) + len(val_na),
    }

    # 5. Print Verification & Balance Summary
    print("\n" + "=" * 80)
    print(f"  {'CLASS NAME':<18} | {'TRAIN (80%)':<12} | {'VAL (20%)':<10} | {'TOTAL IMAGES':<12}")
    print("=" * 80)
    tot_train = 0
    tot_val = 0
    for c in CANONICAL_CLASSES:
        st = final_stats[c]
        tot_train += st["train"]
        tot_val += st["val"]
        print(f"  {c:<18} | {st['train']:<12} | {st['val']:<10} | {st['total']:<12}")
    print("=" * 80)
    print(f"  {'GRAND TOTAL':<18} | {tot_train:<12} | {tot_val:<10} | {tot_train + tot_val:<12}")
    print("=" * 80)

    # 6. Final Leakage Check (Gate 3 Confirmation)
    print("\n[5] Running Final Cross-Split Leakage Check...")
    train_hashes = {compute_md5(p) for p in TRAIN_DIR.rglob("*.*") if p.is_file()}
    val_hashes = {compute_md5(p) for p in VAL_DIR.rglob("*.*") if p.is_file()}
    leakage = train_hashes.intersection(val_hashes)

    assert len(leakage) == 0, f"Critical Data Leakage Detected: {len(leakage)} overlapping images!"
    print(f"  -> ZERO cross-split data leakage verified. Train hashes: {len(train_hashes)}, Val hashes: {len(val_hashes)}.")
    print("  -> ALL GATES PASSED! Clean large-scale dataset ready at:")
    print(f"     {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
