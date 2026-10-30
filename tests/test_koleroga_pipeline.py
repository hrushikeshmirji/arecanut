"""
ArecaGuard - Koleroga / Fruit Rot End-to-End Pipeline Integration Test
======================================================================
Tests the full diagnostic and advisory pipeline on a real test sample:
1. Feeds a sample image from dataset_koleroga through hybrid inference.
2. Verifies YOLO detection / fallback and ViT v2 classifier output.
3. Generates and validates Grad-CAM attention heatmap overlay.
4. Generates and validates multi-head self-attention token maps.
5. Verifies advisory resolution from backend/recommendations.py.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Add backend directory to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

import numpy as np
import torch
from PIL import Image

from detector import run_hybrid_inference, vit_model, vit_processor, _VIT_DIR
from explainability import ViTGradCAM
from main import LABEL_TO_DISEASE
from recommendations import get_recommendation


def select_sample_image() -> Path:
    """Find a verified Koleroga validation or test image."""
    search_paths = [
        PROJECT_ROOT / "dataset_koleroga" / "valid" / "images",
        PROJECT_ROOT / "dataset_koleroga" / "test" / "images",
    ]
    for p in search_paths:
        if p.exists():
            for f in sorted(p.iterdir()):
                if f.suffix.lower() in [".jpg", ".jpeg", ".png"] and "koleroga" in f.name.lower():
                    return f
            # If no file with koleroga in name, pick first image
            for f in sorted(p.iterdir()):
                if f.suffix.lower() in [".jpg", ".jpeg", ".png"]:
                    return f

    raise FileNotFoundError("Could not locate a test image in dataset_koleroga/valid or test splits.")


def test_pipeline():
    print("=" * 65)
    print("  ARECAGUARD END-TO-END INTEGRATION TEST: KOLEROGA PIPELINE")
    print("=" * 65)

    sample_img_path = select_sample_image()
    print(f"  [1] Target Sample Image : {sample_img_path.name}")
    print(f"      Source Path         : {sample_img_path}")
    print(f"      Active ViT Weights  : {_VIT_DIR}")

    with Image.open(sample_img_path) as img:
        img_w, img_h = img.size
        print(f"      Image Resolution    : {img_w} x {img_h} px")

    # 1. Run Hybrid Detection Pipeline
    print("\n  [2] Running Hybrid Inference Pipeline...")
    detections = run_hybrid_inference(str(sample_img_path))
    print(f"      Total Regions Evaluated : {len(detections)}")

    assert len(detections) > 0, "Pipeline returned 0 detections."
    primary = max(detections, key=lambda x: x["confidence"])

    print(f"      Primary Disease Label   : {primary['disease']}")
    print(f"      Prediction Confidence   : {primary['confidence'] * 100:.2f}%")
    print(f"      Bounding Box Coordinates: {primary['bbox']}")

    # Verification: Must recognize mahali_koleroga or fruit_rot
    recognized_names = {"mahali_koleroga", "fruit_rot", "koleroga"}
    is_fruit_rot = primary["disease"].lower() in recognized_names
    assert is_fruit_rot, f"Expected fruit rot class, but received: {primary['disease']}"
    assert primary["confidence"] >= 0.50, f"Confidence too low: {primary['confidence']}"
    print("      >> Verification PASSED: Valid Koleroga detection with high confidence.")

    # 2. Explainability Artifact: Grad-CAM Heatmap
    print("\n  [3] Generating Explainability Artifacts (Grad-CAM)...")
    explainer = ViTGradCAM(vit_model)
    raw_pil = Image.open(sample_img_path).convert("RGB")

    x1, y1, x2, y2 = primary["bbox"]
    crop = raw_pil.crop((x1, y1, x2, y2)) if (x2 > x1 and y2 > y1) else raw_pil

    heatmap_b64 = explainer.generate_heatmap(crop, vit_processor)
    assert heatmap_b64.startswith("data:image/jpeg;base64,"), "Invalid Grad-CAM data URL."
    print(f"      Grad-CAM Overlay Base64 : {heatmap_b64[:45]}... ({len(heatmap_b64)} chars)")
    print("      >> Verification PASSED: Valid Grad-CAM overlay generated.")

    # 3. Explainability Artifact: ViT Multi-Head Self-Attention Map
    print("\n  [4] Extracting ViT Multi-Head Self-Attention Map...")
    vit_model.config._attn_implementation = "eager"
    inputs = vit_processor(images=crop, return_tensors="pt").to(next(vit_model.parameters()).device)
    with torch.no_grad():
        outputs = vit_model(**inputs, output_attentions=True)

    assert outputs.attentions is not None and len(outputs.attentions) > 0, "No attention weights returned."
    last_layer_attn = outputs.attentions[-1]  # shape: [batch, num_heads, 197, 197]
    num_heads = last_layer_attn.size(1)
    # Average across all 12 heads for the [CLS] token attending to spatial patches (1:197)
    cls_attention = last_layer_attn[0, :, 0, 1:].mean(dim=0).view(14, 14).cpu().numpy()

    print(f"      Encoder Layers Captured : {len(outputs.attentions)}")
    print(f"      Attention Heads Evaluated: {num_heads}")
    print(f"      Spatial Patch Grid Shape: {cls_attention.shape} (14x14 = 196 patches)")
    print(f"      Attention Weight Range   : [{cls_attention.min():.5f}, {cls_attention.max():.5f}]")
    print("      >> Verification PASSED: ViT Multi-Head Attention Map successfully extracted.")

    # 4. Advisory Retrieval & Routing
    print("\n  [5] Verifying ICAR-CPCRI Advisory Retrieval & Routing...")
    routed_key = LABEL_TO_DISEASE.get(primary["disease"], primary["disease"])
    print(f"      Label-to-Disease Route  : '{primary['disease']}' -> '{routed_key}'")

    advisory = get_recommendation(routed_key)
    print(f"      Common Name             : {advisory.get('common_name')}")
    print(f"      Pathogen                : {advisory.get('pathogen')}")
    print(f"      Severity Level          : {advisory.get('severity_level')}")

    # Verify critical advisory elements
    assert "Phytophthora meadii" in advisory.get("pathogen", ""), f"Wrong pathogen: {advisory.get('pathogen')}"
    assert advisory.get("severity_level") == "critical", f"Wrong severity: {advisory.get('severity_level')}"

    chem_steps = advisory.get("chemical", {}).get("steps", [])
    chem_text = " ".join(chem_steps)
    assert "1% Bordeaux mixture" in chem_text or "Bordeaux mixture" in chem_text, "Missing Bordeaux mixture advice."

    print("      Chemical Treatment Steps :")
    for s in chem_steps:
        print(f"        * {s}")

    cult_steps = advisory.get("cultural", {}).get("steps", [])
    print("      Cultural Control Steps   :")
    for s in cult_steps:
        print(f"        * {s}")

    fert_steps = advisory.get("fertilizer", {}).get("steps", [])
    print("      Nutrient & Drainage Steps:")
    for s in fert_steps:
        print(f"        * {s}")

    print("      >> Verification PASSED: Complete ICAR-CPCRI advisory retrieved with critical protocol.")

    print("\n" + "=" * 65)
    print("  ALL 5 INTEGRATION CHECKS PASSED SUCCESSFULLY (100% OK)")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    test_pipeline()
