# Wave 3 — CTO 기술 설계 (Lian Dash)

작성일: 2026-04-02  
프로젝트: 인하우스 마케터·프리랜서를 위한 통합 마케팅 데이터 분석 SaaS

---

## 1. 기술 스택 확정

### Frontend

| 항목 | 선택 | 버전 | 비고 |
|------|------|------|------|
| Framework | Next.js (App Router) | 14.2.x | SSR + RSC 혼용 |
| UI 컴포넌트 | shadcn/ui + Tailwind CSS | Tailwind 3.4.x | 앱 내부 전용 |
| 차트 | Recharts | 2.12.x | 대시보드 전용 |
| 상태 관리 | Zustand | 4.5.x | 클라이언트 전역 상태 |
| 서버 데이터 패칭 | TanStack Query (React Query) | 5.x | 채널 데이터 캐싱 |
| **3D 랜딩 (신규)** | Three.js | 0.164.x | 랜딩페이지 전용 |
| **3D React 바인딩 (신규)** | @react-three/fiber | 8.x | Three.js React 래퍼 |
| **3D 헬퍼 (신규)** | @react-three/drei | 9.x | OrbitControls, Float, Particles 등 |
| **스크롤 애니메이션 (신규)** | @react-spring/three | 9.x | 스크롤 연동 3D 트랜지션 |

### Backend

| 항목 | 선택 | 버전 | 비고 |
|------|------|------|------|
| Framework | Next.js API Routes | 14.2.x | App Router Route Handlers |
| Database | PostgreSQL | 16.x | Supabase 또는 Railway 권장 |
| ORM | Prisma | 5.14.x | Type-safe 쿼리 |
| 인증 | NextAuth.js v5 (Auth.js) | 5.0.x | 이메일 + Google OAuth |
| 결제 | Stripe | stripe Node 15.x | 구독 + 웹훅 |
| AI 인사이트 | OpenAI GPT-4o API | gpt-4o | 자체 모델 절대 금지 |
| 파일 스토리지 | Vercel Blob 또는 S3 | — | 리포트 PDF 저장 (2차) |
| 배포 | Vercel | — | Edge Runtime 활용 |

---

## 2. DB 스키마

### User
```prisma
model User {
  id            String      @id @default(cuid())
  email         String      @unique
  name          String?
  image         String?
  emailVerified DateTime?
  createdAt     DateTime    @default(now())
  updatedAt     DateTime    @updatedAt

  // 구독 상태
  stripeCustomerId     String?   @unique
  stripeSubscriptionId String?   @unique
  planStatus           PlanStatus @default(TRIAL)
  trialStartedAt       DateTime  @default(now())
  planActivatedAt      DateTime?

  accounts      Account[]
  sessions      Session[]
  workspaces    Workspace[]
  insightLogs   InsightLog[]
  usageLogs     UsageLog[]
}

enum PlanStatus {
  TRIAL      // 14일 무료체험
  ACTIVE     // 결제 완료
  EXPIRED    // 체험 만료, 미결제
  CANCELLED  // 해지
}
```

### Workspace
```prisma
model Workspace {
  id          String   @id @default(cuid())
  name        String
  userId      String
  createdAt   DateTime @default(now())
  updatedAt   DateTime @updatedAt

  user         User          @relation(fields: [userId], references: [id], onDelete: Cascade)
  integrations Integration[]
  insightLogs  InsightLog[]

  // 멀티 워크스페이스 대비 설계 (2차 릴리즈)
  // members   WorkspaceMember[]
}
```

### Integration
```prisma
model Integration {
  id           String          @id @default(cuid())
  workspaceId  String
  channel      ChannelType
  status       IntegrationStatus @default(CONNECTED)
  accessToken  String?         // 암호화 저장 필수
  refreshToken String?         // 암호화 저장 필수
  tokenExpiry  DateTime?
  accountId    String?         // 채널별 계정 ID (GA4 Property ID 등)
  accountName  String?
  createdAt    DateTime        @default(now())
  updatedAt    DateTime        @updatedAt

  workspace    Workspace       @relation(fields: [workspaceId], references: [id], onDelete: Cascade)
  usageLogs    UsageLog[]

  @@unique([workspaceId, channel])
}

enum ChannelType {
  GA4
  META
  NAVER_SA
  // KAKAO_MOMENT  // 2차
  // GOOGLE_ADS    // 2차
}

enum IntegrationStatus {
  CONNECTED
  DISCONNECTED
  ERROR
  MOCK  // 네이버SA PoC 전 Mock 상태
}
```

### InsightLog
```prisma
model InsightLog {
  id          String   @id @default(cuid())
  workspaceId String
  userId      String
  content     String   @db.Text  // GPT-4o 응답 전문
  inputTokens Int
  outputTokens Int
  createdAt   DateTime @default(now())

  workspace   Workspace @relation(fields: [workspaceId], references: [id], onDelete: Cascade)
  user        User      @relation(fields: [userId], references: [id], onDelete: Cascade)

  // 월 10회 제한 체크: WHERE userId = ? AND createdAt >= 이번달 1일
}
```

### UsageLog
```prisma
model UsageLog {
  id            String      @id @default(cuid())
  userId        String
  integrationId String?
  logType       UsageLogType
  channel       ChannelType?
  apiCalls      Int         @default(1)
  tokensUsed    Int?        // OpenAI 전용
  costEstimate  Float?      // USD 추정 비용
  createdAt     DateTime    @default(now())

  user          User        @relation(fields: [userId], references: [id], onDelete: Cascade)
  integration   Integration? @relation(fields: [integrationId], references: [id])
}

enum UsageLogType {
  CHANNEL_API_CALL   // GA4/메타/네이버SA API 호출
  AI_INSIGHT         // GPT-4o 인사이트 생성
}
```

---

## 3. API 구조

### 채널 연동 API

```
POST   /api/integrations/ga4/connect        — GA4 OAuth 시작
GET    /api/integrations/ga4/callback       — GA4 OAuth 콜백 + 토큰 저장
DELETE /api/integrations/ga4/disconnect     — 연동 해제

POST   /api/integrations/meta/connect       — 메타 OAuth 시작
GET    /api/integrations/meta/callback      — 메타 OAuth 콜백
DELETE /api/integrations/meta/disconnect

POST   /api/integrations/naver/connect      — 네이버SA API Key 저장 (OAuth 미지원)
DELETE /api/integrations/naver/disconnect
```

### 대시보드 데이터 조회 API

```
GET /api/dashboard/summary
  — 3채널 KPI 통합 요약 (sessions, impressions, clicks, conversions, ROAS)
  — Query: workspaceId, dateRange (7d/30d/custom)
  — 각 채널 모듈 독립 호출 → 병렬 Promise.all → 통합 응답

GET /api/channels/ga4/metrics
  — Sessions, Users, Bounce Rate, Goal Completions
  — Query: workspaceId, startDate, endDate, dimensions[]

GET /api/channels/meta/metrics
  — Impressions, Clicks, CTR, CPC, ROAS, Spend
  — Query: workspaceId, startDate, endDate

GET /api/channels/naver/metrics
  — Impressions, Clicks, CTR, CPC, Conversions
  — Mock 폴백: Integration.status === 'MOCK' 시 Mock 데이터 반환
```

### AI 인사이트 생성 API

```
POST /api/insights/generate
  — Body: { workspaceId }
  — 사전 체크: 이번달 InsightLog 수 >= 10 → 429 반환
  — 3채널 최근 7일 데이터 수집 → GPT-4o 프롬프트 구성
  — 응답: { insights: string[], inputTokens: number, outputTokens: number }
  — 완료 후 InsightLog + UsageLog 저장

GET /api/insights/history
  — Query: workspaceId, limit (default 10)
  — 이번달 사용 횟수 포함 반환
```

### Stripe 웹훅

```
POST /api/webhooks/stripe
  — customer.subscription.created   → User.planStatus = ACTIVE, planActivatedAt 기록
  — customer.subscription.deleted   → User.planStatus = CANCELLED
  — invoice.payment_failed          → User.planStatus = EXPIRED
  — invoice.paid                    → planStatus EXPIRED → ACTIVE 복구
```

### 인증/결제 기타

```
POST /api/auth/[...nextauth]        — NextAuth 핸들러
GET  /api/billing/portal            — Stripe Customer Portal URL 반환
POST /api/billing/checkout          — Stripe Checkout Session 생성
GET  /api/workspaces/current        — 현재 워크스페이스 정보
```

---

## 4. Engineering Rules (FE/BE 공통 준수)

### 아키텍처 원칙
- **채널 모듈 독립성**: GA4 / 메타 / 네이버SA 각 연동 로직은 `/lib/channels/ga4.ts`, `/lib/channels/meta.ts`, `/lib/channels/naver.ts`로 완전 분리. 공통 인터페이스 `ChannelAdapter` 구현 필수
- **Mock 폴백 표준화**: 모든 채널 모듈에 `getMockData()` 메서드 필수 구현. `NAVER_MOCK=true` 환경변수로 제어
- **토큰 암호화**: DB에 저장되는 accessToken/refreshToken은 반드시 AES-256 암호화 (crypto-js 또는 Node.js crypto)
- **API Route 인증 미들웨어**: 모든 `/api/dashboard/*`, `/api/insights/*`, `/api/channels/*`는 세션 검증 + trial 만료 체크 미들웨어 적용

### FE 규칙
- **App Router 원칙**: 서버 컴포넌트 기본. 인터랙션 필요한 경우만 `'use client'` 선언
- **3D 컴포넌트 격리**: Three.js 관련 코드는 `/components/3d/` 폴더에만. 앱 내부 라우트에서 import 절대 금지 (번들 사이즈 보호)
- **shadcn 컴포넌트**: 커스텀 스타일링보다 shadcn 기본 컴포넌트 우선 사용. 필요 시 variants 확장
- **에러 바운더리**: 각 채널 상세 화면에 Error Boundary 필수 (채널 API 장애 시 앱 전체 다운 방지)
- **로딩 스켈레톤**: 모든 데이터 패칭 구간에 Skeleton UI 구현 (Suspense + loading.tsx)

### BE 규칙
- **Rate Limit**: AI 인사이트 API에 월 10회 제한 체크를 DB 레벨(InsightLog count)과 미들웨어 2중 적용
- **14일 차단 미들웨어**: `trialStartedAt + 14일 < now() && planStatus !== ACTIVE` → 403 반환. `/api/dashboard/*` 전체 적용
- **비용 추정 로깅**: OpenAI API 호출 시 inputTokens × $0.005/1K + outputTokens × $0.015/1K 추정값 UsageLog에 기록
- **환경변수 필수 목록**: `DATABASE_URL`, `NEXTAUTH_SECRET`, `NEXTAUTH_URL`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `META_APP_ID`, `META_APP_SECRET`, `NAVER_SA_CLIENT_ID`, `NAVER_SA_SECRET`, `OPENAI_API_KEY`, `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `ENCRYPTION_KEY`

---

## 5. 리스크 및 완화 전략

### R1. 네이버SA API 미검증 [심각도: 높음]
- **리스크**: 네이버 검색광고 API는 공식 파트너십 심사 필요. 개인 개발자 접근이 제한될 수 있음
- **완화**: MVP에서 Mock 데이터로 UI/UX 완성. PoC 병행 진행. Integration.status = 'MOCK' 플래그로 사용자에게 "연동 준비 중" 표시
- **폴백**: PoC 실패 시 2차 릴리즈로 이동, MVP는 GA4+메타 2채널로 축소

### R2. Stripe 결제 차단 미들웨어 구멍 [심각도: 높음]
- **리스크**: 미들웨어 우회, 클라이언트 조작으로 무료 사용 지속 가능성
- **완화**: 차단 로직을 서버사이드(Route Handler 미들웨어)에만 구현. 클라이언트 상태로 판단 금지. Stripe 웹훅으로 planStatus 실시간 동기화

### R3. AI 비용 폭증 [심각도: 중간]
- **리스크**: 월 10회 제한 버그 시 GPT-4o 호출 무제한 발생
- **완화**: DB 레벨 카운트 + 미들웨어 2중 차단. OpenAI API에 max_tokens: 800 하드캡. UsageLog 기반 월간 비용 대시보드 내부 운영

### R4. OAuth 토큰 만료 [심각도: 중간]
- **리스크**: GA4/메타 accessToken 만료 시 데이터 수집 중단
- **완화**: refreshToken 자동 갱신 로직 각 채널 모듈에 구현. 갱신 실패 시 Integration.status = 'ERROR' + 사용자 재연동 안내

### R5. 3D 랜딩 성능 [심각도: 낮음]
- **리스크**: Three.js 번들이 앱 전체 초기 로드를 늦춤
- **완화**: 3D 컴포넌트 dynamic import + `{ ssr: false }`. 랜딩페이지와 앱 내부 라우트 번들 완전 분리
