"""
Hybrid Inference Engine — YOLOv8 + Vision Transformer
=====================================================
1. YOLOv8 detects lesion bounding boxes on the leaf image.
2. Each detected region is cropped and classified by a fine-tuned ViT.
3. If no bounding boxes are found, the whole image is classified as fallback.
4. Exports vit_model and vit_processor for explainability and downstream use.
"""

from __future__ import annotations

import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

import torch
from PIL import Image
from ultralytics import YOLO
from transformers import ViTForImageClassification, ViTImageProcessor

logger = logging.getLogger(__name__)

# ── Paths ────────────────────────────────────────────────────────────────────
_BASE_DIR = Path(__file__).resolve().parent
_YOLO_WEIGHTS = _BASE_DIR / "weights" / "best.pt"
_VIT_V4_DIR = _BASE_DIR / "weights" / "vit_areca_classifier_v4"
_VIT_V3_DIR = _BASE_DIR / "weights" / "vit_areca_classifier_v3"
_VIT_V2_DIR = _BASE_DIR / "weights" / "vit_areca_classifier_v2"
_VIT_DIR = _VIT_V4_DIR if _VIT_V4_DIR.exists() else (_VIT_V3_DIR if _VIT_V3_DIR.exists() else _VIT_V2_DIR)

# ── Device selection ─────────────────────────────────────────────────────────
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
logger.info("Inference device: %s", device)

# ── Load ViT Model & Processor ───────────────────────────────────────────────
if not _VIT_DIR.exists():
    raise FileNotFoundError(f"ViT checkpoint not found at {_VIT_DIR}")

logger.info("Loading ViT classifier from %s", _VIT_DIR)
vit_processor = ViTImageProcessor.from_pretrained(str(_VIT_DIR))
vit_model = ViTForImageClassification.from_pretrained(str(_VIT_DIR))
vit_model.to(device)
vit_model.eval()

# ── YOLO Model Holder (Singleton) ────────────────────────────────────────────
_yolo_model: YOLO | None = None


def _load_yolo() -> YOLO:
    """Load the YOLOv8 model (singleton)."""
    global _yolo_model
    if _yolo_model is None:
        if not _YOLO_WEIGHTS.exists():
            raise FileNotFoundError(f"YOLOv8 weights not found at {_YOLO_WEIGHTS}")
        logger.info("Loading YOLOv8 from %s", _YOLO_WEIGHTS)
        _yolo_model = YOLO(str(_YOLO_WEIGHTS))
    return _yolo_model


import cv2
import numpy as np

id2label = vit_model.config.id2label
label2id = vit_model.config.label2id

ARECA_CLASSES = [
    "bud_borer", "fruit_rot", "healthy_leaf", "healthy_nut",
    "healthy_trunk", "stem_bleeding", "stem_cracking", "yellow_leaf"
]
areca_ids = [label2id[c] for c in ARECA_CLASSES if c in label2id]
non_areca_id = label2id.get("non_areca", None)
fruit_rot_id = label2id.get("fruit_rot", None)


def _botanical_sanity_check(pil_img: Image.Image, top_areca_prob: float = 0.0, p_na: float = 0.0) -> bool:
    """
    Validates whether the image contains natural botanical/plant features.
    Filters out studio white/marble backgrounds (e.g. non-palm objects on white marble)
    while preserving outdoor palm photos with blue/cloudy skies and harvested
    arecanut samples photographed on white laboratory paper.
    """
    small = pil_img.resize((160, 160))
    arr = np.array(small.convert("RGB"))
    hsv = cv2.cvtColor(arr, cv2.COLOR_RGB2HSV)
    h, s, v = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]
    total = arr.shape[0] * arr.shape[1]

    # Studio white / bright gray background check
    white_studio_ratio = float(np.sum((s < 35) & (v > 200)) / total)

    # Natural botanical signatures (green leaves, yellowing fronds, brown bark / dried rot)
    green_mask = (h >= 25) & (h <= 95) & (s >= 25) & (v >= 25)
    yellow_mask = (h >= 14) & (h < 25) & (s >= 30) & (v >= 30)
    brown_mask = (h >= 5) & (h < 25) & (s >= 20) & (s <= 230) & (v >= 18) & (v <= 190)
    botanical_ratio = float(np.sum(green_mask | yellow_mask | brown_mask) / total)

    # Outdoor blue sky / cloud check (sky blue H in [90, 130])
    sky_ratio = float(np.sum((h >= 90) & (h <= 130) & (s >= 20)) / total)
    is_outdoor_sky = (sky_ratio > 0.15) and (botanical_ratio >= 0.03)

    # If the deep learning model itself has strong arecanut confidence (>60%) with low non_areca (<15%),
    # harvested nuts or fronds on white laboratory paper are legitimate arecanut samples.
    if top_areca_prob >= 0.60 and p_na < 0.15:
        return True

    if is_outdoor_sky:
        return True

    # True non-palm studio / marble table rejection
    if white_studio_ratio > 0.50 and top_areca_prob < 0.55:
        return False

    if botanical_ratio < 0.02 and top_areca_prob < 0.55:
        return False

    return True


def _calibrate_visual_features(best_crop: Image.Image, areca_logits: torch.Tensor, top3_names: List[str], max_raw_areca_prob: float) -> torch.Tensor:
    """
    Balanced all-8-class visual and morphological calibration.
    Acts as a gentle, bounded (+0.5 to +0.8 logit) tie-breaker across all classes
    when the ViT model's top-3 candidates include that class, and never overrides
    a high-confidence (>85%) raw ViT prediction.
    """
    if max_raw_areca_prob >= 0.85:
        return areca_logits

    best_arr = np.array(best_crop.resize((160, 160)))
    b_hsv = cv2.cvtColor(best_arr, cv2.COLOR_RGB2HSV)
    bh, bs, bv = b_hsv[:, :, 0], b_hsv[:, :, 1], b_hsv[:, :, 2]
    tot_px = 160 * 160

    # Color ratios
    y_ratio = float(np.sum((bh >= 18) & (bh <= 34) & (bs >= 45) & (bv >= 90)) / tot_px)
    g_ratio = float(np.sum((bh >= 35) & (bh <= 85) & (bs >= 35) & (bv >= 35)) / tot_px)
    rot_ratio = float(np.sum((bh >= 6) & (bh <= 25) & (bs >= 40) & (bv >= 25) & (bv <= 125)) / tot_px)
    myc_ratio = float(np.sum((bs <= 30) & (bv >= 185)) / tot_px)
    nut_healthy_ratio = float(np.sum(((bh >= 35) & (bh <= 85) & (bs >= 35) & (bv >= 45)) | ((bh >= 14) & (bh < 25) & (bs >= 60) & (bv >= 110))) / tot_px)
    exud_ratio = float(np.sum((bh <= 25) & (bs >= 30) & (bv >= 10) & (bv <= 65)) / tot_px)
    frass_ratio = float(np.sum((bh >= 8) & (bh <= 22) & (bs >= 50) & (bv >= 30) & (bv <= 95)) / tot_px)

    # Vertical linear fissure analysis using Sobel
    gray = cv2.cvtColor(best_arr, cv2.COLOR_RGB2GRAY)
    grad_x = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
    grad_y = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
    vert_fissure_ratio = float(np.sum((np.abs(grad_x) > 2.0 * (np.abs(grad_y) + 1e-4)) & (np.abs(grad_x) > 35.0)) / tot_px)

    bark_mask = (bh >= 5) & (bh <= 30) & (bs >= 10) & (bs <= 180) & (bv >= 30) & (bv <= 210)
    bark_ratio = float(np.sum(bark_mask) / tot_px)

    # 1. yellow_leaf vs healthy_leaf
    if "yellow_leaf" in top3_names and y_ratio >= 0.10 and y_ratio > g_ratio * 0.35:
        areca_logits[label2id["yellow_leaf"]] += 0.8
    elif "healthy_leaf" in top3_names and g_ratio >= 0.35 and y_ratio < 0.05:
        areca_logits[label2id["healthy_leaf"]] += 0.8

    # 2. fruit_rot vs healthy_nut
    if "fruit_rot" in top3_names and (rot_ratio >= 0.08 or myc_ratio >= 0.05):
        areca_logits[label2id["fruit_rot"]] += 0.8
    elif "healthy_nut" in top3_names and nut_healthy_ratio >= 0.20 and rot_ratio < 0.04 and myc_ratio < 0.03:
        areca_logits[label2id["healthy_nut"]] += 0.8

    # 3. stem_bleeding vs stem_cracking vs healthy_trunk
    if "stem_bleeding" in top3_names and exud_ratio >= 0.07:
        areca_logits[label2id["stem_bleeding"]] += 0.8
    elif "stem_cracking" in top3_names and vert_fissure_ratio >= 0.10 and exud_ratio < 0.04:
        areca_logits[label2id["stem_cracking"]] += 0.8
    elif "healthy_trunk" in top3_names and bark_ratio >= 0.25 and exud_ratio < 0.03 and vert_fissure_ratio < 0.08:
        areca_logits[label2id["healthy_trunk"]] += 0.8

    # 4. bud_borer
    if "bud_borer" in top3_names and (frass_ratio >= 0.06 or (rot_ratio >= 0.05 and g_ratio >= 0.15)):
        areca_logits[label2id["bud_borer"]] += 0.8

    return areca_logits


def _classify_patch(patch: Image.Image) -> Dict[str, Any]:
    """
    Run Entropy-Weighted Multi-Scale ROI TTA (5 views) with balanced all-class
    visual calibration and refined OOD gating.
    """
    w, h = patch.size

    # View 1: Full image
    crop_full = patch

    # View 2: 75% Center Crop
    cw = max(16, int(w * 0.75))
    ch = max(16, int(h * 0.75))
    left = (w - cw) // 2
    top = (h - ch) // 2
    crop_center = patch.crop((left, top, left + cw, top + ch))

    # View 3: Upper-Center Crop (palm crown / fronds / yellow leaf / bud borer)
    crop_upper = patch.crop((left, 0, left + cw, max(16, int(h * 0.65))))

    # View 4: Lower-Center Crop (trunk base / stem bleeding / stem cracking)
    crop_lower = patch.crop((left, min(h - 16, int(h * 0.35)), left + cw, h))

    # View 5: Salient ROI or Flipped Center Crop
    crop_roi = crop_center.transpose(Image.FLIP_LEFT_RIGHT)
    if w >= 32 and h >= 32:
        try:
            yolo = _load_yolo()
            yolo_res = yolo.predict(source=patch, conf=0.20, verbose=False)
            if yolo_res and len(yolo_res[0].boxes) > 0:
                b = yolo_res[0].boxes[0]
                bx1, by1, bx2, by2 = [int(v) for v in b.xyxy[0].cpu().tolist()]
                pad_x = int((bx2 - bx1) * 0.15)
                pad_y = int((by2 - by1) * 0.15)
                rx1 = max(0, bx1 - pad_x)
                ry1 = max(0, by1 - pad_y)
                rx2 = min(w, bx2 + pad_x)
                ry2 = min(h, by2 + pad_y)
                if (rx2 - rx1) >= 16 and (ry2 - ry1) >= 16:
                    crop_roi = patch.crop((rx1, ry1, rx2, ry2))
        except Exception:
            pass

    crops = [crop_full, crop_center, crop_upper, crop_lower, crop_roi]
    inputs = vit_processor(images=crops, return_tensors="pt").to(device)

    with torch.no_grad():
        outputs = vit_model(**inputs)
        logits_batch = outputs.logits  # shape (5, num_classes)
        probs_batch = torch.nn.functional.softmax(logits_batch, dim=-1)

    # Entropy-weighted aggregation: crops with clearer disease focus get higher weight
    entropies = -torch.sum(probs_batch * torch.log2(probs_batch + 1e-9), dim=-1)
    weights = 1.0 / (entropies + 1e-4)
    norm_weights = weights / weights.sum()

    agg_probs = (probs_batch * norm_weights.unsqueeze(-1)).sum(dim=0)
    agg_logits = (logits_batch * norm_weights.unsqueeze(-1)).sum(dim=0)

    # Calculate overall aggregated entropy
    probs_np = agg_probs.cpu().numpy()
    non_zero = probs_np[probs_np > 1e-7]
    entropy = float(-np.sum(non_zero * np.log2(non_zero)))

    # Non-Areca & Botanical Check
    p_na = float(agg_probs[non_areca_id].item()) if non_areca_id is not None else 0.0
    top_areca_prob = float(agg_probs[areca_ids].max().item()) if areca_ids else 0.0
    passes_botanical = _botanical_sanity_check(patch, top_areca_prob=top_areca_prob, p_na=p_na)

    # Trigger OOD / Non-Areca rejection if:
    # 1. Image fails botanical check (studio background on non-arecanut object)
    # 2. Non-areca probability is greater than or equal to the top arecanut class probability
    # 3. Non-areca probability alone exceeds 35%
    # 4. Elevated non-areca probability (> 18%) with high entropy (> 1.85) and weak arecanut signal (< 45%)
    is_ood = (
        (not passes_botanical) or
        (p_na >= top_areca_prob) or
        (p_na > 0.35) or
        (p_na > 0.18 and entropy > 1.85 and top_areca_prob < 0.45)
    )

    if is_ood:
        conf_val = round(max(p_na, 0.75), 4)
        top_probabilities = [
            {"disease": vit_model.config.id2label[i], "probability": round(float(p), 4)}
            for i, p in enumerate(probs_np)
        ]
        top_probabilities.sort(key=lambda x: x["probability"], reverse=True)
        return {
            "disease": "non_areca",
            "raw_disease": "non_areca",
            "confidence": conf_val,
            "is_areca": False,
            "entropy": round(entropy, 4),
            "probabilities": top_probabilities[:3],
        }

    # Valid Arecanut Image: zero out non_areca logit so it does not dilute arecanut classes
    areca_logits = agg_logits.clone()
    if non_areca_id is not None:
        areca_logits[non_areca_id] = -1e9

    if areca_ids:
        top3_indices = torch.topk(areca_logits[areca_ids], k=min(3, len(areca_ids))).indices
        top3_names = [vit_model.config.id2label[areca_ids[i.item()]] for i in top3_indices]
    else:
        top3_names = []

    # Best crop index for visual calibration
    best_crop_idx = int(torch.argmin(entropies).item())
    best_crop = crops[best_crop_idx]

    # Balanced all-class visual calibration
    areca_logits = _calibrate_visual_features(best_crop, areca_logits, top3_names, max_raw_areca_prob=top_areca_prob)

    # Standard unsharpened calibrated probabilities (T=1.0)
    unsharpened_probs = torch.nn.functional.softmax(areca_logits[areca_ids], dim=-1)

    # Temperature scaling across arecanut classes (T=0.5 for confident peak)
    scaled_probs = torch.nn.functional.softmax(areca_logits[areca_ids] / 0.5, dim=-1)
    best_idx = scaled_probs.argmax().item()
    winning_label = vit_model.config.id2label[areca_ids[best_idx]]
    winning_conf = round(float(scaled_probs[best_idx].item()), 4)
    calibrated_conf = round(float(unsharpened_probs[best_idx].item()), 4)

    # Re-build top probabilities for arecanut classes
    areca_probs_list = [
        {
            "disease": vit_model.config.id2label[areca_ids[i]],
            "probability": round(float(p.item()), 4),
            "calibrated_probability": round(float(unsharpened_probs[i].item()), 4),
        }
        for i, p in enumerate(scaled_probs)
    ]
    areca_probs_list.sort(key=lambda x: x["probability"], reverse=True)

    # Co-infection detection: check if 2nd disease probability is substantial (>= 20%)
    secondary_info = None
    if len(areca_probs_list) > 1 and areca_probs_list[1]["probability"] >= 0.20:
        sec_d = areca_probs_list[1]["disease"]
        sec_p = areca_probs_list[1]["probability"]
        secondary_info = {
            "disease": sec_d,
            "probability": sec_p,
            "warning": f"Potential co-infection: Secondary symptoms of {sec_d} detected ({sec_p*100:.1f}%). Inspect palm for dual infection.",
        }

    raw_idx = agg_probs.argmax().item()
    raw_disease = vit_model.config.id2label[raw_idx]

    return {
        "disease": winning_label,
        "raw_disease": raw_disease,
        "confidence": winning_conf,
        "calibrated_confidence": calibrated_conf,
        "is_areca": True,
        "entropy": round(entropy, 4),
        "probabilities": areca_probs_list[:3],
        "secondary_diagnosis": secondary_info,
    }


def _extract_saliency_bbox(pil_img: Image.Image) -> Optional[List[int]]:
    """
    Extract a localized bounding box around salient lesions using multi-channel
    gradient energy and color contrast. Used for classes where YOLOv8 has no bounding
    box annotations (e.g., fruit_rot, stem_bleeding, healthy_nut, healthy_trunk).
    """
    try:
        w, h = pil_img.size
        sw, sh = min(w, 320), min(h, 320)
        small = pil_img.resize((sw, sh), Image.Resampling.BILINEAR)
        arr = np.array(small)

        gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
        
        # Spatial gradient energy
        grad_x = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
        mag = cv2.magnitude(grad_x, grad_y)
        
        # Smooth and normalize
        saliency = cv2.GaussianBlur(mag, (7, 7), 0)
        max_val = saliency.max()
        if max_val <= 0:
            return None
        norm_saliency = np.uint8(255 * (saliency / max_val))

        # Otsu thresholding for dominant salient cluster
        _, thresh = cv2.threshold(norm_saliency, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            valid_contours = [
                c for c in contours 
                if (sw * sh * 0.02) < cv2.contourArea(c) < (sw * sh * 0.85)
            ]
            if valid_contours:
                best_cnt = max(valid_contours, key=cv2.contourArea)
                bx, by, bw, bh = cv2.boundingRect(best_cnt)
                
                # Add 12% contextual padding around lesion
                pad_w = int(bw * 0.12)
                pad_h = int(bh * 0.12)
                bx1 = max(0, bx - pad_w)
                by1 = max(0, by - pad_h)
                bx2 = min(sw, bx + bw + pad_w)
                by2 = min(sh, by + bh + pad_h)

                scale_x = w / sw
                scale_y = h / sh
                return [int(bx1 * scale_x), int(by1 * scale_y), int(bx2 * scale_x), int(by2 * scale_y)]
    except Exception as exc:
        logger.debug("Saliency bbox extraction skipped: %s", exc)
    return None


def run_hybrid_inference(image_path: str) -> List[Dict[str, Any]]:
    """
    Execute the full hybrid detection pipeline with OOD gating.
    """
    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    pil_image = Image.open(image_path).convert("RGB")
    w, h = pil_image.size

    # ── Step 0: Holistic Whole-Image OOD Check ───────────────────────────
    whole_img_eval = _classify_patch(pil_image)
    if not whole_img_eval["is_areca"] or whole_img_eval["disease"] == "non_areca":
        logger.info(
            "Whole-image OOD gating triggered: classified as non_areca (conf: %s, entropy: %s)",
            whole_img_eval["confidence"],
            whole_img_eval["entropy"],
        )
        return [{
            "disease": "non_areca",
            "confidence": whole_img_eval["confidence"],
            "calibrated_confidence": whole_img_eval.get("calibrated_confidence", whole_img_eval["confidence"]),
            "bbox": None,
            "detection_source": "ood_gating",
            "is_areca": False,
            "entropy": whole_img_eval["entropy"],
            "probabilities": whole_img_eval["probabilities"],
        }]

    # ── Step 1: YOLO detection for valid arecanut images ─────────────────
    yolo = _load_yolo()
    results = yolo.predict(source=image_path, conf=0.25, verbose=False)
    detections: List[Dict[str, Any]] = []

    if results and len(results) > 0:
        boxes = results[0].boxes
        if boxes is not None and len(boxes) > 0:
            for box in boxes:
                xyxy = box.xyxy[0].cpu().tolist()
                x1, y1, x2, y2 = [int(v) for v in xyxy]

                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(w, x2), min(h, y2)

                patch = pil_image.crop((x1, y1, x2, y2))
                if patch.width < 10 or patch.height < 10:
                    continue

                result = _classify_patch(patch)
                if result["is_areca"] and result["disease"] != "non_areca":
                    detections.append({
                        "disease": result["disease"],
                        "confidence": result["confidence"],
                        "calibrated_confidence": result.get("calibrated_confidence", result["confidence"]),
                        "bbox": [x1, y1, x2, y2],
                        "detection_source": "yolo_detector",
                        "is_areca": True,
                        "probabilities": result["probabilities"],
                        "secondary_diagnosis": result.get("secondary_diagnosis"),
                    })

    # ── Step 2: Fallback to saliency-localized ViT diagnosis ─────────────
    if not detections:
        logger.info("No YOLO lesion boxes — computing ViT saliency localization")
        saliency_bbox = _extract_saliency_bbox(pil_image)
        has_saliency = saliency_bbox is not None
        detections.append({
            "disease": whole_img_eval["disease"],
            "confidence": whole_img_eval["confidence"],
            "calibrated_confidence": whole_img_eval.get("calibrated_confidence", whole_img_eval["confidence"]),
            "bbox": saliency_bbox if has_saliency else [0, 0, w, h],
            "detection_source": "vit_saliency_localization" if has_saliency else "whole_image_holistic",
            "is_areca": True,
            "probabilities": whole_img_eval["probabilities"],
            "secondary_diagnosis": whole_img_eval.get("secondary_diagnosis"),
        })

    detections.sort(key=lambda d: d["confidence"], reverse=True)
    return detections


# ── Explainability Helper Export ─────────────────────────────────────────────
try:
    from backend.xai_pipeline import generate_5_stage_xai
except ImportError:
    try:
        from xai_pipeline import generate_5_stage_xai
    except ImportError:
        generate_5_stage_xai = None

