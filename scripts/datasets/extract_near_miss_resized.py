"""
extract_near_miss_resized.py
=============================
TASK 1: Selective Resolution Resizing & Additional Image Extraction
------------------------------------------------------------------
Extracts near-miss candidate images from dataset_patches where:
  - min(w, h) >= 180 px (strictly rejecting heavily pixelated <180px crops)
  - One or both dimensions < 224 px
  - Upscaled to 224x224 px using high-fidelity LANCZOS interpolation
  - MD5 deduplication against active dataset and existing sanitized dataset
  - Screened by fine-tuned ViT classifier with >= 85.0% confidence threshold
  - Appended cleanly into dataset_legacy_sanitized/<class>/ with manifest updates
"""

import os
import sys
import io
import json
import time
import hashlib
from pathlib import Path
from typing import Dict, List, Set
from PIL import Image
import numpy as np
import torch
from transformers import ViTForImageClassification, ViTImageProcessor

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)

PROJECT_ROOT = Path("D:/arecanut_project").resolve()
ACTIVE_DATASET = PROJECT_ROOT / "dataset_large_scale_verified"
SANITIZED_ROOT = PROJECT_ROOT / "dataset_legacy_sanitized"
PATCHES_DIR = PROJECT_ROOT / "dataset_patches"
WEIGHTS_DIR = PROJECT_ROOT / "backend" / "weights" / "vit_areca_classifier_v2"

CONFIDENCE_THRESHOLD = 0.85
MIN_DIM_THRESHOLD = 180
TARGET_SIZE = (224, 224)
BATCH_SIZE = 16

torch.set_num_threads(os.cpu_count() or 4)


def compute_md5(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


def main():
    print("=" * 80)
    print("  TASK 1: SELECTIVE RESOLUTION RESIZING & EXTRACTION (>= 180px)")
    print("=" * 80)

    # 1. Load existing hashes from active dataset & existing sanitized dataset
    print("[1] Loading existing hashes to prevent duplicates...")
    existing_hashes: Set[str] = set()
    if ACTIVE_DATASET.exists():
        for p in ACTIVE_DATASET.rglob("*.*"):
            if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp", ".webp"}:
                try:
                    with open(p, "rb") as f:
                        existing_hashes.add(compute_md5(f.read()))
                except Exception:
                    pass

    manifest_path = SANITIZED_ROOT / "manifest.json"
    manifest: List[Dict] = []
    if manifest_path.exists():
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        for item in manifest:
            existing_hashes.add(item["md5"])

    print(f"    Indexed {len(existing_hashes)} existing unique image hashes.")

    # Current class counters
    class_counts = {}
    for item in manifest:
        c = item["class"]
        class_counts[c] = class_counts.get(c, 0) + 1
    print(f"    Current sanitized class counts: {class_counts}")

    # 2. Collect near-miss candidates
    print(f"\n[2] Scanning {PATCHES_DIR} for candidates with min_dim >= {MIN_DIM_THRESHOLD}px and < 224px...")
    candidates = []
    for p in PATCHES_DIR.rglob("*.*"):
        if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg", ".png"}:
            try:
                with open(p, "rb") as f:
                    raw = f.read()
                h = compute_md5(raw)
                if h in existing_hashes:
                    continue
                with Image.open(io.BytesIO(raw)) as im:
                    w, h_dim = im.size
                    if min(w, h_dim) >= MIN_DIM_THRESHOLD and (w < 224 or h_dim < 224):
                        candidates.append({
                            "path": p,
                            "orig_size": (w, h_dim),
                            "raw_bytes": raw,
                            "md5": h
                        })
            except Exception:
                pass

    print(f"    Found {len(candidates)} valid near-miss candidates.")

    if not candidates:
        print("    No additional candidates found.")
        return

    # 3. Load ViT Model
    print(f"\n[3] Loading ViT classifier from {WEIGHTS_DIR}...")
    processor = ViTImageProcessor.from_pretrained(str(WEIGHTS_DIR))
    model = ViTForImageClassification.from_pretrained(str(WEIGHTS_DIR))
    model.eval()
    device = torch.device("cpu")
    model.to(device)

    # 4. Upscale with Lanczos and run batch inference
    print("\n[4] Upscaling candidates to 224x224 (Lanczos) & evaluating ViT confidence...")
    accepted_items = []
    rejected_low_conf = 0

    for i in range(0, len(candidates), BATCH_SIZE):
        batch = candidates[i:i + BATCH_SIZE]
        pil_images = []
        for cand in batch:
            orig = Image.open(io.BytesIO(cand["raw_bytes"])).convert("RGB")
            # Gold-standard Lanczos resampling
            upscaled = orig.resize(TARGET_SIZE, Image.Resampling.LANCZOS)
            cand["upscaled_img"] = upscaled
            pil_images.append(upscaled)

        inputs = processor(images=pil_images, return_tensors="pt").to(device)
        with torch.no_grad():
            outputs = model(**inputs)
            probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
            confs, preds = probs.max(dim=-1)

        for j, cand in enumerate(batch):
            conf = float(confs[j].item())
            pred_idx = int(preds[j].item())
            pred_label = model.config.id2label[pred_idx]

            if conf >= CONFIDENCE_THRESHOLD:
                cand["pred_label"] = pred_label
                cand["conf"] = round(conf, 4)
                accepted_items.append(cand)
            else:
                rejected_low_conf += 1

    print(f"\n[5] Results of selective resizing:")
    print(f"    Total candidates evaluated : {len(candidates)}")
    print(f"    Passed (>= 85.0% conf)     : {len(accepted_items)} ({len(accepted_items)/len(candidates)*100:.1f}%)")
    print(f"    Rejected (low confidence)  : {rejected_low_conf}")

    # 5. Save accepted images
    print("\n[6] Saving accepted resized images and updating manifest...")
    new_manifest_entries = []
    for item in accepted_items:
        c = item["pred_label"]
        class_counts[c] = class_counts.get(c, 0) + 1
        seq_num = class_counts[c]
        target_name = f"{c}_leg_{seq_num:04d}.jpg"
        target_folder = SANITIZED_ROOT / c
        target_folder.mkdir(parents=True, exist_ok=True)
        target_path = target_folder / target_name

        # Save with high-quality JPEG
        item["upscaled_img"].save(target_path, "JPEG", quality=95, optimize=True)

        entry = {
            "filename": target_name,
            "class": c,
            "confidence": item["conf"],
            "original_repo": "dataset_patches_upscaled",
            "original_path": str(item["path"].relative_to(PROJECT_ROOT)),
            "original_size": item["orig_size"],
            "final_size": TARGET_SIZE,
            "resampling": "LANCZOS_upscaled_from_ge_180px",
            "md5": item["md5"]
        }
        manifest.append(entry)
        new_manifest_entries.append(entry)

    # Write updated manifest
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"    Updated manifest with {len(new_manifest_entries)} new entries.")
    print(f"    Total images in sanitized repository now: {len(manifest)}")
    print("\nUpdated Class Totals in dataset_legacy_sanitized:")
    for cls_name, total in sorted(class_counts.items()):
        print(f"    - {cls_name:<20}: {total}")
    print("=" * 80)


if __name__ == "__main__":
    main()
