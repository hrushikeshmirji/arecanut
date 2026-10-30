"""
ArecaGuard - Complete Multi-Class Clean Dataset Ingestion
=========================================================
Target Classes (Balanced ~100-140 images per class):
1. fruit_rot      (Koleroga / Mahali)
2. healthy_nut    (Healthy nut bunches)
3. yellow_leaf    (Yellow Leaf Disease / Phytoplasma)
4. stem_bleeding  (Stem bleeding / Thielaviopsis paradoxa)
5. foot_rot       (Anabe Roga / Ganoderma lucidum)
6. healthy_leaf   (Healthy green fronds/canopy)
"""

from __future__ import annotations

import concurrent.futures
import hashlib
import json
import os
import random
import re
import sys
import threading
import time
import urllib.parse
import urllib.request
from io import BytesIO
from pathlib import Path
from typing import List, Set

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)

from curl_cffi import requests as cffi_requests
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CLEAN_DIR = PROJECT_ROOT / "dataset_multiclass_clean"

TARGET_PER_CLASS = 120
MIN_DIM = 100


def file_hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def verify_and_save_image(raw_bytes: bytes, dest_path: Path, min_res: int = 224) -> bool:
    try:
        img = Image.open(BytesIO(raw_bytes)).convert("RGB")
        w, h = img.size
        if w < MIN_DIM or h < MIN_DIM:
            return False

        # If image is smaller than 224 in any dimension, scale up with bicubic interpolation
        if w < min_res or h < min_res:
            scale = max(min_res / w, min_res / h)
            new_w, new_h = int(w * scale), int(h * scale)
            img = img.resize((new_w, new_h), Image.Resampling.BICUBIC)

        img.save(dest_path, "JPEG", quality=92)
        return True
    except Exception:
        return False


def get_existing_hashes(folder: Path) -> Set[str]:
    hashes = set()
    if folder.exists():
        for f in folder.glob("*.jpg"):
            try:
                hashes.add(file_hash(f.read_bytes()))
            except Exception:
                pass
    return hashes


# ── 1. GitHub Direct Download ───────────────────────────────────────────────
def download_github_files(items_url: str, filter_keyword: str | None, class_name: str, target_dir: Path, max_count: int = 120):
    target_dir.mkdir(parents=True, exist_ok=True)
    existing_files = list(target_dir.glob("*.jpg"))
    saved = len(existing_files)
    if saved >= max_count:
        print(f"  [+] {class_name}: Already satisfied with {saved} images.")
        return saved

    seen_hashes = get_existing_hashes(target_dir)
    lock = threading.Lock()

    print(f"  Fetching GitHub directory: {items_url} ...")
    req = urllib.request.Request(items_url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            items = json.loads(resp.read().decode())
    except Exception as e:
        print(f"    [!] Failed to load GitHub repo: {e}")
        return saved

    dl_items = []
    for it in items:
        if it.get("type") != "file":
            continue
        name = it.get("name", "").lower()
        if filter_keyword and filter_keyword.lower() not in name:
            continue
        if it.get("download_url"):
            dl_items.append(it)

    print(f"    Found {len(dl_items)} candidate files for {class_name} on GitHub")

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
                        print(f"      -> {class_name}: {saved}/{max_count}")
        except Exception:
            pass

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        executor.map(worker, dl_items)

    print(f"  [+] {class_name}: Total {saved} images after GitHub ingestion.")
    return saved


# ── 2. Domain Image Ingestion ───────────────────────────────────────────────
def download_domain_images(queries: List[str], class_name: str, target_dir: Path, max_count: int = 120):
    target_dir.mkdir(parents=True, exist_ok=True)
    existing_files = list(target_dir.glob("*.jpg"))
    saved = len(existing_files)
    if saved >= max_count:
        print(f"  [+] {class_name}: Already satisfied with {saved} images.")
        return saved

    seen_hashes = get_existing_hashes(target_dir)
    lock = threading.Lock()

    urls: List[str] = []
    for q in queries:
        for page in [1, 36, 71, 106]:
            query_enc = urllib.parse.quote(q)
            api_url = f"https://www.bing.com/images/async?q={query_enc}&first={page}&count=35"
            try:
                r = cffi_requests.get(api_url, impersonate="chrome120", timeout=10)
                if r.status_code == 200:
                    found = re.findall(r'murl&quot;:&quot;(http[^&]+)&quot;', r.text)
                    for u in found:
                        if u not in urls:
                            urls.append(u)
            except Exception:
                pass

    print(f"    Found {len(urls)} domain image URLs for {class_name}, downloading concurrent...")

    def fetch_url(u: str):
        nonlocal saved
        with lock:
            if saved >= max_count:
                return
        try:
            r = cffi_requests.get(u, impersonate="chrome120", timeout=8)
            if r.status_code == 200 and len(r.content) > 4000:
                h = file_hash(r.content)
                with lock:
                    if saved >= max_count or h in seen_hashes:
                        return
                    dest = target_dir / f"{class_name}_{saved:04d}.jpg"
                    if verify_and_save_image(r.content, dest):
                        seen_hashes.add(h)
                        saved += 1
                        if saved % 20 == 0 or saved == max_count:
                            print(f"      -> {class_name}: {saved}/{max_count}")
        except Exception:
            pass

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(fetch_url, urls)

    print(f"  [+] {class_name}: Total {saved} images after domain search.")
    return saved


def main():
    print("=" * 65)
    print("  BUILDING COMPLETE MULTI-CLASS CLEAN DATASET")
    print("=" * 65)
    CLEAN_DIR.mkdir(parents=True, exist_ok=True)

    # 1. fruit_rot (already populated)
    fr_dir = CLEAN_DIR / "fruit_rot"
    print(f"  [+] fruit_rot: {len(list(fr_dir.glob('*.jpg')))} verified images ready.")

    # 2. healthy_nut (already populated)
    hn_dir = CLEAN_DIR / "healthy_nut"
    print(f"  [+] healthy_nut: {len(list(hn_dir.glob('*.jpg')))} verified images ready.")

    # 3. yellow_leaf (already populated)
    yl_dir = CLEAN_DIR / "yellow_leaf"
    print(f"  [+] yellow_leaf: {len(list(yl_dir.glob('*.jpg')))} verified images ready.")

    # 4. stem_bleeding
    sb_dir = CLEAN_DIR / "stem_bleeding"
    download_domain_images(
        [
            "arecanut stem bleeding thielaviopsis paradoxa",
            "arecanut stem cracking disease trunk",
            "areca palm trunk bleeding lesions",
            "arecanut stem bleeding symptoms",
        ],
        "stem_bleeding",
        sb_dir,
        max_count=TARGET_PER_CLASS,
    )

    # 5. healthy_leaf
    hl_dir = CLEAN_DIR / "healthy_leaf"
    # Download from Shivan-kulal
    download_github_files(
        "https://api.github.com/repos/shivan-kulal-git/Arecanut_final/contents/final_testing-20230830T042904Z-001/final_testing",
        filter_keyword="healthy_leaf",
        class_name="healthy_leaf",
        target_dir=hl_dir,
        max_count=TARGET_PER_CLASS,
    )
    # Download from Pavankumar
    download_github_files(
        "https://api.github.com/repos/Pavankumarv-balekoppa/DISEASE-DETECTION-AND-TREATMENT-OF-ARECANUT/contents/dataset/Healthy_Leaf",
        filter_keyword=None,
        class_name="healthy_leaf",
        target_dir=hl_dir,
        max_count=TARGET_PER_CLASS,
    )
    # Domain search if still below target
    download_domain_images(
        [
            "arecanut healthy green leaf frond",
            "areca palm healthy leaves canopy",
            "areca catechu healthy foliage",
        ],
        "healthy_leaf",
        hl_dir,
        max_count=TARGET_PER_CLASS,
    )

    # 6. foot_rot (Anabe Roga / Ganoderma lucidum)
    ft_dir = CLEAN_DIR / "foot_rot"
    download_domain_images(
        [
            "arecanut foot rot anabe",
            "arecanut foot rot ganoderma lucidum",
            "areca palm basal stem rot anabe roga",
            "arecanut anabe roga disease symptoms",
            "ganoderma lucidum arecanut trunk base",
            "arecanut anabe disease conk",
            "areca palm foot rot fungus",
        ],
        "foot_rot",
        ft_dir,
        max_count=TARGET_PER_CLASS,
    )

    print("\n" + "=" * 65)
    print("  FINAL MULTI-CLASS DATASET VERIFICATION SUMMARY")
    print("=" * 65)
    classes = ["fruit_rot", "foot_rot", "yellow_leaf", "stem_bleeding", "healthy_nut", "healthy_leaf"]
    total = 0
    for c in classes:
        cnt = len(list((CLEAN_DIR / c).glob("*.jpg")))
        total += cnt
        print(f"    {c:<20s} : {cnt:>4d} images")
    print("  " + "-" * 50)
    print(f"    {'TOTAL':<20s} : {total:>4d} images")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    main()
