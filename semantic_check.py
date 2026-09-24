import os
import re
from collections import defaultdict

required_patterns = {
    "Metadata": [r"<meta charset", r"<meta name=\"viewport\"", r"<meta name=\"description\"", r"<meta name=\"keywords\""],
    "Microdata": [r"itemscope", r"itemtype", r"itemprop"],
    "Favicon": [r"<link rel=\"icon\""],
    "Semantic Text": [r"<em\b", r"<strong\b", r"<mark\b", r"<time\b", r"<address\b"],
    "Specific Tags": [r"<code\b", r"<abbr\b", r"<dfn\b", r"<blockquote\b", r"<q\b", r"<cite\b"],
    "Quatrain (br, wbr)": [r"<br\b", r"<wbr\b"],
    "Links": [r"<a\s+href=", r"<a\s+[^>]*download", r"<a\s+href=\"#[^\"]+\""],
    "Lists & Figures": [r"<ul\b", r"<ol\b", r"<dl\b", r"<figure\b", r"<figcaption\b"],
    "Navigation": [r"<nav\b"],
    "Tables": [r"<table\b", r"<thead\b", r"<tbody\b", r"<th\b", r"colspan=", r"rowspan=", r"headers="],
    "Forms Elements": [r"<fieldset\b", r"<legend\b", r"<form\b", r"<input\b", r"<select\b", r"<textarea\b", r"<button\b"],
    "Form Validation": [r"\brequired\b", r"\bpattern=", r"\bminlength=", r"\bmaxlength=", r"\bmin=", r"\bmax="],
    "Media & Embedding": [r"<iframe\b", r"<video\b", r"<audio\b", r"<img\b"],
    "Responsive Images": [r"\bsrcset=", r"\bsizes="],
    "Interactive Elements": [r"<details\b", r"<summary\b"]
}

found_features = {k: {p: False for p in v} for k, v in required_patterns.items()}

html_files = [f for f in os.listdir("rendered_html") if f.endswith(".html")]

for file in html_files:
    with open(os.path.join("rendered_html", file), "r", encoding="utf-8") as f:
        content = f.read()
        for category, patterns in required_patterns.items():
            for p in patterns:
                if re.search(p, content, re.IGNORECASE):
                    found_features[category][p] = True

missing = {}
for category, patterns in found_features.items():
    missing_for_cat = [p for p, found in patterns.items() if not found]
    if missing_for_cat:
        missing[category] = missing_for_cat

if not missing:
    print("ALL semantic requirements met!")
else:
    for cat, items in missing.items():
        print(f"[{cat}] Missing: {items}")
