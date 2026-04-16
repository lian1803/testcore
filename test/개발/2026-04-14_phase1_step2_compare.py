#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 1 단계 2 — 단일 API 호출 BEFORE/AFTER 비교.

토지분석 SaaS 랜딩 히어로 카피를 두 가지 context로 생성 → 결과 비교.

BEFORE: 기존 handoff 방식 (team/{proj}/CLAUDE.md 요약 + PRD)
AFTER : Phase 1 방식 (load_planning_docs role="marketing")
"""
import sys
import os
import io
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

COMPANY_DIR = Path(__file__).resolve().parents[2] / "company"
sys.path.insert(0, str(COMPANY_DIR))
os.chdir(str(COMPANY_DIR))

from dotenv import load_dotenv
load_dotenv(COMPANY_DIR / ".env")

import anthropic
from core.context_loader import load_planning_docs


TEAM_DIR = Path(__file__).resolve().parents[3] / "team" / "phase1_test_토지분석"
MODEL = "claude-sonnet-4-5-20250929"


SYSTEM_PROMPT = """너는 B2B SaaS 마케팅 카피라이터야.
토지 사업성 분석 자동화 SaaS의 랜딩 페이지 히어로 섹션 카피를 작성해.

=== 출력 형식 (정확히 이대로) ===

[헤드라인]
한 문장 (25자 이내)

[서브헤드]
1~2문장 (60~100자)

[CTA 버튼]
버튼 텍스트 (12자 이내)

[핵심 가치 Bullet 3개]
- 가치 1 (20자 이내)
- 가치 2 (20자 이내)
- 가치 3 (20자 이내)

=== 작성 규칙 ===
1. 구체적 페르소나를 의식해서 작성
2. Pain Point는 **숫자로** 찍어 (금액/시간/비율)
3. "AI", "자동화", "혁신", "스마트", "차세대" — 이런 진부한 단어 금지
4. 추상적 표현 금지. 구체명사·숫자·고유명 위주
5. 타겟의 공포/불안을 건드릴 것
"""


def call_claude(client: anthropic.Anthropic, user_content: str, label: str) -> dict:
    resp = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_content}],
    )
    return {
        "label": label,
        "text": resp.content[0].text,
        "input_tokens": resp.usage.input_tokens,
        "output_tokens": resp.usage.output_tokens,
    }


def main():
    # ── Context 준비 ──
    claude_md = (TEAM_DIR / "CLAUDE.md").read_text(encoding="utf-8")
    prd = (TEAM_DIR / "PRD.md").read_text(encoding="utf-8")

    # BEFORE: 기존 handoff 방식 (CLAUDE.md + PRD만)
    before_context = f"{claude_md}\n\n---\n\n# PRD\n{prd}"

    # AFTER: Phase 1 방식 (기획문서/ 역할별 로드)
    after_context = load_planning_docs(str(TEAM_DIR), role="marketing")

    print("=" * 70)
    print("단계 2: BEFORE/AFTER 비교")
    print("=" * 70)
    print(f"\nBEFORE context 길이: {len(before_context):6d} 자")
    print(f"AFTER  context 길이: {len(after_context):6d} 자")

    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    before_user = f"다음 프로젝트 context를 읽고 랜딩 히어로 카피를 작성해.\n\n{before_context}"
    after_user = f"다음 프로젝트 context를 읽고 랜딩 히어로 카피를 작성해.\n\n{after_context}"

    print("\n[1/2] BEFORE 호출 중...")
    before = call_claude(client, before_user, "BEFORE")
    print("[2/2] AFTER 호출 중...")
    after = call_claude(client, after_user, "AFTER")

    # ── 출력 ──
    print("\n" + "=" * 70)
    print("BEFORE 결과 (기존 handoff 방식)")
    print("=" * 70)
    print(before["text"])
    print(f"\n(토큰: in={before['input_tokens']}, out={before['output_tokens']})")

    print("\n" + "=" * 70)
    print("AFTER 결과 (Phase 1 방식)")
    print("=" * 70)
    print(after["text"])
    print(f"\n(토큰: in={after['input_tokens']}, out={after['output_tokens']})")

    # ── 키워드 매칭 자동 검증 ──
    print("\n" + "=" * 70)
    print("키워드 매칭 — 기획문서 고유 단어가 결과에 나타나는가")
    print("=" * 70)

    keywords = [
        "김철수", "시행사", "인허가", "5억", "48시간", "75%",
        "컨설턴트", "500만원", "69만원", "2주", "거절", "블루오션",
        "대표", "매입", "특례법",
    ]

    before_hits = 0
    after_hits = 0
    print(f"\n{'키워드':<12} | BEFORE | AFTER")
    print("-" * 35)
    for kw in keywords:
        b = "✓" if kw in before["text"] else " "
        a = "✓" if kw in after["text"] else " "
        if b == "✓":
            before_hits += 1
        if a == "✓":
            after_hits += 1
        print(f"{kw:<12} |   {b}    |   {a}")

    print(f"\n총 매칭 수: BEFORE = {before_hits}/{len(keywords)}, AFTER = {after_hits}/{len(keywords)}")
    print(f"개선률: +{after_hits - before_hits} 키워드")

    # ── 결과 저장 ──
    results_dir = Path(__file__).parent / "phase1_results"
    results_dir.mkdir(exist_ok=True)
    (results_dir / "before.md").write_text(
        f"# BEFORE\n\n{before['text']}\n\n---\n\ntokens: in={before['input_tokens']}, out={before['output_tokens']}",
        encoding="utf-8",
    )
    (results_dir / "after.md").write_text(
        f"# AFTER\n\n{after['text']}\n\n---\n\ntokens: in={after['input_tokens']}, out={after['output_tokens']}",
        encoding="utf-8",
    )
    print(f"\n결과 저장: {results_dir}")
    print("\n" + "=" * 70)
    print("단계 2 종료")
    print("=" * 70)


if __name__ == "__main__":
    main()
