import json
import urllib.request
from pathlib import Path

sample_img = Path("dataset_multiclass_clean/fruit_rot/fruit_rot_0079.jpg")
boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
body = (
    f"--{boundary}\r\n"
    f'Content-Disposition: form-data; name="file"; filename="{sample_img.name}"\r\n'
    f"Content-Type: image/jpeg\r\n\r\n"
).encode("utf-8") + sample_img.read_bytes() + f"\r\n--{boundary}--\r\n".encode("utf-8")

req = urllib.request.Request(
    "http://127.0.0.1:8000/predict",
    data=body,
    headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    method="POST",
)

with urllib.request.urlopen(req) as resp:
    res = json.loads(resp.read().decode())
    print("HTTP Status Code    :", resp.status)
    print("Primary Disease     :", res.get("primary_disease"))
    print(f"Confidence Score    : {res.get('confidence') * 100:.2f}%")
    print("Advisory Common Name:", res.get("treatment_guidelines", {}).get("common_name"))
    print("Advisory Pathogen   :", res.get("treatment_guidelines", {}).get("pathogen"))
    print("Advisory Severity   :", res.get("treatment_guidelines", {}).get("severity_level"))
    print("Grad-CAM Data URI   :", res.get("gradcam_heatmap", "")[:45], f"({len(res.get('gradcam_heatmap', ''))} chars)")
