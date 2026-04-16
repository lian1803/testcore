#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 1 크로스 도메인 v2 — LLM 기반 키워드 추출 + 4도메인 확증.

v1의 실패 원인: 숫자 키워드 자동 추출이 "시장 규모" 같은 메타 정보 위주였음.
v2 해결: LLM이 "카피에 들어갈 페르소나·Pain·고유명" 15개를 직접 뽑음.
"""
import sys, os, io, json, shutil
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

RESULTS_DIR = Path(__file__).parent / "phase1_results" / f"cross_v2_{datetime.now():%H%M%S}"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def call_claude(system, user, temperature=0.0, max_tokens=1500):
    resp = client.messages.create(
        model=MODEL, max_tokens=max_tokens, temperature=temperature,
        system=system, messages=[{"role": "user", "content": user}],
    )
    return {
        "text": resp.content[0].text,
        "in": resp.usage.input_tokens,
        "out": resp.usage.output_tokens,
    }


KEYWORD_SYSTEM = """너는 카피라이팅 분석가.
주어진 기획 요약을 읽고 **실제 랜딩 히어로 카피에 등장할 법한 키워드 15개**를 뽑아.

추출 기준:
1. 페르소나 호명어 (직업·연령·규모)
2. Pain Point 구체 단어 (업무·감정·상황)
3. 경쟁사명/경쟁 제품명
4. 고유 Pain 숫자 (금액·시간 절감·빈도) — 단, 시장 규모·성장률은 제외
5. 해결책 구체 단어 (기능·결과)

제외:
- 시장 규모, 성장률 같은 통계 수치
- "혁신적", "스마트" 같은 추상어
- 일반 명사 ("데이터", "시스템")

출력: JSON 배열만. 다른 텍스트 금지.
예: ["시행사 대표", "5억 손실", "48시간", "월 500만원", ...]
"""


def extract_keywords_llm(outputs_path: Path) -> list:
    """LLM으로 카피 키워드 15개 추출."""
    from core.planning_summarizer import load_summaries
    summaries = load_summaries(str(outputs_path))
    if not summaries:
        return []
    index_block = ""
    for fn, s in summaries.items():
        if "error" not in s:
            index_block += f"{fn}: {s.get('핵심결론','')} | {s.get('타겟','')} | {s.get('핵심숫자','')}\n"

    r = call_claude(KEYWORD_SYSTEM, index_block[:10000], temperature=0.0, max_tokens=500)
    import re
    m = re.search(r"\[[\s\S]*\]", r["text"])
    if m:
        try:
            return json.loads(m.group())[:16]
        except:
            pass
    return []


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


def prepare_conditions(team_dir, outputs_path):
    claude_md = (team_dir / "CLAUDE.md").read_text(encoding="utf-8")
    prd = (team_dir / "PRD.md").read_text(encoding="utf-8")
    before_ctx = f"{claude_md}\n\n---\n\n# PRD\n{prd}"
    after_full2 = load_planning_docs(str(team_dir), role="marketing")
    summaries = load_summaries(str(outputs_path))
    index_block = format_summaries_as_index(summaries) if summaries else ""
    after_summary = f"=== 기획문서 요약 INDEX ===\n\n{index_block}"
    ultimate = f"{before_ctx}\n\n---\n\n{after_summary}"
    return {
        "BEFORE": before_ctx,
        "AFTER_풀2": after_full2,
        "AFTER_요약": after_summary,
        "ULTIMATE": ultimate,
    }


def partial_match(text: str, keyword: str) -> bool:
    """부분 매칭. '시행사 대표' 같은 문구도 '시행사' or '대표'로 매칭되게."""
    if keyword in text:
        return True
    # 공백으로 나눠서 하나라도 있으면 (2글자 이상)
    parts = [p for p in keyword.split() if len(p) >= 2]
    if len(parts) >= 2:
        return sum(1 for p in parts if p in text) >= len(parts) // 2 + 1
    return False


def run_domain(name, team_dir, outputs_path, keywords):
    print(f"\n{'='*70}\n{name} (temp=0, 2회, 키워드 {len(keywords)}개)\n{'='*70}")
    print(f"  키워드: {keywords}")
    conditions = prepare_conditions(team_dir, outputs_path)
    results = {label: [] for label in conditions}

    for run in range(2):
        for label, ctx in conditions.items():
            user_msg = f"아래 기획 context 읽고 랜딩 히어로 카피 작성.\n\n{ctx}"
            r = call_claude(SYSTEM, user_msg, temperature=0.0)
            hits = sum(1 for k in keywords if partial_match(r["text"], k))
            results[label].append({"text": r["text"], "hits": hits, "in": r["in"]})
            (RESULTS_DIR / f"{name}_{label}_run{run+1}.md").write_text(r["text"], encoding="utf-8")

    summary = {}
    for label, ctx in conditions.items():
        runs = results[label]
        hits_list = [r["hits"] for r in runs]
        summary[label] = {
            "ctx_len": len(ctx),
            "hits_list": hits_list,
            "avg": round(sum(hits_list) / len(hits_list), 2),
            "in_avg": int(sum(r["in"] for r in runs) / len(runs)),
        }

    print(f"\n  조건         | ctx    | runs     | 평균  | 토큰")
    print("  " + "-" * 55)
    for label, s in summary.items():
        print(f"  {label:<12} | {s['ctx_len']:6d} | {str(s['hits_list']):<8} | {s['avg']:4.1f} | {s['in_avg']:6d}")

    return summary


# ── 도메인 4개 ──

domains = {
    "토지분석": {
        "team": CORE_DIR.parent / "team" / "phase1_test_토지분석",
        "outputs": COMPANY_DIR / "outputs" / "2026-04-14_phase1_test_토지분석",
    },
    "혜경": {
        "team": CORE_DIR.parent / "team" / "phase1_test_혜경대시보드",
        "outputs": COMPANY_DIR / "outputs" / "phase1_test_혜경대시보드",
    },
    "완전자동마케팅": {
        "team": CORE_DIR.parent / "team" / "phase1_test_완전자동마케팅",
        "outputs": COMPANY_DIR / "outputs" / "phase1_test_완전자동마케팅",
    },
    "온라인업체": {
        "team": CORE_DIR.parent / "team" / "phase1_test_온라인업체",
        "outputs": COMPANY_DIR / "outputs" / "phase1_test_온라인업체",
    },
}

print("=" * 70)
print("LLM 기반 키워드 추출 + 4도메인 크로스 검증")
print("=" * 70)

all_results = {}
domain_keywords = {}

for name, paths in domains.items():
    print(f"\n[{name}] LLM 키워드 추출 중...")
    kws = extract_keywords_llm(paths["outputs"])
    domain_keywords[name] = kws
    print(f"  → {kws}")

    all_results[name] = run_domain(name, paths["team"], paths["outputs"], kws)

# 최종 요약 (%)
print("\n" + "=" * 70)
print("4도메인 최종 요약 (매칭률 %)")
print("=" * 70)
print(f"\n{'조건':<14} | 토지  | 혜경  | 완자마 | 온라인 | 평균  | 토큰 합")
print("-" * 72)
for label in ["BEFORE", "AFTER_풀2", "AFTER_요약", "ULTIMATE"]:
    scores = []
    tokens = 0
    for dname, res in all_results.items():
        s = res.get(label, {})
        n = len(domain_keywords[dname]) or 1
        pct = s.get("avg", 0) / n * 100
        scores.append(pct)
        tokens += s.get("in_avg", 0)
    avg_pct = sum(scores) / len(scores)
    print(f"{label:<14} | {scores[0]:4.0f}% | {scores[1]:4.0f}% | {scores[2]:5.0f}% | {scores[3]:5.0f}% | {avg_pct:4.1f}% | {tokens:7d}")

(RESULTS_DIR / "SUMMARY.json").write_text(
    json.dumps({
        "keywords": domain_keywords,
        "results": all_results,
    }, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
print(f"\n결과: {RESULTS_DIR}")
