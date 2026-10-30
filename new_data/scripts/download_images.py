"""
Phase 1 — Dataset Acquisition Pipeline
=======================================
Downloads arecanut disease images via Bing Image Search into class folders.

Usage:
    pip install bing-image-downloader
    python new_data/scripts/download_images.py
"""

from __future__ import annotations

import hashlib
import os
import shutil
import sys
import time
from pathlib import Path
from typing import Dict, List

# ── Ensure project root is importable ────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent          # new_data/scripts/
PROJECT_ROOT = SCRIPT_DIR.parent.parent               # arecanut_project/
RAW_DIR = SCRIPT_DIR.parent / "raw"                   # new_data/raw/

# ── Search configuration ────────────────────────────────────────────────────
QUERIES: Dict[str, List[str]] = {
    "fruit_rot": [
        "arecanut fruit rot koleroga",
        "areca catechu mahali disease",
        "phytophthora meadii arecanut",
        "areca nut rot bunch",
    ],
    "foot_rot": [
        "arecanut anabe roga",
        "ganoderma lucidum arecanut",
        "areca palm basal stem rot conk",
        "arecanut foot rot disease",
    ],
    "spindle_bug": [
        "carvalhoia arecae arecanut",
        "areca palm spindle bug feeding marks",
        "arecanut shredded spindle leaf",
    ],
}

IMAGES_PER_QUERY = 25

# ── Valid image extensions ───────────────────────────────────────────────────
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".gif", ".tiff", ".tif"}


def _file_hash(filepath: Path) -> str:
    """Return SHA-256 hex digest of a file (for deduplication)."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _flatten_into(class_dir: Path) -> int:
    """
    bing_image_downloader creates a subdirectory named after the query inside
    the output_dir.  This helper moves all valid images from every nested
    subdirectory up into *class_dir*, renames them sequentially, removes
    duplicates by content hash, and deletes the now-empty subdirectories.

    Returns the number of unique image files kept.
    """
    seen_hashes: set[str] = set()

    # First, catalogue images already present (from previous runs)
    for existing in class_dir.iterdir():
        if existing.is_file() and existing.suffix.lower() in IMAGE_EXTS:
            seen_hashes.add(_file_hash(existing))

    kept = len(seen_hashes)

    # Walk nested dirs created by the downloader
    for sub in sorted(class_dir.iterdir()):
        if not sub.is_dir():
            continue
        for img_file in sorted(sub.rglob("*")):
            if not img_file.is_file():
                continue
            if img_file.suffix.lower() not in IMAGE_EXTS:
                img_file.unlink()          # discard non-image artefacts
                continue
            fhash = _file_hash(img_file)
            if fhash in seen_hashes:
                img_file.unlink()          # duplicate
                continue
            seen_hashes.add(fhash)
            kept += 1
            dest = class_dir / f"{class_dir.name}_{kept:04d}{img_file.suffix.lower()}"
            shutil.move(str(img_file), str(dest))

        # Remove the (now empty) subdirectory tree
        shutil.rmtree(sub, ignore_errors=True)

    return kept


def main() -> None:
    try:
        from bing_image_downloader import downloader  # type: ignore[import-untyped]
    except ImportError:
        print(
            "ERROR: bing-image-downloader is not installed.\n"
            "       Run:  pip install bing-image-downloader",
            file=sys.stderr,
        )
        sys.exit(1)

    print("=" * 60)
    print("  ArecaGuard — Phase 1 Dataset Acquisition")
    print("=" * 60)
    print(f"  Output root : {RAW_DIR}")
    print(f"  Images/query: {IMAGES_PER_QUERY}")
    print(f"  Classes     : {', '.join(QUERIES)}")
    print("=" * 60)

    totals: Dict[str, int] = {}

    for class_name, queries in QUERIES.items():
        class_dir = RAW_DIR / class_name
        class_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n▸ [{class_name.upper()}]  ({len(queries)} queries)")
        print(f"  Target folder: {class_dir}")

        for qi, query in enumerate(queries, 1):
            print(f"    [{qi}/{len(queries)}] Downloading: \"{query}\" ...", end=" ", flush=True)
            t0 = time.time()
            try:
                downloader.download(
                    query,
                    limit=IMAGES_PER_QUERY,
                    output_dir=str(class_dir),
                    adult_filter_off=True,
                    force_replace=False,
                    timeout=10,
                    verbose=False,
                )
                elapsed = time.time() - t0
                print(f"done ({elapsed:.1f}s)")
            except Exception as exc:
                print(f"FAILED ({exc})")

        # Flatten nested subdirs → class_dir, deduplicate
        unique_count = _flatten_into(class_dir)
        totals[class_name] = unique_count
        print(f"  ✓ {class_name}: {unique_count} unique images after dedup")

    # ── Summary ──────────────────────────────────────────────────────────
    grand_total = sum(totals.values())
    print("\n" + "=" * 60)
    print("  DOWNLOAD SUMMARY")
    print("=" * 60)
    for cls, cnt in totals.items():
        print(f"    {cls:<15s} : {cnt:>4d} images")
    print(f"    {'TOTAL':<15s} : {grand_total:>4d} images")
    print("=" * 60)
    print("  Done. Images saved to:", RAW_DIR)
    print("=" * 60)


if __name__ == "__main__":
    main()
