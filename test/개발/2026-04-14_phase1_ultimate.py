#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 1 궁극 조합 테스트 — "BEFORE + 요약 INDEX".

가설: BEFORE(CLAUDE.md + 진짜 PRD)가 이미 충분한 혜경 케이스에,
     요약 INDEX를 보강하면 나머지 파일 정보까지 얻어서 최강일 수 있다.

4조건 x 2 도메인 x 2회 = 16회 호출
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

RESULTS_DIR = Path(__file__).parent / "phase1_results" / f"ultimate_{datetime.now():%H%M%S}"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


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


SYSTEM = """너는 B2B SaaS 마케팅 카피라이터.
랜딩 페이지 히어로 섹션 카피를 작성해.

형식:
[헤드라인] 25자 이내
[서브헤드] 60~100자
[CTA 버튼] 12자 이내
[핵심 가치 Bullet 3개] 각 20자 이내

규칙:
- 구체 페르소나 의식
- Pain은 숫자로
- "AI/자동화/혁신/스마트/차세대" 금지
- 추상 표현 금지
"""


def prepare_conditions(team_dir: Path, outputs_dir: Path):
    """4가지 context 조건 생성."""
    claude_md = (team_dir / "CLAUDE.md").read_text(encoding="utf-8")
    prd = (team_dir / "PRD.md").read_text(encoding="utf-8")

    before_ctx = f"{claude_md}\n\n---\n\n# PRD\n{prd}"

    # AFTER_풀2
    after_full2 = load_planning_docs(str(team_dir), role="marketing")

    # 요약
    summaries = load_summaries(str(outputs_dir))
    index_block = format_summaries_as_index(summaries) if summaries else ""

    # AFTER_요약만
    after_summary = f"=== 기획문서 요약 INDEX ===\n\n{index_block}"

    # ULTIMATE: BEFORE + 요약 INDEX
    ultimate = f"{before_ctx}\n\n---\n\n{after_summary}"

    return {
        "BEFORE": before_ctx,
        "AFTER_풀2": after_full2,
        "AFTER_요약": after_summary,
        "ULTIMATE": ultimate,
    }


def run_domain(name: str, team_dir: Path, outputs_dir: Path, keywords: list):
    print("\n" + "=" * 70)
    print(f"도메인: {name}")
    print("=" * 70)

    conditions = prepare_conditions(team_dir, outputs_dir)

    for label, ctx in conditions.items():
        print(f"  {label:<14}: {len(ctx):7d} 자")

    results = {label: [] for label in conditions}
    for run in range(2):
        print(f"\n  Run {run+1}/2")
        for label, ctx in conditions.items():
            user_msg = f"아래 기획 context 읽고 랜딩 히어로 카피 작성.\n\n{ctx}"
            r = call_claude(SYSTEM, user_msg)
            hits = [k for k in keywords if k in r["text"]]
            results[label].append({
                "text": r["text"],
                "hits": len(hits),
                "in": r["in"],
                "out": r["out"],
            })
            print(f"    [{label}] {len(hits)}/{len(keywords)} (in={r['in']})")
            (RESULTS_DIR / f"{name}_{label}_run{run+1}.md").write_text(r["text"], encoding="utf-8")

    # 평균
    summary = {}
    for label, ctx in conditions.items():
        runs = results[label]
        hits_list = [r["hits"] for r in runs]
        summary[label] = {
            "ctx_len": len(ctx),
            "hits_list": hits_list,
            "avg": sum(hits_list) / len(hits_list),
            "in_avg": sum(r["in"] for r in runs) / len(runs),
        }

    print(f"\n  평균 결과 ({name}):")
    print(f"  {'조건':<14} | ctx    | avg  | in tokens")
    print("  " + "-" * 52)
    for label, s in summary.items():
        print(f"  {label:<14} | {s['ctx_len']:6d} | {s['avg']:4.1f} | {s['in_avg']:9.0f}")

    return summary


# ── 실행 ──

# 토지분석
land_team = CORE_DIR.parent / "team" / "phase1_test_토지분석"
land_outputs = COMPANY_DIR / "outputs" / "2026-04-14_phase1_test_토지분석"
land_keywords = [
    "김철수", "시행사", "인허가", "5억", "48시간", "75%",
    "컨설턴트", "500만원", "69만원", "2주", "거절", "대표",
    "매입", "특례법", "중소", "수도권",
]

# 혜경
hk_team = CORE_DIR.parent / "team" / "phase1_test_혜경대시보드"
hk_outputs = COMPANY_DIR / "outputs" / "phase1_test_혜경대시보드"
hk_keywords = [
    "네이버", "프리랜서", "마케터", "대시보드", "인하우스",
    "4시간", "메타", "GA4", "클라이언트", "VLOOKUP",
    "리포트", "주간", "채널", "엑셀", "금요일",
    "병합", "통합", "CPC", "ROAS",
]

print("=" * 70)
print("Phase 1 Ultimate — 4조건 × 2도메인 × 2회 = 16 호출")
print("=" * 70)

all_results = {}
all_results["토지분석"] = run_domain("토지분석", land_team, land_outputs, land_keywords)
all_results["혜경"] = run_domain("혜경", hk_team, hk_outputs, hk_keywords)

# 최종 요약
print("\n" + "=" * 70)
print("최종 크로스 도메인 요약")
print("=" * 70)
print(f"\n{'조건':<14} | 토지분석 평균 | 혜경 평균 | 토지 토큰 | 혜경 토큰")
print("-" * 70)
conditions_order = ["BEFORE", "AFTER_풀2", "AFTER_요약", "ULTIMATE"]
for label in conditions_order:
    land = all_results["토지분석"].get(label, {})
    hk = all_results["혜경"].get(label, {})
    print(f"{label:<14} | {land.get('avg', 0):12.1f} | {hk.get('avg', 0):8.1f} | {land.get('in_avg', 0):8.0f} | {hk.get('in_avg', 0):8.0f}")

(RESULTS_DIR / "SUMMARY.json").write_text(
    json.dumps(all_results, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
print(f"\n결과: {RESULTS_DIR}")
