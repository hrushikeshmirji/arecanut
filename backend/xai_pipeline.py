"""
ArecaGuard — 5-Stage Explainable AI (XAI) Pipeline
===================================================
Additive visual interpretability suite:
  Stage 1: Clean Original Image
  Stage 2: YOLO Detection + High-Activation Lesion Contours
  Stage 3: Early-Layer Feature Map (Viridis Activation Projection)
  Stage 4: ViT Self-Attention Rollout Heatmap (Inferno Token Focus)
  Stage 5: High-Resolution Grad-CAM Attention Heatmap

SAFETY GUARANTEE:
  Every stage operates strictly in torch.no_grad() or cleans up hooks in finally: blocks.
  All operations are isolated in individual try...except blocks so inference can NEVER fail.
"""

from __future__ import annotations

import base64
import io
import logging
from typing import Any, Dict, List, Optional

import cv2
import numpy as np
import torch
from PIL import Image

logger = logging.getLogger(__name__)


def _pil_to_base64(img: Image.Image, quality: int = 75) -> str:
    """Encode a PIL image to a Base64 JPEG data URL with size optimization."""
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality, optimize=True)
    b64_str = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{b64_str}"


def _cv2_to_base64(cv_rgb: np.ndarray, quality: int = 75) -> str:
    """Encode an RGB numpy array (cv2 image) to a Base64 JPEG data URL with size optimization."""
    cv_bgr = cv2.cvtColor(cv_rgb, cv2.COLOR_RGB2BGR)
    ok, buf = cv2.imencode(".jpg", cv_bgr, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
    if not ok:
        raise RuntimeError("Failed to encode cv2 image to JPEG")
    b64_str = base64.b64encode(buf).decode("utf-8")
    return f"data:image/jpeg;base64,{b64_str}"


def generate_5_stage_xai(
    raw_img: Image.Image,
    vit_model: Any,
    vit_processor: Any,
    gradcam_explainer: Any,
    detections: List[Dict[str, Any]],
    primary: Dict[str, Any],
    max_dim: int = 640,
) -> Dict[str, Optional[str]]:
    """
    Generate the safe additive 5-stage explainability suite.

    Returns
    -------
    dict with keys:
      'original_image', 'yolo_detection_image', 'feature_map_image',
      'attention_map_image', 'gradcam_image'
    """
    xai_results: Dict[str, Optional[str]] = {
        "original_image": None,
        "yolo_detection_image": None,
        "feature_map_image": None,
        "attention_map_image": None,
        "gradcam_image": None,
    }

    # Prepare snappy display image to keep JSON payload performant
    try:
        scale = min(1.0, max_dim / max(raw_img.width, raw_img.height))
        disp_w = max(16, int(raw_img.width * scale))
        disp_h = max(16, int(raw_img.height * scale))
        display_img = raw_img.resize((disp_w, disp_h), Image.Resampling.LANCZOS)
        np_orig = np.array(display_img)
    except Exception as exc:
        logger.warning("Display resize error in XAI pipeline: %s", exc)
        display_img = raw_img
        disp_w, disp_h = raw_img.size
        scale = 1.0
        np_orig = np.array(display_img)

    # ── Stage 1: Clean Input Image ───────────────────────────────────────────
    try:
        xai_results["original_image"] = _pil_to_base64(display_img)
    except Exception as exc:
        logger.warning("Stage 1 (Original Image) generation failed: %s", exc)

    # ── Stage 2: YOLO Detection + Lesion Contour Thresholding ─────────────────
    try:
        np_yolo = np_orig.copy()
        disease_label = primary.get("disease", "Lesion")
        conf_val = primary.get("confidence", 0.0)

        # Draw detected bounding boxes
        has_box = False
        for det in detections:
            bbox = det.get("bbox")
            if bbox and len(bbox) == 4:
                x1, y1, x2, y2 = bbox
                if x2 > x1 and y2 > y1 and not (x1 == 0 and y1 == 0 and x2 == raw_img.width and y2 == raw_img.height):
                    has_box = True
                    # Scale to display dimensions
                    bx1, by1 = max(0, int(x1 * scale)), max(0, int(y1 * scale))
                    bx2, by2 = min(disp_w, int(x2 * scale)), min(disp_h, int(y2 * scale))

                    det_source = det.get("detection_source", "yolo_detector")
                    is_saliency = (det_source == "vit_saliency_localization")
                    theme_color = (168, 85, 247) if is_saliency else (34, 197, 94)

                    # Bounding box border
                    cv2.rectangle(np_yolo, (bx1, by1), (bx2, by2), theme_color, 2)

                    # Label pill banner
                    tag = " [ViT Saliency]" if is_saliency else ""
                    label_str = f"{det.get('disease', disease_label)}{tag} {det.get('confidence', conf_val)*100:.1f}%"
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    font_scale = 0.5
                    thickness = 1
                    (text_w, text_h), baseline = cv2.getTextSize(label_str, font, font_scale, thickness)
                    banner_y1 = max(0, by1 - text_h - baseline - 4)
                    banner_y2 = by1
                    banner_x2 = min(disp_w, bx1 + text_w + 8)

                    cv2.rectangle(np_yolo, (bx1, banner_y1), (banner_x2, banner_y2), theme_color, -1)
                    cv2.putText(
                        np_yolo,
                        label_str,
                        (bx1 + 4, banner_y2 - baseline),
                        font,
                        font_scale,
                        (255, 255, 255),
                        thickness,
                        cv2.LINE_AA,
                    )

                    # High-activation contour thresholding inside the crop
                    crop = np_orig[by1:by2, bx1:bx2]
                    if crop.shape[0] > 10 and crop.shape[1] > 10:
                        gray_crop = cv2.cvtColor(crop, cv2.COLOR_RGB2GRAY)
                        blurred = cv2.GaussianBlur(gray_crop, (7, 7), 0)
                        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
                        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                        # Draw tight lesion contours in amber/gold
                        target_roi = np_yolo[by1:by2, bx1:bx2]
                        cv2.drawContours(target_roi, contours, -1, (245, 158, 11), 1, cv2.LINE_AA)

        # Fallback if no specific sub-box detected (e.g., whole-leaf fallback)
        if not has_box:
            # Draw subtle diagnostic frame around image
            cv2.rectangle(np_yolo, (4, 4), (disp_w - 4, disp_h - 4), (14, 165, 233), 2)  # Sky blue
            label_str = f"Whole-Image Context: {disease_label} ({conf_val*100:.1f}%)"
            cv2.putText(np_yolo, label_str, (12, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (14, 165, 233), 2, cv2.LINE_AA)

        xai_results["yolo_detection_image"] = _cv2_to_base64(np_yolo)
    except Exception as exc:
        logger.warning("Stage 2 (YOLO Detection) generation failed: %s", exc)

    # ── Stage 3: Early-Layer Feature Map (Viridis Activation Projection) ──────
    try:
        captured_activations: List[torch.Tensor] = []

        def _feature_hook(module, inp, out):
            if isinstance(out, (list, tuple)):
                tensor = out[0]
            else:
                tensor = out
            captured_activations.append(tensor.detach())

        # Safely find first ViT encoder layer across transformers versions
        target_layer = None
        if hasattr(vit_model, "vit"):
            if hasattr(vit_model.vit, "layers") and len(vit_model.vit.layers) > 0:
                target_layer = vit_model.vit.layers[0]
            elif hasattr(vit_model.vit, "encoder") and hasattr(vit_model.vit.encoder, "layer"):
                target_layer = vit_model.vit.encoder.layer[0]

        if target_layer is not None:
            hook_handle = target_layer.register_forward_hook(_feature_hook)
            try:
                device = next(vit_model.parameters()).device
                inputs = vit_processor(images=display_img, return_tensors="pt").to(device)
                with torch.no_grad():
                    _ = vit_model(**inputs)
            finally:
                # MANDATORY: Remove hook so model state is never mutated
                hook_handle.remove()

            if captured_activations:
                # Shape: [batch, 197 tokens, 768 channels]
                # Tokens: index 0 is CLS, indices 1..196 are the 14x14 spatial patches
                raw_act = captured_activations[0]
                if raw_act.ndim == 3 and raw_act.size(1) >= 197:
                    spatial_patches = raw_act[0, 1:, :]  # [196, 768]
                    # Compute feature activation magnitude
                    mag = torch.norm(spatial_patches, dim=-1).view(14, 14).cpu().numpy()
                    mag_resized = cv2.resize(mag, (disp_w, disp_h))
                    norm_mag = np.uint8(255 * (mag_resized - mag_resized.min()) / (mag_resized.max() - mag_resized.min() + 1e-8))
                    colormap_feat = cv2.applyColorMap(norm_mag, cv2.COLORMAP_VIRIDIS)
                    colormap_feat_rgb = cv2.cvtColor(colormap_feat, cv2.COLOR_BGR2RGB)
                    # Blend 55% original photo + 45% early feature activations
                    blend_feat = cv2.addWeighted(np_orig, 0.55, colormap_feat_rgb, 0.45, 0)
                    xai_results["feature_map_image"] = _cv2_to_base64(blend_feat)
    except Exception as exc:
        logger.warning("Stage 3 (Feature Map) generation failed: %s", exc)

    # ── Stage 4: ViT Self-Attention Rollout Heatmap (Inferno Token Focus) ─────
    try:
        orig_attn = getattr(vit_model.config, "_attn_implementation", "sdpa")
        try:
            # Dynamically activate eager attention for attention matrix extraction
            vit_model.config._attn_implementation = "eager"
            device = next(vit_model.parameters()).device
            inputs = vit_processor(images=display_img, return_tensors="pt").to(device)
            with torch.no_grad():
                out = vit_model(**inputs, output_attentions=True)
        finally:
            # MANDATORY: Restore original attention implementation
            vit_model.config._attn_implementation = orig_attn

        if hasattr(out, "attentions") and out.attentions is not None and len(out.attentions) > 0:
            num_tokens = out.attentions[0].size(-1)  # 197
            rollout = torch.eye(num_tokens, device=device)
            for layer_attn in out.attentions:
                # Average across 12 attention heads
                head_mean = layer_attn[0].mean(dim=0)  # [197, 197]
                # Residual connection: A = 0.5 * head_mean + 0.5 * I
                A = 0.5 * head_mean + 0.5 * torch.eye(num_tokens, device=device)
                A = A / A.sum(dim=-1, keepdim=True)
                rollout = torch.matmul(A, rollout)

            # CLS token (index 0) attention rollout to spatial patches (index 1 to 196)
            cls_attn = rollout[0, 1:].view(14, 14).cpu().numpy()
            attn_resized = cv2.resize(cls_attn, (disp_w, disp_h))
            norm_attn = np.uint8(255 * (attn_resized - attn_resized.min()) / (attn_resized.max() - attn_resized.min() + 1e-8))
            colormap_attn = cv2.applyColorMap(norm_attn, cv2.COLORMAP_INFERNO)
            colormap_attn_rgb = cv2.cvtColor(colormap_attn, cv2.COLOR_BGR2RGB)
            # Blend 50% original photo + 50% attention rollout
            blend_attn = cv2.addWeighted(np_orig, 0.50, colormap_attn_rgb, 0.50, 0)
            xai_results["attention_map_image"] = _cv2_to_base64(blend_attn)
    except Exception as exc:
        logger.warning("Stage 4 (Attention Map Rollout) generation failed: %s", exc)

    # ── Stage 5: Grad-CAM Overlay ────────────────────────────────────────────
    try:
        if gradcam_explainer is not None:
            # Target crop or whole image
            bbox = primary.get("bbox")
            if bbox and len(bbox) == 4 and (bbox[2] > bbox[0] and bbox[3] > bbox[1]):
                target_crop = raw_img.crop((bbox[0], bbox[1], bbox[2], bbox[3]))
            else:
                target_crop = raw_img
            xai_results["gradcam_image"] = gradcam_explainer.generate_heatmap(target_crop, vit_processor)
    except Exception as exc:
        logger.warning("Stage 5 (Grad-CAM) generation failed: %s", exc)

    return xai_results
