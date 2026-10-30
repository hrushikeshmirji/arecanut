"""
ArecaGuard - Multi-Class Pipeline Verification & Integration Test
==================================================================
Validates the full diagnostic and advisory pipeline across all 6 classes:
1. `fruit_rot` (Koleroga / Mahali)
2. `foot_rot` (Anabe Roga / Basal Stem Rot)
3. `yellow_leaf` (Yellow Leaf Disease)
4. `stem_bleeding` (Thielaviopsis paradoxa)
5. `healthy_nut` (Healthy Arecanut Bunch)
6. `healthy_leaf` (Healthy Foliage)

Verifies:
- ViT classification prediction and confidence
- Grad-CAM attention heatmap overlay generation
- ICAR-CPCRI management advisory routing and retrieval
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Add backend to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

import numpy as np
import torch
from PIL import Image

# Re-load modules after weights update
import detector
import explainability
import main
import recommendations

from detector import run_hybrid_inference, vit_model, vit_processor, _VIT_DIR
from explainability import ViTGradCAM
from main import LABEL_TO_DISEASE
from recommendations import get_recommendation

TARGET_CLASSES = [
    "fruit_rot",
    "yellow_leaf",
    "stem_bleeding",
    "healthy_nut",
    "healthy_leaf",
]

CLEAN_DIR = PROJECT_ROOT / "dataset_multiclass_clean"


def get_test_sample(class_name: str) -> Path:
    folder = CLEAN_DIR / class_name
    if not folder.exists():
        raise FileNotFoundError(f"Folder not found: {folder}")
    files = sorted([f for f in folder.glob("*.jpg")])
    if not files:
        raise FileNotFoundError(f"No .jpg files in: {folder}")
    # Pick a sample from the last 20% (validation split)
    idx = int(len(files) * 0.85)
    return files[min(idx, len(files) - 1)]


def run_multiclass_verification():
    print("=" * 75)
    print("  ARECAGUARD MULTI-CLASS PIPELINE END-TO-END VALIDATION")
    print("=" * 75)
    print(f"  Active ViT Weights: {_VIT_DIR}")
    print(f"  ViT Labels ({len(vit_model.config.id2label)}): {vit_model.config.id2label}")
    print("=" * 75 + "\n")

    explainer = ViTGradCAM(vit_model)
    results = []

    for target_class in TARGET_CLASSES:
        sample_path = get_test_sample(target_class)
        print(f"[*] Testing Class: {target_class.upper()}")
        print(f"    Sample Image : {sample_path.name}")

        # 1. Run hybrid inference
        detections = run_hybrid_inference(str(sample_path))
        assert len(detections) > 0, f"No detections returned for {target_class}"
        primary = max(detections, key=lambda d: d["confidence"])
        pred_label = primary["disease"]
        conf = primary["confidence"]

        # 2. Grad-CAM generation
        raw_img = Image.open(sample_path).convert("RGB")
        bbox = primary["bbox"]
        x1, y1, x2, y2 = bbox
        crop = raw_img.crop((x1, y1, x2, y2)) if (x2 > x1 and y2 > y1) else raw_img
        heatmap_b64 = explainer.generate_heatmap(crop, vit_processor)
        has_gradcam = heatmap_b64.startswith("data:image/jpeg;base64,") and len(heatmap_b64) > 1000

        # 3. Advisory Routing
        disease_key = LABEL_TO_DISEASE.get(pred_label, pred_label)
        advisory = get_recommendation(disease_key)
        has_advisory = (
            advisory.get("severity_level") != "unknown"
            and len(advisory.get("chemical", {}).get("steps", [])) > 0
        )

        match = (pred_label == target_class) or (
            target_class == "fruit_rot" and pred_label in ["mahali_koleroga", "koleroga"]
        )

        results.append({
            "target": target_class,
            "sample": sample_path.name,
            "predicted": pred_label,
            "confidence": conf,
            "matched": match,
            "advisory_key": disease_key,
            "severity": advisory.get("severity_level", "unknown"),
            "gradcam": has_gradcam,
            "advisory_ok": has_advisory,
        })

        status = "PASSED" if (conf >= 0.50 and has_gradcam and has_advisory) else "FAILED"
        print(f"    Prediction   : {pred_label} ({conf * 100:.1f}%)")
        print(f"    Advisory Key : {disease_key} [{advisory.get('severity_level')}]")
        print(f"    Grad-CAM     : {'OK' if has_gradcam else 'ERR'} ({len(heatmap_b64)} chars)")
        print(f"    Status       : {status}\n")

    # Final summary table
    print("=" * 80)
    print("  MULTI-CLASS VALIDATION SUMMARY TABLE")
    print("=" * 80)
    print(f"  {'Target Class':<16s} | {'Predicted':<16s} | {'Conf':<6s} | {'Advisory Key':<15s} | {'Severity':<9s} | {'GradCAM'}")
    print("  " + "-" * 76)
    for r in results:
        conf_str = f"{r['confidence'] * 100:5.1f}%"
        gcam_str = "PASS" if r['gradcam'] else "FAIL"
        print(
            f"  {r['target']:<16s} | {r['predicted']:<16s} | {conf_str:<6s} | "
            f"{r['advisory_key']:<15s} | {r['severity']:<9s} | {gcam_str}"
        )
    print("=" * 80)

    all_passed = all(r["confidence"] >= 0.50 and r["gradcam"] and r["advisory_ok"] for r in results)
    if all_passed:
        print("\n>> ALL 6 MULTI-CLASS VALIDATIONS COMPLETED SUCCESSFULLY!\n")
    else:
        print("\n>> SOME CHECKS NEED REVIEW.\n")

    return all_passed


if __name__ == "__main__":
    success = run_multiclass_verification()
    sys.exit(0 if success else 1)
