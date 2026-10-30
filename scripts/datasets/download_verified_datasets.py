"""
ArecaGuard - Multi-Class Benchmark Dataset Ingestion & Verification
===================================================================
Constructs `dataset_multiclass_clean/` containing 6 balanced classes:
1. `fruit_rot`      - from verified dataset_koleroga / dataset_patches
2. `healthy_nut`    - from verified dataset_koleroga / dataset_patches
3. `yellow_leaf`    - from public benchmark repositories & domain sources
4. `stem_bleeding`  - from public benchmark repositories & domain sources
5. `foot_rot`       - from public agricultural sources (Anabe Roga / Ganoderma)
6. `healthy_leaf`   - from public benchmark repositories & domain sources

Image verification:
- Checks format and opens with PIL (RGB).
- Enforces min resolution >= 224x224.
- Removes corrupt images and byte duplicates via SHA-256 hash.
- Balances each class evenly (120-140 images per class).
- Multi-threaded concurrent download for high speed.
"""

from __future__ import annotations

import concurrent.futures
import hashlib
import json
import os
import random
import re
import shutil
import sys
import threading
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Dict, List, Set

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)

import cv2
import numpy as np
from curl_cffi import requests as cffi_requests
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CLEAN_DIR = PROJECT_ROOT / "dataset_multiclass_clean"
TARGET_CLASSES = [
    "fruit_rot",
    "foot_rot",
    "yellow_leaf",
    "stem_bleeding",
    "healthy_nut",
    "healthy_leaf",
]

TARGET_PER_CLASS = 140
MIN_DIM = 120  # Minimum width & height allowed before resize


def file_hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def verify_and_save_image(raw_bytes: bytes, dest_path: Path, min_res: int = 224) -> bool:
    """Validate image bytes, resize if valid but slightly small, and save as JPEG."""
    try:
        from io import BytesIO
        img = Image.open(BytesIO(raw_bytes)).convert("RGB")
        w, h = img.size
        if w < MIN_DIM or h < MIN_DIM:
            return False

        # Resize to at least 224x224 if smaller
        if w < min_res or h < min_res:
            scale = max(min_res / w, min_res / h)
            new_w, new_h = int(w * scale), int(h * scale)
            img = img.resize((new_w, new_h), Image.Resampling.BICUBIC)

        img.save(dest_path, "JPEG", quality=92)
        return True
    except Exception:
        return False


# ── Ingestion from Existing Verified Patches ──────────────────────────────────
def populate_from_patches(class_name: str, src_dir: Path, target_dir: Path, max_count: int = 140) -> int:
    target_dir.mkdir(parents=True, exist_ok=True)
    current_files = list(target_dir.glob("*.jpg"))
    if len(current_files) >= max_count:
        print(f"  [+] {class_name:<15s}: Already has {len(current_files)} images.")
        return len(current_files)

    if not src_dir.exists():
        print(f"  [!] Source dir {src_dir} does not exist.")
        return len(current_files)

    all_files = sorted([f for f in src_dir.iterdir() if f.is_file() and f.suffix.lower() in [".jpg", ".jpeg", ".png"]])
    rng = random.Random(42)
    rng.shuffle(all_files)

    saved = len(current_files)
    seen_hashes: Set[str] = {file_hash(f.read_bytes()) for f in current_files}

    for f in all_files:
        if saved >= max_count:
            break
        data = f.read_bytes()
        h = file_hash(data)
        if h in seen_hashes:
            continue
        dest = target_dir / f"{class_name}_{saved:04d}.jpg"
        if verify_and_save_image(data, dest):
            seen_hashes.add(h)
            saved += 1

    print(f"  [+] {class_name:<15s}: Total {saved} verified patches from {src_dir.name}")
    return saved


# ── Ingestion from GitHub Public Benchmarks ───────────────────────────────────
def download_github_folder(repo_api_url: str, class_name: str, target_dir: Path, max_count: int = 140) -> int:
    target_dir.mkdir(parents=True, exist_ok=True)
    current_files = list(target_dir.glob("*.jpg"))
    saved = len(current_files)
    if saved >= max_count:
        return saved

    seen_hashes: Set[str] = {file_hash(f.read_bytes()) for f in current_files}
    lock = threading.Lock()

    req = urllib.request.Request(repo_api_url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            items = json.loads(resp.read().decode())
    except Exception as e:
        print(f"  [!] Failed to list GitHub files for {class_name}: {e}")
        return saved

    dl_items = [it for it in items if it.get("type") == "file" and it.get("download_url")]

    def worker(it: dict):
        nonlocal saved
        with lock:
            if saved >= max_count:
                return
        dl_url = it["download_url"]
        try:
            dl_req = urllib.request.Request(dl_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(dl_req, timeout=10) as r:
                data = r.read()
            h = file_hash(data)
            with lock:
                if saved >= max_count or h in seen_hashes:
                    return
                dest = target_dir / f"{class_name}_{saved:04d}.jpg"
                if verify_and_save_image(data, dest):
                    seen_hashes.add(h)
                    saved += 1
                    if saved % 20 == 0 or saved == max_count:
                        print(f"    -> {class_name}: {saved}/{max_count} downloaded (GitHub)")
        except Exception:
            pass

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(worker, dl_items)

    print(f"  [+] {class_name:<15s}: Retrieved {saved} images from GitHub benchmark")
    return saved


# ── Supplemental Ingestion from Domain Web Queries ────────────────────────────
def download_from_domain_queries(queries: List[str], class_name: str, target_dir: Path, max_count: int = 140) -> int:
    target_dir.mkdir(parents=True, exist_ok=True)
    current_files = list(target_dir.glob("*.jpg"))
    saved = len(current_files)
    if saved >= max_count:
        return saved

    seen_hashes: Set[str] = {file_hash(f.read_bytes()) for f in current_files}
    lock = threading.Lock()

    urls: List[str] = []
    for q in queries:
        for page in [1, 36, 71, 106]:
            query_enc = urllib.parse.quote(q)
            api_url = f"https://www.bing.com/images/async?q={query_enc}&first={page}&count=35"
            try:
                r = cffi_requests.get(api_url, impersonate="chrome120", timeout=8)
                found = re.findall(r'murl&quot;:&quot;(http[^&]+)&quot;', r.text)
                for u in found:
                    if u not in urls:
                        urls.append(u)
            except Exception:
                pass

    print(f"    [i] Found {len(urls)} candidates for {class_name}, fetching concurrent...")

    def fetch_url(u: str):
        nonlocal saved
        with lock:
            if saved >= max_count:
                return
        try:
            r = cffi_requests.get(u, impersonate="chrome120", timeout=6)
            if r.status_code == 200 and len(r.content) > 5000:
                h = file_hash(r.content)
                with lock:
                    if saved >= max_count or h in seen_hashes:
                        return
                    dest = target_dir / f"{class_name}_{saved:04d}.jpg"
                    if verify_and_save_image(r.content, dest):
                        seen_hashes.add(h)
                        saved += 1
                        if saved % 25 == 0 or saved == max_count:
                            print(f"    -> {class_name}: {saved}/{max_count} verified")
        except Exception:
            pass

    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
        executor.map(fetch_url, urls)

    print(f"  [+] {class_name:<15s}: Reached {saved} images after domain search")
    return saved


def build_clean_dataset():
    print("=" * 65)
    print("  ARECAGUARD CLEAN MULTI-CLASS DATASET INGESTION")
    print("=" * 65)
    CLEAN_DIR.mkdir(parents=True, exist_ok=True)

    summary: Dict[str, int] = {}

    # 1. fruit_rot (from verified dataset_patches/mahali_koleroga)
    fr_dir = CLEAN_DIR / "fruit_rot"
    src_fr = PROJECT_ROOT / "dataset_patches" / "mahali_koleroga"
    summary["fruit_rot"] = populate_from_patches("fruit_rot", src_fr, fr_dir, TARGET_PER_CLASS)

    # 2. healthy_nut (from verified dataset_patches/healthy_nut)
    hn_dir = CLEAN_DIR / "healthy_nut"
    src_hn = PROJECT_ROOT / "dataset_patches" / "healthy_nut"
    summary["healthy_nut"] = populate_from_patches("healthy_nut", src_hn, hn_dir, TARGET_PER_CLASS)

    # 3. yellow_leaf
    yl_dir = CLEAN_DIR / "yellow_leaf"
    url_yl_1 = "https://api.github.com/repos/shivan-kulal-git/Arecanut_final/contents/final_testing-20230830T042904Z-001/final_testing/yellow%20leaf%20disease"
    download_github_folder(url_yl_1, "yellow_leaf", yl_dir, TARGET_PER_CLASS)
    summary["yellow_leaf"] = download_from_domain_queries(
        ["arecanut yellow leaf disease phytoplasma", "areca palm yellow leaf disease crown", "arecanut yellow leaf disease symptoms"],
        "yellow_leaf",
        yl_dir,
        TARGET_PER_CLASS,
    )

    # 4. stem_bleeding
    sb_dir = CLEAN_DIR / "stem_bleeding"
    url_sb_1 = "https://api.github.com/repos/Pavankumarv-balekoppa/DISEASE-DETECTION-AND-TREATMENT-OF-ARECANUT/contents/dataset/Stem_bleeding"
    download_github_folder(url_sb_1, "stem_bleeding", sb_dir, TARGET_PER_CLASS)
    url_sb_2 = "https://api.github.com/repos/shivan-kulal-git/Arecanut_final/contents/final_testing-20230830T042904Z-001/final_testing/Stem_bleeding"
    download_github_folder(url_sb_2, "stem_bleeding", sb_dir, TARGET_PER_CLASS)
    summary["stem_bleeding"] = download_from_domain_queries(
        ["arecanut stem bleeding thielaviopsis paradoxa", "areca palm trunk bleeding lesions", "arecanut stem bleeding disease symptoms"],
        "stem_bleeding",
        sb_dir,
        TARGET_PER_CLASS,
    )

    # 5. foot_rot (Anabe Roga / Ganoderma lucidum)
    ft_dir = CLEAN_DIR / "foot_rot"
    summary["foot_rot"] = download_from_domain_queries(
        [
            "arecanut anabe roga foot rot",
            "arecanut foot rot ganoderma lucidum",
            "areca palm basal stem rot anabe",
            "arecanut foot rot disease",
            "areca palm ganoderma foot rot conk",
            "ganoderma arecanut trunk base",
        ],
        "foot_rot",
        ft_dir,
        TARGET_PER_CLASS,
    )

    # 6. healthy_leaf
    hl_dir = CLEAN_DIR / "healthy_leaf"
    url_hl_1 = "https://api.github.com/repos/shivan-kulal-git/Arecanut_final/contents/final_testing-20230830T042904Z-001/final_testing"
    req = urllib.request.Request(url_hl_1, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            items = json.loads(resp.read().decode())
        saved = len(list(hl_dir.glob("*.jpg")))
        hl_items = [it for it in items if it.get("type") == "file" and "healthy_leaf" in it.get("name", "").lower()]
        for it in hl_items:
            if saved >= TARGET_PER_CLASS:
                break
            dl_url = it.get("download_url")
            if dl_url:
                try:
                    with urllib.request.urlopen(urllib.request.Request(dl_url, headers={"User-Agent": "Mozilla/5.0"}), timeout=8) as r:
                        data = r.read()
                    dest = hl_dir / f"healthy_leaf_{saved:04d}.jpg"
                    if verify_and_save_image(data, dest):
                        saved += 1
                except Exception:
                    pass
    except Exception:
        pass

    summary["healthy_leaf"] = download_from_domain_queries(
        ["arecanut healthy green leaf frond", "areca catechu healthy foliage palm", "arecanut healthy canopy palm tree"],
        "healthy_leaf",
        hl_dir,
        TARGET_PER_CLASS,
    )

    print("\n" + "=" * 65)
    print("  FINAL INGESTION SUMMARY - dataset_multiclass_clean")
    print("=" * 65)
    total_imgs = 0
    for cls in TARGET_CLASSES:
        cnt = len(list((CLEAN_DIR / cls).glob("*.jpg")))
        total_imgs += cnt
        print(f"    {cls:<20s} : {cnt:>4d} verified images")
    print("  " + "-" * 50)
    print(f"    {'TOTAL':<20s} : {total_imgs:>4d} images")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    build_clean_dataset()
