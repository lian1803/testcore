"""
실행 전 예상 비용 계산기
main.py 시작 시 호출 → 과금 예정 금액 출력
"""

# ── 모델별 단가 (달러 / 1M 토큰) ──────────────────────────────
PRICES = {
    "claude-sonnet-4-6":       {"input": 3.0,   "output": 15.0},
    "claude-haiku-4-5-20251001": {"input": 0.8,  "output": 4.0},
    "claude-opus-4-6":         {"input": 15.0,  "output": 75.0},
    "gpt-4o":                  {"input": 2.5,   "output": 10.0},
    "gemini-2.5-flash":        {"input": 0.075, "output": 0.30},
    "sonar-pro":               {"input": 3.0,   "output": 15.0},  # Perplexity
}

# ── 에이전트별 예상 토큰 (min / max) ──────────────────────────
# (input_tokens, output_tokens)
AGENTS = [
    {
        "name": "시은 - 아이디어 명확화",
        "model": "claude-sonnet-4-6",
        "input":  (2_000, 4_000),
        "output": (1_000, 2_000),
        "note": "Claude Sonnet",
    },
    {
        "name": "태호 - 트렌드 스카우팅",
        "model": "claude-haiku-4-5-20251001",
        "input":  (2_000, 3_000),
        "output": (1_500, 2_500),
        "note": "Claude Haiku",
    },
    {
        "name": "서윤 - 시장조사",
        "model": "sonar-pro",
        "input":  (1_000, 2_000),
        "output": (2_000, 4_000),
        "note": "Perplexity Sonar Pro",
    },
    {
        "name": "민수 - 전략/수익모델",
        "model": "gpt-4o",
        "input":  (4_000, 7_000),
        "output": (2_000, 3_500),
        "note": "GPT-4o",
    },
    {
        "name": "하은 - 팩트 검증/반론",
        "model": "gemini-2.5-flash",
        "input":  (5_000, 9_000),
        "output": (1_500, 3_000),
        "note": "Gemini 2.5 Flash",
    },
    {
        "name": "토론 루프 (민수↔하은, 2라운드)",
        "model": "gpt-4o",           # 민수 재반박 기준
        "input":  (6_000, 10_000),
        "output": (1_000, 2_000),
        "note": "GPT-4o + Gemini 혼합",
    },
    {
        "name": "준혁 - GO/NO-GO 최종 판단",
        "model": "claude-opus-4-6",
        "input":  (7_000, 12_000),
        "output": (1_500, 3_000),
        "note": "Claude Opus ← 가장 비쌈",
    },
    {
        "name": "지훈 - PRD 작성",
        "model": "claude-sonnet-4-6",
        "input":  (7_000, 12_000),
        "output": (2_500, 5_000),
        "note": "Claude Sonnet",
    },
    {
        "name": "시은 - 인터뷰 + 팀 설계",
        "model": "claude-sonnet-4-6",
        "input":  (4_000, 7_000),
        "output": (1_500, 3_000),
        "note": "Claude Sonnet",
    },
    {
        "name": "도윤 - 교육팀 커리큘럼 설계",
        "model": "claude-opus-4-6",
        "input":  (5_000, 9_000),
        "output": (2_500, 5_000),
        "note": "Claude Opus ← 가장 비쌈",
    },
    {
        "name": "서윤 - 교육팀 지식 수집",
        "model": "sonar-pro",
        "input":  (1_000, 2_000),
        "output": (4_000, 8_000),
        "note": "Perplexity Sonar Pro",
    },
]

EXCHANGE_RATE = 1400  # 달러 → 원 환산


def _calc(model: str, input_tok: int, output_tok: int) -> float:
    p = PRICES.get(model, {"input": 3.0, "output": 15.0})
    return (input_tok * p["input"] + output_tok * p["output"]) / 1_000_000


def estimate(verbose: bool = True) -> tuple[float, float]:
    """
    예상 비용 계산 후 출력.
    Returns: (min_usd, max_usd)
    """
    total_min = 0.0
    total_max = 0.0

    if verbose:
        print("\n" + "=" * 60)
        print("  [예상 비용 안내]")
        print("=" * 60)
        print(f"  {'에이전트':<30} {'최소':>8} {'최대':>8}  {'모델'}")
        print(f"  {'-'*30} {'-'*8} {'-'*8}  {'-'*20}")

    for agent in AGENTS:
        lo = _calc(agent["model"], agent["input"][0], agent["output"][0])
        hi = _calc(agent["model"], agent["input"][1], agent["output"][1])
        total_min += lo
        total_max += hi

        if verbose:
            print(f"  {agent['name']:<30} ${lo:>6.3f}  ${hi:>6.3f}  {agent['note']}")

    if verbose:
        print(f"  {'─'*60}")
        print(f"  {'합계':<30} ${total_min:>6.3f}  ${total_max:>6.3f}")
        print()
        krw_min = int(total_min * EXCHANGE_RATE)
        krw_max = int(total_max * EXCHANGE_RATE)
        print(f"  예상 범위: ${total_min:.2f} ~ ${total_max:.2f}")
        print(f"           (약 {krw_min:,}원 ~ {krw_max:,}원, 환율 {EXCHANGE_RATE}원 기준)")
        print()
        print(f"  * 실제 금액은 아이디어 복잡도에 따라 달라질 수 있어요")
        print(f"  * NO-GO 판정 시 지훈/교육팀 단계는 생략되어 더 저렴해요")
        print("=" * 60)

    return total_min, total_max


def confirm_proceed() -> bool:
    """비용 안내 후 진행 여부 확인"""
    estimate(verbose=True)
    print("\n  계속 진행할까? (y/n, 엔터 = y): ", end="")
    try:
        answer = input().strip().lower()
    except EOFError:
        answer = "y"
    return answer in ("", "y", "yes", "ㅇ", "ㅇㅇ", "응", "어", "진행", "ok")
