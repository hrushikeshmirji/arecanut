import requests

def test(url, method="get", **kwargs):
    try:
        print(f"Testing {method.upper()} {url}...")
        r = getattr(requests, method)(url, timeout=3, **kwargs)
        print(f"Status: {r.status_code}, Response: {r.text[:100]}")
    except Exception as e:
        print(f"ERROR: {e}")

test("http://127.0.0.1:8000/api/v1/health")
test("http://127.0.0.1:8000/api/v1/specimens")
test("http://127.0.0.1:8000/api/v1/assistant/chat", method="post", json={"message": "hello"})
test("http://127.0.0.1:8000/api/v1/detect?specimenId=fruit_rot", method="post")
