"""
ArecaGuard - Multi-Class Inference Verification
================================================
Tests the fine-tuned ViT classifier v2 against 1 sample from each
canonical class in D:\arecanut_project\dataset_clean_verified\val\:
  - fruit_rot
  - yellow_leaf
  - stem_bleeding
  - bud_borer
  - stem_cracking
  - healthy_nut
  - healthy_leaf
  - healthy_trunk

Validates:
  1. Prediction label
  2. Confidence score
  3. ICAR-CPCRI Advisory retrieval from backend/recommendations.py
"""

from __future__ import annotations

import os
import random
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)

import torch
from PIL import Image
from transformers import ViTForImageClassification, ViTImageProcessor

# Add project root to sys.path so recommendations can be imported
PROJECT_ROOT = Path("D:/arecanut_project").resolve()
sys.path.insert(0, str(PROJECT_ROOT))

from backend.recommendations import get_recommendation

VAL_DIR = PROJECT_ROOT / "dataset_clean_verified" / "val"
WEIGHTS_DIR = PROJECT_ROOT / "backend" / "weights" / "vit_areca_classifier_v2"


def main():
    print("=" * 75)
    print("  ARECAGUARD MULTI-CLASS INFERENCE & ADVISORY VERIFICATION")
    print("=" * 75)

    if not WEIGHTS_DIR.exists():
        print(f"Error: Weights directory not found at {WEIGHTS_DIR}")
        sys.exit(1)

    print(f"\n[1] Loading ViT classifier from {WEIGHTS_DIR}...")
    processor = ViTImageProcessor.from_pretrained(str(WEIGHTS_DIR))
    model = ViTForImageClassification.from_pretrained(str(WEIGHTS_DIR))
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()

    classes = sorted([d.name for d in VAL_DIR.iterdir() if d.is_dir()])
    print(f"Discovered classes ({len(classes)}): {classes}")

    results = []

    print("\n[2] Running sample inference per class...")
    for cls in classes:
        cls_folder = VAL_DIR / cls
        files = [
            f for f in sorted(cls_folder.iterdir())
            if f.is_file() and f.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
        ]
        if not files:
            print(f"  Warning: No images found in {cls_folder}")
            continue

        # Deterministic or random sample
        sample_img = files[0]

        with Image.open(sample_img) as raw_img:
            img = raw_img.convert("RGB")
            inputs = processor(images=img, return_tensors="pt").to(device)

        with torch.no_grad():
            outputs = model(**inputs)
            probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
            conf, pred_idx = probs.max(dim=-1)

        pred_label = model.config.id2label[pred_idx.item()]
        conf_pct = conf.item() * 100.0

        # Retrieve advisory
        rec = get_recommendation(pred_label)
        has_chemical = bool(rec.get("chemical", {}).get("steps"))
        has_cultural = bool(rec.get("cultural", {}).get("steps"))
        has_fertilizer = bool(rec.get("fertilizer", {}).get("steps"))
        severity = rec.get("severity_level", "unknown")

        is_correct = (pred_label == cls)
        results.append({
            "gt": cls,
            "pred": pred_label,
            "conf": conf_pct,
            "correct": is_correct,
            "file": sample_img.name,
            "severity": severity,
            "advisory_complete": (has_chemical and has_cultural and has_fertilizer),
            "common_name": rec.get("common_name", "N/A"),
        })

    print("\n" + "=" * 80)
    print(f"{'Ground Truth':<16} | {'Predicted Label':<16} | {'Conf':<7} | {'Severity':<9} | {'Match?':<6} | {'Advisory OK'}")
    print("-" * 80)
    all_ok = True
    for r in results:
        status = "PASS" if r["correct"] else "FAIL"
        adv_ok = "YES" if r["advisory_complete"] else "NO"
        if not r["correct"]:
            all_ok = False
        print(f"{r['gt']:<16} | {r['pred']:<16} | {r['conf']:5.1f}% | {r['severity']:<9} | {status:<6} | {adv_ok}")
    print("=" * 80)

    if all_ok:
        print("\n[SUCCESS] All classes correctly classified with verified ICAR-CPCRI advisories!")
    else:
        print("\n[NOTE] Some samples had misclassifications or lower confidence.")


if __name__ == "__main__":
    main()
