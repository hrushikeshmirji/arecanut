import requests
import time

print("1. Submitting detection job...")
try:
    resp = requests.post("http://127.0.0.1:8000/api/v1/detect", json={"specimenId": "fruit_rot"}, timeout=15)
    print("Submit response code:", resp.status_code)
    data = resp.json()
    print("Submit data:", data)
    job_id = data["data"]["job_id"]

    for attempt in range(25):
        time.sleep(1)
        r = requests.get(f"http://127.0.0.1:8000/api/v1/jobs/{job_id}", timeout=10)
        res = r.json()["data"]
        print(f"Poll {attempt+1}: status={res['status']}, progress={res.get('progressPercent')}%")
        if res["status"] == "done":
            result = res["result"]
            print("=== DETECTION SUCCESS ===")
            print("Disease:", result["disease"])
            print("Confidence:", result["confidence"])
            print("Severity:", result["severity"])
            print("Treatments:", len(result["treatments"]))
            print("YOLO Boxes:", len(result["yoloBoxes"]))
            print("Attention map:", bool(result.get("attentionMapUrl")))
            print("Grad-CAM:", bool(result.get("gradCamUrl")))
            break
        elif res["status"] == "failed":
            print("FAILED:", res.get("error"))
            break
except Exception as e:
    print("EXCEPTION:", e)
