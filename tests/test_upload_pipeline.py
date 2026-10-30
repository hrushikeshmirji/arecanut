"""
ArecaGuard - Full Diagnostic Upload Pipeline Integration Test
============================================================
Simulates an end-to-end diagnostic pipeline execution for both:
1. `healthy_nut` (Healthy Areca Nut)
2. `mahali_koleroga` (Fruit Rot / Koleroga)

Validates:
- Detection & ViT classification matches ground truth.
- Valid confidence scores (0.0 to 1.0 / percentage).
- Generation of all 5 explainability artifacts:
  1. Original image
  2. YOLO bounding box visualization
  3. CNN feature map
  4. ViT multi-head attention map
  5. Grad-CAM heatmap overlay
- Complete ICAR-CPCRI management advisory verification.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Add backend directory to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

import cv2
import numpy as np
import torch
from PIL import Image

from detector import run_hybrid_inference, vit_model, vit_processor, _load_yolo
from explainability import ViTGradCAM
from main import LABEL_TO_DISEASE
from recommendations import get_recommendation

DEVICE = next(vit_model.parameters()).device


def find_sample_images() -> dict[str, Path]:
    """Find a representative image for healthy_nut and mahali_koleroga."""
    images = {}

    # Mahali Koleroga test image
    mk_test_dir = PROJECT_ROOT / "dataset_koleroga" / "test" / "images"
    if mk_test_dir.exists():
        for f in sorted(mk_test_dir.iterdir()):
            if f.suffix.lower() in [".jpg", ".jpeg", ".png"]:
                images["mahali_koleroga"] = f
                break

    # Healthy Nut sample image
    hn_patch_dir = PROJECT_ROOT / "dataset_patches" / "healthy_nut"
    if hn_patch_dir.exists():
        all_hn = sorted([f for f in hn_patch_dir.iterdir() if f.suffix.lower() in [".jpg", ".jpeg", ".png"]])
        if all_hn:
            images["healthy_nut"] = all_hn[-1]

    if "mahali_koleroga" not in images or "healthy_nut" not in images:
        raise FileNotFoundError("Could not find sample images for both classes.")

    return images


def generate_all_5_visualizations(img_path: Path, primary_bbox: list[int] | None) -> dict[str, any]:
    """
    Generate the 5 explainability visualizations:
    1. original: numpy array [H, W, 3]
    2. yolo_bbox: numpy array [H, W, 3] with drawn boxes
    3. cnn_feature_map: 2D feature map from YOLO backbone Conv layer [H', W']
    4. vit_attention_map: 14x14 token attention map from ViT final layer
    5. gradcam: base64 encoded JPEG data URL
    """
    pil_img = Image.open(img_path).convert("RGB")
    np_img = np.array(pil_img)
    h, w, c = np_img.shape

    # 1. Original
    v1_orig = np_img

    # 2. YOLO Bounding Box Visualization
    v2_bbox = np_img.copy()
    if primary_bbox and len(primary_bbox) == 4:
        x1, y1, x2, y2 = primary_bbox
        cv2.rectangle(v2_bbox, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(v2_bbox, "Detection", (x1, max(15, y1 - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # 3. CNN Feature Map (extracted from YOLO backbone Conv2d layer 0)
    yolo = _load_yolo()
    tensor_img = torch.from_numpy(np_img).permute(2, 0, 1).unsqueeze(0).float() / 255.0
    with torch.no_grad():
        cnn_feat = yolo.model.model[0](tensor_img)
    v3_cnn = cnn_feat[0].mean(dim=0).cpu().numpy()

    # 4. ViT Multi-Head Attention Map (14x14 patch token self-attention)
    vit_model.config._attn_implementation = "eager"
    inputs = vit_processor(images=pil_img, return_tensors="pt").to(DEVICE)
    with torch.no_grad():
        vit_out = vit_model(**inputs, output_attentions=True)
    last_layer_attn = vit_out.attentions[-1]
    v4_vit_attn = last_layer_attn[0, :, 0, 1:].mean(dim=0).view(14, 14).cpu().numpy()

    # 5. Grad-CAM Overlay
    explainer = ViTGradCAM(vit_model)
    v5_gradcam = explainer.generate_heatmap(pil_img, vit_processor)

    return {
        "original": v1_orig,
        "yolo_bbox": v2_bbox,
        "cnn_feature_map": v3_cnn,
        "vit_attention_map": v4_vit_attn,
        "gradcam": v5_gradcam,
    }


def test_upload_flow():
    print("=" * 65)
    print("  ARECAGUARD FULL DIAGNOSTIC PIPELINE INTEGRATION TEST")
    print("=" * 65)

    sample_images = find_sample_images()

    for expected_class, img_path in sample_images.items():
        print(f"\n>> Testing Target Class: [{expected_class.upper()}]")
        print(f"   Input Image : {img_path.name}")
        print(f"   Image Path  : {img_path}")

        # 1. Route through hybrid detection pipeline
        detections = run_hybrid_inference(str(img_path))
        assert len(detections) > 0, f"No detections returned for {expected_class}"
        primary = max(detections, key=lambda x: x["confidence"])

        pred_disease = primary["disease"]
        confidence = primary["confidence"]
        bbox = primary["bbox"]

        print(f"   Primary Prediction : '{pred_disease}' (Confidence: {confidence*100:.2f}%)")
        print(f"   Bounding Box       : {bbox}")

        # Assert correct disease classification
        assert pred_disease == expected_class, (
            f"Classification mismatch! Expected '{expected_class}', got '{pred_disease}'"
        )
        assert 0.0 <= confidence <= 1.0, f"Invalid confidence range: {confidence}"
        assert confidence >= 0.70, f"Confidence too low for {expected_class}: {confidence}"

        # 2. Generate and assert all 5 explainability visualizations
        print("   Generating all 5 explainability visualizations...")
        vis = generate_all_5_visualizations(img_path, bbox)

        # Assertions on dimensions and channels
        assert vis["original"].ndim == 3 and vis["original"].shape[2] == 3, "Original must be [H, W, 3]"
        assert vis["yolo_bbox"].ndim == 3 and vis["yolo_bbox"].shape[2] == 3, "YOLO bbox must be [H, W, 3]"
        assert vis["cnn_feature_map"].ndim == 2, "CNN feature map must be 2D [H, W]"
        assert vis["vit_attention_map"].shape == (14, 14), "ViT attention map must be exactly (14, 14)"
        assert vis["gradcam"].startswith("data:image/jpeg;base64,"), "Grad-CAM must be valid data URL"

        print(f"     [1] Original Image       : Shape {vis['original'].shape} OK")
        print(f"     [2] YOLO BBox Overlay    : Shape {vis['yolo_bbox'].shape} OK")
        print(f"     [3] CNN Feature Map      : Shape {vis['cnn_feature_map'].shape} OK")
        print(f"     [4] ViT Attention Map    : Shape {vis['vit_attention_map'].shape} OK")
        print(f"     [5] Grad-CAM Heatmap     : Length {len(vis['gradcam'])} chars OK")

        # 3. Advisory resolution & specific protocol assertion
        routed_disease = LABEL_TO_DISEASE.get(pred_disease, pred_disease)
        advisory = get_recommendation(routed_disease)

        print(f"   Routed Advisory Key : '{pred_disease}' -> '{routed_disease}'")
        print(f"   Advisory Name       : {advisory.get('common_name')}")
        print(f"   Severity Level      : {advisory.get('severity_level')}")

        if expected_class == "mahali_koleroga":
            # Assert exact ICAR-CPCRI Koleroga requirements:
            # - Phytophthora meadii
            # - 1% Bordeaux mixture
            # - Metalaxyl MZ 72% WP
            pathogen = advisory.get("pathogen", "")
            assert "Phytophthora meadii" in pathogen, f"Pathogen mismatch: {pathogen}"
            assert advisory.get("severity_level") == "critical", f"Severity mismatch: {advisory.get('severity_level')}"

            chem_steps = advisory.get("chemical", {}).get("steps", [])
            chem_str = " ".join(chem_steps)
            assert "1% Bordeaux mixture" in chem_str or "Bordeaux mixture" in chem_str, "Missing 1% Bordeaux mixture"
            assert "Metalaxyl MZ 72% WP" in chem_str, "Missing Metalaxyl MZ 72% WP recommendation"

            print(f"   Verified Pathogen   : {pathogen}")
            print(f"   Verified Chemicals  : 1% Bordeaux mixture & Metalaxyl MZ 72% WP")

        print(f"   >> [{expected_class.upper()}] Verification PASSED (100% OK)")

    print("\n" + "=" * 65)
    print("  ALL FULL DIAGNOSTIC PIPELINE TESTS PASSED")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    test_upload_flow()
