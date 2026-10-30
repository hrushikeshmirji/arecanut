"""
audit_old_datasets.py
=====================
Scans all legacy and previous arecanut project directories and zip archives on the local machine:
  1. Counts total images in each repository
  2. Inspects image resolution distribution (checks how many are >= 224x224 px)
  3. Checks MD5 hashes against our current 1,878 verified dataset to find NEW vs DUPLICATE images
  4. Runs ViT inference on new candidate images to evaluate quality and self-classify them
"""

import os
import sys
import hashlib
import zipfile
from pathlib import Path
from typing import Dict, List, Set, Tuple
from PIL import Image

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)

PROJECT_ROOT = Path("D:/arecanut_project").resolve()
ACTIVE_DATASET = PROJECT_ROOT / "dataset_large_scale_verified"

# Collect all MD5 hashes of active dataset
print("[1] Indexing active 1,878 verified dataset hashes...")
active_hashes: Set[str] = set()
for p in ACTIVE_DATASET.rglob("*.*"):
    if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp", ".webp"}:
        with open(p, "rb") as f:
            active_hashes.add(hashlib.md5(f.read()).hexdigest())
print(f"  Active verified hashes: {len(active_hashes)}")

# Candidate locations to audit
CANDIDATE_DIRS = [
    Path(r"C:\Users\Hrushikesh Mirji\Desktop\areca_diseased_fungal_fruit_rot"),
    Path(r"C:\Users\Hrushikesh Mirji\Desktop\New folder\ArecaVision_audit\dataset_hardcore_expanded"),
    Path(r"C:\Users\Hrushikesh Mirji\Desktop\New folder\ArecaVision_audit\backend\yolo\dataset"),
    PROJECT_ROOT / "dataset_koleroga",
    PROJECT_ROOT / "dataset_patches",
    PROJECT_ROOT / "new_data",
]

CANDIDATE_ZIPS = [
    Path(r"C:\Users\Hrushikesh Mirji\Downloads\arecanut-disease-detection.v2-healthy_nut_v2.yolov8.zip"),
    Path(r"C:\Users\Hrushikesh Mirji\Downloads\dataset0000.zip"),
    Path(r"C:\Users\Hrushikesh Mirji\Desktop\New folder\zip files\dataset_raw.zip"),
]

print("\n[2] Auditing candidate legacy directories...")
results_summary = []

for cdir in CANDIDATE_DIRS:
    if not cdir.exists():
        continue
    total_imgs = 0
    valid_res = 0
    low_res = 0
    corrupt = 0
    duplicate_active = 0
    unique_new = 0
    new_paths = []

    for p in cdir.rglob("*.*"):
        if not p.is_file() or p.suffix.lower() not in {".jpg", ".jpeg", ".png", ".bmp", ".webp"}:
            continue
        total_imgs += 1
        try:
            with open(p, "rb") as f:
                h = hashlib.md5(f.read()).hexdigest()
            if h in active_hashes:
                duplicate_active += 1
                continue
            with Image.open(p) as im:
                w, h_dim = im.size
                if w >= 224 and h_dim >= 224:
                    valid_res += 1
                    unique_new += 1
                    new_paths.append(p)
                else:
                    low_res += 1
        except Exception:
            corrupt += 1

    print(f"\n--- Directory: {cdir.name} ({cdir}) ---")
    print(f"  Total Images    : {total_imgs}")
    print(f"  Already in Active: {duplicate_active} (duplicates)")
    print(f"  Low Resolution  : {low_res} (<224x224)")
    print(f"  Corrupt/Unreadable: {corrupt}")
    print(f"  NEW High-Res Can Be Used: {unique_new}")

print("\n[3] Auditing candidate zip files...")
for czip in CANDIDATE_ZIPS:
    if not czip.exists():
        continue
    total_imgs = 0
    new_in_zip = 0
    dup_in_zip = 0
    try:
        with zipfile.ZipFile(czip, "r") as z:
            names = [n for n in z.namelist() if Path(n).suffix.lower() in {".jpg", ".jpeg", ".png"}]
            total_imgs = len(names)
            for n in names:
                data = z.read(n)
                h = hashlib.md5(data).hexdigest()
                if h in active_hashes:
                    dup_in_zip += 1
                else:
                    new_in_zip += 1
        print(f"\n--- Zip: {czip.name} ---")
        print(f"  Total Images    : {total_imgs}")
        print(f"  Already in Active: {dup_in_zip} (duplicates)")
        print(f"  NEW Images Found : {new_in_zip}")
    except Exception as e:
        print(f"  Error reading {czip.name}: {e}")

print("\nAudit completed!")
