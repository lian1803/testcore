#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 1-B: 파일별 자동 요약 프로토타입.

Step 1: 토지분석 outputs의 16개 md 파일 → 각각 Claude API로 5줄 요약
Step 2: _summaries.json 저장
Step 3: 요약 INDEX를 context로 준 AFTER_B 카피 생성
Step 4: 기존 AFTER(역할별 2개 풀 로드)와 비교

비교 조건:
- AFTER_풀2: 현재 방식 (02c + 01, 총 30k자)
- AFTER_요약: 16개 요약 INDEX만 (약 4~6k자)
- AFTER_하이브리드: 16개 요약 INDEX + 역할 필수 1개(02c) 풀
"""
import sys, os, io, json
from pathlib import Path
from datetime import datetime

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

COMPANY_DIR = Path(__file__).resolve().parents[2] / "company"
CORE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(COMPANY_DIR))
os.chdir(str(COMPANY_DIR))

from dotenv import load_dotenv
load_dotenv(COMPANY_DIR / ".env")

import anthropic
from core.context_loader import load_planning_docs
from core.planning_summarizer import (
    summarize_planning_dir,
    format_summaries_as_index,
    save_summaries,
    load_summaries,
)

MODEL = "claude-sonnet-4-5-20250929"
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

RESULTS_DIR = Path(__file__).parent / "phase1_results" / f"b_summary_{datetime.now():%H%M%S}"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

OUTPUTS_DIR = COMPANY_DIR / "outputs" / "2026-04-14_phase1_test_토지분석"
TEAM_DIR = CORE_DIR.parent / "team" / "phase1_test_토지분석"


def call_claude(system: str, user: str, max_tokens: int = 1500) -> dict:
    resp = client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return {
        "text": resp.content[0].text,
        "in": resp.usage.input_tokens,
        "out": resp.usage.output_tokens,
    }


# ── Step 1: 요약 생성 (캐시 활용) ────────────────────────────────

print("=" * 70)
print("Step 1: 16개 md 파일 자동 요약")
print("=" * 70)

summaries = load_summaries(str(OUTPUTS_DIR))
if summaries:
    print(f"  캐시 발견: {len(summaries)}개 파일 요약 이미 있음")
else:
    print("  새로 생성 중...")
    summaries = summarize_planning_dir(str(OUTPUTS_DIR), client)
    save_summaries(summaries, str(OUTPUTS_DIR))
    print(f"  완료: {len(summaries)}개")

# 에러 체크
errors = [fn for fn, s in summaries.items() if "error" in s]
if errors:
    print(f"  ⚠️  요약 실패: {errors}")

# 요약 INDEX 블록 생성
index_block = format_summaries_as_index(summaries)
(RESULTS_DIR / "SUMMARIES_INDEX.md").write_text(index_block, encoding="utf-8")
print(f"\n  INDEX 블록 길이: {len(index_block)} 자")
print(f"  저장: {RESULTS_DIR / 'SUMMARIES_INDEX.md'}")


# ── Step 2: 3가지 context 생성 ────────────────────────────────

print("\n" + "=" * 70)
print("Step 2: 3가지 AFTER 조건 생성")
print("=" * 70)

# AFTER_풀2: 현재 방식
ctx_full2 = load_planning_docs(str(TEAM_DIR), role="marketing")
print(f"  AFTER_풀2  (현재)   : {len(ctx_full2)} 자")

# AFTER_요약: 요약 INDEX만
ctx_summary = f"=== 기획문서 요약 INDEX ===\n\n{index_block}"
print(f"  AFTER_요약          : {len(ctx_summary)} 자")

# AFTER_하이브리드: 요약 + 02c(핵심 1개) 풀
bm_file = TEAM_DIR / "기획문서" / "02c_비즈니스모델_설계자.md"
bm_full = bm_file.read_text(encoding="utf-8")[:20000] if bm_file.exists() else ""
ctx_hybrid = f"{ctx_summary}\n\n---\n\n## 02c_비즈니스모델_설계자.md (풀 원본)\n\n{bm_full}"
print(f"  AFTER_하이브리드    : {len(ctx_hybrid)} 자")


# ── Step 3: 3가지 카피 생성 ──────────────────────────────────────

print("\n" + "=" * 70)
print("Step 3: 3가지 조건으로 카피 생성")
print("=" * 70)

system = """너는 B2B SaaS 마케팅 카피라이터.
랜딩 페이지 히어로 섹션 카피를 작성해.

형식:
[헤드라인] 25자 이내
[서브헤드] 60~100자
[CTA 버튼] 12자 이내
[핵심 가치 Bullet 3개] 각 20자 이내

규칙:
- 구체 페르소나 의식
- Pain은 숫자로 (금액·시간·비율)
- "AI/자동화/혁신/스마트/차세대" 금지
- 추상 표현 금지
"""

configs = {
    "AFTER_풀2": ctx_full2,
    "AFTER_요약": ctx_summary,
    "AFTER_하이브리드": ctx_hybrid,
}

results = {}
for label, ctx in configs.items():
    print(f"\n  [{label}] 호출 중...")
    user_msg = f"아래 기획 context를 읽고 랜딩 히어로 카피를 작성해.\n\n{ctx}"
    r = call_claude(system, user_msg)

    # 키워드 매칭
    land_keywords = [
        "김철수", "시행사", "인허가", "5억", "48시간", "75%",
        "컨설턴트", "500만원", "69만원", "2주", "거절", "대표",
        "매입", "특례법", "중소", "수도권",
    ]
    hits = [k for k in land_keywords if k in r["text"]]

    results[label] = {
        "ctx_len": len(ctx),
        "text": r["text"],
        "hits": len(hits),
        "matched": hits,
        "in": r["in"],
        "out": r["out"],
    }

    print(f"    키워드: {len(hits)}/{len(land_keywords)} | tokens in={r['in']} out={r['out']}")
    (RESULTS_DIR / f"{label}.md").write_text(r["text"], encoding="utf-8")


# ── Step 4: 비교 결과 ────────────────────────────────────────────

print("\n" + "=" * 70)
print("Step 4: 비교 결과")
print("=" * 70)

print(f"\n{'조건':<20} | ctx(자) | 매칭 | in tokens | out tokens")
print("-" * 65)
for label, r in results.items():
    print(f"{label:<20} | {r['ctx_len']:7d} | {r['hits']:4d} | {r['in']:9d} | {r['out']:9d}")

print("\n\n=== 각 카피 원문 ===\n")
for label, r in results.items():
    print(f"\n### {label}")
    print("-" * 50)
    print(r["text"])
    print()

# SUMMARY 저장
(RESULTS_DIR / "SUMMARY.json").write_text(
    json.dumps({
        "summaries_count": len(summaries),
        "summaries_errors": errors,
        "results": {k: {kk: vv for kk, vv in v.items() if kk != "text"} for k, v in results.items()},
    }, ensure_ascii=False, indent=2),
    encoding="utf-8",
)

print(f"\n결과: {RESULTS_DIR}")
