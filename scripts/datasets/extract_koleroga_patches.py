"""
Multi-Class Patch Extraction Pipeline
======================================
Reads every class from dataset_koleroga/data.yaml, scans train/valid/test
splits, crops YOLO bounding-box patches per class, and saves them into
dataset_patches/<class_name>/.

Usage:
    python extract_koleroga_patches.py
"""

import os
import sys
from pathlib import Path

import yaml
from PIL import Image

# ── Paths ────────────────────────────────────────────────────────────────────
DATASET_DIR = Path(r"D:\arecanut_project\dataset_koleroga")
YAML_PATH = DATASET_DIR / "data.yaml"
OUTPUT_ROOT = Path(r"D:\arecanut_project\dataset_patches")

SPLITS = ["train", "valid", "test"]
IMAGE_EXTS = [".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG"]
MIN_PATCH_PX = 20  # skip crops smaller than 20×20


def load_class_names() -> list[str]:
    """Parse data.yaml and return an ordered list of class names."""
    with open(YAML_PATH, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    names = cfg.get("names", [])
    if isinstance(names, dict):
        names = [names[k] for k in sorted(names.keys())]
    return names


def find_image(img_dir: Path, base_name: str) -> Path | None:
    """Return the first matching image path for a label basename."""
    for ext in IMAGE_EXTS:
        candidate = img_dir / (base_name + ext)
        if candidate.exists():
            return candidate
    return None


def extract_patches(names: list[str]) -> dict[str, dict[str, int]]:
    """
    Iterate every split, parse YOLO labels, crop patches per class.

    Returns
    -------
    dict  class_name -> { split -> count }
    """
    # Initialise counters
    counts: dict[str, dict[str, int]] = {
        name: {s: 0 for s in SPLITS} for name in names
    }

    for split in SPLITS:
        img_dir = DATASET_DIR / split / "images"
        lbl_dir = DATASET_DIR / split / "labels"

        if not img_dir.exists() or not lbl_dir.exists():
            continue

        label_files = sorted(lbl_dir.glob("*.txt"))
        for lbl_path in label_files:
            base_name = lbl_path.stem
            img_path = find_image(img_dir, base_name)
            if img_path is None:
                continue

            # Read all annotations
            lines = lbl_path.read_text(encoding="utf-8").strip().splitlines()
            if not lines:
                continue

            # Group boxes by class index
            boxes_by_cls: dict[int, list[list[float]]] = {}
            for line in lines:
                parts = line.strip().split()
                if len(parts) < 5:
                    continue
                cls_idx = int(parts[0])
                if 0 <= cls_idx < len(names):
                    boxes_by_cls.setdefault(cls_idx, []).append(
                        [float(p) for p in parts[1:5]]
                    )

            if not boxes_by_cls:
                continue

            # Open image once, crop all relevant boxes
            try:
                with Image.open(img_path).convert("RGB") as img:
                    w, h = img.size

                    for cls_idx, boxes in boxes_by_cls.items():
                        cls_name = names[cls_idx]
                        out_dir = OUTPUT_ROOT / cls_name
                        out_dir.mkdir(parents=True, exist_ok=True)

                        for i, (xc, yc, bw, bh) in enumerate(boxes):
                            x1 = max(0, int((xc - bw / 2) * w))
                            y1 = max(0, int((yc - bh / 2) * h))
                            x2 = min(w, int((xc + bw / 2) * w))
                            y2 = min(h, int((yc + bh / 2) * h))

                            if (x2 - x1) < MIN_PATCH_PX or (y2 - y1) < MIN_PATCH_PX:
                                continue

                            crop = img.crop((x1, y1, x2, y2))
                            crop_name = f"{split}_{base_name}_crop{i}.jpg"
                            crop.save(str(out_dir / crop_name), quality=95)
                            counts[cls_name][split] += 1

            except Exception as exc:
                print(f"  ⚠ Skipping {img_path.name}: {exc}")

    return counts


def print_summary(names: list[str], counts: dict[str, dict[str, int]]) -> None:
    """Print a formatted summary table."""
    col_w = max(len(n) for n in names) + 2
    header = f"  {'Class':<{col_w}} {'train':>7} {'valid':>7} {'test':>7} {'TOTAL':>7}"
    sep = "  " + "-" * (col_w + 32)

    print()
    print("=" * 60)
    print("  PATCH EXTRACTION SUMMARY")
    print("=" * 60)
    print(header)
    print(sep)

    grand = 0
    for name in names:
        tr = counts[name].get("train", 0)
        va = counts[name].get("valid", 0)
        te = counts[name].get("test", 0)
        total = tr + va + te
        grand += total
        print(f"  {name:<{col_w}} {tr:>7} {va:>7} {te:>7} {total:>7}")

    print(sep)
    print(f"  {'GRAND TOTAL':<{col_w}} {'':>7} {'':>7} {'':>7} {grand:>7}")
    print("=" * 60)
    print(f"  Output: {OUTPUT_ROOT}")
    print("=" * 60)


def main() -> None:
    if not YAML_PATH.exists():
        print(f"ERROR: data.yaml not found at {YAML_PATH}", file=sys.stderr)
        sys.exit(1)

    names = load_class_names()
    print(f"Dataset : {DATASET_DIR}")
    print(f"Classes : {names}")
    print(f"Splits  : {SPLITS}")
    print(f"Output  : {OUTPUT_ROOT}\n")
    print("Extracting patches ...")

    counts = extract_patches(names)
    print_summary(names, counts)


if __name__ == "__main__":
    main()
