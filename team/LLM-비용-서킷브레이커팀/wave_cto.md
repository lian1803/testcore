# CTO 분석 — LLM 비용 서킷브레이커 (llm-guard)

## 1. 기술 스택 확정

| 항목 | 선택 | 이유 |
|------|------|------|
| 프론트엔드 | Next.js 14 App Router + TypeScript + Tailwind + shadcn/ui | PRD 지정. App Router Server Component로 초기 로드 최소화 |
| 백엔드 | Next.js API Routes (app/api/) | 별도 서버 불필요. Vercel Functions로 자동 배포 |
| DB | Supabase (PostgreSQL) | Auth + Realtime + DB 원스톱. 베타 10명은 Free 500MB 충분 |
| 실시간 | Supabase Realtime (Postgres CDC) | usage_logs 변경 → 브라우저 차트 즉시 업데이트 |
| 캐시 / 카운터 | Upstash Redis | SDK에서 비동기 누적 카운터. 서버리스 환경에서 커넥션 풀 문제 없는 HTTP 기반 Redis |
| Python SDK | PyPI 패키지 `llm-guard` | 순수 Python. openai/anthropic/google 패키지 의존 |
| 결제 | Stripe Checkout + Webhooks | PRD 지정 |
| 이메일 | SendGrid | 차단 이벤트 즉시 알림 |
| 알림 | Slack Webhook | Pro+ 사용자 예산 임계값 알림 |
| 배포 | Vercel (FE + API Routes) | PRD 지정. Serverless Functions 리전: iad1(미국동부) |
| 토큰 카운팅 | tiktoken (OpenAI), anthropic tokenizer, 구글은 추정식 | 각 모델 네이티브 카운터 사용 |

**스택 결정 근거:**
- Cloudflare Workers 대신 Vercel 선택 이유: Supabase Realtime + Stripe Webhook이 Node.js 런타임 필요. Cloudflare Workers의 128MB 메모리 제한이 Stripe SDK와 충돌 가능성 있음.
- Upstash Redis 선택 이유: Vercel Serverless Function은 커넥션 수명이 짧다. ioredis 같은 TCP 기반 Redis는 Function 호출마다 새 커넥션 = 비효율. Upstash는 HTTP REST로 동작 — 서버리스에 최적.

---

## 2. DB 스키마 (Supabase)

### 멀티테넌트 격리 전략: Pool 모델 (공유 DB + RLS)
베타 10명 규모에서 Silo 모델은 과하다. `user_id` FK + Row Level Security로 충분히 격리.

```sql
-- =============================================
-- 1. users (Supabase Auth 확장 — auth.users와 연결)
-- =============================================
CREATE TABLE public.users (
  id          UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email       TEXT NOT NULL,
  plan        TEXT NOT NULL DEFAULT 'free',  -- 'free' | 'pro' | 'team'
  stripe_customer_id  TEXT,
  stripe_subscription_id TEXT,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
CREATE POLICY users_self ON public.users
  USING (id = auth.uid());

-- =============================================
-- 2. projects (유저별 프로젝트 — 예산 단위)
-- =============================================
CREATE TABLE public.projects (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  name        TEXT NOT NULL,
  description TEXT,
  budget_usd  NUMERIC(10, 4) NOT NULL DEFAULT 10.0,  -- 월 예산 $
  reset_day   SMALLINT NOT NULL DEFAULT 1,            -- 매월 몇 일에 리셋 (1~28)
  is_active   BOOLEAN NOT NULL DEFAULT true,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE public.projects ENABLE ROW LEVEL SECURITY;
CREATE POLICY projects_owner ON public.projects
  USING (user_id = auth.uid());

-- 인덱스: user_id 기준 조회가 가장 많음
CREATE INDEX idx_projects_user_id ON public.projects(user_id, created_at DESC);

-- =============================================
-- 3. api_keys (대시보드에서 발급하는 llm_guard_key)
-- =============================================
CREATE TABLE public.api_keys (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  project_id  UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
  name        TEXT NOT NULL,                          -- "프로덕션 키", "테스트 키" 등
  key_hash    TEXT NOT NULL UNIQUE,                   -- bcrypt 해시. 원본은 발급 시 1회만 노출
  key_prefix  TEXT NOT NULL,                          -- "lg_" + 앞 8자. 목록에서 식별용
  last_used_at TIMESTAMPTZ,
  is_active   BOOLEAN NOT NULL DEFAULT true,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE public.api_keys ENABLE ROW LEVEL SECURITY;
CREATE POLICY api_keys_owner ON public.api_keys
  USING (user_id = auth.uid());

CREATE INDEX idx_api_keys_key_hash ON public.api_keys(key_hash);
CREATE INDEX idx_api_keys_project ON public.api_keys(project_id);

-- =============================================
-- 4. usage_logs (모든 LLM 호출 이벤트)
-- =============================================
CREATE TABLE public.usage_logs (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id      UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
  user_id         UUID NOT NULL,                      -- RLS용 denormalize
  model           TEXT NOT NULL,                      -- "gpt-4o", "claude-3-5-sonnet-20241022"
  provider        TEXT NOT NULL,                      -- "openai" | "anthropic" | "google"
  input_tokens    INTEGER NOT NULL DEFAULT 0,
  output_tokens   INTEGER NOT NULL DEFAULT 0,
  cost_usd        NUMERIC(10, 6) NOT NULL DEFAULT 0,  -- 소수점 6자리 (마이크로달러)
  is_blocked      BOOLEAN NOT NULL DEFAULT false,     -- 예산 초과로 차단됐는지
  block_reason    TEXT,                               -- NULL | "budget_exceeded" | "loop_detected"
  request_hash    TEXT,                               -- 루프 감지용 컨텍스트 해시
  latency_ms      INTEGER,                            -- 실제 API 레이턴시
  called_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE public.usage_logs ENABLE ROW LEVEL SECURITY;
CREATE POLICY usage_logs_owner ON public.usage_logs
  USING (user_id = auth.uid());

-- 성능 핵심 인덱스
CREATE INDEX idx_usage_logs_project_called
  ON public.usage_logs(project_id, called_at DESC);
CREATE INDEX idx_usage_logs_user_called
  ON public.usage_logs(user_id, called_at DESC);
-- 월간 집계 쿼리용 (date_trunc('month', called_at))
CREATE INDEX idx_usage_logs_month
  ON public.usage_logs(project_id, date_trunc('month', called_at));

-- Realtime 활성화 (대시보드 실시간 차트)
ALTER PUBLICATION supabase_realtime ADD TABLE public.usage_logs;

-- =============================================
-- 5. budgets (월별 예산 스냅샷 — 집계 캐시)
-- =============================================
-- 매 호출마다 usage_logs SUM하면 느림 → budgets에 누적값 유지
CREATE TABLE public.budgets (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id      UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
  user_id         UUID NOT NULL,
  period_start    DATE NOT NULL,                      -- 해당 월 시작일 (매월 reset_day 기준)
  spent_usd       NUMERIC(10, 4) NOT NULL DEFAULT 0,
  call_count      INTEGER NOT NULL DEFAULT 0,
  blocked_count   INTEGER NOT NULL DEFAULT 0,
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE(project_id, period_start)
);

ALTER TABLE public.budgets ENABLE ROW LEVEL SECURITY;
CREATE POLICY budgets_owner ON public.budgets
  USING (user_id = auth.uid());

CREATE INDEX idx_budgets_project_period
  ON public.budgets(project_id, period_start DESC);

-- =============================================
-- 6. alerts (알림 설정)
-- =============================================
CREATE TABLE public.alerts (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id      UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
  user_id         UUID NOT NULL,
  threshold_pct   SMALLINT NOT NULL,                  -- 50 | 80 | 100 (예산 대비 %)
  channel         TEXT NOT NULL,                      -- "email" | "slack"
  slack_webhook   TEXT,                               -- Pro+만 사용
  is_active       BOOLEAN NOT NULL DEFAULT true,
  last_fired_at   TIMESTAMPTZ,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE public.alerts ENABLE ROW LEVEL SECURITY;
CREATE POLICY alerts_owner ON public.alerts
  USING (user_id = auth.uid());
```

### 집계 함수 (Supabase DB Function)
```sql
-- 현재 월 누적 비용 조회 (SDK 차단 판단용)
CREATE OR REPLACE FUNCTION get_current_spend(p_project_id UUID)
RETURNS NUMERIC AS $$
  SELECT COALESCE(spent_usd, 0)
  FROM public.budgets
  WHERE project_id = p_project_id
    AND period_start = date_trunc('month', now())::date
$$ LANGUAGE sql STABLE SECURITY DEFINER;
```

---

## 3. API 설계

### 인증 방식
- 대시보드 API: Supabase Auth JWT (Bearer Token) — 유저가 로그인 후 사용
- SDK API: `X-LLM-Guard-Key` 헤더 — `lg_` 접두어 키, 서버에서 bcrypt 검증

### Base URL
`https://llm-guard.com/api/v1`

### 엔드포인트 목록

#### SDK 전용 API (Python SDK가 호출)

| 메서드 | 경로 | 역할 | 인증 |
|--------|------|------|------|
| POST | `/sdk/check` | Pre-call 예산 체크. 누적 비용 + 예상 비용 계산 → 허용/차단 결정 | API Key |
| POST | `/sdk/report` | 실제 호출 완료 후 토큰/비용 기록 (비동기 fire-and-forget) | API Key |

**POST /sdk/check — Request**
```json
{
  "model": "gpt-4o",
  "provider": "openai",
  "estimated_tokens": 1250,
  "request_hash": "sha256(messages)",
  "context_count": 3
}
```

**POST /sdk/check — Response**
```json
{
  "allowed": true,
  "current_spend_usd": 7.23,
  "budget_usd": 10.0,
  "remaining_usd": 2.77,
  "estimated_cost_usd": 0.0025
}
```
차단 시:
```json
{
  "allowed": false,
  "reason": "budget_exceeded",
  "current_spend_usd": 10.02,
  "budget_usd": 10.0,
  "remaining_usd": -0.02
}
```

**POST /sdk/report — Request**
```json
{
  "model": "gpt-4o",
  "provider": "openai",
  "input_tokens": 1180,
  "output_tokens": 312,
  "cost_usd": 0.00619,
  "latency_ms": 1240,
  "is_blocked": false,
  "request_hash": "sha256(messages)"
}
```

#### 대시보드 API (Next.js API Routes)

| 메서드 | 경로 | 역할 |
|--------|------|------|
| GET | `/projects` | 유저 프로젝트 목록 + 현재 월 spend |
| POST | `/projects` | 프로젝트 생성 |
| PATCH | `/projects/:id` | 예산/이름 수정 |
| DELETE | `/projects/:id` | 프로젝트 삭제 |
| GET | `/projects/:id/usage` | 시계열 usage 조회 (쿼리: period, granularity) |
| GET | `/projects/:id/logs` | 차단 이벤트 + 호출 로그 목록 (pagination) |
| GET | `/api-keys` | API 키 목록 (key_prefix만 노출) |
| POST | `/api-keys` | 신규 키 발급 (원본 1회만 응답) |
| DELETE | `/api-keys/:id` | 키 비활성화 |
| GET | `/alerts` | 알림 설정 목록 |
| POST | `/alerts` | 알림 설정 생성 |
| PATCH | `/alerts/:id` | 알림 수정/비활성화 |
| GET | `/billing/status` | 현재 플랜 + 구독 상태 |
| POST | `/billing/checkout` | Stripe Checkout 세션 생성 |
| POST | `/billing/portal` | Stripe Customer Portal URL 발급 |
| POST | `/webhooks/stripe` | Stripe 이벤트 수신 (플랜 업데이트) |

### 에러 응답 형식 (통일)
```typescript
interface ApiError {
  code: string;       // "BUDGET_EXCEEDED" | "INVALID_API_KEY" | "PLAN_LIMIT" 등
  message: string;    // 사람이 읽을 수 있는 설명
  requestId: string;  // Vercel trace ID
}
```

---

## 4. SDK 아키텍처 (Python llm-guard)

### 패키지 구조
```
llm_guard/
├── __init__.py
├── openai.py          # from llm_guard.openai import OpenAI
├── anthropic.py       # from llm_guard.anthropic import Anthropic
├── google.py          # from llm_guard.google import GenerativeModel
├── core/
│   ├── client.py      # LLMGuardClient — API Key 보관 + HTTP 통신
│   ├── estimator.py   # 토큰 추정 로직
│   ├── loop_detector.py  # 에이전트 루프 감지
│   └── exceptions.py  # BudgetExceededError, LoopDetectedError
└── utils/
    ├── pricing.py     # 모델별 단가 테이블
    └── hasher.py      # request_hash 생성
```

### 핵심 클래스 설계

#### LLMGuardClient (core/client.py)
```python
class LLMGuardClient:
    """
    대시보드 API와 통신하는 싱글톤 클라이언트.
    SDK 초기화 시 1회 생성, 이후 래퍼들이 공유.
    """
    def __init__(self, llm_guard_key: str, budget_usd: float,
                 on_exceed: str = "raise"):
        self.api_key = llm_guard_key
        self.budget_usd = budget_usd
        self.on_exceed = on_exceed  # "raise" | "warn" | "log"
        self._session = httpx.AsyncClient(
            base_url="https://llm-guard.com/api/v1",
            headers={"X-LLM-Guard-Key": llm_guard_key},
            timeout=2.0  # 타임아웃 2초 — 초과 시 allow-through (가용성 우선)
        )
        self._loop_detector = LoopDetector()

    async def check(self, model: str, provider: str,
                    messages: list, estimated_tokens: int) -> CheckResult:
        """Pre-call 체크. 2초 타임아웃 내 응답 없으면 허용 처리."""
        request_hash = compute_hash(messages)
        loop_count = self._loop_detector.count(request_hash)

        try:
            resp = await self._session.post("/sdk/check", json={
                "model": model,
                "provider": provider,
                "estimated_tokens": estimated_tokens,
                "request_hash": request_hash,
                "context_count": loop_count,
            })
            return CheckResult(**resp.json())
        except httpx.TimeoutException:
            # 서비스 장애 시 SDK가 원본 LLM 호출을 막으면 안 됨
            return CheckResult(allowed=True, current_spend_usd=0, ...)

    def report(self, **kwargs) -> None:
        """비동기 fire-and-forget — 실제 호출 완료 후 백그라운드 전송."""
        asyncio.create_task(self._async_report(**kwargs))
```

#### TokenEstimator (core/estimator.py)
```python
class TokenEstimator:
    """
    Pre-call 토큰 추정. 실제 API 호출 전에 실행.
    추정값이므로 ±15% 오차 허용.
    """

    # tiktoken 인코더 캐시 (모델별 1회만 로딩)
    _encoders: dict[str, tiktoken.Encoding] = {}

    @classmethod
    def estimate_openai(cls, model: str, messages: list[dict]) -> int:
        """
        OpenAI 공식 토큰 카운팅 방식:
        messages 구조 오버헤드(4 tokens per message) + content tokens
        """
        enc = cls._get_encoder(model)
        token_count = 0
        for msg in messages:
            token_count += 4  # role + separators
            token_count += len(enc.encode(msg.get("content", "")))
        token_count += 2  # reply priming
        return token_count

    @classmethod
    def estimate_anthropic(cls, model: str, messages: list[dict]) -> int:
        """
        Anthropic은 tiktoken cl100k_base로 근사치 계산.
        실제 claude tokenizer는 비공개 — 오차 약 ±10%.
        """
        enc = tiktoken.get_encoding("cl100k_base")
        return sum(len(enc.encode(m.get("content", ""))) for m in messages)

    @classmethod
    def estimate_google(cls, model: str, contents: list) -> int:
        """
        Google Gemini: cl100k_base 근사 + 멀티모달 보정 계수 적용.
        텍스트만 있을 때 오차 ±15%.
        """
        enc = tiktoken.get_encoding("cl100k_base")
        total = 0
        for c in contents:
            if isinstance(c, str):
                total += len(enc.encode(c))
            elif isinstance(c, dict) and "text" in c:
                total += len(enc.encode(c["text"]))
        return total
```

#### LoopDetector (core/loop_detector.py)
```python
class LoopDetector:
    """
    에이전트 루프 감지: 동일 컨텍스트 해시가 N회 연속 → 루프 판정.
    세션 내 메모리에만 저장 (Redis 의존 없음 — SDK 오프라인 동작 보장).
    """
    LOOP_THRESHOLD = 10  # 동일 해시 10회 반복 = 루프
    WINDOW_SECONDS = 300  # 5분 내 반복만 카운트

    def __init__(self):
        self._counts: dict[str, list[float]] = {}  # hash -> [timestamps]

    def count(self, request_hash: str) -> int:
        """현재 해시의 윈도우 내 호출 횟수 반환."""
        now = time.time()
        window_start = now - self.WINDOW_SECONDS
        timestamps = self._counts.get(request_hash, [])
        # 윈도우 밖 타임스탬프 제거
        valid = [t for t in timestamps if t > window_start]
        valid.append(now)
        self._counts[request_hash] = valid
        return len(valid)

    def is_loop(self, request_hash: str) -> bool:
        return self.count(request_hash) >= self.LOOP_THRESHOLD
```

#### OpenAI 래퍼 (openai.py)
```python
class ChatCompletions:
    """openai.chat.completions를 그대로 대체하는 래퍼."""

    def create(self, model: str, messages: list, **kwargs):
        # 1. 토큰 추정
        estimated = TokenEstimator.estimate_openai(model, messages)

        # 2. 루프 감지
        req_hash = compute_hash(messages)
        if self._guard.loop_detector.is_loop(req_hash):
            raise LoopDetectedError(
                f"Loop detected: same context called "
                f"{self._guard.loop_detector.LOOP_THRESHOLD}+ times in 5 minutes"
            )

        # 3. 예산 체크 (동기 래퍼 — asyncio event loop 유무 모두 처리)
        result = self._guard.check_sync(
            model=model, provider="openai",
            messages=messages, estimated_tokens=estimated
        )

        if not result.allowed:
            if self._guard.on_exceed == "raise":
                raise BudgetExceededError(
                    current_usd=result.current_spend_usd,
                    budget_usd=result.budget_usd,
                    remaining_usd=result.remaining_usd,
                )
            elif self._guard.on_exceed == "warn":
                warnings.warn(f"Budget exceeded: ${result.current_spend_usd:.4f} / ${result.budget_usd}")

        # 4. 실제 API 호출
        response = self._original_client.chat.completions.create(
            model=model, messages=messages, **kwargs
        )

        # 5. 비동기 리포트 (fire-and-forget)
        self._guard.report(
            model=model, provider="openai",
            input_tokens=response.usage.prompt_tokens,
            output_tokens=response.usage.completion_tokens,
            cost_usd=calculate_cost("openai", model,
                                    response.usage.prompt_tokens,
                                    response.usage.completion_tokens),
            latency_ms=...,
            is_blocked=False,
            request_hash=req_hash,
        )
        return response
```

### 모델 단가 테이블 (utils/pricing.py)
```python
# 2026년 4월 기준. 주기적 업데이트 필요.
PRICING = {
    "openai": {
        "gpt-4o":             {"input": 2.50,  "output": 10.00},  # per 1M tokens
        "gpt-4o-mini":        {"input": 0.15,  "output": 0.60},
        "o1":                 {"input": 15.00, "output": 60.00},
        "o3-mini":            {"input": 1.10,  "output": 4.40},
    },
    "anthropic": {
        "claude-3-5-sonnet-20241022": {"input": 3.00, "output": 15.00},
        "claude-3-5-haiku-20241022":  {"input": 0.80, "output": 4.00},
        "claude-opus-4-5":            {"input": 15.00, "output": 75.00},
    },
    "google": {
        "gemini-2.0-flash":   {"input": 0.10,  "output": 0.40},
        "gemini-2.5-pro":     {"input": 1.25,  "output": 10.00},
    },
}

def calculate_cost(provider: str, model: str,
                   input_tokens: int, output_tokens: int) -> float:
    p = PRICING.get(provider, {}).get(model)
    if not p:
        return 0.0  # 알 수 없는 모델 — 0 처리 (과금 미스보다 차단 미스가 낫다)
    return (input_tokens * p["input"] + output_tokens * p["output"]) / 1_000_000
```

### BudgetExceededError
```python
class BudgetExceededError(Exception):
    def __init__(self, current_usd: float, budget_usd: float, remaining_usd: float):
        self.current_usd = current_usd
        self.budget_usd = budget_usd
        self.remaining_usd = remaining_usd
        super().__init__(
            f"LLM budget exceeded: ${current_usd:.4f} spent "
            f"(budget: ${budget_usd:.2f}, remaining: ${remaining_usd:.4f})"
        )
```

---

## 5. Engineering Rules

### 코딩 컨벤션

**FE (Next.js)**
1. Server Component 기본값. `'use client'`는 인터랙션이 있는 leaf 컴포넌트에만.
2. 데이터 페칭은 Server Component에서 직접. 대시보드 실시간 데이터만 Supabase Realtime 구독.
3. API 호출 결과 타입은 `zod` 스키마로 파싱 후 사용. `as any` 절대 금지.
4. 컴포넌트 파일명: PascalCase. 유틸/훅: camelCase.
5. `app/api/` 라우트는 반드시 try-catch + 통일된 에러 응답 형식 반환.
6. 환경변수는 `lib/env.ts`에서 zod로 검증 후 export. 컴포넌트에서 `process.env` 직접 접근 금지.
7. Supabase 클라이언트는 `lib/supabase/server.ts`와 `lib/supabase/client.ts` 두 파일에서만 초기화.

**BE (API Routes)**
1. 인증 미들웨어(`middleware.ts`)로 `/api/` 전체 보호. `/api/sdk/*`는 별도 API Key 검증.
2. SDK API (`/api/v1/sdk/*`)는 응답 시간 p99 < 50ms 목표. Redis 조회 1회 + DB write 비동기.
3. Stripe Webhook은 `stripe.webhooks.constructEvent`로 서명 검증 필수. 미검증 요청 즉시 400 반환.
4. DB 쿼리는 Supabase JS SDK만 사용. Raw SQL은 DB Function으로 캡슐화.
5. `/api/v1/sdk/check`는 서킷브레이커 패턴 적용: 연속 5회 DB 오류 시 60초간 allow-through 모드 전환 (서비스 장애가 고객 LLM 중단으로 이어지면 안 됨).

**Python SDK**
1. 외부 의존성 최소화: `httpx`, `tiktoken`만 필수. anthropic/openai/google은 optional.
2. 동기/비동기 모두 지원: `create()` 동기, `acreate()` 비동기 버전 각각 구현.
3. SDK 타임아웃 2초 초과 시 반드시 allow-through. 절대 원본 LLM 호출을 막지 않는 것이 우선.
4. 단가 테이블은 패키지 업데이트 없이 갱신 가능하도록 CDN JSON fallback 구현 (Month 2).
5. `LLMGUARD_KEY` 환경변수 지원: 코드에 키 하드코딩 방지.

**보안 규칙**
1. API Key 원본은 발급 시 1회만 응답. DB에는 bcrypt 해시만 저장.
2. LLM Provider API Key (sk-, claude-, AIza- 등)는 절대 서버로 전송하지 않음. SDK는 클라이언트 사이드 프로세스에서만 실행.
3. Slack Webhook URL은 DB에 암호화 저장 (Supabase Vault 또는 AES-256 + 서버 키).
4. 모든 API 응답에 `requestId` 포함. 디버깅 추적 가능하게.
5. `console.log`는 프로덕션 코드에서 금지. 로깅은 `lib/logger.ts` (Vercel 로그 연동) 사용.
6. CORS: `Access-Control-Allow-Origin`은 `https://llm-guard.com`만. `*` 절대 금지.

**성능 목표**
| 지표 | 목표 |
|------|------|
| SDK pre-call check p99 | < 50ms (Redis 캐시 포함) |
| SDK 오버헤드 (check + report) | p99 < 10ms 추가 레이턴시 |
| 대시보드 페이지 LCP | < 2.5s |
| Realtime 차트 업데이트 지연 | < 1초 |
| API Routes cold start | < 500ms (Vercel Fluid Compute 활용) |

---

## 6. 리스크 & 제약

### OpenAI ToS 리스크
- **리스크:** OpenAI ToS 섹션 3 "Restrictions" — "reverse engineer, decompile, or work around technical limitations" 조항.
- **판단:** llm-guard는 프록시가 아니라 클라이언트 사이드 래퍼. OpenAI Python 패키지를 그대로 감싸고 API를 직접 호출. 중간에서 트래픽을 가로채지 않음. **ToS 위반 아님.**
- **예방:** README와 문서에 "클라이언트 사이드 SDK 래퍼. OpenAI API를 직접 호출. 프록시 없음."을 명시.
- **에스컬레이션:** 법적 이슈 발생 시 플랜 B로 LangChain 콜백 기반 구현으로 전환 가능 (동일 기능, 다른 래핑 방식).

### Supabase Free Tier 제약
- **제약:** DB 500MB, 프로젝트 2개, Realtime 200 concurrent connections, 월 50만 row reads.
- **베타 10명 기준 계산:**
  - 사용자당 하루 100회 LLM 호출 가정 → 10명 * 30일 * 100회 = 300만 rows/월
  - **월 50만 row reads 초과 가능.** usage_logs 조회를 budgets 집계 캐시로 최소화 필수.
  - DB 500MB: row당 약 200bytes * 300만 = 600MB → **초과 가능**
  - **해결:** 90일 이상 된 usage_logs 자동 파티션 삭제 또는 Pro ($25/월) 전환 준비.
- **베타 초기 대응:** usage_logs 보관 기간 30일로 제한. 30일 지난 로그는 집계 후 삭제.

### Upstash Redis 제약
- **제약:** Free tier 10,000 commands/일. 베타 10명 * 100회 호출 * 2 commands = 2,000/일 → 충분.
- **Pro 이후:** 사용자 증가 시 Pay-per-use ($0.2/10만 commands) 전환.

### 멀티테넌트 격리 리스크
- **리스크:** RLS 정책 누락 시 타 유저 데이터 노출.
- **해결:** 모든 테이블에 RLS 활성화 + 정책 명시. `SECURITY DEFINER` 함수는 최소화.
- **테스트:** 베타 배포 전 E2E 테스트에서 A 유저 토큰으로 B 유저 리소스 접근 시도 케이스 반드시 포함.

### SDK 타이밍 어택 리스크
- **리스크:** API Key 해시 검증 시간이 일정하지 않으면 timing attack으로 유효 키 추론 가능.
- **해결:** `hmac.compare_digest()` 사용 (상수 시간 비교). `==` 연산자 사용 금지.

### 단가 테이블 구식화 리스크
- **리스크:** LLM 제공사가 가격 변경 시 SDK 업데이트 필요 → 사용자가 업데이트 안 하면 과소 차단.
- **해결 (MVP):** 패키지 버전 업데이트로 대응.
- **해결 (Month 2):** SDK 초기화 시 `https://llm-guard.com/api/pricing.json` 조회 → 캐시 1시간. 장애 시 로컬 테이블 fallback.

### 알림 발송 실패 리스크
- **리스크:** Slack Webhook / SendGrid 장애 시 알림 미발송.
- **해결:** 알림 발송을 Vercel Cron Job으로 분리. `last_fired_at` 기록으로 중복 발송 방지. 실패 시 3회 재시도 (exponential backoff).

---

## 7. 시스템 아키텍처 다이어그램

```
[Python SDK — 사용자 로컬]
  llm_guard.openai.OpenAI
        |
        | 1. POST /api/v1/sdk/check (X-LLM-Guard-Key)
        v
[Vercel Edge Middleware]  ← API Key 유효성 1차 검증
        |
        v
[Next.js API Route /api/v1/sdk/check]
        |
        |-- GET budgets (Upstash Redis 캐시, TTL 30s)
        |     └── Cache miss → Supabase budgets 테이블 조회
        |
        |-- 허용 여부 계산
        |
        v
  응답: {allowed, current_spend_usd, remaining_usd}
        |
        | (허용 시) 실제 openai.OpenAI().chat.completions.create() 호출
        |
        | 2. POST /api/v1/sdk/report (비동기, fire-and-forget)
        v
[Next.js API Route /api/v1/sdk/report]
        |
        |-- INSERT usage_logs (Supabase)
        |-- UPDATE budgets.spent_usd += cost_usd
        |-- INVALIDATE Redis cache (project budgets)
        |-- CHECK alert thresholds → Vercel Queue → Slack/SendGrid
        v

[Supabase Realtime CDC]
        |
        | usage_logs INSERT 이벤트
        v
[브라우저 대시보드]
  Recharts 실시간 차트 업데이트
```

---

## 8. Week별 우선순위 (기술 관점)

| Week | 기술 태스크 | 완료 기준 |
|------|------------|---------|
| 1 | Python SDK 코어 (openai 래퍼 + check/report API + Supabase 스키마) | `pip install llm-guard` 후 BudgetExceededError 발생 확인 |
| 2 | 랜딩페이지 + 대시보드 로그인 + Realtime 차트 + Slack 알림 | 브라우저에서 실시간 비용 증가 확인 |
| 3 | Anthropic/Google 래퍼 + 베타 10명 온보딩 + 버그 수정 | 3종 LLM 모두 차단 동작 확인 |
| 4 | Stripe 결제 + Pro 플랜 제한 + 루프 감지 고도화 | 카드 결제 후 Pro 기능 활성화 확인 |
| 5-6 | 안정화 + 단가 테이블 CDN fallback + Supabase Pro 전환 준비 | p99 < 50ms 달성 확인 |

---

## CDO에게 요청

1. **Empty State 우선 설계 필수**: 대시보드 최초 진입 시 데이터 없음 → "첫 API 키 발급하기" CTA가 핵심 전환 포인트. 이 화면을 가장 먼저 디자인해야 함.
2. **차단 이벤트 시각화**: 라인 차트에서 차단된 시점을 빨간 점(●)으로 표시. 단순 비용 그래프가 아니라 "막힌 사건"이 보여야 제품 가치가 전달됨.
3. **BudgetExceededError 터미널 출력 스타일**: 사용자가 처음 에러를 보는 순간이 제품 경험의 첫인상. 에러 메시지 포맷 디자인 필요 (색상 코드 포함).
4. **코드 비교 섹션**: Before/After 코드 블록의 diff 하이라이트 방식. 변경되는 1줄이 명확하게 강조돼야 함.

## CPO에게 피드백

1. **루프 감지 임계값 10회는 MVP에서 하드코딩**: 유저별 설정 가능하게 하면 구현 복잡도 급증. Week 3 베타 피드백 수집 후 Pro 기능으로 노출 여부 결정 권고.
2. **Free 플랜 OpenAI 전용 제한은 기술적으로 강제 가능**: API Key 검증 시 플랜 체크 + 403 반환. 단, 이 제한이 전환율에 미치는 영향은 베타 후 데이터 보고 판단 권고.
3. **SDK report API는 fire-and-forget**: 실패해도 원본 LLM 응답은 반환됨. 즉, 극히 드물게 비용이 기록 안 될 수 있음. 이는 의도된 트레이드오프 (사용자 UX > 정확한 집계). PRD에 명시 권고.
4. **`reset_day` 커스텀**: 월 예산 리셋일을 1일 고정으로 하면 구현 단순. 커스텀이 필요한지 베타 전에 확인 필요. 현재 스키마에는 컬럼 있으나 MVP에서는 1일 고정 권고.
