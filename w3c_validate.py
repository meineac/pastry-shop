import os
import urllib.request
import urllib.error
import json
import time

url = "https://validator.w3.org/nu/?out=json"
headers = {"Content-Type": "text/html; charset=utf-8", "User-Agent": "Mozilla/5.0"}

results = {}

for file in sorted(os.listdir("rendered_html")):
    if not file.endswith(".html"):
        continue
    path = os.path.join("rendered_html", file)
    with open(path, "rb") as f:
        data = f.read()

    print(f"Validating {file}...", end=" ", flush=True)
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")

    messages = []
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req) as response:
                res_json = json.loads(response.read().decode("utf-8"))
                messages = res_json.get("messages", [])
                print(f"OK ({len(messages)} issues)")
                break
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 3:
                wait_time = (attempt + 1) * 3
                print(f"rate limited (429), waiting {wait_time}s...", end=" ", flush=True)
                time.sleep(wait_time)
                continue
            messages = [{"type": "error", "message": str(e)}]
            print(f"ERROR: {e}")
            break
        except Exception as e:
            messages = [{"type": "error", "message": str(e)}]
            print(f"ERROR: {e}")
            break

    results[file] = messages
    time.sleep(1.5)

with open("w3c_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("Validation done")
