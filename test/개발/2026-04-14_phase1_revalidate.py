#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 1 재검증 — 애매했던 결과 2개 재확인.

1. 혜경 대시보드: 개념어 키워드로 재검증 (숫자 키워드 말고)
2. BE 역할: 역할별 파일 조정하면 개선 폭 늘어나는지
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
from core.context_loader import load_planning_docs

MODEL = "claude-sonnet-4-5-20250929"
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

RESULTS_DIR = Path(__file__).parent / "phase1_results" / f"revalidate_{datetime.now():%H%M%S}"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def call_claude(system: str, user: str) -> dict:
    resp = client.messages.create(
        model=MODEL,
        max_tokens=1500,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return {
        "text": resp.content[0].text,
        "in": resp.usage.input_tokens,
        "out": resp.usage.output_tokens,
    }


def extract_concept_keywords(planning_dir: Path, top_n: int = 15) -> list:
    """기획문서에서 개념어/고유명사 자동 추출.
    - 페르소나 관련: 직업, 연령, 소속
    - 반복 등장 단어 중 2~5글자 한글
    """
    text = ""
    for f in planning_dir.glob("*.md"):
        text += f.read_text(encoding="utf-8")

    # 한글 2~5글자 단어 추출
    words = re.findall(r"[가-힣]{2,5}", text)

    # 불용어 제거
    stopwords = {
        "있는", "없는", "있다", "없다", "하는", "하고", "위한", "따른", "대한",
        "이것", "그것", "저것", "이런", "그런", "저런", "수도", "경우", "때문",
        "통해", "또한", "또는", "그리고", "하지만", "따라", "관련", "다음",
        "이상", "이하", "여기", "저기", "내용", "결과", "현재", "이전",
        "우리", "저희", "본사", "하는데", "것은", "것이", "것을", "있음",
        "없음", "기반", "방식", "부분", "전체", "일부", "가장", "매우",
        "많이", "적게", "그리", "그래", "이미", "아직",
    }

    # 빈도 집계
    from collections import Counter
    counts = Counter(w for w in words if w not in stopwords)

    return [w for w, c in counts.most_common(top_n) if c >= 3]


# ── Test 1: 혜경 재검증 ─────────────────────────────────────────

print("=" * 70)
print("재검증 1: 혜경 대시보드 (개념어 키워드)")
print("=" * 70)

hk_team = CORE_DIR.parent / "team" / "phase1_test_혜경대시보드"
hk_planning = hk_team / "기획문서"

if not hk_team.exists():
    print("❌ 혜경 team 폴더 없음")
    sys.exit(1)

hk_keywords = extract_concept_keywords(hk_planning, top_n=20)
print(f"\n자동 추출 키워드: {hk_keywords}")

# Context
claude_md = (hk_team / "CLAUDE.md").read_text(encoding="utf-8")
prd = (hk_team / "PRD.md").read_text(encoding="utf-8")
before_ctx = f"{claude_md}\n\n---\n\n# PRD\n{prd}"
after_ctx = load_planning_docs(str(hk_team), role="marketing")

system = """너는 B2B SaaS 마케팅 카피라이터.
랜딩 페이지 히어로 섹션 카피를 작성해.

형식:
[헤드라인] 25자 이내
[서브헤드] 60~100자
[CTA 버튼] 12자 이내
[핵심 가치 Bullet 3개] 각 20자 이내

규칙:
- 구체 페르소나 의식
- 페르소나가 실제 쓰는 말투로
- "AI/자동화/혁신/스마트/차세대" 금지
- 추상 표현 금지, 구체 명사 중심
"""

print("\nBEFORE 호출...")
b = call_claude(system, f"context:\n{before_ctx}\n\n위 읽고 히어로 카피 작성.")
print("AFTER 호출...")
a = call_claude(system, f"context:\n{after_ctx}\n\n위 읽고 히어로 카피 작성.")

# 개념어 매칭
b_hits = [k for k in hk_keywords if k in b["text"]]
a_hits = [k for k in hk_keywords if k in a["text"]]
print(f"\nBEFORE 매칭: {len(b_hits)}/{len(hk_keywords)} — {b_hits[:8]}")
print(f"AFTER  매칭: {len(a_hits)}/{len(hk_keywords)} — {a_hits[:8]}")

(RESULTS_DIR / "hk_before.md").write_text(b["text"], encoding="utf-8")
(RESULTS_DIR / "hk_after.md").write_text(a["text"], encoding="utf-8")

print("\n--- BEFORE 카피 ---")
print(b["text"])
print("\n--- AFTER 카피 ---")
print(a["text"])


# ── Test 2: BE 재조정 ──────────────────────────────────────────
# BE는 현재 05(PRD) + 02c(BM) 받는데, 사실 05만 있으면 될 수도
# 반대로 05 + 02b(전략브리프) 조합이 더 나을 수도

print("\n\n" + "=" * 70)
print("재검증 2: BE 필독 파일 재조정 (토지분석)")
print("=" * 70)

land_team = CORE_DIR.parent / "team" / "phase1_test_토지분석"
land_planning = land_team / "기획문서"

# PRD만
prd_only = (land_planning / "05_PRD_지훈.md").read_text(encoding="utf-8")[:30000]

# PRD + BM (현재)
prd_bm = (load_planning_docs(str(land_team), role="be"))

# PRD + 전략브리프
strat = (land_planning / "02b_전략브리프_설계자.md").read_text(encoding="utf-8")
prd_strat = f"## 05_PRD_지훈.md\n\n{prd_only}\n\n---\n\n## 02b_전략브리프_설계자.md\n\n{strat}"[:30000]

be_system = """너는 시니어 백엔드 엔지니어.
MVP P0 기능 기준으로 핵심 API 엔드포인트 5개를 설계해.

형식:
| # | Method | Path | 역할 | Request | Response |

각 엔드포인트 아래:
- 기획의 어떤 P0 기능을 구현하는지 한 줄
- 예상 부하/지연 주의점 한 줄

규칙:
- 기획의 실제 기능 기반 (일반적 CRUD 금지)
- 에러 응답 코드 명시
"""

# 3가지 context로 호출
configs = {
    "PRD만": prd_only,
    "PRD+BM(현재)": prd_bm,
    "PRD+전략브리프": prd_strat,
}

land_keywords = [
    "인허가", "승인확률", "48시간", "특례법", "용도지역", "건폐율",
    "OCR", "PDF", "ML", "로지스틱", "부동산", "지자체",
    "개요서", "유사사례", "리포트",
]

be_results = {}
for label, ctx in configs.items():
    print(f"\n[{label}] 호출 중... (context {len(ctx)} 자)")
    r = call_claude(be_system, f"context:\n{ctx}\n\n위 읽고 API 엔드포인트 5개 설계.")
    hits = [k for k in land_keywords if k in r["text"]]
    be_results[label] = {
        "hits": len(hits),
        "matched": hits,
        "in": r["in"],
        "out": r["out"],
    }
    print(f"  키워드 매칭: {len(hits)}/{len(land_keywords)} — {hits}")
    (RESULTS_DIR / f"be_{label.replace('(현재)', '').replace('+', '_')}.md").write_text(
        r["text"], encoding="utf-8"
    )

print("\n\nBE 요약:")
print(json.dumps(be_results, ensure_ascii=False, indent=2))

# 저장
(RESULTS_DIR / "SUMMARY.json").write_text(
    json.dumps({
        "hk_before_hits": len(b_hits),
        "hk_after_hits": len(a_hits),
        "hk_keywords": hk_keywords,
        "be_results": be_results,
    }, ensure_ascii=False, indent=2),
    encoding="utf-8",
)

print(f"\n결과: {RESULTS_DIR}")
