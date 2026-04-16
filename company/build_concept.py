#!/usr/bin/env python3
"""concepts.json에서 특정 컨셉을 직접 빌드"""
import sys, os, io, json, re
if sys.platform == "win32":
    try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except: sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    try: sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except: sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(__file__))
from dotenv import load_dotenv
load_dotenv()
import anthropic
from teams.디자인팀.builder import build_html, validate_html, validate_html_browser

if len(sys.argv) < 4:
    print("Usage: build_concept.py <concepts.json> <A|B|C> <output_dir>")
    sys.exit(1)

concepts_path, pick, output_dir = sys.argv[1], sys.argv[2].upper(), sys.argv[3]
project_desc = "웨딩 플라워 스튜디오 FLEURIR — 드레스보다 꽃을 더 오래 기억하게 만드는 감성 웨딩 플로리스트"

with open(concepts_path, encoding="utf-8") as f:
    data = json.load(f)

concept = next((c for c in data["concepts"] if c["id"] == pick), None)
if not concept:
    print(f"컨셉 {pick} 없음"); sys.exit(1)

print(f"\n[빌드] {pick} — {concept['name']}")
client = anthropic.Anthropic()
html = build_html(concept, project_desc, client)
html = re.sub(r"```\w*\n?", '', html)
html = re.sub(r"'''\w*\n?", '', html)

os.makedirs(output_dir, exist_ok=True)
out_path = os.path.join(output_dir, "index.html")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(html)
print(f"💾 저장: {out_path}")

# 검증
passed, issues = validate_html(html, concept)
print(f"문자열 검증: {'✅' if passed else '❌'} {issues}")
b_passed, b_issues = validate_html_browser(out_path)
print(f"브라우저 검증: {'✅' if b_passed else '❌'} {b_issues}")
print("완료")
