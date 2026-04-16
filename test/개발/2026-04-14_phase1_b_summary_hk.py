#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 1-B 혜경 대시보드 재검증.

토지분석에서 요약 전략 성능 확인됨. 혜경(친숙 도메인)에서도 동일 패턴인지.
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

RESULTS_DIR = Path(__file__).parent / "phase1_results" / f"b_summary_hk_{datetime.now():%H%M%S}"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

OUTPUTS_DIR = COMPANY_DIR / "outputs" / "phase1_test_혜경대시보드"
TEAM_DIR = CORE_DIR.parent / "team" / "phase1_test_혜경대시보드"


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


# ── 혜경 outputs 경로 확인 ──
if not OUTPUTS_DIR.exists():
    print(f"⚠️  혜경 outputs 없음: {OUTPUTS_DIR}")
    print("이전 multi_test에서 복사해야 함")
    # 바탕화면에서 다시 복사
    import shutil
    src = Path(r"C:\Users\lian1\Desktop\사업기획서_결과\혜경_인하우스마케터_대시보드")
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    for f in src.iterdir():
        if f.is_file():
            shutil.copy2(f, OUTPUTS_DIR / f.name)
    print(f"  복사 완료: {OUTPUTS_DIR}")

# ── Step 1: 요약 ──
print("=" * 70)
print("Step 1: 혜경 대시보드 요약")
print("=" * 70)

summaries = load_summaries(str(OUTPUTS_DIR))
if not summaries:
    print("  새로 생성 중...")
    summaries = summarize_planning_dir(str(OUTPUTS_DIR), client)
    save_summaries(summaries, str(OUTPUTS_DIR))

errors = [fn for fn, s in summaries.items() if "error" in s]
success = [fn for fn, s in summaries.items() if "error" not in s]
print(f"  성공: {len(success)}, 실패: {len(errors)}")
if errors:
    for e in errors:
        print(f"    ⚠️  {e}")

index_block = format_summaries_as_index(summaries)
(RESULTS_DIR / "SUMMARIES_INDEX.md").write_text(index_block, encoding="utf-8")
print(f"  INDEX: {len(index_block)} 자")

# ── Step 2: context 준비 ──
claude_md = (TEAM_DIR / "CLAUDE.md").read_text(encoding="utf-8")
prd = (TEAM_DIR / "PRD.md").read_text(encoding="utf-8")
before_ctx = f"{claude_md}\n\n---\n\n# PRD\n{prd}"

after_full2 = load_planning_docs(str(TEAM_DIR), role="marketing")
after_summary = f"=== 기획문서 요약 INDEX ===\n\n{index_block}"

# 하이브리드: 요약 + 02c 풀
bm_file = TEAM_DIR / "기획문서" / "02c_비즈니스모델_설계자.md"
bm_full = bm_file.read_text(encoding="utf-8")[:20000] if bm_file.exists() else ""
after_hybrid = f"{after_summary}\n\n---\n\n## 02c_비즈니스모델_설계자.md (풀 원본)\n\n{bm_full}"

print(f"\nBEFORE:     {len(before_ctx):7d} 자")
print(f"AFTER_풀2:  {len(after_full2):7d} 자")
print(f"AFTER_요약: {len(after_summary):7d} 자")
print(f"AFTER_하이브: {len(after_hybrid):7d} 자")

# ── Step 3: 카피 생성 ──
print("\n" + "=" * 70)
print("Step 3: 4가지 조건 카피 생성")
print("=" * 70)

system = """너는 B2B SaaS 마케팅 카피라이터.
랜딩 페이지 히어로 섹션 카피를 작성해.

형식:
[헤드라인] 25자 이내
[서브헤드] 60~100자
[CTA 버튼] 12자 이내
[핵심 가치 Bullet 3개] 각 20자 이내

규칙:
- 구체 페르소나 의식 (페르소나가 실제 쓰는 말투)
- Pain은 숫자로
- "AI/자동화/혁신/스마트/차세대" 금지
- 추상 표현 금지
"""

configs = {
    "BEFORE": before_ctx,
    "AFTER_풀2": after_full2,
    "AFTER_요약": after_summary,
    "AFTER_하이브리드": after_hybrid,
}

results = {}
# 혜경 도메인 키워드 (개념어 + 숫자 혼합)
keywords = [
    "네이버", "프리랜서", "마케터", "대시보드", "인하우스",
    "4시간", "메타", "GA4", "클라이언트", "VLOOKUP",
    "리포트", "주간", "채널", "엑셀", "금요일",
    "병합", "통합", "CPC", "ROAS",
]

for label, ctx in configs.items():
    print(f"\n  [{label}] 호출...")
    r = call_claude(system, f"아래 기획 context 읽고 랜딩 히어로 카피 작성.\n\n{ctx}")

    hits = [k for k in keywords if k in r["text"]]
    results[label] = {
        "ctx_len": len(ctx),
        "text": r["text"],
        "hits": len(hits),
        "matched": hits,
        "in": r["in"],
        "out": r["out"],
    }
    print(f"    키워드 {len(hits)}/{len(keywords)} | in={r['in']} out={r['out']}")
    (RESULTS_DIR / f"{label}.md").write_text(r["text"], encoding="utf-8")

# ── 요약 ──
print("\n" + "=" * 70)
print("혜경 결과")
print("=" * 70)
print(f"\n{'조건':<20} | ctx(자) | 매칭 | in tokens")
print("-" * 55)
for label, r in results.items():
    print(f"{label:<20} | {r['ctx_len']:7d} | {r['hits']:4d} | {r['in']:9d}")

print("\n\n=== 카피 ===\n")
for label, r in results.items():
    print(f"\n### {label}")
    print("-" * 50)
    print(r["text"][:1500])  # 너무 길면 자름
    print()

(RESULTS_DIR / "SUMMARY.json").write_text(
    json.dumps({
        "summaries_success": len(success),
        "summaries_errors": errors,
        "results": {k: {kk: vv for kk, vv in v.items() if kk != "text"} for k, v in results.items()},
    }, ensure_ascii=False, indent=2),
    encoding="utf-8",
)

print(f"\n결과: {RESULTS_DIR}")
