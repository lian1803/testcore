# Wave 3 — PM 태스크 분해 (Lian Dash)

작성일: 2026-04-02  
기준: PRD Must Have + CLAUDE.md MVP 제약 + CTO 설계 (wave_cto.md)

---

## 구현 순서 원칙

1. BE 기반 먼저 (스키마 → 인증 → 채널 연동) → FE 연동
2. 채널 독립 모듈로 분리 — GA4 완성 후 메타, 네이버SA 순
3. 네이버SA는 Mock 폴백으로 병렬 진행
4. 결제/차단 미들웨어는 BE Task 8 완료 전에 어떤 대시보드도 프로덕션 배포 금지

---

## FE 태스크 (총 8개)

### FE-1. 랜딩페이지 3D 히어로 섹션
- **파일**: `app/(landing)/page.tsx`, `components/3d/Hero3D.tsx`, `components/3d/FloatingObject.tsx`, `components/3d/ParticleField.tsx`
- **작업 내용**:
  - Three.js + @react-three/fiber + @react-three/drei 설치 및 설정
  - `Hero3D` 컴포넌트: WebGL 캔버스 풀스크린, dynamic import + `{ ssr: false }`
  - `FloatingObject`: ChartCube (와이어프레임 정육면체), DataSphere (데이터 구체) — Float(drei) 사용
  - `ParticleField`: 500개 파티클, 숫자 텍스처, 랜덤 퍼플-블루 색상
  - ScrollControls(drei) 연동: 스크롤 시 카메라 후퇴 + 파티클 흩날림 애니메이션
  - CTA 오버레이 (HTML absolute): 타이틀 + 부제 + "무료로 시작하기" 글로우 버튼
  - 광원 3종: AmbientLight + PointLight × 2 (퍼플/블루)
- **완료 기준**: Hero 섹션 3D 렌더링 정상, 스크롤 반응 동작, LCP 3초 이내
- **의존성**: 없음 (독립 작업 가능)
- **주의**: Three.js 번들 반드시 dynamic import로 격리 — 앱 내부 JS 번들에 포함되면 안 됨

### FE-2. 랜딩 피처/프라이싱/CTA/푸터 섹션
- **파일**: `components/landing/FeatureCard.tsx`, `components/landing/PricingTable.tsx`, `components/landing/Footer.tsx`
- **작업 내용**:
  - Feature 섹션: 3열 그리드, 다크 카드, hover 보더 퍼플 glow
  - Pricing 섹션: 스타터(₩49,000) / 프로(₩99,000) 카드, Pro 카드 퍼플 테두리 + 인기 뱃지
  - 최하단 CTA 섹션: "지금 무료로 시작하세요" + 버튼
  - Footer: 서비스명, 이용약관, 개인정보처리방침 링크
  - 다크 배경 (#0A0A0F ~ #12121A) 일관 유지
- **완료 기준**: 랜딩페이지 전체 스크롤 완성, 반응형 (모바일 1열 / 태블릿 2열 / 데스크탑 3열)
- **의존성**: FE-1 완료 후 같은 페이지에 붙임

### FE-3. 회원가입/로그인 화면
- **파일**: `app/(auth)/signup/page.tsx`, `app/(auth)/login/page.tsx`, `components/auth/AuthForm.tsx`
- **작업 내용**:
  - 중앙 정렬 카드 레이아웃 (반다크 배경 → 앱 내부 라이트 전환 포인트)
  - 이메일 + 비밀번호 폼 (shadcn Input + Button)
  - "구글로 계속하기" 버튼 (Google OAuth)
  - 에러 메시지 표시 (NextAuth 에러 코드 → 한국어 변환)
  - 로그인 성공 → `/onboarding` 또는 `/dashboard` 리다이렉트 (통합 연동 여부에 따라)
- **완료 기준**: 이메일 가입, 구글 가입, 로그인 모두 동작
- **의존성**: BE-2 (NextAuth 설정) 완료 후 연동 가능

### FE-4. 온보딩 플로우 (3단계)
- **파일**: `app/(app)/onboarding/page.tsx`, `components/onboarding/StepProgress.tsx`, `components/onboarding/IntegrationConnect.tsx`, `components/onboarding/SuccessAnimation.tsx`
- **작업 내용**:
  - Step 1: 워크스페이스 이름 입력
  - Step 2: 채널 연동 선택 (GA4 / 메타 / 네이버SA 카드 3개, 각 "연결" 버튼)
  - Step 3: 연동 완료 요약 + "대시보드 시작" 버튼
  - `StepProgress`: 현재 단계 강조, 완료 단계 체크 표시
  - `IntegrationConnect`: 채널 로고 + 연결 상태 표시 (연결됨 / 연결 필요 / Mock)
  - `SuccessAnimation`: 채널 연동 성공 시 애니메이션 (CSS keyframes 또는 Lottie)
  - "나중에 설정" 스킵 링크 → 바로 대시보드
- **완료 기준**: 3단계 진행 정상, 최소 1채널 연동 후 대시보드 진입 가능
- **의존성**: BE-3 (GA4 연동 API) 완료 후 실제 연동 연결

### FE-5. 대시보드 메인 (KPI + 트렌드 차트)
- **파일**: `app/(app)/dashboard/page.tsx`, `components/dashboard/Sidebar.tsx`, `components/dashboard/MetricCard.tsx`, `components/dashboard/TrendChart.tsx`, `components/dashboard/ChannelTab.tsx`, `components/dashboard/TrialBanner.tsx`
- **작업 내용**:
  - `Sidebar`: 240px 고정, 다크 (#111827), 네비게이션 + 플랜 뱃지
  - `TrialBanner`: 14일 체험 D-Day 카운트다운 상단 배너 (EXPIRED 상태 시 결제 안내로 전환)
  - `DateRangePicker`: 7일/30일/커스텀 선택, shadcn Popover + Calendar 기반
  - `MetricCard` × 4~6개: 채널별 KPI (Sessions, Impressions, Clicks, ROAS, Conversions, Spend)
  - `TrendChart`: Recharts LineChart, 3채널 비교, 퍼플/파랑/초록 라인
  - `ChannelTab`: GA4 / 메타 / 네이버SA 탭 전환
  - Skeleton UI: 데이터 로딩 중 MetricCard + TrendChart 스켈레톤
  - TanStack Query로 `/api/dashboard/summary` 패칭, 5분 캐시
- **완료 기준**: 3채널 KPI 카드 표시, 트렌드 차트 동작, 날짜 범위 변경 시 데이터 갱신
- **의존성**: BE-6 (대시보드 데이터 집계 API), BE-8 (차단 미들웨어)

### FE-6. AI 인사이트 화면
- **파일**: `app/(app)/dashboard/insights/page.tsx`, `components/insights/InsightGenerator.tsx`, `components/insights/InsightCard.tsx`, `components/insights/InsightHistory.tsx`, `components/insights/UsageBar.tsx`
- **작업 내용**:
  - `UsageBar`: 이번달 사용량 프로그레스 바 (예: 3/10회 사용)
  - `InsightGenerator`: "인사이트 생성하기" 버튼, 로딩 상태 (AI 분석 중... 스피너), 10회 도달 시 비활성화 + 업그레이드 CTA
  - `InsightCard`: 퍼플-블루 그라디언트 카드, 개선점 3가지 리스트, 우선순위 뱃지
  - `InsightHistory`: 이전 인사이트 목록 (날짜 + 요약 미리보기)
  - 생성 버튼 클릭 → POST `/api/insights/generate` → 스트리밍 없이 완료 후 표시
- **완료 기준**: 인사이트 생성 정상, 사용량 카운터 동작, 10회 제한 시 버튼 비활성화
- **의존성**: BE-7 (AI 인사이트 생성 API)

### FE-7. GA4/메타/네이버SA 채널 상세 화면
- **파일**: `app/(app)/dashboard/ga4/page.tsx`, `app/(app)/dashboard/meta/page.tsx`, `app/(app)/dashboard/naver/page.tsx`
- **작업 내용**:
  - GA4 상세: Sessions, Users, Bounce Rate, Goal Completions — Recharts AreaChart + 데이터 테이블
  - 메타 상세: Impressions, Clicks, CTR, CPC, ROAS, Spend — BarChart + 캠페인별 테이블
  - 네이버SA 상세: Impressions, Clicks, CTR, CPC, Conversions — Mock 데이터 시 "데이터 연동 준비 중" 배너 표시
  - 각 화면 Error Boundary 필수 (채널 API 오류 시 해당 화면만 에러 표시)
  - 연동 미완료 상태: "채널 연결하기" 빈 상태 화면
- **완료 기준**: 3채널 각각 데이터 표시, 에러 상태 + 미연동 상태 UI 처리
- **의존성**: BE-3, BE-4, BE-5 (각 채널 연동 API)

### FE-8. 설정 화면 (연동 / 결제 / 계정)
- **파일**: `app/(app)/settings/integrations/page.tsx`, `app/(app)/settings/billing/page.tsx`, `app/(app)/settings/account/page.tsx`
- **작업 내용**:
  - 연동 설정: 3채널 `IntegrationCard` — 연결 상태, 마지막 동기화 시각, 연결/해제 버튼
  - 결제 설정: 현재 플랜 표시, "결제 관리" → Stripe Customer Portal 새창 열기, 체험 만료 D-Day 카운트
  - 계정 설정: 이름 변경 폼, 비밀번호 변경 (이메일 가입자만), 계정 탈퇴 (위험 영역)
  - 설정 페이지 좌측 서브 내비 (shadcn Tabs 또는 좌측 링크 목록)
- **완료 기준**: 연동 해제 동작, Stripe Portal 링크 정상, 계정 정보 수정 저장
- **의존성**: BE-2, BE-8, BE-9

---

## BE 태스크 (총 9개)

### BE-1. DB 스키마 + Prisma 마이그레이션
- **파일**: `prisma/schema.prisma`, `prisma/migrations/`, `lib/prisma.ts`
- **작업 내용**:
  - wave_cto.md 스키마 그대로 구현: User, Account, Session, Workspace, Integration, InsightLog, UsageLog
  - `lib/prisma.ts`: PrismaClient 싱글턴 (개발 환경 핫리로드 대응)
  - `npx prisma migrate dev --name init` 실행
  - Enum: PlanStatus, ChannelType, IntegrationStatus, UsageLogType
  - 인덱스: `InsightLog(userId, createdAt)`, `UsageLog(userId, createdAt)`, `Integration(workspaceId, channel)` 유니크
- **완료 기준**: `prisma migrate dev` 성공, `prisma studio`에서 모든 테이블 확인
- **의존성**: 없음 (최우선 작업)

### BE-2. NextAuth 설정 (이메일 + 구글)
- **파일**: `app/api/auth/[...nextauth]/route.ts`, `auth.ts`, `middleware.ts`
- **작업 내용**:
  - NextAuth v5 설정: EmailProvider (Resend 또는 Nodemailer) + GoogleProvider
  - PrismaAdapter 연결 (next-auth/prisma-adapter)
  - JWT 전략: userId, planStatus, trialStartedAt 포함
  - 회원가입 콜백: User 생성 시 Workspace 자동 생성 (기본 워크스페이스)
  - 세션 콜백: planStatus DB에서 최신화하여 JWT에 주입
  - `middleware.ts`: `/dashboard/*`, `/settings/*`, `/onboarding` 미인증 시 `/login` 리다이렉트
- **완료 기준**: 이메일 가입, 구글 가입, 로그인, 로그아웃 모두 동작
- **의존성**: BE-1 완료

### BE-3. GA4 OAuth 연동 API
- **파일**: `app/api/integrations/ga4/connect/route.ts`, `app/api/integrations/ga4/callback/route.ts`, `app/api/integrations/ga4/disconnect/route.ts`, `lib/channels/ga4.ts`
- **작업 내용**:
  - `lib/channels/ga4.ts`: ChannelAdapter 인터페이스 구현
    - `connect()`: Google OAuth URL 생성 (scope: analytics.readonly)
    - `handleCallback(code)`: 토큰 교환 + AES-256 암호화 후 DB 저장
    - `getMetrics(params)`: GA4 Data API v1 호출 (sessions, users, bounceRate, goal completions)
    - `refreshToken()`: accessToken 만료 시 자동 갱신
    - `getMockData()`: 개발/테스트용 Mock 데이터
  - Integration 레코드 생성/업데이트
  - UsageLog 기록 (CHANNEL_API_CALL)
- **완료 기준**: GA4 OAuth 연동 성공, 기본 지표 수집 동작
- **의존성**: BE-1, BE-2

### BE-4. 메타 API 연동
- **파일**: `app/api/integrations/meta/connect/route.ts`, `app/api/integrations/meta/callback/route.ts`, `app/api/integrations/meta/disconnect/route.ts`, `lib/channels/meta.ts`
- **작업 내용**:
  - `lib/channels/meta.ts`: ChannelAdapter 인터페이스 구현
    - `connect()`: Facebook OAuth URL 생성 (scope: ads_read, read_insights)
    - `handleCallback(code)`: 토큰 교환 + Long-lived Token 변환 + 암호화 저장
    - `getMetrics(params)`: Meta Marketing API v19.0 — impressions, clicks, ctr, cpc, spend, roas
    - `getMockData()`: 개발용 Mock
  - 광고 계정 목록 조회 → 사용자 선택 → accountId 저장
- **완료 기준**: 메타 광고 OAuth 연동, 광고 성과 데이터 수집 동작
- **의존성**: BE-1, BE-2

### BE-5. 네이버SA API 연동 (Mock 폴백)
- **파일**: `app/api/integrations/naver/connect/route.ts`, `app/api/integrations/naver/disconnect/route.ts`, `lib/channels/naver.ts`
- **작업 내용**:
  - `lib/channels/naver.ts`: ChannelAdapter 인터페이스 구현
    - `connect(apiKey, secret)`: 네이버SA API Key 입력 방식 (OAuth 미지원 → Form 입력)
    - `getMetrics(params)`: 네이버 검색광고 API — impressions, clicks, ctr, cpc, conversions
    - `getMockData()`: PoC 전 Mock 반환 (Integration.status === 'MOCK')
    - API 호출 실패 시 자동으로 Mock 폴백
  - `NAVER_MOCK=true` 환경변수로 강제 Mock 모드
  - Integration 생성 시 status = 'MOCK' 기본값
- **완료 기준**: Mock 데이터 정상 반환, 실제 API Key 입력 시 실데이터 시도 + 실패 시 Mock 폴백
- **의존성**: BE-1, BE-2

### BE-6. 대시보드 데이터 집계 API
- **파일**: `app/api/dashboard/summary/route.ts`, `app/api/channels/ga4/metrics/route.ts`, `app/api/channels/meta/metrics/route.ts`, `app/api/channels/naver/metrics/route.ts`
- **작업 내용**:
  - `/api/dashboard/summary`: 3채널 병렬 호출 (`Promise.all`) → 통합 응답
    - 채널별 KPI (sessions, impressions, clicks, conversions, spend, roas)
    - 7일/30일 트렌드 데이터 (날짜별 배열)
    - 채널 연동 상태 포함 (미연동 채널 → null 반환)
  - 각 채널별 상세 API: 채널 전용 지표 + 날짜별 분해
  - 14일 체험 만료 체크 미들웨어 적용
  - 인증 미들웨어: 세션 검증 필수
  - TanStack Query 캐시 대응: `Cache-Control: max-age=300` 헤더
- **완료 기준**: summary API 3채널 통합 응답, 각 채널 상세 API 정상 동작
- **의존성**: BE-3, BE-4, BE-5

### BE-7. AI 인사이트 생성 API
- **파일**: `app/api/insights/generate/route.ts`, `app/api/insights/history/route.ts`, `lib/ai/insight.ts`
- **작업 내용**:
  - **월 10회 제한 체크**: `InsightLog` count WHERE userId = ? AND createdAt >= 이번달 1일 → >= 10이면 429 반환
  - 3채널 최근 7일 데이터 수집 (채널 모듈 호출)
  - GPT-4o 프롬프트 구성:
    ```
    역할: 디지털 마케팅 전문가 AI
    데이터: [GA4 요약] [메타 요약] [네이버SA 요약]
    요청: 이번 주 개선이 필요한 부분 3가지를 구체적 수치와 함께 한국어로 작성
    형식: JSON { insights: [{title, description, priority, metric}] }
    ```
  - `max_tokens: 800` 하드캡 필수
  - 응답 파싱 → `InsightLog` 저장 (inputTokens, outputTokens 포함)
  - `UsageLog` 저장 (AI_INSIGHT, 토큰 수, 비용 추정)
  - `/api/insights/history`: 최근 InsightLog 목록 + 이번달 사용 횟수
- **완료 기준**: 인사이트 생성 정상, 10회 도달 시 429, 토큰/비용 로깅 정상
- **의존성**: BE-6 완료 (데이터 수집 필요)

### BE-8. Stripe 웹훅 + 14일 차단 미들웨어
- **파일**: `app/api/webhooks/stripe/route.ts`, `app/api/billing/checkout/route.ts`, `app/api/billing/portal/route.ts`, `lib/middleware/trialCheck.ts`
- **작업 내용**:
  - Stripe 웹훅 (`/api/webhooks/stripe`):
    - `customer.subscription.created`: `planStatus = ACTIVE`, `planActivatedAt` 기록
    - `customer.subscription.deleted`: `planStatus = CANCELLED`
    - `invoice.payment_failed`: `planStatus = EXPIRED`
    - `invoice.paid`: `planStatus = ACTIVE` 복구
    - 웹훅 서명 검증 (`stripe.webhooks.constructEvent`) 필수
  - Checkout API (`/api/billing/checkout`): Stripe Checkout Session 생성 (구독 플랜)
  - Portal API (`/api/billing/portal`): Customer Portal Session URL 반환
  - 차단 미들웨어 (`lib/middleware/trialCheck.ts`):
    - `trialStartedAt + 14일 < now() && planStatus !== ACTIVE` → 403 JSON 반환
    - `/api/dashboard/*`, `/api/channels/*`, `/api/insights/*` 전체 적용
    - 클라이언트 측 판단 금지 — 반드시 서버사이드에서만
- **완료 기준**: Stripe 웹훅 수신 + planStatus 업데이트, 14일 만료 후 API 403 반환
- **의존성**: BE-1, BE-2

### BE-9. 사용량 로깅 + 관리자용 모니터링 쿼리
- **파일**: `lib/usage/logger.ts`, `app/api/admin/usage/route.ts` (내부용)
- **작업 내용**:
  - `logUsage(params)` 유틸: UsageLog 생성 헬퍼 함수 (모든 API에서 임포트)
  - 비용 추정 공식:
    - OpenAI GPT-4o: input × $0.005/1K + output × $0.015/1K
    - 채널 API: 무료 (호출 수만 기록)
  - 내부 모니터링 API (`/api/admin/usage`): 
    - 사용자별 월간 AI 호출 수
    - 총 예상 OpenAI 비용
    - 채널별 API 호출 수 집계
    - 어드민 Secret 헤더 인증 (`X-Admin-Key`)
  - 월간 비용 알람 기준: $50 초과 시 콘솔 경고 로그
- **완료 기준**: 모든 API 호출 시 UsageLog 자동 기록, 모니터링 쿼리 정상 반환
- **의존성**: BE-1

---

## 태스크 의존성 맵

```
BE-1 (스키마)
  └─► BE-2 (인증)
        └─► BE-3 (GA4)  ─┐
        └─► BE-4 (메타)  ─┼─► BE-6 (집계 API) ─► BE-7 (AI 인사이트)
        └─► BE-5 (네이버) ┘
        └─► BE-8 (결제/차단)

BE-1
  └─► BE-9 (로깅) ─► 모든 BE에서 임포트

FE-1, FE-2 (랜딩) → 의존성 없음
FE-3 (인증 화면) → BE-2
FE-4 (온보딩) → BE-3
FE-5 (대시보드) → BE-6, BE-8
FE-6 (인사이트) → BE-7
FE-7 (채널 상세) → BE-3, BE-4, BE-5
FE-8 (설정) → BE-2, BE-8, BE-9
```

---

## 병렬 작업 가능 구간

| 구간 | 병렬 가능 태스크 |
|------|----------------|
| 시작 즉시 | BE-1 + FE-1 + FE-2 |
| BE-1 완료 후 | BE-2 + BE-9 동시 |
| BE-2 완료 후 | BE-3 + BE-4 + BE-5 + BE-8 동시 |
| BE-2 완료 후 | FE-3 + FE-4 동시 |
| BE-6 완료 후 | BE-7 + FE-5 동시 |

---

## 예상 소요 시간 (참고)

| 태스크 | 예상 |
|--------|------|
| BE-1 | 2h |
| BE-2 | 3h |
| BE-3 | 4h |
| BE-4 | 3h |
| BE-5 | 2h (Mock 포함) |
| BE-6 | 3h |
| BE-7 | 3h |
| BE-8 | 4h |
| BE-9 | 2h |
| FE-1 | 5h (3D 복잡도 높음) |
| FE-2 | 3h |
| FE-3 | 2h |
| FE-4 | 3h |
| FE-5 | 5h |
| FE-6 | 3h |
| FE-7 | 4h |
| FE-8 | 3h |
| **합계** | **~54h** |
