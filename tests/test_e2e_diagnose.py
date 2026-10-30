"""
End-to-End API Test for ArecaGuard Multi-Class, 5-Stage XAI & Bilingual Advisory
================================================================================
Tests:
1. Direct backend: http://127.0.0.1:8000/api/diagnose
2. Frontend Vite proxy: http://localhost:5173/api/diagnose
For both:
  - Valid Arecanut sample (fruit_rot)
  - Non-Arecanut sample (non_areca)
Verifies:
  - Backward compatibility of all existing keys
  - Safe additive 5-Stage XAI images (original, yolo, feature_map, attention_map, gradcam)
  - Bilingual translations (English and Kannada / ಕನ್ನಡ)
  - Out-of-Distribution non_areca gating
"""

import sys
from pathlib import Path
import requests

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path("D:/arecanut_project").resolve()
VAL_DIR = PROJECT_ROOT / "dataset_clean_verified" / "val"

FRUIT_ROT_IMG = next((VAL_DIR / "fruit_rot").glob("*.jpg"), None) or next((VAL_DIR / "fruit_rot").glob("*.png"), None)
NON_ARECA_IMG = next((VAL_DIR / "non_areca").glob("*.jpg"), None) or next((VAL_DIR / "non_areca").glob("*.png"), None)

assert FRUIT_ROT_IMG is not None, "No fruit_rot test image found"
assert NON_ARECA_IMG is not None, "No non_areca test image found"

ENDPOINTS = [
    ("Backend Direct", "http://127.0.0.1:8000/api/diagnose"),
    ("Frontend Vite Proxy", "http://localhost:5173/api/diagnose"),
]

def test_endpoint(name: str, url: str):
    print(f"\n=======================================================")
    print(f"Testing {name}: {url}")
    print(f"=======================================================")

    # Test 1: Valid Arecanut (fruit_rot)
    print(f"\n[Test 1] Uploading Valid Arecanut Image: {FRUIT_ROT_IMG.name}")
    with open(FRUIT_ROT_IMG, "rb") as f:
        resp = requests.post(url, files={"file": (FRUIT_ROT_IMG.name, f, "image/jpeg")}, timeout=30)
    
    assert resp.status_code == 200, f"Failed with status {resp.status_code}: {resp.text}"
    data = resp.json()
    print(f"  Status       : {resp.status_code}")
    print(f"  Primary Dis  : {data.get('primary_disease')}")
    print(f"  is_areca     : {data.get('is_areca')}")
    print(f"  Confidence   : {data.get('confidence')}")
    print(f"  BBox         : {data.get('bbox')}")
    print(f"  Severity     : {data.get('severity')}")
    assert data.get("is_areca") is True, "Expected is_areca == True for arecanut sample"
    assert data.get("disease_id") == "fruit_rot", f"Expected fruit_rot, got {data.get('disease_id')}"
    assert "chemical" in data.get("treatment_guidelines", {}), "Missing chemical treatment"

    # Check 5-Stage XAI outputs
    orig_b64 = data.get("original_image")
    yolo_b64 = data.get("yolo_detection_image")
    feat_b64 = data.get("feature_map_image")
    attn_b64 = data.get("attention_map_image")
    grad_b64 = data.get("gradcam_image") or data.get("gradcam_heatmap")

    print(f"  5-Stage XAI  : Original={bool(orig_b64)}, YOLO={bool(yolo_b64)}, FeatMap={bool(feat_b64)}, AttnMap={bool(attn_b64)}, GradCAM={bool(grad_b64)}")
    assert orig_b64 and orig_b64.startswith("data:image/"), "Missing valid original_image"
    assert yolo_b64 and yolo_b64.startswith("data:image/"), "Missing valid yolo_detection_image"
    assert feat_b64 and feat_b64.startswith("data:image/"), "Missing valid feature_map_image"
    assert attn_b64 and attn_b64.startswith("data:image/"), "Missing valid attention_map_image"
    assert grad_b64 and grad_b64.startswith("data:image/"), "Missing valid gradcam_image"

    # Check Kannada translation
    kn_data = data.get("treatment_guidelines", {}).get("translations", {}).get("kn")
    assert kn_data is not None, "Missing translations.kn in treatment_guidelines"
    print(f"  Kannada Title: {kn_data.get('common_name')}")
    assert "ಕೊಳೆ ರೋಗ" in kn_data.get("common_name", ""), "Expected Kannada name for fruit_rot"
    print("  -> Valid Arecanut Sample & 5-Stage XAI: PASS")

    # Test 2: Non-Arecanut Sample
    print(f"\n[Test 2] Uploading Non-Arecanut Image: {NON_ARECA_IMG.name}")
    with open(NON_ARECA_IMG, "rb") as f:
        resp = requests.post(url, files={"file": (NON_ARECA_IMG.name, f, "image/jpeg")}, timeout=30)
    
    assert resp.status_code == 200, f"Failed with status {resp.status_code}: {resp.text}"
    data = resp.json()
    print(f"  Status       : {resp.status_code}")
    print(f"  Primary Dis  : {data.get('primary_disease')}")
    print(f"  is_areca     : {data.get('is_areca')}")
    print(f"  Confidence   : {data.get('confidence')}")
    print(f"  BBox         : {data.get('bbox')}")
    print(f"  Severity     : {data.get('severity')}")
    print(f"  Cultural Tit : {data.get('treatment_guidelines', {}).get('cultural', {}).get('title')}")
    assert data.get("is_areca") is False, "Expected is_areca == False for non-areca sample"
    assert data.get("disease_id") == "non_areca", f"Expected non_areca, got {data.get('disease_id')}"
    assert data.get("bbox") is None, "Expected bbox is None for non-areca sample"
    assert data.get("gradcam_heatmap") is None, "Expected gradcam_heatmap is None for non-areca sample"
    print("  -> Non-Arecanut Sample Gating: PASS")

def main():
    for name, url in ENDPOINTS:
        test_endpoint(name, url)
    print("\n" + "=" * 55)
    print("  ALL END-TO-END TESTS PASSED WITH 5-STAGE XAI & KANNADA!")
    print("=" * 55)

if __name__ == "__main__":
    main()
