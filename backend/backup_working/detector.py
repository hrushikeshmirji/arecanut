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
_VIT_V2_DIR = _BASE_DIR / "weights" / "vit_areca_classifier_v2"
_VIT_DIR = _VIT_V2_DIR

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


import numpy as np

def _classify_patch(patch: Image.Image) -> Dict[str, Any]:
    """
    Run ViT classification on a single image patch.
    Calculates top class, confidence, Shannon entropy, and OOD gating.
    """
    inputs = vit_processor(images=patch, return_tensors="pt").to(device)

    with torch.no_grad():
        outputs = vit_model(**inputs)
        logits = outputs.logits
        probs = torch.nn.functional.softmax(logits, dim=-1)[0]
        conf, idx = probs.max(dim=-1)

    label = vit_model.config.id2label[idx.item()]
    conf_val = round(conf.item(), 4)

    # Shannon Entropy calculation: H = -sum(p * log2(p))
    probs_np = probs.cpu().numpy()
    non_zero = probs_np[probs_np > 1e-7]
    entropy = float(-np.sum(non_zero * np.log2(non_zero)))

    # OOD & Non-Areca Gating:
    # 1. Top class is 'non_areca'
    # 2. Top confidence is below 0.60 (60%)
    # 3. High Shannon entropy (> 2.0 out of ~3.17 max for 9 classes)
    is_areca = True
    if label == "non_areca" or conf_val < 0.60 or entropy > 2.0:
        is_areca = False

    effective_label = label if is_areca else "non_areca"

    top_probabilities = [
        {"disease": vit_model.config.id2label[i], "probability": round(float(p), 4)}
        for i, p in enumerate(probs_np)
    ]
    top_probabilities.sort(key=lambda x: x["probability"], reverse=True)

    return {
        "disease": effective_label,
        "raw_disease": label,
        "confidence": conf_val,
        "is_areca": is_areca,
        "entropy": round(entropy, 4),
        "probabilities": top_probabilities[:3],
    }


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
            "bbox": None,
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
                        "bbox": [x1, y1, x2, y2],
                        "is_areca": True,
                        "probabilities": result["probabilities"],
                    })

    # ── Step 2: Fallback to whole-image classification ───────────────────
    if not detections:
        logger.info("No valid YOLO lesion boxes — using whole-image ViT diagnosis")
        detections.append({
            "disease": whole_img_eval["disease"],
            "confidence": whole_img_eval["confidence"],
            "bbox": [0, 0, w, h],
            "is_areca": True,
            "probabilities": whole_img_eval["probabilities"],
        })

    detections.sort(key=lambda d: d["confidence"], reverse=True)
    return detections
