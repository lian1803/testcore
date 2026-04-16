#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 1 End-to-End 싼 검증 (A + C 조합).

A: 풀 설계 문서 BEFORE vs AFTER — 2회 호출
C: CTO → BE → FE 순차 체이닝 with INDEX — 3회 호출

총 5회 호출, 예상 $1 이내, 20~30분.

목표: "기획 페르소나·Pain이 실제 실행팀 결과물 끝까지 살아있는가" 검증.
"""
import sys, os, io, json, re
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
from core.context_loader import load_planning_summary

MODEL = "claude-sonnet-4-5-20250929"
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

RESULTS_DIR = Path(__file__).parent / "phase1_results" / f"e2e_{datetime.now():%H%M%S}"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

TEAM_DIR = CORE_DIR.parent / "team" / "phase1_test_토지분석"

# 토지분석 검증 키워드 (이전 실험에서 LLM 추출)
KEYWORDS = [
    "시행사 대표", "건축사무소 소장", "사업팀장", "인허가 거절",
    "5억 손실", "48시간", "월 500만원", "월 69만원", "86% 절감",
    "승인확률 75%", "데이터노우즈", "제너레잇", "엑셀 월 50시간",
    "의사결정 2주",
]


def call(system, user, temperature=0.0, max_tokens=2500):
    resp = client.messages.create(
        model=MODEL, max_tokens=max_tokens, temperature=temperature,
        system=system, messages=[{"role": "user", "content": user}],
    )
    return {
        "text": resp.content[0].text,
        "in": resp.usage.input_tokens,
        "out": resp.usage.output_tokens,
    }


def partial_match(text, kw):
    if kw in text:
        return True
    parts = [p for p in kw.split() if len(p) >= 2]
    if len(parts) >= 2:
        return sum(1 for p in parts if p in text) >= len(parts) // 2 + 1
    return False


def measure(text, label=""):
    hits = [kw for kw in KEYWORDS if partial_match(text, kw)]
    return {
        "hits": len(hits),
        "total": len(KEYWORDS),
        "pct": round(len(hits) / len(KEYWORDS) * 100),
        "matched": hits,
    }


def verify_hallucinations(text):
    """숫자 표현 역검색 — 기획문서에 있는지."""
    all_planning_text = ""
    for f in (TEAM_DIR / "기획문서").glob("*.md"):
        all_planning_text += f.read_text(encoding="utf-8")

    patterns = {
        "%": re.findall(r"\d+%", text),
        "만원": re.findall(r"\d+만원", text),
        "억": re.findall(r"\d+억", text),
        "시간": re.findall(r"\d+시간", text),
        "일": re.findall(r"\d+일", text),
    }

    total, verified, fabricated_all = 0, 0, []
    for kind, vs in patterns.items():
        vs = list(set(vs))
        total += len(vs)
        for v in vs:
            if v in all_planning_text:
                verified += 1
            else:
                fabricated_all.append(f"{v}({kind})")

    return {
        "total": total,
        "verified": verified,
        "rate": round(verified / max(total, 1) * 100),
        "fabricated": fabricated_all,
    }


# ── Context 준비 ──

claude_md = (TEAM_DIR / "CLAUDE.md").read_text(encoding="utf-8")
prd = (TEAM_DIR / "PRD.md").read_text(encoding="utf-8")

before_ctx = f"{claude_md}\n\n---\n\n# PRD\n{prd}"
summary = load_planning_summary(str(TEAM_DIR))
after_ctx = f"{summary}\n\n---\n\n# PRD\n{prd}"

print(f"BEFORE: {len(before_ctx)} 자")
print(f"AFTER : {len(after_ctx)} 자")


# ========================================================================
# 테스트 A: 풀 설계 문서 한 편 (BEFORE vs AFTER)
# ========================================================================

print("\n" + "=" * 70)
print("[A] 풀 설계 문서 BEFORE vs AFTER")
print("=" * 70)

FULL_DOC_SYSTEM = """너는 시니어 프로덕트 팀 리드 (CTO + PM + 디자이너 + 카피 역할).
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
- 섹션 이름은 "About/Features/Pricing" 같은 템플릿 금지
- 기획 페르소나 감정에 맞춰

## 5. 히어로 카피 (마케팅)
- 헤드라인 25자
- 서브헤드 80자
- CTA 12자
- Bullet 3개 각 20자

규칙:
- 기획의 페르소나·Pain·숫자를 **정확히** 그대로 인용
- 지어내는 숫자 금지
- "AI/자동화/혁신" 같은 진부한 단어 금지
"""

for label, ctx in [("BEFORE", before_ctx), ("AFTER", after_ctx)]:
    print(f"\n[{label}] 호출...")
    r = call(FULL_DOC_SYSTEM, f"context:\n{ctx}\n\n위 context 읽고 통합 설계 문서 작성.", max_tokens=3000)
    m = measure(r["text"])
    h = verify_hallucinations(r["text"])
    print(f"  키워드: {m['hits']}/{m['total']} ({m['pct']}%)")
    print(f"  할루시네이션: {h['verified']}/{h['total']} 검증됨 ({h['rate']}%)")
    if h['fabricated']:
        print(f"  지어낸 숫자: {h['fabricated']}")
    print(f"  토큰: in={r['in']}, out={r['out']}")
    (RESULTS_DIR / f"A_{label}.md").write_text(r["text"], encoding="utf-8")


# ========================================================================
# 테스트 C: CTO → BE → FE 순차 체이닝 (AFTER만)
# ========================================================================

print("\n\n" + "=" * 70)
print("[C] 순차 체이닝 CTO → BE → FE (AFTER)")
print("=" * 70)

# Step 1: CTO
CTO_SYSTEM = """너는 시니어 CTO.
주어진 기획 context로 **아키텍처 설계서**를 작성해.

형식:
## 제품 요약
페르소나·핵심 가치·주요 Pain 3줄

## 기술 스택
- FE: 라이브러리 + 근거 1줄
- BE: 언어/프레임워크 + 근거 1줄
- DB: 선택 + 근거 1줄
- 인프라: 배포 + 근거 1줄

## 핵심 모듈 3~5개
각 모듈 이름 + 기획의 어떤 기능 구현 + 처리 흐름 1줄

## 아키텍처 리스크 3개
기획의 어떤 부분에서 발생 + 대응

규칙:
- 기획 페르소나/Pain/숫자 정확히 인용
- 지어내지 마라
"""

print("\n[C.1] CTO 호출...")
cto = call(CTO_SYSTEM, f"context:\n{after_ctx}\n\n위 context로 아키텍처 설계.", max_tokens=2500)
cto_m = measure(cto["text"])
cto_h = verify_hallucinations(cto["text"])
print(f"  키워드: {cto_m['hits']}/{cto_m['total']} ({cto_m['pct']}%) | 할루시: {cto_h['rate']}%")
(RESULTS_DIR / "C1_CTO.md").write_text(cto["text"], encoding="utf-8")

# Step 2: BE — CTO 결과 + INDEX 받음
BE_SYSTEM = """너는 시니어 백엔드 엔지니어.
CTO 아키텍처 문서 + 기획 INDEX 를 읽고 **API 엔드포인트 8개** 설계해.

형식:
| # | Method | Path | 역할 | Request | Response |
|---|--------|------|------|---------|----------|

각 엔드포인트 아래:
- 기획의 어떤 P0/P1 기능 구현하는지
- 어떤 페르소나가 호출하는지
- 예상 지연·부하 주의점

규칙:
- CTO의 스택 선택 존중
- 기획 페르소나 그대로 인용
- 일반 CRUD 금지, 도메인 특화
"""

print("\n[C.2] BE 호출 (CTO 결과 전달)...")
be_user = f"=== 기획 INDEX ===\n{summary}\n\n=== CTO 아키텍처 문서 ===\n{cto['text']}\n\n위 두 문서 읽고 API 엔드포인트 8개 설계."
be = call(BE_SYSTEM, be_user, max_tokens=2500)
be_m = measure(be["text"])
be_h = verify_hallucinations(be["text"])
print(f"  키워드: {be_m['hits']}/{be_m['total']} ({be_m['pct']}%) | 할루시: {be_h['rate']}%")
(RESULTS_DIR / "C2_BE.md").write_text(be["text"], encoding="utf-8")

# Step 3: FE — CTO + BE + INDEX 받음
FE_SYSTEM = """너는 시니어 프론트엔드 디자이너.
CTO + BE 문서 + 기획 INDEX 를 읽고 **랜딩 페이지 + 대시보드 컴포넌트 구조** 설계.

형식:
## 1. 랜딩 페이지 (섹션 6~8개)
각 섹션:
- 이름 (템플릿 금지)
- 주요 메시지 (페르소나 감정 트리거)
- 들어갈 숫자/인용

## 2. 히어로 카피
- 헤드라인 25자
- 서브헤드 80자
- CTA 12자
- Bullet 3개

## 3. 대시보드 핵심 화면 3개
각 화면: 이름 + 어떤 BE API 호출하는지 + 페르소나가 여기서 뭘 확인하는지

규칙:
- BE 엔드포인트 이름 정확히 참조
- 기획 페르소나·Pain 숫자 인용
- 지어내지 마라
"""

print("\n[C.3] FE 호출 (CTO + BE 결과 전달)...")
fe_user = f"=== 기획 INDEX ===\n{summary}\n\n=== CTO 아키텍처 ===\n{cto['text'][:3000]}\n\n=== BE API 목록 ===\n{be['text']}\n\n위 문서 읽고 랜딩 + 대시보드 설계."
fe = call(FE_SYSTEM, fe_user, max_tokens=2800)
fe_m = measure(fe["text"])
fe_h = verify_hallucinations(fe["text"])
print(f"  키워드: {fe_m['hits']}/{fe_m['total']} ({fe_m['pct']}%) | 할루시: {fe_h['rate']}%")
(RESULTS_DIR / "C3_FE.md").write_text(fe["text"], encoding="utf-8")


# ========================================================================
# 종합
# ========================================================================

print("\n\n" + "=" * 70)
print("종합 결과")
print("=" * 70)

# 토큰 비용 계산 (Sonnet 4.5 기준)
def cost(tokens_in, tokens_out):
    return tokens_in * 3 / 1_000_000 + tokens_out * 15 / 1_000_000

total_in = cto["in"] + be["in"] + fe["in"]
total_out = cto["out"] + be["out"] + fe["out"]

print(f"\n[C 체이닝] 누적 토큰: in={total_in}, out={total_out}")
print(f"[C 체이닝] 누적 비용: ${cost(total_in, total_out):.3f}")

print(f"\n{'단계':<12} | 키워드 | 할루시검증")
print("-" * 45)
print(f"{'CTO':<12} | {cto_m['hits']:2d}/{cto_m['total']} ({cto_m['pct']}%) | {cto_h['verified']}/{cto_h['total']} ({cto_h['rate']}%)")
print(f"{'BE (CTO→)':<12} | {be_m['hits']:2d}/{be_m['total']} ({be_m['pct']}%) | {be_h['verified']}/{be_h['total']} ({be_h['rate']}%)")
print(f"{'FE (CTO+BE→)':<12} | {fe_m['hits']:2d}/{fe_m['total']} ({fe_m['pct']}%) | {fe_h['verified']}/{fe_h['total']} ({fe_h['rate']}%)")

# BE가 CTO 결과물을 실제로 참조하는지 확인
# CTO가 언급한 기술 스택 단어가 BE에도 나오는지
cto_tech = re.findall(r"(FastAPI|Node|Express|PostgreSQL|MongoDB|Redis|React|Next\.js|AWS|Cloudflare|GCP|Docker|Kubernetes|Python|TypeScript|Go)", cto["text"])
cto_tech = list(set(cto_tech))
be_refs = sum(1 for t in cto_tech if t in be["text"])
fe_refs_be = sum(1 for word in ["POST /", "GET /", "엔드포인트", "/api"] if word in fe["text"])

print(f"\n체이닝 일관성:")
print(f"  CTO 기술 스택 → BE 참조: {be_refs}/{len(cto_tech)} — {cto_tech}")
print(f"  BE API → FE 참조: {fe_refs_be}개 언급 확인")

# 저장
(RESULTS_DIR / "SUMMARY.json").write_text(json.dumps({
    "CTO": {"measure": cto_m, "hallucination": cto_h, "in": cto["in"], "out": cto["out"]},
    "BE": {"measure": be_m, "hallucination": be_h, "in": be["in"], "out": be["out"]},
    "FE": {"measure": fe_m, "hallucination": fe_h, "in": fe["in"], "out": fe["out"]},
    "chaining": {
        "cto_tech": cto_tech,
        "be_refs_to_cto": be_refs,
        "fe_refs_to_be": fe_refs_be,
    },
    "cost_usd": round(cost(total_in, total_out), 3),
}, ensure_ascii=False, indent=2), encoding="utf-8")

print(f"\n결과: {RESULTS_DIR}")
