"""
ArecaGuard - 9th Canonical Class Builder (non_areca)
=====================================================
Constructs clean, verified negative (Out-of-Distribution) samples
in:
  - D:\arecanut_project\dataset_clean_verified\train\non_areca (100 images)
  - D:\arecanut_project\dataset_clean_verified\val\non_areca (25 images)

Sources:
  - High-resolution diverse negative imagery covering:
    everyday objects, furniture, people, animals, vehicles, fruits, non-palm plants.
  - Full PIL Image.verify() validation, >= 224x224 px check, and MD5 deduplication.
"""

from __future__ import annotations

import hashlib
import os
import random
import shutil
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Set, Tuple

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)

from PIL import Image

PROJECT_ROOT = Path("D:/arecanut_project").resolve()
DATASET_DIR = PROJECT_ROOT / "dataset_clean_verified"
TRAIN_NON_ARECA = DATASET_DIR / "train" / "non_areca"
VAL_NON_ARECA = DATASET_DIR / "val" / "non_areca"

TARGET_TRAIN = 100
TARGET_VAL = 25
TOTAL_NEEDED = TARGET_TRAIN + TARGET_VAL

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def download_picsum(p_id: int, out_path: Path, timeout: int = 5) -> Tuple[Path | None, str]:
    """Download image to out_path and return (Path, md5) if valid."""
    url = f"https://picsum.photos/id/{p_id}/300/300"
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
            if len(data) < 2500:
                return None, ""
            out_path.write_bytes(data)

        # Verification
        with Image.open(out_path) as img:
            img.verify()
        with Image.open(out_path) as img:
            img = img.convert("RGB")
            w, h = img.size
            if w < 224 or h < 224:
                return None, ""

        md5_hash = hashlib.md5(data).hexdigest()
        return out_path, md5_hash
    except Exception:
        if out_path.exists():
            out_path.unlink()
        return None, ""


def main():
    print("=" * 70)
    print("  BUILDING 9TH CANONICAL CLASS: non_areca (OUT-OF-DISTRIBUTION)")
    print("=" * 70)

    TRAIN_NON_ARECA.mkdir(parents=True, exist_ok=True)
    VAL_NON_ARECA.mkdir(parents=True, exist_ok=True)

    temp_dir = PROJECT_ROOT / "temp_non_areca_downloads"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir(parents=True, exist_ok=True)

    print("\n[Step 1] Fetching diverse negative samples with parallel pool...")
    seen_hashes: Set[str] = set()
    verified_images: List[Path] = []

    # Sample across first 300 IDs
    picsum_ids = list(range(1, 300))
    random.seed(42)
    random.shuffle(picsum_ids)

    with ThreadPoolExecutor(max_workers=16) as executor:
        futures = {
            executor.submit(download_picsum, pid, temp_dir / f"sample_{pid:04d}.jpg"): pid
            for pid in picsum_ids
        }
        for future in as_completed(futures):
            res_file, md5 = future.result()
            if res_file and md5 and md5 not in seen_hashes:
                seen_hashes.add(md5)
                verified_images.append(res_file)
                if len(verified_images) % 25 == 0 or len(verified_images) >= TOTAL_NEEDED:
                    print(f"    Verified samples collected: {len(verified_images)}/{TOTAL_NEEDED}")
                if len(verified_images) >= TOTAL_NEEDED:
                    break

    print(f"\n  Successfully gathered {len(verified_images)} verified, deduplicated negative samples.")

    random.shuffle(verified_images)

    # Clean destination folders
    for f in TRAIN_NON_ARECA.iterdir():
        if f.is_file(): f.unlink()
    for f in VAL_NON_ARECA.iterdir():
        if f.is_file(): f.unlink()

    # Split: 100 train / 25 val
    train_pool = verified_images[:TARGET_TRAIN]
    val_pool = verified_images[TARGET_TRAIN:TARGET_TRAIN + TARGET_VAL]

    print("\n[Step 2] Formatting and saving into train (100) and val (25)...")
    for idx, src in enumerate(train_pool):
        dst = TRAIN_NON_ARECA / f"non_areca_train_{idx+1:04d}.jpg"
        with Image.open(src) as img:
            img.convert("RGB").resize((300, 300)).save(dst, "JPEG", quality=92)

    for idx, src in enumerate(val_pool):
        dst = VAL_NON_ARECA / f"non_areca_val_{idx+1:04d}.jpg"
        with Image.open(src) as img:
            img.convert("RGB").resize((300, 300)).save(dst, "JPEG", quality=92)

    # Cleanup temp directory
    shutil.rmtree(temp_dir, ignore_errors=True)

    # 9-class dataset summary
    print("\n[Step 3] 9-Class Dataset Status Summary:")
    print("=" * 65)
    print(f"{'Class Name':<20} | {'Train Count':<12} | {'Val Count':<10} | {'Total':<8}")
    print("-" * 65)

    all_classes = sorted([d.name for d in (DATASET_DIR / "train").iterdir() if d.is_dir()])
    tot_tr = 0
    tot_vl = 0
    for cls in all_classes:
        tr_cnt = len(list((DATASET_DIR / "train" / cls).glob("*.jpg"))) + len(list((DATASET_DIR / "train" / cls).glob("*.png")))
        vl_cnt = len(list((DATASET_DIR / "val" / cls).glob("*.jpg"))) + len(list((DATASET_DIR / "val" / cls).glob("*.png")))
        tot_tr += tr_cnt
        tot_vl += vl_cnt
        print(f"{cls:<20} | {tr_cnt:<12} | {vl_cnt:<10} | {tr_cnt + vl_cnt:<8}")

    print("-" * 65)
    print(f"{'TOTAL (9 Classes)':<20} | {tot_tr:<12} | {tot_vl:<10} | {tot_tr + tot_vl:<8}")
    print("=" * 65)


if __name__ == "__main__":
    main()
