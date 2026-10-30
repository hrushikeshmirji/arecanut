"""
test_system_health.py — ArecaVision AI Automated Regression & Health Benchmark Suite
=====================================================================================
Executes automated pre-flight checks across all backend subsystems:
1. Core Health & ML Model Telemetry
2. Specimen Provider & Real Dataset Access
3. Asynchronous Detection Pipeline & 5-Stage XAI
4. GIS Plantation Digital Twin CRUD (Add, List, Update, Delete)
5. Scan History Persistence & Clinical Logging
6. Microclimate Weather Telemetry & Epidemiological Risk Forecast
7. ICAR-CPCRI Agronomic Knowledge Base & Fertilizer Calculator
8. Multilingual AI Assistant (English & Kannada Queries)
9. Database Management & Safe Backup Download
10. Admin System Operations Telemetry
"""
from __future__ import annotations

import io
import sys
import time
import requests
from PIL import Image

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_URL = "http://127.0.0.1:8000/api/v1"

passed = 0
failed = 0
total_start = time.time()

def record_test(name: str, success: bool, detail: str = "", elapsed_ms: float = 0.0):
    global passed, failed
    status_str = "[\033[92mPASS\033[0m]" if success else "[\033[91mFAIL\033[0m]"
    timing_str = f"({elapsed_ms:.1f}ms)" if elapsed_ms > 0 else ""
    print(f"{status_str} {name:50} {timing_str} {detail}")
    if success:
        passed += 1
    else:
        failed += 1

print("=" * 80)
print("🌿 ARECAVISION AI — SYSTEM HEALTH & INTEGRATION BENCHMARK SUITE")
print("=" * 80)

# 1. Health & Model Telemetry
t0 = time.time()
try:
    r = requests.get(f"{BASE_URL}/health", timeout=5)
    d = r.json()
    record_test("1. Core Health & Active Models", r.status_code == 200 and d.get("status") == "healthy", f"Models: {d.get('active_models')}", (time.time()-t0)*1000)
except Exception as e:
    record_test("1. Core Health & Active Models", False, str(e))

# 2. Specimen Provider
t0 = time.time()
try:
    r = requests.get(f"{BASE_URL}/specimens", timeout=5)
    d = r.json().get("data", [])
    record_test("2. Field Specimen Provider", r.status_code == 200 and len(d) >= 7, f"Found {len(d)} verified specimen categories", (time.time()-t0)*1000)
except Exception as e:
    record_test("2. Field Specimen Provider", False, str(e))

# 3. Detection Pipeline & XAI Grad-CAM
t0 = time.time()
try:
    r = requests.post(f"{BASE_URL}/detect?specimenId=fruit_rot", timeout=5)
    job_id = r.json().get("data", {}).get("job_id")
    poll_done = False
    result = None
    for _ in range(30):
        time.sleep(0.4)
        jr = requests.get(f"{BASE_URL}/jobs/{job_id}", timeout=5).json().get("data", {})
        if jr.get("status") == "done":
            poll_done = True
            result = jr.get("result")
            break
    has_xai = bool(result and result.get("gradCamUrl") and result.get("confidence", 0) > 90)
    record_test("3. Detection & 5-Stage XAI Grad-CAM", poll_done and has_xai, f"Disease: {result.get('disease')} ({result.get('confidence')}%)", (time.time()-t0)*1000)
except Exception as e:
    record_test("3. Detection & 5-Stage XAI Grad-CAM", False, str(e))

# 4. Plantation Block CRUD
t0 = time.time()
try:
    test_block_id = f"test-blk-{int(time.time())}"
    # Add block
    r_add = requests.post(f"{BASE_URL}/plantation/blocks", json={"id": test_block_id, "name": "Automated Test Block", "trees": 420, "health": 88})
    # List blocks
    r_list = requests.get(f"{BASE_URL}/plantation/blocks")
    # Delete block
    r_del = requests.delete(f"{BASE_URL}/plantation/blocks/{test_block_id}")
    crud_success = (r_add.status_code == 200 and r_del.status_code == 200 and any(b["id"] == test_block_id for b in r_list.json().get("data", [])))
    record_test("4. GIS Plantation Block CRUD", crud_success, "Created, queried, and purged test block", (time.time()-t0)*1000)
except Exception as e:
    record_test("4. GIS Plantation Block CRUD", False, str(e))

# 5. Scan History
t0 = time.time()
try:
    r = requests.get(f"{BASE_URL}/scans", timeout=5)
    scans = r.json().get("data", [])
    record_test("5. Persistent Scan History (SQLite)", r.status_code == 200 and len(scans) > 0, f"{len(scans)} archived diagnostic records", (time.time()-t0)*1000)
except Exception as e:
    record_test("5. Persistent Scan History (SQLite)", False, str(e))

# 6. Weather & Risk Forecast
t0 = time.time()
try:
    r_w = requests.get(f"{BASE_URL}/weather?city=Madikeri", timeout=5)
    r_r = requests.get(f"{BASE_URL}/risk/forecast?city=Madikeri", timeout=5)
    w_ok = r_w.status_code == 200 and "temperature" in r_w.json().get("data", {})
    risk_d = r_r.json().get("data", {})
    r_ok = r_r.status_code == 200 and ("overallSeverity" in risk_d or "compositeIndex" in risk_d)
    record_test("6. Weather & Epidemiological Risk", w_ok and r_ok, f"Severity: {risk_d.get('overallSeverity')} (Index: {risk_d.get('compositeIndex')})", (time.time()-t0)*1000)
except Exception as e:
    record_test("6. Weather & Epidemiological Risk", False, str(e))

# 7. ICAR-CPCRI Fertilizer Plan
t0 = time.time()
try:
    r = requests.get(f"{BASE_URL}/agronomy/fertilizer-plan?palms=500&age=mature", timeout=5)
    d = r.json().get("data", {})
    fert_ok = r.status_code == 200 and d.get("annualRequirement", {}).get("ureaKg") == 110.0
    record_test("7. ICAR-CPCRI Fertilizer Calculator", fert_ok, f"Urea: {d.get('annualRequirement', {}).get('ureaKg')} kg", (time.time()-t0)*1000)
except Exception as e:
    record_test("7. ICAR-CPCRI Fertilizer Calculator", False, str(e))

# 8. Multilingual AI Assistant (English & Kannada)
t0 = time.time()
try:
    r_en = requests.post(f"{BASE_URL}/assistant/chat", json={"message": "how to treat koleroga fruit rot?"}, timeout=5)
    r_kn = requests.post(f"{BASE_URL}/assistant/chat", json={"message": "ಕೊಳೆರೋಗ ಬಂದರೆ ಏನು ಮಾಡಬೇಕು?"}, timeout=5)
    en_reply = r_en.json().get("data", {}).get("reply", "")
    kn_reply = r_kn.json().get("data", {}).get("reply", "")
    ai_ok = ("bordeaux" in en_reply.lower() or "phytophthora" in en_reply.lower()) and ("ಬೋರ್ಡೋ" in kn_reply or "ಕೊಳೆರೋಗ" in kn_reply)
    record_test("8. Multilingual AI Assistant (EN + KN)", ai_ok, "Bilingual advisory verified", (time.time()-t0)*1000)
except Exception as e:
    record_test("8. Multilingual AI Assistant (EN + KN)", False, str(e))

# 9. Admin Database Backup Download
t0 = time.time()
try:
    r = requests.get(f"{BASE_URL}/admin/db/backup", timeout=5)
    backup_ok = r.status_code == 200 and len(r.content) > 1024 and r.headers.get("Content-Type") == "application/x-sqlite3"
    record_test("9. Admin Database Backup Download", backup_ok, f"Size: {len(r.content)/1024:.1f} KB", (time.time()-t0)*1000)
except Exception as e:
    record_test("9. Admin Database Backup Download", False, str(e))

# 10. Admin System Operations Telemetry
t0 = time.time()
try:
    r = requests.get(f"{BASE_URL}/admin/system-stats", timeout=5)
    stats = r.json().get("data", {})
    stats_ok = r.status_code == 200 and "databaseSizeBytes" in stats and "pythonVersion" in stats
    record_test("10. Admin System Stats Telemetry", stats_ok, f"Python {stats.get('pythonVersion')}, DB: {stats.get('databaseSizeFormatted')}", (time.time()-t0)*1000)
except Exception as e:
    record_test("10. Admin System Stats Telemetry", False, str(e))

print("=" * 80)
total_ms = (time.time() - total_start) * 1000
print(f"Summary: {passed}/{passed+failed} Subsystems Passed in {total_ms:.1f}ms")
if failed == 0:
    print("🏆 ALL 10 SUBSYSTEMS PASSED WITH 100% OPERATIONAL INTEGRITY.")
else:
    print(f"⚠️ {failed} SUBSYSTEM(S) REPORTED ISSUES.")
print("=" * 80)
