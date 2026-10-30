import json
import re
import urllib.parse
from curl_cffi import requests

def test_bing():
    q = "arecanut anabe roga"
    url = f"https://www.bing.com/images/async?q={urllib.parse.quote(q)}&first=1&count=35"
    r = requests.get(url, impersonate="chrome120", timeout=10)
    print("Bing status:", r.status_code)
    murls = re.findall(r'murl&quot;:&quot;(http[^&]+)&quot;', r.text)
    print("Bing found:", len(murls))
    if murls:
        print("Sample:", murls[0])

if __name__ == "__main__":
    test_bing()
