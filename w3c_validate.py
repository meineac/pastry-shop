import os
import urllib.request
import json
import time

url = "https://validator.w3.org/nu/?out=json"
headers = {"Content-Type": "text/html; charset=utf-8", "User-Agent": "Mozilla/5.0"}

results = {}

for file in os.listdir("rendered_html"):
    if not file.endswith(".html"): continue
    path = os.path.join("rendered_html", file)
    with open(path, "rb") as f:
        data = f.read()
    
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as response:
            res_json = json.loads(response.read().decode("utf-8"))
            results[file] = res_json.get("messages", [])
    except Exception as e:
        results[file] = [{"type": "error", "message": str(e)}]
    time.sleep(1) # Be nice to W3C API

with open("w3c_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("Validation done")
