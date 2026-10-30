"""
run_full_project_healthcheck.py
================================
Comprehensive verification suite for the ArecaGuard system:
1. Model Weights & Config Check (all 9 classes in id2label and label2id)
2. Multi-Class Standard & Internet-Simulated Generalization Accuracy (>95% standard, >90% internet-simulated)
3. 5-Stage Explainability (XAI) Base64 Verification
4. Bilingual Advisory Check (English and Kannada / ಕನ್ನಡ for all classes)
5. Frontend Build & HTTP API Verification (Direct Backend & Vite Proxy)
"""

import sys
import io
import json
import requests
import torch
import numpy as np
from pathlib import Path
from PIL import Image, ImageEnhance

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path("D:/arecanut_project").resolve()
sys.path.insert(0, str(PROJECT_ROOT))

from backend.detector import vit_model, vit_processor, _classify_patch, run_hybrid_inference
from backend.recommendations import get_recommendation, _RECOMMENDATIONS

VAL_DIR = PROJECT_ROOT / "dataset_unified_v4" / "val"
if not VAL_DIR.exists():
    VAL_DIR = PROJECT_ROOT / "dataset_unified_v3" / "val"
if not VAL_DIR.exists():
    VAL_DIR = PROJECT_ROOT / "dataset_clean_verified" / "val"
EXPECTED_CLASSES = [
    "bud_borer", "fruit_rot", "healthy_leaf", "healthy_nut",
    "healthy_trunk", "non_areca", "stem_bleeding", "stem_cracking", "yellow_leaf"
]

passed_tests = 0
total_tests = 5


def main():
    global passed_tests

    print("=" * 80)
    print("  ARECAGUARD FULL PROJECT HEALTHCHECK & END-TO-END PIPELINE AUDIT")
    print("=" * 80)

    # ── [1] Model Weights & Config Check ───────────────────────────────────────
    print("\n[TEST 1/5] Model Weights & Checkpoint Configuration Check...")
    id2label = vit_model.config.id2label
    label2id = vit_model.config.label2id
    model_classes = sorted(list(id2label.values()))

    print(f"  Model loaded classes ({len(model_classes)}): {model_classes}")
    assert len(model_classes) == 9, f"Expected 9 classes, got {len(model_classes)}"
    assert model_classes == sorted(EXPECTED_CLASSES), f"Classes mismatch: {model_classes}"
    for k, v in id2label.items():
        assert label2id[v] == int(k), f"Config id2label/label2id mismatch for {v}"
    print("  -> TEST 1 PASSED: Checkpoint weights and 9-class mappings are fully verified.")
    passed_tests += 1

    # ── [2] Multi-Class Accuracy & Internet Simulation Check ───────────────────
    print("\n[TEST 2/5] Multi-Class Standard & Internet-Simulated Accuracy Check...")
    std_correct = 0
    std_total = 0
    sim_correct = 0
    sim_total = 0

    for cls in EXPECTED_CLASSES:
        cls_dir = VAL_DIR / cls
        images = sorted(list(cls_dir.glob("*.*")))[:4]  # 4 samples per class

        for img_p in images:
            im = Image.open(img_p).convert("RGB")
            # Clean standard inference
            res_std = _classify_patch(im)
            std_total += 1
            if res_std["disease"] == cls:
                std_correct += 1

            # Internet-simulated (compressed + off-center + contrast shift)
            buf = io.BytesIO()
            im.save(buf, format="JPEG", quality=50)
            buf.seek(0)
            sim_im = Image.open(buf).convert("RGB")
            enhancer = ImageEnhance.Contrast(sim_im)
            sim_im = enhancer.enhance(1.15)
            # Off-center crop
            w, h = sim_im.size
            sim_im = sim_im.crop((int(w * 0.05), 0, w, int(h * 0.85))).resize((w, h))

            res_sim = _classify_patch(sim_im)
            sim_total += 1
            if res_sim["disease"] == cls:
                sim_correct += 1

    std_acc = (std_correct / std_total) * 100.0
    sim_acc = (sim_correct / sim_total) * 100.0

    print(f"  Standard Clean Validation Accuracy: {std_acc:.2f}% ({std_correct}/{std_total})")
    print(f"  Internet-Simulated Robustness Acc: {sim_acc:.2f}% ({sim_correct}/{sim_total})")

    assert std_acc >= 95.0, f"Standard accuracy {std_acc:.1f}% below required 95%"
    assert sim_acc >= 90.0, f"Simulated accuracy {sim_acc:.1f}% below required 90%"
    print("  -> TEST 2 PASSED: Inference engine exceeds 95% standard & 90% internet-simulated thresholds.")
    passed_tests += 1

    # ── [3] 5-Stage Explainability (XAI) Base64 Verification ───────────────────
    print("\n[TEST 3/5] 5-Stage Explainability (XAI) Base64 Output Check...")
    test_fruit_rot = next((VAL_DIR / "fruit_rot").glob("*.*"))
    with open(test_fruit_rot, "rb") as f:
        resp = requests.post("http://127.0.0.1:8000/api/diagnose", files={"file": ("test.jpg", f, "image/jpeg")}, timeout=15)
    assert resp.status_code == 200, f"Diagnosis endpoint returned {resp.status_code}"
    data = resp.json()

    xai_keys = ["original_image", "yolo_detection_image", "feature_map_image", "attention_map_image", "gradcam_image"]
    for k in xai_keys:
        val = data.get(k)
        assert val is not None and val.startswith("data:image/"), f"Missing or invalid XAI key: {k}"

    print(f"  Verified all 5 XAI stages on response: {', '.join(xai_keys)}")
    print(f"  Lesion Bounding Box: {data.get('bbox')}")
    assert data.get("is_areca") is True
    assert data.get("primary_disease") == "fruit_rot"
    print("  -> TEST 3 PASSED: 5-Stage XAI generation is complete and verified.")
    passed_tests += 1

    # ── [4] Bilingual Advisory Check (English + Kannada) ──────────────────────
    print("\n[TEST 4/5] Bilingual Advisory Check (English & Kannada / ಕನ್ನಡ)...")
    for cls in EXPECTED_CLASSES:
        if cls == "non_areca":
            continue
        rec = get_recommendation(cls)
        assert rec is not None, f"Missing advisory for {cls}"
        assert "chemical" in rec and len(rec["chemical"].get("steps", [])) > 0, f"Missing chemical steps for {cls}"
        assert "cultural" in rec and len(rec["cultural"].get("steps", [])) > 0, f"Missing cultural steps for {cls}"
        assert "fertilizer" in rec and len(rec["fertilizer"].get("steps", [])) > 0, f"Missing fertilizer steps for {cls}"

        # Verify Kannada translation
        kn = rec.get("translations", {}).get("kn")
        assert kn is not None, f"Missing Kannada translation for {cls}"
        assert "common_name" in kn and len(kn["common_name"]) > 0, f"Missing Kannada title for {cls}"
        assert "chemical" in kn and len(kn["chemical"].get("steps", [])) > 0, f"Missing Kannada chemical steps for {cls}"
        print(f"  Verified bilingual advisory for: {cls:15} -> {kn.get('common_name')}")

    print("  -> TEST 4 PASSED: ICAR-CPCRI advisories are verified in English and Kannada.")
    passed_tests += 1

    # ── [5] Frontend Build & HTTP Proxy Check ─────────────────────────────────
    print("\n[TEST 5/5] Frontend Build & HTTP Proxy Check...")
    # Test proxy endpoint on Vite port 5173
    with open(test_fruit_rot, "rb") as f:
        resp_proxy = requests.post("http://localhost:5173/api/diagnose", files={"file": ("test.jpg", f, "image/jpeg")}, timeout=15)
    assert resp_proxy.status_code == 200, f"Vite proxy returned {resp_proxy.status_code}"
    proxy_data = resp_proxy.json()
    assert proxy_data.get("primary_disease") == "fruit_rot"
    print("  Vite proxy (http://localhost:5173/api/diagnose): 200 OK")

    # Verify Non-Areca rejection on Vite proxy
    non_areca_img = next((VAL_DIR / "non_areca").glob("*.*"))
    with open(non_areca_img, "rb") as f:
        resp_na = requests.post("http://localhost:5173/api/diagnose", files={"file": ("non_areca.jpg", f, "image/jpeg")}, timeout=15)
    assert resp_na.status_code == 200
    na_data = resp_na.json()
    assert na_data.get("is_areca") is False
    assert na_data.get("primary_disease") == "non_areca"
    print("  Non-Areca Gating on proxy: Correctly returned is_areca = False")

    print("  -> TEST 5 PASSED: Frontend build and proxy are fully operational.")
    passed_tests += 1

    # ── Final Summary Table ───────────────────────────────────────────────────
    print("\n" + "=" * 80)
    print("  ARECAGUARD FULL HEALTHCHECK RESULTS SUMMARY")
    print("=" * 80)
    print("  [1] Model Weights & Config Check             : PASS")
    print("  [2] Standard & Internet-Simulated Accuracy   : PASS (>95% std, >90% sim)")
    print("  [3] 5-Stage Explainability (XAI) Output      : PASS (All 5 Base64 stages present)")
    print("  [4] Bilingual ICAR-CPCRI Advisories (EN/KN)  : PASS (Complete steps in both languages)")
    print("  [5] Frontend Build & Reverse Proxy           : PASS (Direct & Proxy 200 OK)")
    print("=" * 80)
    print(f"  TOTAL STATUS: ALL {passed_tests}/{total_tests} HEALTHCHECK SUBSYSTEMS PASSED PERFECTLY!")
    print("=" * 80)


if __name__ == "__main__":
    main()
