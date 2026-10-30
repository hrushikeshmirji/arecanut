"""
ArecaGuard - Dataset Visual Verification Grid
==============================================
Samples 4 random images from each class folder in dataset_multiclass_clean/
and exports a labeled composite grid to evaluation_reports/dataset_verification_grid.png.
Also prints a summary table showing image counts per class.
"""
from __future__ import annotations

import random
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)

from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CLEAN_DIR = PROJECT_ROOT / "dataset_multiclass_clean"
OUTPUT_PATH = PROJECT_ROOT / "evaluation_reports" / "dataset_verification_grid.png"

SAMPLES_PER_CLASS = 4
THUMB_SIZE = 224
PADDING = 10
LABEL_HEIGHT = 30

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def main():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not CLEAN_DIR.exists():
        print(f"ERROR: {CLEAN_DIR} does not exist.")
        sys.exit(1)

    # Discover classes
    classes = sorted(
        d.name for d in CLEAN_DIR.iterdir()
        if d.is_dir() and any(f.suffix.lower() in IMAGE_EXTS for f in d.iterdir() if f.is_file())
    )

    if not classes:
        print("ERROR: No classes found in dataset_multiclass_clean/")
        sys.exit(1)

    # Print summary table
    print("=" * 55)
    print("  DATASET MULTICLASS CLEAN - IMAGE COUNT SUMMARY")
    print("=" * 55)
    total = 0
    class_counts = {}
    for cls in classes:
        folder = CLEAN_DIR / cls
        count = sum(1 for f in folder.iterdir() if f.is_file() and f.suffix.lower() in IMAGE_EXTS)
        class_counts[cls] = count
        total += count
        print(f"    {cls:<20s}: {count:>5d} images")
    print("  " + "-" * 45)
    print(f"    {'TOTAL':<20s}: {total:>5d} images")
    print("=" * 55)

    # Build grid
    num_rows = len(classes)
    num_cols = SAMPLES_PER_CLASS
    cell_w = THUMB_SIZE + PADDING
    cell_h = THUMB_SIZE + LABEL_HEIGHT + PADDING

    grid_w = PADDING + num_cols * cell_w
    grid_h = PADDING + num_rows * cell_h
    grid = Image.new("RGB", (grid_w, grid_h), color=(255, 255, 255))
    draw = ImageDraw.Draw(grid)

    # Try to use a font, fall back to default
    try:
        font = ImageFont.truetype("arial.ttf", 14)
    except Exception:
        font = ImageFont.load_default()

    rng = random.Random(42)

    for row, cls in enumerate(classes):
        folder = CLEAN_DIR / cls
        all_imgs = [f for f in folder.iterdir() if f.is_file() and f.suffix.lower() in IMAGE_EXTS]
        sampled = rng.sample(all_imgs, min(SAMPLES_PER_CLASS, len(all_imgs)))

        for col, img_path in enumerate(sampled):
            x = PADDING + col * cell_w
            y = PADDING + row * cell_h

            # Draw class label
            draw.text((x + 2, y + 2), cls, fill=(0, 0, 0), font=font)

            # Draw thumbnail
            try:
                img = Image.open(img_path).convert("RGB")
                img.thumbnail((THUMB_SIZE, THUMB_SIZE), Image.Resampling.BICUBIC)
                grid.paste(img, (x, y + LABEL_HEIGHT))
            except Exception:
                draw.rectangle(
                    [x, y + LABEL_HEIGHT, x + THUMB_SIZE, y + LABEL_HEIGHT + THUMB_SIZE],
                    fill=(200, 200, 200),
                )
                draw.text((x + 20, y + LABEL_HEIGHT + 90), "ERR", fill=(255, 0, 0), font=font)

    grid.save(OUTPUT_PATH)
    print(f"\nVerification grid saved to: {OUTPUT_PATH}")
    print(f"Grid dimensions: {grid_w} x {grid_h} px ({num_rows} classes x {num_cols} samples)")


if __name__ == "__main__":
    main()
