#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BEFORE만 진짜 PRD로 재실행."""
import sys, os, io, json, re
from pathlib import Path
from datetime import datetime

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

COMPANY_DIR = Path(__file__).resolve().parents[2] / "company"
CORE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(COMPANY_DIR))
os.chdir(str(COMPANY_DIR))

from dotenv import load_dotenv
load_dotenv(COMPANY_DIR / ".env")

import anthropic
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
MODEL = "claude-sonnet-4-5-20250929"

TEAM_DIR = CORE_DIR.parent / "team" / "phase1_test_토지분석"
KEYWORDS = [
    "시행사 대표", "건축사무소 소장", "사업팀장", "인허가 거절",
    "5억 손실", "48시간", "월 500만원", "월 69만원", "86% 절감",
    "승인확률 75%", "데이터노우즈", "제너레잇", "엑셀 월 50시간",
    "의사결정 2주",
]

def partial_match(text, kw):
    if kw in text:
        return True
    parts = [p for p in kw.split() if len(p) >= 2]
    if len(parts) >= 2:
        return sum(1 for p in parts if p in text) >= len(parts) // 2 + 1
    return False

def verify_halluc(text):
    all_text = ""
    for f in (TEAM_DIR / "기획문서").glob("*.md"):
        all_text += f.read_text(encoding="utf-8")
    patterns = {
        "%": re.findall(r"\d+%", text),
        "만원": re.findall(r"\d+만원", text),
        "억": re.findall(r"\d+억", text),
        "시간": re.findall(r"\d+시간", text),
        "일": re.findall(r"\d+일", text),
    }
    total, verified, fab = 0, 0, []
    for kind, vs in patterns.items():
        for v in set(vs):
            total += 1
            if v in all_text:
                verified += 1
            else:
                fab.append(v)
    return {"total": total, "verified": verified, "rate": round(verified/max(total,1)*100), "fab": fab}


claude_md = (TEAM_DIR / "CLAUDE.md").read_text(encoding="utf-8")
prd = (TEAM_DIR / "PRD.md").read_text(encoding="utf-8")
before_ctx = f"{claude_md}\n\n---\n\n# PRD\n{prd}"
print(f"BEFORE context (진짜 PRD 포함): {len(before_ctx)} 자")

SYSTEM = """너는 시니어 프로덕트 팀 리드 (CTO + PM + 디자이너 + 카피 역할).
주어진 기획 context로 **Wave 3~5 통합 설계 문서 한 편**을 작성해.

반드시 이 섹션 순서로:

# 제품 설계 통합 문서

## 1. 타겟 페르소나 (구체 호명)
3~5줄 — 이름/연령/직업/회사 규모/과거 경험

## 2. 핵심 아키텍처 (CTO)
스택 선택 + 근거 3줄

## 3. API 엔드포인트 5개 (BE)
| # | Method | Path | 역할 |
- 각 엔드포인트가 해결하는 Pain Point 1줄

## 4. 랜딩 페이지 섹션 6개 (FE)
각 섹션: 이름 + 무엇을 보여주나 + 어떤 Pain 해결

## 5. 히어로 카피 (마케팅)
- 헤드라인 25자
- 서브헤드 80자
- CTA 12자
- Bullet 3개

규칙:
- 기획의 페르소나·Pain·숫자를 **정확히** 그대로 인용
- 지어내는 숫자 금지
"""

resp = client.messages.create(
    model=MODEL, max_tokens=3000, temperature=0.0,
    system=SYSTEM,
    messages=[{"role": "user", "content": f"context:\n{before_ctx}\n\n위 context 읽고 통합 설계 문서 작성."}],
)
text = resp.content[0].text
hits = [kw for kw in KEYWORDS if partial_match(text, kw)]
h = verify_halluc(text)
print(f"\nBEFORE 재실행 (진짜 PRD):")
print(f"  키워드: {len(hits)}/{len(KEYWORDS)} ({len(hits)*100//len(KEYWORDS)}%) — {hits}")
print(f"  할루시네이션: {h['verified']}/{h['total']} 검증됨 ({h['rate']}%)")
if h['fab']:
    print(f"  지어낸 숫자: {h['fab']}")
print(f"  토큰: in={resp.usage.input_tokens}, out={resp.usage.output_tokens}")

out_dir = Path(__file__).parent / "phase1_results" / f"before_fix_{datetime.now():%H%M%S}"
out_dir.mkdir(parents=True, exist_ok=True)
(out_dir / "BEFORE_with_real_prd.md").write_text(text, encoding="utf-8")
print(f"\n저장: {out_dir}")
