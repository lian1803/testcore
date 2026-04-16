#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 1-B 공정 비교 — 토지분석 4조건 (진짜 PRD 포함 BEFORE).

이전 실험 오류 발견: 토지분석의 BEFORE가 더미 PRD(58자)로 돌아갔음.
이번엔 진짜 PRD(28KB) 포함해서 재실행.

4가지 조건:
- BEFORE: 기존 방식 (CLAUDE.md + PRD 진짜)
- AFTER_풀2: 역할별 파일 2개 풀 로드
- AFTER_요약: 자동 요약 INDEX만
- AFTER_하이브리드: 요약 + 02c 풀
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
    format_summaries_as_index,
    load_summaries,
)

MODEL = "claude-sonnet-4-5-20250929"
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

RESULTS_DIR = Path(__file__).parent / "phase1_results" / f"fair_{datetime.now():%H%M%S}"
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


# ── 진짜 PRD 재확인 ──
prd_path = TEAM_DIR / "PRD.md"
prd_size = prd_path.stat().st_size
print(f"PRD.md 크기: {prd_size} 바이트")
assert prd_size > 10000, f"PRD가 너무 작음: {prd_size}. 진짜 PRD로 교체 필요."

# ── Context 생성 ──
claude_md = (TEAM_DIR / "CLAUDE.md").read_text(encoding="utf-8")
prd = prd_path.read_text(encoding="utf-8")

# BEFORE: 기존 handoff 방식 (CLAUDE.md + 진짜 PRD)
before_ctx = f"{claude_md}\n\n---\n\n# PRD\n{prd}"

# AFTER_풀2
after_full2 = load_planning_docs(str(TEAM_DIR), role="marketing")

# AFTER_요약: 저장된 요약 불러오기
summaries = load_summaries(str(OUTPUTS_DIR))
index_block = format_summaries_as_index(summaries)
after_summary = f"=== 기획문서 요약 INDEX ===\n\n{index_block}"

# AFTER_하이브리드
bm_file = TEAM_DIR / "기획문서" / "02c_비즈니스모델_설계자.md"
bm_full = bm_file.read_text(encoding="utf-8")[:20000]
after_hybrid = f"{after_summary}\n\n---\n\n## 02c_비즈니스모델_설계자.md (풀 원본)\n\n{bm_full}"

print("\nContext 길이:")
print(f"  BEFORE           : {len(before_ctx):7d} 자 (PRD {prd_size} 포함)")
print(f"  AFTER_풀2        : {len(after_full2):7d} 자")
print(f"  AFTER_요약       : {len(after_summary):7d} 자")
print(f"  AFTER_하이브리드 : {len(after_hybrid):7d} 자")


# ── 카피 생성 ──
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
    "BEFORE": before_ctx,
    "AFTER_풀2": after_full2,
    "AFTER_요약": after_summary,
    "AFTER_하이브리드": after_hybrid,
}

keywords = [
    "김철수", "시행사", "인허가", "5억", "48시간", "75%",
    "컨설턴트", "500만원", "69만원", "2주", "거절", "대표",
    "매입", "특례법", "중소", "수도권",
]

print("\n" + "=" * 70)
print("카피 생성 (4 조건 × 2회 = 8회 호출)")
print("=" * 70)

# 2회 돌려서 평균 — 랜덤성 줄이기
results = {label: [] for label in configs}
for run in range(2):
    print(f"\n--- Run {run+1}/2 ---")
    for label, ctx in configs.items():
        user_msg = f"아래 기획 context 읽고 랜딩 히어로 카피 작성.\n\n{ctx}"
        r = call_claude(system, user_msg)
        hits = [k for k in keywords if k in r["text"]]
        results[label].append({
            "text": r["text"],
            "hits": len(hits),
            "matched": hits,
            "in": r["in"],
            "out": r["out"],
        })
        print(f"  [{label}] run{run+1}: {len(hits)}/{len(keywords)} (in={r['in']})")
        (RESULTS_DIR / f"{label}_run{run+1}.md").write_text(r["text"], encoding="utf-8")

# ── 평균 & 요약 ──
print("\n" + "=" * 70)
print("평균 결과 (2회 평균)")
print("=" * 70)
print(f"\n{'조건':<18} | ctx(자) | run1 | run2 | 평균  | in tokens")
print("-" * 70)
summary = {}
for label, ctx in configs.items():
    runs = results[label]
    hits_list = [r["hits"] for r in runs]
    avg = sum(hits_list) / len(hits_list)
    summary[label] = {
        "ctx_len": len(ctx),
        "hits_per_run": hits_list,
        "avg_hits": avg,
        "in_tokens_avg": sum(r["in"] for r in runs) / len(runs),
    }
    print(f"{label:<18} | {len(ctx):7d} | {hits_list[0]:4d} | {hits_list[1]:4d} | {avg:4.1f} | {summary[label]['in_tokens_avg']:9.0f}")

(RESULTS_DIR / "SUMMARY.json").write_text(
    json.dumps(summary, ensure_ascii=False, indent=2),
    encoding="utf-8",
)

# Run 1 결과만 본문 출력
print("\n\n=== Run 1 카피 ===\n")
for label in configs:
    print(f"\n### {label}")
    print("-" * 50)
    print(results[label][0]["text"][:1200])
    print()

print(f"\n결과: {RESULTS_DIR}")
