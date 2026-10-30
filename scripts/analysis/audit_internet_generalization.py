"""
audit_internet_generalization.py
=================================
Diagnoses how the ArecaGuard inference pipeline handles simulated real-world
internet and hand-held camera conditions:
- Off-center framing (palm crown at top, stem at bottom)
- High JPEG compression (quality 50, typical of web/WhatsApp)
- Contrast / brightness shifts (harsh tropical sun vs. cloudy monsoon)
- Wide/tall aspect ratios with outdoor sky/ground exposure
- Cross-class interference from aggressive fruit_rot tie-breaker
"""

import sys
import io
import torch
import numpy as np
from pathlib import Path
from PIL import Image, ImageEnhance
from typing import Dict, List, Tuple

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path("D:/arecanut_project").resolve()
sys.path.insert(0, str(PROJECT_ROOT))

from backend.detector import _classify_patch, run_hybrid_inference, vit_model, vit_processor

VAL_DIR = PROJECT_ROOT / "dataset_clean_verified" / "val"
CLASSES = [
    "bud_borer", "fruit_rot", "healthy_leaf", "healthy_nut",
    "healthy_trunk", "stem_bleeding", "stem_cracking", "yellow_leaf", "non_areca"
]


def simulate_internet_distortions(img: Image.Image, scenario: str) -> Image.Image:
    """Apply realistic web / smartphone distortions."""
    w, h = img.size

    if scenario == "jpeg_compression":
        # Simulate WhatsApp / Web JPEG compression
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=45)
        buf.seek(0)
        return Image.open(buf).convert("RGB")

    elif scenario == "brightness_sun":
        # Tropical harsh direct sunlight
        enhancer = ImageEnhance.Brightness(img)
        img_bright = enhancer.enhance(1.3)
        enhancer = ImageEnhance.Contrast(img_bright)
        return enhancer.enhance(1.2)

    elif scenario == "cloudy_shade":
        # Monsoon dim overcast lighting
        enhancer = ImageEnhance.Brightness(img)
        img_dim = enhancer.enhance(0.75)
        enhancer = ImageEnhance.Contrast(img_dim)
        return enhancer.enhance(0.85)

    elif scenario == "off_center_crop":
        # Image where user framed subject in upper 70% or lower 70%
        crop_h = int(h * 0.75)
        return img.crop((0, 0, w, crop_h)).resize((w, h))

    elif scenario == "sky_background_pad":
        # Outdoor palm shot with 35% bright cloudy sky at the top
        new_h = int(h * 1.35)
        new_img = Image.new("RGB", (w, new_h), (210, 225, 240))  # Light sky blue/grey
        new_img.paste(img, (0, new_h - h))
        return new_img.resize((w, h))

    return img


def run_audit():
    print("=" * 80)
    print("  ARECAGUARD INTERNET GENERALIZATION & ROBUSTNESS AUDIT")
    print("=" * 80)

    scenarios = ["clean", "jpeg_compression", "brightness_sun", "cloudy_shade", "off_center_crop", "sky_background_pad"]
    results: Dict[str, Dict[str, Tuple[int, int]]] = {c: {s: [0, 0] for s in scenarios} for c in CLASSES}
    failure_details = []

    for cls in CLASSES:
        cls_dir = VAL_DIR / cls
        if not cls_dir.exists():
            continue
        test_images = sorted(list(cls_dir.glob("*.*")))[:5]  # Test 5 samples per class

        for img_p in test_images:
            try:
                base_img = Image.open(img_p).convert("RGB")
            except Exception:
                continue

            for s in scenarios:
                dist_img = simulate_internet_distortions(base_img, s)
                pred = _classify_patch(dist_img)
                pred_label = pred["disease"]
                is_correct = (pred_label == cls)

                results[cls][s][1] += 1
                if is_correct:
                    results[cls][s][0] += 1
                else:
                    failure_details.append({
                        "class": cls,
                        "file": img_p.name,
                        "scenario": s,
                        "predicted": pred_label,
                        "confidence": pred.get("confidence", 0),
                        "is_areca": pred.get("is_areca", True)
                    })

    # Print Summary Table
    print("\n--- Summary: Accuracy by Class and Internet Distortion Scenario ---")
    headers = f"{'Class':16} | " + " | ".join([f"{s[:9]:9}" for s in scenarios]) + " | Total Acc"
    print(headers)
    print("-" * len(headers))

    total_correct = 0
    total_evaluated = 0

    for cls in CLASSES:
        row = f"{cls:16} | "
        cls_c = 0
        cls_t = 0
        for s in scenarios:
            c, t = results[cls][s]
            acc = (c / t * 100) if t > 0 else 0
            row += f"{acc:8.1f}% | "
            cls_c += c
            cls_t += t
        cls_acc = (cls_c / cls_t * 100) if cls_t > 0 else 0
        row += f"{cls_acc:8.1f}%"
        print(row)
        total_correct += cls_c
        total_evaluated += cls_t

    overall_acc = (total_correct / total_evaluated * 100) if total_evaluated > 0 else 0
    print("-" * len(headers))
    print(f"Overall Accuracy Across All Scenarios: {overall_acc:.2f}% ({total_correct}/{total_evaluated})")

    print(f"\n--- Failure Pattern Analysis (Total Failures: {len(failure_details)}) ---")
    failure_counts = {}
    for f in failure_details:
        key = f"{f['class']} -> {f['predicted']} ({f['scenario']})"
        failure_counts[key] = failure_counts.get(key, 0) + 1

    for k, cnt in sorted(failure_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  * {k}: {cnt} occurrence(s)")


if __name__ == "__main__":
    run_audit()
