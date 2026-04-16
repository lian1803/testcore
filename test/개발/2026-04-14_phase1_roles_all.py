#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 1 역할별 전체 검증 — FE / BE / 영업 × 4도메인 × BEFORE vs 요약.

마케팅 검증 완료 후 다른 역할에서도 같은 패턴인지 확인.
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
from core.planning_summarizer import format_summaries_as_index, load_summaries

MODEL = "claude-sonnet-4-5-20250929"
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

RESULTS_DIR = Path(__file__).parent / "phase1_results" / f"roles_all_{datetime.now():%H%M%S}"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def call_claude(system, user, temperature=0.0, max_tokens=2000):
    resp = client.messages.create(
        model=MODEL, max_tokens=max_tokens, temperature=temperature,
        system=system, messages=[{"role": "user", "content": user}],
    )
    return {"text": resp.content[0].text, "in": resp.usage.input_tokens, "out": resp.usage.output_tokens}


ROLE_PROMPTS = {
    "FE": """너는 시니어 프론트엔드 아키텍트. 랜딩 페이지 컴포넌트 계층을 설계해.

형식:
## 컴포넌트 트리
```
<Page>
  <Section1 name="..." />
  ...
</Page>
```

## 각 섹션 목적 (2~3줄)
1. Section1: 어떤 페르소나가 여기서 뭘 느껴야 하나, 기획의 어떤 Pain을 겨냥하나
2. ...

규칙:
- 섹션 5~7개
- "About/Features/Pricing" 같은 템플릿 금지
- 각 섹션이 기획의 구체 Pain을 연결
""",
    "BE": """너는 시니어 백엔드 엔지니어. MVP P0 기능 기반 핵심 API 엔드포인트 5개 설계해.

형식:
| # | Method | Path | 역할 |

각 엔드포인트 아래:
- 기획의 어떤 P0 기능을 구현하는지 한 줄
- 어떤 페르소나가 이걸 호출하는지 한 줄

규칙:
- 기획의 실제 기능 기반 (일반 CRUD 금지)
""",
    "영업": """너는 B2B 엔터프라이즈 세일즈 전문가. 타겟 페르소나에게 보낼 콜드 메일 2종 작성.

형식:
## Short (80자 이내)
[subject] ...
[body] ...

## Long (300자 이내)
[subject] ...
[body] ...

규칙:
- 페르소나 호명 구체적
- Pain을 숫자로 찍음
- "혹시 시간 되시면" 같은 클리셰 금지
- CTA는 구체 (15분 미팅)
""",
}

USER_SUFFIX = {
    "FE": "위 기획 context 읽고 랜딩 페이지 컴포넌트 트리 설계.",
    "BE": "위 기획 context 읽고 MVP P0 기반 API 엔드포인트 5개 설계.",
    "영업": "위 기획 context 읽고 콜드메일 2종 작성.",
}


def prepare_conditions(team_dir, outputs_path):
    claude_md = (team_dir / "CLAUDE.md").read_text(encoding="utf-8")
    prd = (team_dir / "PRD.md").read_text(encoding="utf-8")
    before_ctx = f"{claude_md}\n\n---\n\n# PRD\n{prd}"

    summaries = load_summaries(str(outputs_path))
    index_block = format_summaries_as_index(summaries) if summaries else ""
    after_summary = f"=== 기획문서 요약 INDEX ===\n\n{index_block}"

    return {"BEFORE": before_ctx, "AFTER_요약": after_summary}


def partial_match(text, keyword):
    if keyword in text:
        return True
    parts = [p for p in keyword.split() if len(p) >= 2]
    if len(parts) >= 2:
        return sum(1 for p in parts if p in text) >= (len(parts) // 2 + 1)
    return False


# ── 도메인 설정 + 이전에 추출한 키워드 재사용 ──

# 이전 cross_v2 결과에서 추출된 LLM 키워드 재사용 (마케팅용이었지만 역할 초월 공통 페르소나/Pain)
DOMAIN_KEYWORDS = {
    "토지분석": ['시행사 대표', '건축사무소 소장', '사업팀장', '인허가 거절', '5억 손실', '48시간', '월 500만원', '월 69만원', '86% 절감', '승인확률 75%', '데이터노우즈', '제너레잇', '엑셀 월 50시간', '의사결정 2주'],
    "혜경": ['인하우스 마케터', '프리랜서 마케터', '1~5인팀', '클라이언트 3~10개', '주 3시간 엑셀 취합', '월 60만원', '주 4시간', '월 200만원', '4시간→30분', '월 80만원', '네이버SA', 'GA4', '메타'],
    "완전자동마케팅": ['스마트스토어 셀러', '뷰티샵 원장', '카페 사장님', '1인 사업자', '월 500만원 매출', '광고비 80만원', 'ROI 불명확', '엑셀 수동 합산', '월 25시간', 'PostDot', '마케팅대행사'],
    "온라인업체": ['스마트스토어 셀러', '쿠팡 셀러', '월 500만원', '월 3,000만원', '1~5인 운영팀', '여러 에이전시', '월 300만', '콘텐츠 제작 150시간', 'ROAS', '월 50시간 절감', '월 29만원', '월 49만원', '월 89만원'],
}

DOMAINS = {
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


# ── 실행 ──

print("=" * 70)
print("Phase 1 역할별 전체 검증")
print(f"3 역할 × 4 도메인 × 2 조건 × 1 run = 24 호출")
print("=" * 70)

all_results = {}  # {role: {domain: {condition: result}}}

for role, system_prompt in ROLE_PROMPTS.items():
    print(f"\n\n{'#' * 70}\n# {role}\n{'#' * 70}")
    all_results[role] = {}

    for dname, paths in DOMAINS.items():
        print(f"\n[{role} × {dname}]")
        keywords = DOMAIN_KEYWORDS[dname]
        conditions = prepare_conditions(paths["team"], paths["outputs"])
        all_results[role][dname] = {}

        for label, ctx in conditions.items():
            user = f"{USER_SUFFIX[role]}\n\n{ctx}"
            r = call_claude(system_prompt, user, temperature=0.0)
            hits = sum(1 for k in keywords if partial_match(r["text"], k))
            all_results[role][dname][label] = {
                "ctx_len": len(ctx),
                "hits": hits,
                "keywords_total": len(keywords),
                "pct": round(hits / len(keywords) * 100, 1),
                "in": r["in"],
                "out": r["out"],
            }
            (RESULTS_DIR / f"{role}_{dname}_{label}.md").write_text(r["text"], encoding="utf-8")
            print(f"  {label:<14}: {hits}/{len(keywords)} ({all_results[role][dname][label]['pct']:.0f}%) | in={r['in']}")


# ── 최종 요약 ──
print("\n" + "=" * 70)
print("역할별 크로스 도메인 요약 (매칭률 %)")
print("=" * 70)

for role in ROLE_PROMPTS.keys():
    print(f"\n### {role}")
    print(f"{'도메인':<14} | BEFORE | AFTER_요약 | 개선 | 토큰 BEFORE | 토큰 AFTER")
    print("-" * 75)
    for dname in DOMAINS.keys():
        r = all_results[role][dname]
        b = r["BEFORE"]
        a = r["AFTER_요약"]
        diff = a["pct"] - b["pct"]
        arrow = "↑" if diff > 0 else ("↓" if diff < 0 else "=")
        print(f"{dname:<14} | {b['pct']:5.0f}% | {a['pct']:8.0f}% | {diff:+5.0f}{arrow} | {b['in']:11d} | {a['in']:10d}")

    # 역할 평균
    b_avg = sum(all_results[role][d]["BEFORE"]["pct"] for d in DOMAINS) / len(DOMAINS)
    a_avg = sum(all_results[role][d]["AFTER_요약"]["pct"] for d in DOMAINS) / len(DOMAINS)
    b_tok = sum(all_results[role][d]["BEFORE"]["in"] for d in DOMAINS)
    a_tok = sum(all_results[role][d]["AFTER_요약"]["in"] for d in DOMAINS)
    print(f"{'평균':<14} | {b_avg:5.0f}% | {a_avg:8.0f}% | {a_avg-b_avg:+5.0f}{'↑' if a_avg > b_avg else '↓'} | {b_tok:11d} | {a_tok:10d}")

# 전체 평균
print("\n" + "=" * 70)
print("3 역할 × 4 도메인 전체 평균")
print("=" * 70)
all_b, all_a, all_b_tok, all_a_tok = [], [], 0, 0
for role in ROLE_PROMPTS:
    for d in DOMAINS:
        all_b.append(all_results[role][d]["BEFORE"]["pct"])
        all_a.append(all_results[role][d]["AFTER_요약"]["pct"])
        all_b_tok += all_results[role][d]["BEFORE"]["in"]
        all_a_tok += all_results[role][d]["AFTER_요약"]["in"]
print(f"BEFORE 평균: {sum(all_b)/len(all_b):.1f}% | 총 토큰 {all_b_tok:,}")
print(f"AFTER  평균: {sum(all_a)/len(all_a):.1f}% | 총 토큰 {all_a_tok:,}")
print(f"개선폭: {sum(all_a)/len(all_a) - sum(all_b)/len(all_b):+.1f}%p")
print(f"토큰 절감: {(1 - all_a_tok/all_b_tok)*100:.0f}%")

(RESULTS_DIR / "SUMMARY.json").write_text(
    json.dumps(all_results, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
print(f"\n결과: {RESULTS_DIR}")
