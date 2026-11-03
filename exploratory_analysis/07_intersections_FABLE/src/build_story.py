"""Inline story_data.json into the template and write the self-contained HTML story.

Writes two files:
  dashboard/seats_and_voices.html           full document, opens by double-click, works offline (fonts fall back)
  dashboard/seats_and_voices_artifact.html  the same page without the document skeleton, for publishing as a claude.ai Artifact
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths as P  # noqa: E402

template = (P.ROOT / "src" / "story_template.html").read_text()
data = json.loads((P.PROCESSED / "story_data.json").read_text())
blob = json.dumps(data, separators=(",", ":")).replace("</", "<\\/")
html = template.replace("__DATA__", blob)
out = P.ROOT / "dashboard" / "seats_and_voices.html"
out.parent.mkdir(exist_ok=True)
out.write_text(html)
print("wrote", out, f"{out.stat().st_size/1024:.0f} KB")

# Artifact variant: strip the document skeleton (the Artifact host wraps the file itself) but keep head content first.
head = re.search(r"<head>(.*?)</head>", html, re.S).group(1)
body = re.search(r"<body>(.*?)</body>", html, re.S).group(1)
head = re.sub(r'<meta charset="utf-8">\s*', "", head)
head = re.sub(r'<meta name="viewport"[^>]*>\s*', "", head)
art = head.strip() + "\n" + body.strip() + "\n"
out2 = P.ROOT / "dashboard" / "seats_and_voices_artifact.html"
out2.write_text(art)
print("wrote", out2, f"{out2.stat().st_size/1024:.0f} KB")
