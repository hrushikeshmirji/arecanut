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

# Test 1: Direct backend 127.0.0.1:8000
print("[1] Testing Direct Backend (http://127.0.0.1:8000/api/diagnose)...")
req1 = urllib.request.Request(
    "http://127.0.0.1:8000/api/diagnose",
    data=body,
    headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    method="POST",
)
with urllib.request.urlopen(req1, timeout=30) as r1:
    res1 = json.loads(r1.read().decode())
    print("  Status Code    :", r1.status)
    print("  Primary Disease:", res1.get("primary_disease"))
    print(f"  Confidence     : {res1.get('confidence') * 100:.2f}%")

# Test 2: Proxied through Vite http://localhost:5173/api/diagnose
print("\n[2] Testing Vite Proxy (http://localhost:5173/api/diagnose)...")
req2 = urllib.request.Request(
    "http://localhost:5173/api/diagnose",
    data=body,
    headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    method="POST",
)
with urllib.request.urlopen(req2, timeout=30) as r2:
    res2 = json.loads(r2.read().decode())
    print("  Status Code    :", r2.status)
    print("  Primary Disease:", res2.get("primary_disease"))
    print(f"  Confidence     : {res2.get('confidence') * 100:.2f}%")
print("\n>> BOTH DIRECT AND PROXIED INFERENCE ENDPOINTS OPERATING PERFECTLY!")
