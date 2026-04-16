#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 1 크로스 도메인 확증 — 완전자동마케팅 + 온라인업체 추가 검증.

기존 토지분석·혜경 외에 2개 도메인으로 AFTER_요약 안정성 확증.
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
from core.handoff import PipelineHandoff
from core.planning_summarizer import (
    summarize_planning_dir,
    format_summaries_as_index,
    save_summaries,
    load_summaries,
)

MODEL = "claude-sonnet-4-5-20250929"
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

RESULTS_DIR = Path(__file__).parent / "phase1_results" / f"cross_{datetime.now():%H%M%S}"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def call_claude(system, user, temperature=0.0, max_tokens=1500):
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


def prepare_project(desktop_src: Path, slug: str) -> tuple:
    """바탕화면 → outputs 복사 + handoff 실행 + 요약 생성."""
    outputs_path = COMPANY_DIR / "outputs" / slug
    if not outputs_path.exists():
        outputs_path.mkdir(parents=True)
        for f in desktop_src.iterdir():
            if f.is_file():
                shutil.copy2(f, outputs_path / f.name)

    # 진짜 PRD
    prd_file = outputs_path / "05_PRD_지훈.md"
    prd_content = prd_file.read_text(encoding="utf-8") if prd_file.exists() else ""

    team_dir = CORE_DIR.parent / "team" / slug
    if not (team_dir / "기획문서" / "INDEX.md").exists():
        context = {
            "idea": slug, "prd": prd_content, "verdict": "GO", "score": 7.5,
            "is_commercial": True, "is_software": True, "clarified": slug,
            "taeho": "", "seoyun": "", "minsu": "", "haeun": "", "junhyeok_text": "",
        }
        handoff = PipelineHandoff(context, str(outputs_path))
        team_dir = Path(handoff.generate())
        # 진짜 PRD 복사 (handoff가 더미 넣었을 수 있음)
        (team_dir / "PRD.md").write_text(prd_content, encoding="utf-8")

    # 요약 생성 (없으면)
    summaries = load_summaries(str(outputs_path))
    if not summaries:
        print(f"  요약 생성 중 ({slug})...")
        summaries = summarize_planning_dir(str(outputs_path), client)
        save_summaries(summaries, str(outputs_path))

    return team_dir, outputs_path


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


def extract_keywords_auto(outputs_path: Path, n: int = 16) -> list:
    """기획문서에서 자동 키워드 추출 (페르소나, 숫자, 고유명)."""
    import re
    text = ""
    for md in outputs_path.glob("*.md"):
        text += md.read_text(encoding="utf-8")

    # 카테고리별 추출
    keywords = set()
    # 숫자 + 단위
    for p in [r"\d+만원", r"\d+억", r"\d+시간", r"\d+%", r"\d+분", r"\d+일", r"\d+개월", r"\d+명"]:
        for m in re.findall(p, text):
            keywords.add(m)

    # 자주 등장하는 한글 3~5글자 명사
    from collections import Counter
    stopwords = {
        "있는", "없는", "하는", "하고", "이것", "그것", "경우", "대한", "통해", "또한",
        "따라", "관련", "내용", "결과", "현재", "이전", "다음", "우리", "저희", "방식",
        "때문", "위한", "있다", "없다", "이상", "이하", "가장", "매우", "전체", "일부",
    }
    words = re.findall(r"[가-힣]{3,5}", text)
    counts = Counter(w for w in words if w not in stopwords)
    for w, c in counts.most_common(30):
        if c >= 5 and len(keywords) < n * 2:
            keywords.add(w)

    result = list(keywords)[:n]
    return result


def run_domain(name, team_dir, outputs_path, keywords):
    print(f"\n{'='*70}\n{name} (temp=0, 2회, 키워드 {len(keywords)}개)\n{'='*70}")
    conditions = prepare_conditions(team_dir, outputs_path)
    results = {label: [] for label in conditions}

    for run in range(2):
        for label, ctx in conditions.items():
            user_msg = f"아래 기획 context 읽고 랜딩 히어로 카피 작성.\n\n{ctx}"
            r = call_claude(SYSTEM, user_msg, temperature=0.0)
            hits = [k for k in keywords if k in r["text"]]
            results[label].append({"text": r["text"], "hits": len(hits), "in": r["in"]})
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

    return summary, keywords


# ── 준비 ─────────────────────────────────────────────────

DESKTOP = Path(r"C:\Users\lian1\Desktop\사업기획서_결과")

# 완전자동마케팅
print("\n[준비] 완전자동마케팅_솔루션")
jm_team, jm_out = prepare_project(DESKTOP / "완전자동마케팅_솔루션", "phase1_test_완전자동마케팅")
jm_keywords = extract_keywords_auto(jm_out)
print(f"  키워드: {jm_keywords}")

# 온라인업체_마케팅
print("\n[준비] 온라인업체_마케팅")
ob_team, ob_out = prepare_project(DESKTOP / "온라인업체_마케팅", "phase1_test_온라인업체")
ob_keywords = extract_keywords_auto(ob_out)
print(f"  키워드: {ob_keywords}")


# ── 실행 ─────────────────────────────────────────────────

all_results = {}
all_results["완전자동마케팅"] = run_domain("완전자동마케팅", jm_team, jm_out, jm_keywords)
all_results["온라인업체"] = run_domain("온라인업체", ob_team, ob_out, ob_keywords)


# ── 최종 요약 ─────────────────────────────────────────────

print("\n" + "=" * 70)
print("크로스 도메인 확증 (temp=0)")
print("=" * 70)
print(f"\n{'조건':<14} | 완자마 | 온라인 | 합계  | 토큰 합")
print("-" * 55)
for label in ["BEFORE", "AFTER_풀2", "AFTER_요약", "ULTIMATE"]:
    jm = all_results["완전자동마케팅"][0].get(label, {})
    ob = all_results["온라인업체"][0].get(label, {})
    total = jm.get("avg", 0) + ob.get("avg", 0)
    tokens = jm.get("in_avg", 0) + ob.get("in_avg", 0)
    print(f"{label:<14} | {jm.get('avg', 0):4.1f}  | {ob.get('avg', 0):4.1f}  | {total:4.1f} | {tokens:7d}")

# 이전 결과와 통합
prev = {
    "BEFORE":      {"토지": 8.3,  "혜경": 11.0},
    "AFTER_풀2":   {"토지": 9.3,  "혜경": 9.7},
    "AFTER_요약":  {"토지": 11.7, "혜경": 14.7},
    "ULTIMATE":    {"토지": 8.3,  "혜경": 17.7},
}

print(f"\n\n4개 도메인 전체 평균:")
print(f"{'조건':<14} | 토지 | 혜경 | 완자마 | 온라인 | 4도메인 평균")
print("-" * 70)
for label in ["BEFORE", "AFTER_풀2", "AFTER_요약", "ULTIMATE"]:
    jm = all_results["완전자동마케팅"][0].get(label, {}).get("avg", 0)
    ob = all_results["온라인업체"][0].get(label, {}).get("avg", 0)
    land = prev[label]["토지"]
    hk = prev[label]["혜경"]
    # 정규화: 각 도메인 최대 키워드 수 다름
    # 토지:16, 혜경:19, 완자마:len(jm_keywords), 온라인:len(ob_keywords)
    land_pct = land / 16 * 100
    hk_pct = hk / 19 * 100
    jm_pct = jm / len(jm_keywords) * 100 if jm_keywords else 0
    ob_pct = ob / len(ob_keywords) * 100 if ob_keywords else 0
    avg_pct = (land_pct + hk_pct + jm_pct + ob_pct) / 4
    print(f"{label:<14} | {land_pct:3.0f}% | {hk_pct:3.0f}% | {jm_pct:3.0f}%  | {ob_pct:3.0f}%  | {avg_pct:5.1f}%")

(RESULTS_DIR / "SUMMARY.json").write_text(
    json.dumps({
        "kw_완자마": jm_keywords,
        "kw_온라인": ob_keywords,
        "results": {k: v[0] for k, v in all_results.items()},
        "previous": prev,
    }, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
print(f"\n결과: {RESULTS_DIR}")
