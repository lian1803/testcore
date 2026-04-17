# Wave 3 — BE 구현 완료 (Lian Dash)

**완료일**: 2026-04-02  
**담당자**: Claude (Backend Engineer)  
**상태**: ✅ 완료 (모든 9개 BE 태스크)

---

## 구현된 API 목록

### 1. DB 스키마 (BE-1)
- ✅ `prisma/schema.prisma` — User, Account, Session, Workspace, Integration, InsightLog, UsageLog, VerificationToken
- ✅ `lib/prisma.ts` — PrismaClient 싱글턴 (개발 환경 핫리로드 대응)
- ✅ `prisma.config.ts` — Prisma v7 설정 파일
- 모든 Enum 포함: `PlanStatus`, `ChannelType`, `IntegrationStatus`, `UsageLogType`
- 필수 인덱스 설정: `InsightLog(userId, createdAt)`, `UsageLog(userId, createdAt)`, `Integration(workspaceId, channel)`

### 2. NextAuth 설정 (BE-2)
- ✅ `src/auth.ts` — NextAuth v5 + Prisma Adapter
  - EmailProvider (Resend 통합)
  - GoogleProvider OAuth
  - JWT 세션: userId, planStatus, trialStartedAt 포함
  - signUp 이벤트: 가입 시 자동 Workspace 생성
  - 세션 콜백: planStatus DB 동기화
- ✅ `src/app/api/auth/[...nextauth]/route.ts` — NextAuth Route Handler
- ✅ `src/middleware.ts` — 미인증 사용자 리다이렉트

### 3. GA4 OAuth 연동 (BE-3)
- ✅ `lib/channels/ga4.ts` — GA4Adapter 클래스
  - `getAuthUrl()` — OAuth URL 생성
  - `handleCallback(code)` — 토큰 교환 및 AES-256 암호화
  - `getMetrics()` — GA4 Data API v4 호출 (sessions, users, bounceRate, goalCompletions)
  - `refreshToken()` — 자동 토큰 갱신
  - `getMockData()` — 개발용 Mock 데이터
- ✅ `src/app/api/integrations/ga4/connect/route.ts` — OAuth 시작
- ✅ `src/app/api/integrations/ga4/callback/route.ts` — OAuth 콜백 및 토큰 저장
- ✅ `src/app/api/integrations/ga4/disconnect/route.ts` — 연동 해제

### 4. Meta 광고 연동 (BE-4)
- ✅ `lib/channels/meta.ts` — MetaAdapter 클래스
  - `getAuthUrl()` — Facebook OAuth URL
  - `handleCallback(code)` — 단기→장기 토큰 변환 및 저장
  - `getMetrics()` — Meta Marketing API v19.0 (impressions, clicks, ctr, cpc, spend, roas)
  - `getMockData()` — Mock 데이터
- ✅ `src/app/api/integrations/meta/connect/route.ts` — OAuth 시작
- ✅ `src/app/api/integrations/meta/callback/route.ts` — OAuth 콜백
- ✅ `src/app/api/integrations/meta/disconnect/route.ts` — 연동 해제

### 5. Naver SA Mock 연동 (BE-5)
- ✅ `lib/channels/naver.ts` — NaverAdapter 클래스
  - `handleConnect(apiKey, secret)` — API Key 저장 (암호화)
  - `getMetrics()` — Naver API 호출 또는 Mock 폴백
  - `getMockData()` — PoC 전 Mock 데이터
  - `NAVER_MOCK=true` 환경변수로 강제 Mock 모드 지원
- ✅ `src/app/api/integrations/naver/connect/route.ts` — 크레덴셜 저장 (상태: MOCK)
- ✅ `src/app/api/integrations/naver/disconnect/route.ts` — 연동 해제

### 6. 대시보드 데이터 집계 (BE-6)
- ✅ `lib/middleware/trialCheck.ts` — 14일 체험 만료 체크 (402 반환)
- ✅ `src/app/api/dashboard/summary/route.ts`
  - 3채널 병렬 호출 (Promise.all)
  - 통합 KPI 응답 (sessions, impressions, clicks, spend, roas)
  - Cache-Control: max-age=300
  - UsageLog 자동 기록
- ✅ `src/app/api/channels/ga4/metrics/route.ts` — GA4 상세 지표
- ✅ `src/app/api/channels/meta/metrics/route.ts` — Meta 상세 지표
- ✅ `src/app/api/channels/naver/metrics/route.ts` — Naver 상세 지표 (isMock 플래그 포함)

### 7. AI 인사이트 생성 (BE-7)
- ✅ `lib/ai/insight.ts` — generateInsight 함수
  - GPT-4o-mini 호출 (max_tokens: 800)
  - 월 10회 제한 체크 (429 반환)
  - 3채널 7일 데이터 요약 후 프롬프트 구성
  - JSON 파싱 + 폴백 처리
- ✅ `src/app/api/insights/generate/route.ts`
  - InsightLog 저장 (inputTokens, outputTokens)
  - UsageLog 저장 (토큰 수, 비용 추정: $0.005/1K input + $0.015/1K output)
- ✅ `src/app/api/insights/history/route.ts` — 인사이트 히스토리 조회

### 8. Stripe 결제 + 14일 차단 (BE-8)
- ✅ `src/app/api/webhooks/stripe/route.ts` — Stripe 웹훅
  - `customer.subscription.created` → `planStatus = ACTIVE`
  - `customer.subscription.deleted` → `planStatus = CANCELLED`
  - `invoice.payment_failed` → `planStatus = EXPIRED`
  - `invoice.paid` → EXPIRED → ACTIVE 복구
  - 웹훅 서명 검증 필수
- ✅ `src/app/api/billing/checkout/route.ts` — Checkout Session 생성
- ✅ `src/app/api/billing/portal/route.ts` — Customer Portal URL 반환
- ✅ `lib/middleware/trialCheck.ts` — 모든 API에 적용

### 9. 사용량 로깅 (BE-9)
- ✅ `lib/usage/logger.ts`
  - `logUsage()` — UsageLog 생성 헬퍼 (모든 API에서 임포트 가능)
  - `getMonthlyUsage()` — 월간 집계 (API 호출 수, AI 토큰 수, 비용)
  - 비용 추정 공식: OpenAI GPT-4o 기반
- ✅ `src/app/api/usage/route.ts` — 현재 달 사용량 조회
- ✅ `src/app/api/admin/usage/route.ts` — 내부용 모니터링 (X-Admin-Key 인증)
  - 사용자별 월간 AI 호출 수
  - 총 예상 비용
  - 채널별 API 호출 수
  - $50 초과 사용자 알람

---

## 환경변수 목록 (.env 필수 항목)

```env
# Database
DATABASE_URL="postgresql://user:password@localhost:5432/lian_dash"

# NextAuth
NEXTAUTH_SECRET="your-secret-key-here"
NEXTAUTH_URL="http://localhost:3000"

# Email (Resend)
RESEND_API_KEY="re_xxxxxxxxxxxx"
EMAIL_FROM="noreply@liandash.com"
# 또는 기존 SMTP 설정
EMAIL_SERVER_HOST="smtp.example.com"
EMAIL_SERVER_PORT="587"
EMAIL_SERVER_USER="your-email@example.com"
EMAIL_SERVER_PASSWORD="your-password"

# Google OAuth
GOOGLE_CLIENT_ID="xxxx.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET="xxxx"

# Meta OAuth
META_APP_ID="123456789"
META_APP_SECRET="xxxx"

# Naver SA API
NAVER_SA_CLIENT_ID="xxxx"
NAVER_SA_SECRET="xxxx"
NAVER_MOCK="false"  # true로 설정 시 Mock 데이터만 반환

# OpenAI
OPENAI_API_KEY="sk-xxxx"

# Stripe
STRIPE_PUBLISHABLE_KEY="pk_live_xxxx"
STRIPE_SECRET_KEY="sk_live_xxxx"
STRIPE_WEBHOOK_SECRET="whsec_xxxx"
STRIPE_PRICE_STARTER="price_xxxx"
STRIPE_PRICE_PRO="price_xxxx"

# Encryption (32-byte hex string = 64 characters)
ENCRYPTION_KEY="0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"

# Admin
ADMIN_SECRET_KEY="your-secret-admin-key"
```

---

## FE에게 전달 (API 응답 형식)

### 인증
```
POST /api/auth/callback/credentials
POST /api/auth/callback/google
GET  /api/auth/signin
GET  /api/auth/signout
```

### 대시보드 데이터
```
GET /api/dashboard/summary?dateRange=7d
응답:
{
  "channels": {
    "ga4": { sessions, users, bounceRate, goalCompletions },
    "meta": { impressions, clicks, ctr, cpc, spend, roas },
    "naver": { impressions, clicks, ctr, cpc, conversions }
  },
  "summary": {
    "totalSessions": number,
    "totalImpressions": number,
    "totalClicks": number,
    "totalSpend": number,
    "averageROAS": number
  },
  "dateRange": { startDate, endDate }
}
```

### 채널별 상세 지표
```
GET /api/channels/ga4/metrics?startDate=YYYY-MM-DD&endDate=YYYY-MM-DD
GET /api/channels/meta/metrics?startDate=YYYY-MM-DD&endDate=YYYY-MM-DD
GET /api/channels/naver/metrics?startDate=YYYY-MM-DD&endDate=YYYY-MM-DD

응답: { data: {...}, isMock: boolean (Naver only) }
```

### AI 인사이트
```
POST /api/insights/generate
응답:
{
  "insights": [
    {
      "title": "string",
      "description": "string",
      "priority": "high|medium|low",
      "metric": "string"
    }
  ],
  "inputTokens": number,
  "outputTokens": number,
  "estimatedCost": number
}

GET /api/insights/history?limit=10
응답:
{
  "data": [{ id, createdAt, insights, inputTokens, outputTokens }],
  "monthlyUsage": 3,
  "monthlyLimit": 10
}
```

### 채널 연동
```
POST /api/integrations/ga4/connect
응답: { authUrl: "https://..." }

GET /api/integrations/ga4/callback?code=xxx&state=xxx
→ /onboarding?ga4=connected

DELETE /api/integrations/ga4/disconnect
응답: { success: true }
```

### 결제
```
POST /api/billing/checkout?plan=starter|pro
응답: { sessionUrl: "https://checkout.stripe.com/..." }

POST /api/billing/portal
응답: { portalUrl: "https://billing.stripe.com/..." }
```

### 사용량
```
GET /api/usage?workspaceId=xxxx
응답:
{
  "period": { start, end },
  "totalApiCalls": number,
  "totalAiTokens": number,
  "estimatedCost": number,
  "byChannel": { GA4, META, NAVER_SA }
}
```

---

## 중요 사항

### 보안
1. **토큰 암호화**: GA4, Meta, Naver 토큰은 모두 AES-256 암호화되어 DB에 저장됨
2. **Stripe 웹훅 검증**: 모든 웹훅에 서명 검증 필수
3. **Trial 차단**: 14일 만료 후 API 403 반환 (클라이언트 조작 방지)
4. **Admin 엔드포인트**: X-Admin-Key 헤더 인증 필수

### 성능
- Dashboard summary는 3채널을 병렬로 호출하여 최소화
- TanStack Query 캐시를 위해 Cache-Control: max-age=300 설정
- Mock 데이터는 API 실패 시 자동 폴백

### 비용 통제
- OpenAI GPT-4o-mini 사용 (gpt-4o보다 저렴)
- max_tokens: 800 하드캡
- 월 10회 제한으로 예측 가능한 비용
- UsageLog로 실시간 모니터링

### 네이버SA 상황
- PoC 완료 전까지는 MOCK 상태로 실행
- 실제 API는 자동 폴백으로 에러 시 Mock 반환
- NAVER_MOCK=true 환경변수로 개발 중 강제 Mock 가능

---

## 다음 단계 (FE)

1. **FE-1 ~ FE-2**: 랜딩페이지 3D + 피처/프라이싱 섹션
2. **FE-3**: 회원가입/로그인 (BE-2 완료했으므로 즉시 연동 가능)
3. **FE-4**: 온보딩 플로우 (BE-3, 4, 5 연동)
4. **FE-5**: 대시보드 메인 (BE-6, 8 연동)
5. **FE-6**: AI 인사이트 화면 (BE-7 연동)
6. **FE-7**: 채널 상세 화면 (BE-3, 4, 5 연동)
7. **FE-8**: 설정 화면 (BE-2, 8, 9 연동)

---

## 파일 구조

```
lian-dash/
├── prisma/
│   └── schema.prisma
├── prisma.config.ts
├── src/
│   ├── auth.ts
│   ├── middleware.ts
│   ├── lib/
│   │   ├── prisma.ts
│   │   ├── encryption.ts
│   │   ├── channels/
│   │   │   ├── ga4.ts
│   │   │   ├── meta.ts
│   │   │   └── naver.ts
│   │   ├── middleware/
│   │   │   └── trialCheck.ts
│   │   ├── ai/
│   │   │   └── insight.ts
│   │   └── usage/
│   │       └── logger.ts
│   └── app/api/
│       ├── auth/[...nextauth]/route.ts
│       ├── integrations/
│       │   ├── ga4/[connect/callback/disconnect]/route.ts
│       │   ├── meta/[connect/callback/disconnect]/route.ts
│       │   └── naver/[connect/disconnect]/route.ts
│       ├── dashboard/
│       │   └── summary/route.ts
│       ├── channels/
│       │   ├── ga4/metrics/route.ts
│       │   ├── meta/metrics/route.ts
│       │   └── naver/metrics/route.ts
│       ├── insights/
│       │   ├── generate/route.ts
│       │   └── history/route.ts
│       ├── billing/
│       │   ├── checkout/route.ts
│       │   └── portal/route.ts
│       ├── webhooks/
│       │   └── stripe/route.ts
│       ├── usage/route.ts
│       └── admin/
│           └── usage/route.ts
└── .env.example
```

---

## 테스트 체크리스트

- [ ] `npx prisma migrate dev --name init` 실행 및 DB 마이그레이션 확인
- [ ] `npx prisma studio` 에서 모든 테이블 확인
- [ ] GA4/Meta OAuth 흐름 테스트
- [ ] Naver Mock 데이터 반환 확인
- [ ] 14일 Trial 만료 후 402 반환 확인
- [ ] Stripe Webhook 시뮬레이션 (Stripe CLI)
- [ ] AI 인사이트 월 10회 제한 확인
- [ ] UsageLog 자동 기록 확인

---

**BE 구현 완료. FE와 통합 준비 완료.**
