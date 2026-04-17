# LLM 비용 서킷브레이커 PRD

## 개요
AI 에이전트가 루프 돌다 수만 달러 태우기 전에 실시간으로 잡아서 끊는 SDK 래퍼 SaaS.
`pip install llm-guard` 한 줄 → openai/anthropic/google 클라이언트를 래핑 → 예산 초과 시 자동 차단.

**Pain 검증 완료 (2026-04-08):**
- $82K (Gemini API키 도용), $72K (OpenAI 재시도루프), $70K+ (Gemini 빌링버그), $30K (OpenAI 예상외 청구) 등 10건 실제 확인
- HackerNews, Reddit, OpenAI Community, The Register 출처

**경쟁사 분석:**
- OpenRouter: 프록시 방식 → SPOF + 레이턴시 추가
- Portkey: Enterprise only ($499+/월)
- Helicone: 시간창 rate limit만, 절대 누적 예산 미지원
- LangSmith/Langfuse: 알림만, 자동 차단 없음
- **우리 차별화: SDK 래퍼 방식(레이턴시 0) + 무료부터 + 에이전트 루프 특화**

## 기술 스택
- **Frontend**: Next.js 14 App Router + TypeScript + Tailwind CSS + shadcn/ui
- **Backend**: Next.js API Routes + Supabase (DB + Auth + Realtime)
- **Python SDK**: PyPI 패키지 (`llm-guard`) — openai/anthropic/google 래퍼
- **결제**: Stripe (Checkout + Webhook)
- **인프라**: Vercel (FE + API), Supabase (DB + Realtime), Upstash Redis (토큰 카운터)
- **알림**: Slack Webhook + SendGrid (이메일)

## Python SDK 핵심 스펙 (`llm-guard`)

### 설치 및 사용
```python
# 설치
pip install llm-guard

# 기존 코드 — 1줄만 바꾸면 됨
# from openai import OpenAI         ← 기존
from llm_guard.openai import OpenAI  # ← 변경

client = OpenAI(
    api_key="sk-...",
    llm_guard_key="lg-...",     # 대시보드에서 발급
    budget_usd=10.0,             # 월 $10 초과 시 차단
    on_exceed="raise",           # raise | warn | log
)
```

### SDK 래퍼 동작
1. `client.chat.completions.create()` 호출 전 — 토큰 수 추정 (tiktoken)
2. 누적 비용 + 예상 비용 > 예산 → `BudgetExceededError` raise (호출 차단)
3. 호출 허용 시 → 실제 토큰 수로 DB 업데이트 (비동기)
4. 에이전트 루프 감지: 동일 컨텍스트 N회 반복 → 자동 차단

### 지원 LLM
- OpenAI (gpt-4o, gpt-4o-mini, o1, o3 등)
- Anthropic (claude-3-5-sonnet, claude-opus-4 등)
- Google (gemini-2.0-flash, gemini-2.5-pro 등)

## 핵심 기능

### 1. SDK 래퍼 (Week 1 MVP 핵심)
- Pre-call 토큰 추정 → 예산 초과 시 즉시 차단
- `BudgetExceededError` — 현재 누적 비용 + 남은 예산 포함
- 에이전트 루프 감지 (동일 컨텍스트 10회 반복 = 루프)
- 비동기 실제 토큰 카운팅 (성능 오버헤드 p99 < 10ms)

### 2. 실시간 대시보드 (Week 2)
- 오늘 비용 / 월 예산 대비 % / 남은 예산 — 상단 고정
- 실시간 비용 차트 (Supabase Realtime)
- 차단 이벤트 로그 (언제, 어떤 모델, 얼마에서 차단됐는지)
- API 키 관리 (발급/삭제/권한)
- 프로젝트별 예산 분리

### 3. 알림 시스템 (Week 2)
- Slack Webhook: 예산 50%, 80%, 100% 도달 시
- 이메일: 차단 이벤트 발생 시 즉시 (SendGrid)
- 임계값 커스텀 가능 (Pro+)

### 4. 결제 (Week 3-4)
- Stripe Checkout (카드 결제)
- Free → Pro 업그레이드 플로우
- 연간 결제 20% 할인

## 수익 모델 (가격)

| 플랜 | 가격 | 프로젝트 | 알림 채널 | 지원 LLM |
|------|------|---------|---------|---------|
| **Free** | $0 | 1개 | 이메일만 | OpenAI만 |
| **Pro** | $49/월 | 5개 | Slack+이메일 | 3종 모두 |
| **Team** | $99/월 | 무제한 | 팀 공유 대시보드 | 3종 + 우선 지원 |

## 페이지 구조

```
/ (랜딩)            → 히어로 + 사고사례($82K/$72K) + 1줄 코드 데모 + 웨이팅리스트
/dashboard          → 실시간 비용 대시보드 (로그인 필요)
/dashboard/projects → 프로젝트별 예산 관리
/dashboard/alerts   → 알림 설정
/dashboard/billing  → 구독 관리 (Stripe)
/docs               → SDK 설치 가이드 (OpenAI/Anthropic/Google)
/pricing            → 가격 페이지
```

## UI/UX 요구사항

### 랜딩 페이지 (임팩트 중심)
- Three.js 배경: 터미널 느낌 + 빨간 경고등 파티클 (비용 폭주 → 차단되는 시각화)
- 커스텀 커서 (dot + lagging ring)
- IntersectionObserver 스크롤 애니메이션
- clamp() 반응형 타이포그래피
- 히어로: "하룻밤에 $72,000이 날아갔다" → "한 줄로 막는다"
- 색상: 다크 (#0d1117) + 레드 경고 (#ff4444) + 그린 차단성공 (#00ff88)
- 실제 사고 사례 섹션 (숫자 카운트업 애니메이션: $82K, $72K, $70K...)
- 코드 비교: Before (openai.OpenAI) vs After (llm_guard.openai.OpenAI)

### 대시보드 (기능 중심, Stitch 스타일)
- 깔끔한 숫자 중심 레이아웃
- 실시간 비용 라인 차트 (Recharts)
- 빈 상태(Empty State) 우선 설계 → "첫 API 키 발급하기" CTA

## MVP 범위 (Week 1-4)

| Week | 완료 기준 |
|------|---------|
| 1 | Python SDK(`llm-guard`) PyPI 배포 + OpenAI 래퍼 작동 + 예산 초과 시 차단 |
| 2 | 랜딩페이지 배포 + 대시보드 로그인 + 실시간 비용 차트 + Slack 알림 |
| 3 | 베타 사용자 10명 온보딩 + Anthropic/Google 래퍼 추가 + 피드백 수집 |
| 4 | Stripe 결제 연동 + 첫 유료 전환 1명 달성 ($49 Pro) |

## 성공 지표
- Week 4: 유료 고객 1명 이상 (카드 결제 확인)
- 베타 NPS 50+
- SDK 래퍼 실제 차단 이벤트 1건 이상
- 랜딩 웨이팅리스트 100명+

## 제약 조건
- OpenAI ToS 확인 필요: 래퍼/프록시 조항 (SDK 래퍼 방식은 프록시 아님 — 클라이언트 사이드)
- Supabase Free: 프로젝트 2개, 500MB DB — 베타 10명은 충분
- 법적: API 키를 서버에 저장하지 않음 (클라이언트 사이드 래퍼 → 키 노출 없음)
