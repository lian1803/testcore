#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 1 노이즈 제거 테스트 — temperature=0 + 3회 평균.

이전 테스트에서 랜덤성 큼 (run1/run2 분산 3~6).
temperature=0 고정 + 3회로 진짜 패턴 확증.
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

RESULTS_DIR = Path(__file__).parent / "phase1_results" / f"temp0_{datetime.now():%H%M%S}"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def call_claude(system: str, user: str, temperature: float = 0.0, max_tokens: int = 1500) -> dict:
    resp = client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        temperature=temperature,
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


def prepare_conditions(team_dir, outputs_dir):
    claude_md = (team_dir / "CLAUDE.md").read_text(encoding="utf-8")
    prd = (team_dir / "PRD.md").read_text(encoding="utf-8")
    before_ctx = f"{claude_md}\n\n---\n\n# PRD\n{prd}"

    after_full2 = load_planning_docs(str(team_dir), role="marketing")

    summaries = load_summaries(str(outputs_dir))
    index_block = format_summaries_as_index(summaries) if summaries else ""
    after_summary = f"=== 기획문서 요약 INDEX ===\n\n{index_block}"

    ultimate = f"{before_ctx}\n\n---\n\n{after_summary}"

    return {
        "BEFORE": before_ctx,
        "AFTER_풀2": after_full2,
        "AFTER_요약": after_summary,
        "ULTIMATE": ultimate,
    }


def run_domain(name: str, team_dir: Path, outputs_dir: Path, keywords: list):
    print("\n" + "=" * 70)
    print(f"{name} (temperature=0, 3회)")
    print("=" * 70)

    conditions = prepare_conditions(team_dir, outputs_dir)
    results = {label: [] for label in conditions}

    for run in range(3):
        print(f"\n  Run {run+1}/3")
        for label, ctx in conditions.items():
            user_msg = f"아래 기획 context 읽고 랜딩 히어로 카피 작성.\n\n{ctx}"
            r = call_claude(SYSTEM, user_msg, temperature=0.0)
            hits = [k for k in keywords if k in r["text"]]
            results[label].append({
                "text": r["text"],
                "hits": len(hits),
                "in": r["in"],
                "out": r["out"],
            })
            print(f"    [{label}] {len(hits)}/{len(keywords)}")
            (RESULTS_DIR / f"{name}_{label}_run{run+1}.md").write_text(r["text"], encoding="utf-8")

    # 요약
    summary = {}
    for label, ctx in conditions.items():
        runs = results[label]
        hits_list = [r["hits"] for r in runs]
        summary[label] = {
            "ctx_len": len(ctx),
            "hits_list": hits_list,
            "avg": round(sum(hits_list) / len(hits_list), 2),
            "min": min(hits_list),
            "max": max(hits_list),
            "variance": round(max(hits_list) - min(hits_list), 2),
            "in_avg": int(sum(r["in"] for r in runs) / len(runs)),
        }

    print(f"\n{name} 결과:")
    print(f"  {'조건':<14} | ctx    | runs        | 평균  | 분산 | in tokens")
    print("  " + "-" * 65)
    for label, s in summary.items():
        runs_str = str(s["hits_list"])
        print(f"  {label:<14} | {s['ctx_len']:6d} | {runs_str:<11} | {s['avg']:4.1f} | {s['variance']:4d} | {s['in_avg']:7d}")

    return summary


land_team = CORE_DIR.parent / "team" / "phase1_test_토지분석"
land_outputs = COMPANY_DIR / "outputs" / "2026-04-14_phase1_test_토지분석"
land_keywords = [
    "김철수", "시행사", "인허가", "5억", "48시간", "75%",
    "컨설턴트", "500만원", "69만원", "2주", "거절", "대표",
    "매입", "특례법", "중소", "수도권",
]

hk_team = CORE_DIR.parent / "team" / "phase1_test_혜경대시보드"
hk_outputs = COMPANY_DIR / "outputs" / "phase1_test_혜경대시보드"
hk_keywords = [
    "네이버", "프리랜서", "마케터", "대시보드", "인하우스",
    "4시간", "메타", "GA4", "클라이언트", "VLOOKUP",
    "리포트", "주간", "채널", "엑셀", "금요일",
    "병합", "통합", "CPC", "ROAS",
]

print("=" * 70)
print("Phase 1 temp=0 결정론 테스트 — 4 × 2 × 3 = 24 호출")
print("=" * 70)

all_results = {}
all_results["토지분석"] = run_domain("토지분석", land_team, land_outputs, land_keywords)
all_results["혜경"] = run_domain("혜경", hk_team, hk_outputs, hk_keywords)

# 최종
print("\n" + "=" * 70)
print("최종 크로스 도메인 (temp=0)")
print("=" * 70)
print(f"\n{'조건':<14} | 토지 avg±분산 | 혜경 avg±분산 | 합계 | 토큰(토지+혜경)")
print("-" * 75)
for label in ["BEFORE", "AFTER_풀2", "AFTER_요약", "ULTIMATE"]:
    land = all_results["토지분석"].get(label, {})
    hk = all_results["혜경"].get(label, {})
    total = land.get("avg", 0) + hk.get("avg", 0)
    tokens = land.get("in_avg", 0) + hk.get("in_avg", 0)
    print(f"{label:<14} | {land.get('avg', 0):5.1f} ± {land.get('variance', 0):2d} | {hk.get('avg', 0):5.1f} ± {hk.get('variance', 0):2d} | {total:4.1f} | {tokens:7d}")

(RESULTS_DIR / "SUMMARY.json").write_text(
    json.dumps(all_results, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
print(f"\n결과: {RESULTS_DIR}")
