"""
build_dataset_unified_v4.py
===========================
Constructs dataset_unified_v4 by combining:
1. dataset_unified_v3 (3,147 verified images across 9 classes)
2. Kannadapranesh Kaggle Arecanut_YellowBrownSpot (681 authentic 12MP images -> yellow_leaf)
3. Kannadapranesh Kaggle Healthy_Leaves (123 authentic images -> healthy_leaf)
4. Kannadapranesh Kaggle Coconut Palm Field Images (200 authentic DSLR images -> non_areca)

Enforces 5 quality gates:
1. Valid decodable PIL Image
2. Minimum dimension >= 224x224 px
3. Laplacian variance >= 15.0 (non-blurry)
4. Full MD5 hash deduplication
5. Stratified 80/20 train/val split with 0% cross-split leakage
"""

import os
import sys
import shutil
import hashlib
import random
import cv2
import numpy as np
from PIL import Image
from pathlib import Path
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RANDOM_SEED = 42
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

PROJECT_ROOT = Path(r"D:\arecanut_project")
SOURCE_V3 = PROJECT_ROOT / "dataset_unified_v3"
DEST_V4 = PROJECT_ROOT / "dataset_unified_v4"

KAGGLE_BASE = Path(r"C:\Users\Hrushikesh Mirji\.cache\kagglehub\datasets\kannadapranesh\coconut-and-arecanut-diseases\versions\1\archive")

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

def compute_md5(file_path):
    hasher = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

def check_image_quality(file_path, min_dim=224, min_var=15.0):
    try:
        with Image.open(file_path) as img:
            w, h = img.size
            if w < min_dim or h < min_dim:
                return False, f"Resolution too low: {w}x{h}"
        
        cv_img = cv2.imread(str(file_path), cv2.IMREAD_GRAYSCALE)
        if cv_img is None:
            return False, "Failed to decode with OpenCV"
        var = cv2.Laplacian(cv_img, cv2.CV_64F).var()
        if var < min_var:
            return False, f"Blurry: variance {var:.1f} < {min_var}"
        return True, "OK"
    except Exception as e:
        return False, str(e)

def main():
    print("=" * 70)
    print("BUILDING DATASET UNIFIED V4")
    print("=" * 70)

    # 1. Collect all images from dataset_unified_v3
    print("\n[Step 1] Indexing dataset_unified_v3...")
    class_images = defaultdict(list)
    global_hashes = {}
    
    for split in ["train", "val"]:
        split_dir = SOURCE_V3 / split
        if not split_dir.exists():
            continue
        for cls_name in os.listdir(split_dir):
            if cls_name not in CANONICAL_CLASSES:
                continue
            cls_dir = split_dir / cls_name
            for f in os.listdir(cls_dir):
                if f.lower().endswith((".jpg", ".jpeg", ".png")):
                    fp = cls_dir / f
                    h = compute_md5(fp)
                    if h not in global_hashes:
                        global_hashes[h] = fp
                        class_images[cls_name].append((fp, h, "v3"))
                        
    for c in CANONICAL_CLASSES:
        print(f"  v3 {c}: {len(class_images[c])} images")
    print(f"Total unique images from v3: {len(global_hashes)}")

    # 2. Ingest Kaggle Arecanut_YellowBrownSpot -> yellow_leaf
    print("\n[Step 2] Ingesting Kaggle Arecanut_YellowBrownSpot -> yellow_leaf...")
    spot_dir = KAGGLE_BASE / "Arecanut_YellowBrownSpot" / "Arecanut_YellowBrownSpot"
    spot_added = 0
    if spot_dir.exists():
        for f in os.listdir(spot_dir):
            if f.lower().endswith((".jpg", ".jpeg", ".png")):
                fp = spot_dir / f
                h = compute_md5(fp)
                if h in global_hashes:
                    continue
                valid, reason = check_image_quality(fp)
                if valid:
                    global_hashes[h] = fp
                    class_images["yellow_leaf"].append((fp, h, "kaggle_spot"))
                    spot_added += 1
    print(f"  Added {spot_added} new authentic images to yellow_leaf (now {len(class_images['yellow_leaf'])})")

    # 3. Ingest Kaggle Healthy_Leaves -> healthy_leaf
    print("\n[Step 3] Ingesting Kaggle Healthy_Leaves -> healthy_leaf...")
    healthy_dir = KAGGLE_BASE / "Healthy_Leaves" / "Healthy_Leaves"
    healthy_added = 0
    if healthy_dir.exists():
        for f in os.listdir(healthy_dir):
            if f.lower().endswith((".jpg", ".jpeg", ".png")):
                fp = healthy_dir / f
                h = compute_md5(fp)
                if h in global_hashes:
                    continue
                valid, reason = check_image_quality(fp)
                if valid:
                    global_hashes[h] = fp
                    class_images["healthy_leaf"].append((fp, h, "kaggle_healthy"))
                    healthy_added += 1
    print(f"  Added {healthy_added} new authentic images to healthy_leaf (now {len(class_images['healthy_leaf'])})")

    # 4. Ingest Kaggle Coconut Field Images -> non_areca (200 images sampled evenly)
    print("\n[Step 4] Ingesting Kaggle Coconut Field Images -> non_areca...")
    coco_cats = ["CCI_Leaflets", "WCLWD_DryingofLeaflets", "WCLWD_Flaccidity", "WCLWD_Yellowing"]
    coco_added = 0
    for cat in coco_cats:
        cat_dir = KAGGLE_BASE / cat / cat
        if not cat_dir.exists():
            continue
        files = [f for f in os.listdir(cat_dir) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
        random.shuffle(files)
        cat_added = 0
        for f in files:
            if cat_added >= 50:  # 50 per category = 200 total
                break
            fp = cat_dir / f
            h = compute_md5(fp)
            if h in global_hashes:
                continue
            valid, reason = check_image_quality(fp)
            if valid:
                global_hashes[h] = fp
                class_images["non_areca"].append((fp, h, f"kaggle_coco_{cat}"))
                cat_added += 1
                coco_added += 1
        print(f"  Added {cat_added} from {cat}")
    print(f"  Total added to non_areca: {coco_added} (now {len(class_images['non_areca'])})")

    # 5. Summary of Unified V4
    total_v4 = sum(len(imgs) for imgs in class_images.values())
    print("\n" + "=" * 70)
    print(f"TOTAL UNIFIED V4 IMAGES: {total_v4}")
    for c in CANONICAL_CLASSES:
        print(f"  {c:<16}: {len(class_images[c]):>5} images")
    print("=" * 70)

    # 6. Stratified 80/20 train/validation split
    print("\n[Step 5] Performing Stratified 80/20 Train/Validation Split...")
    if DEST_V4.exists():
        print(f"  Cleaning existing {DEST_V4}...")
        shutil.rmtree(DEST_V4)

    train_hashes = set()
    val_hashes = set()
    train_counts = defaultdict(int)
    val_counts = defaultdict(int)

    for c in CANONICAL_CLASSES:
        imgs = class_images[c]
        random.shuffle(imgs)
        split_idx = int(0.80 * len(imgs))
        train_set = imgs[:split_idx]
        val_set = imgs[split_idx:]

        target_train_dir = DEST_V4 / "train" / c
        target_val_dir = DEST_V4 / "val" / c
        target_train_dir.mkdir(parents=True, exist_ok=True)
        target_val_dir.mkdir(parents=True, exist_ok=True)

        for idx, (src_path, h, origin) in enumerate(train_set):
            ext = src_path.suffix.lower()
            dst_name = f"{c}_train_{origin}_{idx:04d}_{h[:8]}{ext}"
            dst_path = target_train_dir / dst_name
            shutil.copy2(src_path, dst_path)
            train_hashes.add(h)
            train_counts[c] += 1

        for idx, (src_path, h, origin) in enumerate(val_set):
            ext = src_path.suffix.lower()
            dst_name = f"{c}_val_{origin}_{idx:04d}_{h[:8]}{ext}"
            dst_path = target_val_dir / dst_name
            shutil.copy2(src_path, dst_path)
            val_hashes.add(h)
            val_counts[c] += 1

    # 7. Verification of 0% Data Leakage
    leakage = train_hashes.intersection(val_hashes)
    print("\n[Step 6] Cryptographic Verification:")
    print(f"  Train images: {len(train_hashes)}")
    print(f"  Val images:   {len(val_hashes)}")
    print(f"  Intersection: {len(leakage)}")
    if len(leakage) == 0:
        print("  [SUCCESS] 0% Data Leakage Verified: train_hashes AND val_hashes are strictly disjoint!")
    else:
        raise ValueError(f"CRITICAL ERROR: {len(leakage)} overlapping hashes detected between train and val!")

    print("\nFinal Class Distribution in dataset_unified_v4:")
    print(f"{'Class Name':<16} {'Train':>8} {'Val':>8} {'Total':>8}")
    print("-" * 44)
    for c in CANONICAL_CLASSES:
        t = train_counts[c]
        v = val_counts[c]
        print(f"{c:<16} {t:>8} {v:>8} {t+v:>8}")
    print("-" * 44)
    print(f"{'TOTAL':<16} {sum(train_counts.values()):>8} {sum(val_counts.values()):>8} {sum(train_counts.values()) + sum(val_counts.values()):>8}")
    print("\ndataset_unified_v4 successfully built!")

if __name__ == "__main__":
    main()
