# 모델 이름 중앙 관리
# 신모델 나오면 여기만 바꾸면 됨

# ── Anthropic ─────────────────────────────────────────────────
CLAUDE_OPUS      = "claude-opus-4-6"        # 최고급 추론·의사결정
CLAUDE_SONNET    = "claude-sonnet-4-6"       # 범용 전략·글쓰기
CLAUDE_HAIKU     = "claude-haiku-4-5-20251001"  # 빠름·저렴·반복 작업

# ── Google Gemini ──────────────────────────────────────────────
GEMINI_FLASH     = "gemini-2.5-flash"        # 멀티모달·빠른 비전
GEMINI_PRO       = "gemini-2.5-pro"          # 긴 문서·복잡 분석 (1M context)
GEMINI_31_PRO    = "gemini-3.1-pro-preview"  # 최신 Gemini 3.1 프리뷰 (프리뷰 주의)
GEMINI_31_FLASH  = "gemini-3.1-flash-lite-preview"  # 최신 Gemini 3.1 빠른 버전 (프리뷰 주의)

# ── OpenAI ────────────────────────────────────────────────────
GPT4O            = "gpt-4o"                  # 범용 GPT, 한국어 강점
GPT4O_MINI       = "gpt-4o-mini"             # 저렴한 GPT-4o
GPT41            = "gpt-4.1"                 # 코딩·구조화 출력 특화
GPT41_MINI       = "gpt-4.1-mini"            # 저렴한 GPT-4.1
GPT41_NANO       = "gpt-4.1-nano"            # 가장 빠름·가장 저렴
O4_MINI          = "o4-mini"                 # 추론 특화 (수학·코딩·논리)
O3_MINI          = "o3-mini-2025-01-31"      # 추론 특화 이전 버전

# ── Perplexity ────────────────────────────────────────────────
SONAR_PRO        = "sonar-pro"               # 실시간 웹 검색
SONAR            = "sonar"                   # 빠른 웹 검색
SONAR_REASONING  = "sonar-reasoning-pro"     # 실시간 검색 + 추론

