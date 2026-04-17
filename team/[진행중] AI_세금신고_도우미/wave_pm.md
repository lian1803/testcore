# AI 세금신고 도우미 — PM 개발 태스크 분해서 v1.0

**작성자**: PM (Wave 시스템)
**작성일**: 2026-04-03
**기반 문서**: PRD.md v1.0, wave_cto.md v1.0, DESIGN.md v1.0
**프로젝트 상태**: CONDITIONAL_GO — MVP 범위 엄수 필수

---

## 1. FE 태스크 목록

---

### FE-1. 프로젝트 초기 셋업

**설명**: Next.js 14 App Router 기반 프로젝트 초기화 및 공통 설정 완료

**파일 경로**
```
ai-tax-assistant/
├── app/layout.tsx                  # 루트 레이아웃 (Pretendard 폰트, 기본 메타데이터)
├── app/globals.css                 # Tailwind 커스텀 컬러 변수 (primary, accent 등)
├── tailwind.config.ts              # 커스텀 컬러 팔레트 등록
├── tsconfig.json                   # strict: true, noImplicitAny: true 필수
├── .env.local.example              # 환경변수 템플릿 (절대 실제 값 커밋 금지)
└── components/ui/                  # shadcn/ui CLI로 컴포넌트 초기 설치
```

**주요 컴포넌트**
- Pretendard 폰트 CDN 임포트: `@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/...')`
- Tailwind 커스텀 컬러: `primary(#1E3A5F)`, `accent(#22C55E)`, `background(#F8FAFC)`, `surface(#FFFFFF)` 등
- shadcn/ui 초기 설치: Button, Input, Card, Select, Dialog, Toast, Badge, Progress, Tabs, Switch 등

**API 연결 포인트**: 없음 (초기 설정)

---

### FE-2. 랜딩 페이지 (`/`)

**설명**: 첫 인상 + 가치 전달 + 무료 회원가입 전환 페이지

**파일 경로**
```
app/page.tsx                        # 랜딩 페이지 루트 (SSR)
components/landing/
├── Navbar.tsx                      # 네비게이션 바 (sticky, backdrop-blur)
├── HeroSection.tsx                 # Hero 섹션 (헤드라인 + CTA)
├── FeatureCards.tsx                # 기능 소개 카드 3개 (OCR/분류/신고서)
├── TrustSection.tsx                # 신뢰 지표 섹션 (97%/10초/절세금액)
├── PricingSection.tsx              # 가격 플랜 카드 (무료/프리미엄)
├── TestimonialSection.tsx          # 이용 후기 섹션
└── Footer.tsx                      # 푸터
```

**주요 컴포넌트**
- Navbar: 좌측 로고, 우측 "로그인"(ghost 버튼) + "무료로 시작하기"(primary 버튼), `h-16`, sticky
- HeroSection: 헤드라인 `text-4xl font-bold`, CTA 버튼 `accent(#22C55E)` 배경, `min-h-[600px]`
- FeatureCards: `grid grid-cols-1 md:grid-cols-3 gap-6`, surface 배경, rounded-2xl
- TrustSection: `primary(#1E3A5F)` 배경 + 흰 텍스트, grid-cols-3 수치
- PricingSection: 무료/프리미엄 카드, 추천 플랜에 `ring-2 ring-accent` 강조

**API 연결 포인트**: 없음 (정적 페이지)

---

### FE-3. 회원가입 / 로그인 (`/signup`, `/login`)

**설명**: 이메일 + 소셜 로그인(카카오/구글) 통합 인증 화면

**파일 경로**
```
app/(auth)/
├── signup/page.tsx                 # 회원가입 페이지
├── login/page.tsx                  # 로그인 페이지
└── layout.tsx                      # Auth 레이아웃 (좌측 브랜드 영역 + 우측 카드)
components/auth/
├── SignupForm.tsx                   # 이메일/비밀번호 + 소셜 로그인 폼
├── LoginForm.tsx                   # 로그인 폼
├── SocialLoginButtons.tsx          # 카카오(#FEE500) + 구글 버튼
└── PasswordInput.tsx               # 눈 아이콘 토글 비밀번호 Input
```

**주요 컴포넌트**
- 중앙 카드 레이아웃: `max-w-md mx-auto`, `min-h-screen flex items-center`
- SocialLoginButtons: 카카오 `bg-[#FEE500]`, 구글 `border border-border bg-white`
- 실시간 유효성 검사: 포커스 아웃 시 `border-error` + `text-error text-sm`
- 제출 버튼 로딩 상태: 스피너 + 비활성화 처리
- 회원가입 성공 → `/onboarding`, 로그인 성공 → `/dashboard` 리다이렉트

**API 연결 포인트**
- `POST /api/auth/register` — 이메일 회원가입
- `POST /api/auth/[...nextauth]` — 소셜 로그인 (NextAuth)
- `POST /api/auth/forgot-password` — 비밀번호 찾기

---

### FE-4. 온보딩 (`/onboarding`)

**설명**: 사업자 세금 프로필 3단계 Wizard로 수집 (업종 → 과세유형 → 신고연도)

**파일 경로**
```
app/(auth)/onboarding/page.tsx      # 온보딩 페이지
components/onboarding/
├── OnboardingWizard.tsx            # Wizard 컨테이너 (스텝 관리, 슬라이드 애니메이션)
├── StepIndicator.tsx               # 상단 Progress 인디케이터 (1/3 → 2/3 → 3/3)
├── Step1BusinessType.tsx           # 업종 선택 (국세청 업종코드 드롭다운)
├── Step2TaxationType.tsx           # 과세유형 라디오 + 사업자등록번호 Input
└── Step3TaxYear.tsx                # 신고 연도 선택 + 완료
```

**주요 컴포넌트**
- StepIndicator: `Progress h-2 bg-primary`, 스텝 번호 텍스트
- Step1: `Select` 업종코드 드롭다운, 선택 시 공제 항목 안내 텍스트 동적 표시
- Step2: `RadioGroup` — 일반과세자/간이과세자/면세사업자/개인(사업자등록 없음)
- Step3: `Select` 연도 + warning 배경 안내 박스 ("종합소득세 신고 기간: 매년 5월 1일~31일")
- 이전/다음 버튼, 슬라이드 애니메이션 (`translate-x` 트랜지션)
- 필수 항목 미선택 시 다음 버튼 비활성화

**API 연결 포인트**
- `POST /api/profile` — 온보딩 완료 시 사업자 프로필 생성

---

### FE-5. 대시보드 레이아웃 + 사이드바 네비게이션

**설명**: 대시보드 전체 Shell 레이아웃 (사이드바 + 헤더 + 콘텐츠 영역)

**파일 경로**
```
app/(dashboard)/layout.tsx          # 대시보드 공통 레이아웃
components/layout/
├── Sidebar.tsx                     # 사이드바 (데스크탑 고정, 모바일 Sheet)
├── SidebarNav.tsx                  # 네비게이션 메뉴 (아이콘 + 텍스트)
├── HeaderBar.tsx                   # 상단 헤더 바 (페이지 타이틀 + 액션 버튼)
├── UserProfile.tsx                 # 사이드바 하단 사용자 프로필
└── UsageMeter.tsx                  # 무료 한도 Progress 바 ("영수증 N/20건")
```

**주요 컴포넌트**
- Sidebar: `surface(#FFFFFF)`, `border-r border-border`, `w-64` (데스크탑), `lg` 이상 고정
- SidebarNav 메뉴: 대시보드/영수증/경비 목록/신고서/설정, 활성 시 `primary` 배경 + 흰 텍스트 `rounded-lg`
- 모바일: `Sheet` 컴포넌트로 사이드바 대체, 하단 탭바 네비게이션
- UsageMeter: `Progress` 컴포넌트, `/api/usage` 데이터 연결

**API 연결 포인트**
- `GET /api/usage` — 사이드바 한도 표시

---

### FE-6. 대시보드 메인 (`/dashboard`)

**설명**: 경비 현황 KPI 카드 + 월별 바 차트 + 최근 영수증 리스트

**파일 경로**
```
app/(dashboard)/dashboard/page.tsx  # 대시보드 메인
components/dashboard/
├── KpiCards.tsx                    # KPI 카드 4개 (총경비/예상세액/영수증수/절세액)
├── MonthlyExpenseChart.tsx         # Recharts 월별 경비 바 차트
├── RecentReceiptsList.tsx          # 최근 영수증 5건 리스트
└── DashboardEmptyState.tsx         # 빈 상태 (영수증 0건 안내)
```

**주요 컴포넌트**
- KpiCards: `grid grid-cols-2 lg:grid-cols-4 gap-4`, surface 배경, rounded-xl, p-6, shadow-sm
  - 절세 예상액: `border-l-4 border-accent` 강조
  - 예상 세액: `text-error`
- MonthlyExpenseChart: `Recharts BarChart`, X축 1~12월, Y축 만원 단위, 카테고리 누적 바 토글
- RecentReceiptsList: [썸네일][상호명+날짜][카테고리 Badge][금액]
- FAB (모바일): 우측 하단 고정 `+` 버튼 → `/receipts/new`
- 빈 상태: 일러스트 + "첫 영수증을 추가해보세요" CTA

**API 연결 포인트**
- `GET /api/expenses/summary` — KPI 카드 + 차트 데이터
- `GET /api/receipts` — 최근 영수증 목록 (limit=5)
- `GET /api/usage` — 영수증 사용 수 KPI

---

### FE-7. 영수증 업로드 + OCR 결과 확인 (`/receipts/new`)

**설명**: 영수증 업로드 → OCR 처리 로딩 → AI 분류 결과 수정 → 저장 (목표 10초)

**파일 경로**
```
app/(dashboard)/receipts/new/page.tsx
components/receipt/
├── ReceiptUploader.tsx             # 드래그앤드롭 + 카메라 촬영 업로드 UI
├── OcrLoadingOverlay.tsx           # OCR 처리 중 스캔 라인 애니메이션 오버레이
├── OcrResultEditor.tsx             # 분류 결과 수정 폼 (날짜/금액/상호명/카테고리)
├── ReceiptImagePreview.tsx         # 업로드된 영수증 이미지 썸네일 (클릭 시 확대)
└── CategorySelector.tsx            # 카테고리 드롭다운 (AI 분류 + 수동 변경)
```

**주요 컴포넌트**
- ReceiptUploader: 점선 드래그앤드롭 존 (`border-2 border-dashed`), 드래그 오버 시 `border-primary bg-primary/5`
- OcrLoadingOverlay: 스캔 라인 CSS 애니메이션, 단계 텍스트 "이미지 분석 중 → 텍스트 인식 중 → 카테고리 분류 중"
- OcrResultEditor: Input(날짜/금액/상호명) + Select(카테고리) + Switch(사업관련 여부) + Textarea(메모)
  - 신뢰도 낮은 필드: 노란 배경 + "확인 필요" Badge
  - AI 분류 근거 표시: `text-sm text-secondary`
- TanStack Query 폴링으로 OCR 완료 상태 감지

**API 연결 포인트**
- `POST /api/receipts/upload-url` — S3 Presigned URL 발급
- S3 직접 업로드 (Presigned URL 사용)
- `POST /api/receipts` — Receipt DB 레코드 생성 + OCR 큐 등록
- `GET /api/receipts/[id]` — OCR 완료 상태 폴링
- `PUT /api/expenses/[id]` — 사용자 확인 후 저장 (`userVerified: true`)

---

### FE-8. 경비 목록 (`/expenses`)

**설명**: 등록된 모든 경비 목록 테이블 + 필터 + 인라인 수정/삭제

**파일 경로**
```
app/(dashboard)/expenses/page.tsx
components/expense/
├── ExpenseTable.tsx                # 경비 테이블 (날짜/상호명/카테고리/금액/액션)
├── ExpenseFilters.tsx              # 월별/카테고리/검색어 필터
├── ExpenseEditDialog.tsx           # 인라인 수정 Dialog
├── ExpenseDeleteDialog.tsx         # 삭제 확인 Dialog
└── ExpenseSummaryBar.tsx           # 필터 기간 총 경비 합계 표시
```

**주요 컴포넌트**
- ExpenseTable: 컬럼 [날짜][상호명][카테고리][금액][사업관련][액션], 행 높이 `h-14`, 짝수 행 `bg-gray-50/50`
  - 카테고리 Badge 색상 체계: 식비 `#FEF3C7`, 교통비 `#DBEAFE`, 통신비 `#F3E8FF` 등
  - 액션 버튼: 행 호버 시 펜 + 휴지통 아이콘 표시
  - 모바일: 카드 리스트 뷰 (lg 미만)
- ExpenseFilters: Select(월) + Select(카테고리) + Input(검색)
- 페이지네이션: 20건/페이지 기본
- 금액 우측 정렬, `font-semibold`

**API 연결 포인트**
- `GET /api/expenses` — 경비 목록 (연도/카테고리/월 필터 + 페이지네이션)
- `PUT /api/expenses/[id]` — 경비 수정
- `DELETE /api/expenses/[id]` — 경비 삭제

---

### FE-9. 신고서 생성 Wizard (`/tax-return`)

**설명**: 종합소득세 신고서 초안 4단계 생성 + PDF/Excel 다운로드

**파일 경로**
```
app/(dashboard)/tax-return/page.tsx
components/tax-return/
├── TaxReturnWizard.tsx             # Wizard 컨테이너 (4단계)
├── Step1IncomeInput.tsx            # 소득 정보 입력 (매출액/기타소득/부양가족)
├── Step2ExpenseReview.tsx          # 카테고리별 경비 확인 (읽기 전용)
├── Step3Preview.tsx                # 신고서 미리보기 (세액 계산 결과)
├── Step4Download.tsx               # 다운로드 + 홈택스 입력 가이드
├── TaxSummaryCard.tsx              # 주요 세금 항목 카드 (수입/경비/세액)
└── DisclaimerBanner.tsx            # 법적 고지 배너 (필수, 전 단계 고정)
```

**주요 컴포넌트**
- Step3Preview: 예상 납부세액 `text-3xl font-bold text-error`, 절세 예상액 `text-accent`
- DisclaimerBanner: `bg-warning/10 border border-warning rounded-xl p-4` — 모든 신고 관련 화면 고정
- Step4Download: "PDF 다운로드"(primary) + "Excel 다운로드"(outline) 버튼
- 홈택스 입력 가이드: `Accordion` 컴포넌트, 단계별 스크린샷 포함
- 경비 0건 시 빈 상태: "영수증 추가하기" CTA

**API 연결 포인트**
- `GET /api/expenses/summary` — 경비 확인 스텝 데이터
- `POST /api/tax-returns` — 신고서 생성 요청 (소득 정보 포함)
- `GET /api/tax-returns/[id]` — 생성 완료 폴링
- `GET /api/tax-returns/[id]/download?format=pdf` — PDF 다운로드
- `GET /api/tax-returns/[id]/download?format=excel` — Excel 다운로드

---

### FE-10. 설정 / 구독 (`/settings`)

**설명**: 계정 정보 수정 + 플랜 업그레이드 + 개인정보 보호 설정

**파일 경로**
```
app/(dashboard)/settings/page.tsx
components/settings/
├── AccountSettings.tsx             # 계정 정보 탭 (이름/업종/비밀번호)
├── SubscriptionSettings.tsx        # 구독 플랜 탭 (현재 플랜 + 업그레이드 CTA)
├── PrivacySettings.tsx             # 개인정보 보호 탭 (이미지 삭제 토글 등)
├── PlanUpgradeCard.tsx             # 플랜 카드 (무료/프리미엄 나란히)
└── PaywallModal.tsx                # 무료 한도 초과 시 페이월 Dialog
```

**주요 컴포넌트**
- `Tabs` + `TabsList`: 계정 정보 / 구독 플랜 / 개인정보 보호
- SubscriptionSettings: 현재 플랜 배너 `bg-primary/5`, 다음 결제일, 결제 수단 마지막 4자리
- PlanUpgradeCard: 무료 Progress 바 `N/20건`, 프리미엄 `ring-2 ring-accent` + 기능 체크리스트
- PrivacySettings: "영수증 원본 이미지 자동 삭제" `Switch` (기본값 ON — 필수 제공)
- "계정 탈퇴" 링크: `text-error`, 하단 분리 (삭제 확인 Dialog)

**API 연결 포인트**
- `GET /api/profile`, `PUT /api/profile` — 프로필 조회/수정
- `GET /api/subscription` — 구독 상태 조회
- `POST /api/subscription/checkout` — Stripe Checkout 세션 생성
- `POST /api/subscription/portal` — Stripe Customer Portal
- `POST /api/subscription/cancel` — 구독 해지 예약

---

## 2. BE 태스크 목록

---

### BE-1. DB 스키마 + Prisma 셋업

**설명**: PostgreSQL + Prisma ORM 초기화, 전체 스키마 정의 및 마이그레이션

**엔드포인트**: 없음 (DB 레이어)

**파일 경로**
```
prisma/schema.prisma
lib/db.ts                           # Prisma Client 싱글톤
```

**스키마 모델**
- `User`: 회원 기본 정보, `planStatus(FREE/PREMIUM/EXPIRED)`
- `BusinessProfile`: 업종코드, 과세유형(GENERAL/SIMPLIFIED/TAX_FREE/INCOME_ONLY), 사업자등록번호(선택), 신고연도
- `Receipt`: S3 이미지 키, OCR 원본 텍스트(AES-256 암호화), 신뢰도, 처리 상태(PENDING/PROCESSING/COMPLETED/FAILED)
- `ExpenseItem`: 경비 항목, 카테고리 enum 11개, `userVerified` 필드 (법적 책임 분산 핵심)
- `TaxReturn`: 신고서 초안, `@@unique([userId, taxYear])` — 연도별 1개 제한
- `Subscription`: Stripe 구독 정보 (stripeCustomerId, 상태)
- `UsageLog`: 무료 플랜 한도 추적 (RECEIPT_UPLOAD/TAX_RETURN_GENERATE), `@@index([userId, action, createdAt])`
- NextAuth 필수 모델: `Account`, `Session`, `VerificationToken`

**비즈니스 로직 요약**
- 모든 금액 필드는 `Int` (원 단위, 소수점 없음) — Rule 5 준수
- `ocrRawText`, `registrationNumber` 컬럼 AES-256 암호화 적용
- `onDelete: Cascade` — 회원 탈퇴 시 모든 데이터 연쇄 삭제

---

### BE-2. NextAuth 인증 (이메일 + 구글/카카오 소셜 로그인)

**설명**: NextAuth.js v5 기반 인증 전체 구현 (소셜 로그인 + 이메일/비밀번호)

**엔드포인트**

| 메서드 | 경로 | 설명 |
|--------|------|------|
| ALL | `/api/auth/[...nextauth]` | NextAuth.js 핸들러 (소셜 로그인, 세션) |
| POST | `/api/auth/register` | 이메일 회원가입 (비밀번호 해싱) |
| POST | `/api/auth/verify-email` | 이메일 인증 토큰 확인 |
| POST | `/api/auth/forgot-password` | 비밀번호 재설정 메일 발송 |
| POST | `/api/auth/reset-password` | 토큰 검증 후 비밀번호 변경 |

**입력 타입 (Zod 스키마 필수)**
```typescript
// 회원가입
RegisterInput: { email: string, password: string (min 8, 특수문자), name?: string }
// 로그인
LoginInput: { email: string, password: string }
```

**출력 타입**
```typescript
// 회원가입 성공
{ user: { id, email, name }, message: "이메일 인증 발송됨" }
// 에러
{ error: string, statusCode: number }
```

**비즈니스 로직 요약**
- 비밀번호: `bcrypt` 해싱 (salt rounds 12)
- 이메일 인증: Resend로 토큰 발송, 24시간 만료
- 소셜 로그인: Google OAuth, Kakao OAuth 연동
- 세션: HTTPS 전용 쿠키, JWT 방식
- Rate Limiting: 로그인 10회/분 (Upstash Redis)

**파일 경로**
```
lib/auth.ts                         # NextAuth.js 설정 (providers, callbacks)
app/api/auth/[...nextauth]/route.ts
app/api/auth/register/route.ts
app/api/auth/verify-email/route.ts
app/api/auth/forgot-password/route.ts
app/api/auth/reset-password/route.ts
lib/validators/auth.ts              # Zod 스키마
```

---

### BE-3. 영수증 업로드 API (S3 Presigned URL)

**설명**: S3 직접 업로드용 Presigned URL 발급 + Receipt DB 레코드 관리

**엔드포인트**

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/api/receipts` [auth] | 영수증 목록 조회 (페이지네이션, 날짜 필터) |
| POST | `/api/receipts/upload-url` [auth] | S3 Presigned Upload URL 발급 |
| POST | `/api/receipts` [auth] | 업로드 완료 후 Receipt 레코드 생성 |
| GET | `/api/receipts/[id]` [auth] | 영수증 상세 + OCR 결과 조회 |
| DELETE | `/api/receipts/[id]` [auth] | 영수증 + S3 이미지 삭제 |
| POST | `/api/receipts/[id]/process` [auth] | OCR 재처리 요청 |

**입력 타입 (Zod 스키마 필수)**
```typescript
// Presigned URL 요청
UploadUrlInput: { fileName: string, fileType: "image/jpeg" | "image/png" | "image/webp", fileSize: number (max 10MB) }

// Receipt 생성
CreateReceiptInput: { s3Key: string }
```

**출력 타입**
```typescript
// Presigned URL 응답
{ uploadUrl: string, s3Key: string, expiresIn: 300 }

// Receipt 생성 응답
{ receiptId: string, status: "PENDING" }
```

**비즈니스 로직 요약**
- Presigned URL 만료: 5분 (`expiresIn: 300`)
- 업로드 전 무료 플랜 한도 체크: `checkUsageLimit(userId, "RECEIPT_UPLOAD")` → 초과 시 HTTP 402
- UsageLog 기록: `RECEIPT_UPLOAD` 액션
- S3 Bucket: 퍼블릭 액세스 차단, SSE-S3 서버사이드 암호화
- 삭제 시: S3 `deleteObject` + `imageDeleted: true` 업데이트

**파일 경로**
```
app/api/receipts/route.ts
app/api/receipts/upload-url/route.ts
app/api/receipts/[id]/route.ts
app/api/receipts/[id]/process/route.ts
lib/s3.ts                           # S3 클라이언트 + presigned URL 헬퍼
lib/usage.ts                        # 한도 체크 함수
lib/validators/receipt.ts           # Zod 스키마
```

---

### BE-4. OCR 파이프라인 (Google Vision + GPT-4o 분류)

**설명**: 영수증 이미지 → OCR → AI 경비 분류 → ExpenseItem 저장 파이프라인

**엔드포인트**: `POST /api/receipts` 내부에서 비동기 트리거 (또는 Vercel Edge Function)

**파이프라인 플로우**
```
1. 이미지 전처리 (크기 검증 10MB, JPEG 정규화)
2. Google Cloud Vision API (TEXT_DETECTION) 호출
   - ocrConfidence 저장
   - 신뢰도 < 0.7 → GPT-4o Vision 폴백
3. GPT-4o Vision 폴백 (저신뢰도/실패/타임아웃)
   - ocrEngine: GPT4O_VISION 기록
4. GPT-4o 경비 분류 (response_format: json_object 필수)
   - 입력: OCR 텍스트 + 업종코드 + 과세유형 + 카테고리 목록
   - 출력: { date, amount, merchantName, category, isBusinessExpense, confidence }
5. ExpenseItem DB 저장 (userVerified: false)
6. Receipt status: COMPLETED 업데이트
```

**출력 타입 (GPT-4o JSON)**
```typescript
OcrClassificationResult: {
  date: string,           // "YYYY-MM-DD"
  amount: number,         // 정수, Math.round() 처리
  merchantName: string,
  category: ExpenseCategory,
  isBusinessExpense: boolean,
  confidence: number      // 0~1
}
```

**비즈니스 로직 요약**
- Google Vision 우선 (비용 절감: GPT-4o 대비 약 10배 저렴)
- GPT-4o 폴백 조건: 신뢰도 0.7 미만, Vision API 실패, 10초 타임아웃
- OCR 실패 시: `status: FAILED`, FE에서 수동 입력 안내
- AI 분류 실패 시: category: OTHER 기본 분류, 사용자 수동 수정 유도
- 금액은 반드시 `Math.round()` 후 정수 저장 — Rule 5 준수
- Sentry 에러 추적: OCR 실패율 월 5% 초과 시 알림

**파일 경로**
```
lib/ocr/google-vision.ts            # Google Cloud Vision API 래퍼
lib/ocr/gpt4o-vision.ts             # GPT-4o Vision 폴백
lib/ocr/pipeline.ts                 # OCR 파이프라인 오케스트레이터
lib/ai/expense-classifier.ts        # GPT-4o 경비 분류 (Zod 응답 검증)
```

---

### BE-5. 경비 항목 CRUD API

**설명**: 경비 항목 생성/조회/수정/삭제 + 대시보드용 집계 API

**엔드포인트**

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/api/expenses` [auth] | 경비 목록 조회 (연도/카테고리/월 필터) |
| POST | `/api/expenses` [auth] | 경비 수동 추가 (영수증 없이) |
| PUT | `/api/expenses/[id]` [auth] | 경비 수정 (카테고리/금액/검증 완료) |
| DELETE | `/api/expenses/[id]` [auth] | 경비 삭제 |
| GET | `/api/expenses/summary` [auth] | 연간/월별 경비 집계 |

**입력 타입 (Zod 스키마 필수)**
```typescript
// 경비 생성/수정
ExpenseInput: {
  date: string,            // "YYYY-MM-DD"
  amount: number,          // 양의 정수
  merchantName: string,
  category: ExpenseCategory,
  isBusinessExpense: boolean,
  userVerified?: boolean,
  memo?: string,
  taxYear: number
}

// 목록 조회 쿼리
ExpenseQuery: { taxYear?: number, month?: number, category?: ExpenseCategory, page?: number, limit?: number }
```

**출력 타입**
```typescript
// 집계 (summary)
ExpenseSummary: {
  totalAmount: number,
  byMonth: { month: number, amount: number }[],
  byCategory: { category: ExpenseCategory, amount: number }[]
}
```

**비즈니스 로직 요약**
- 조회 시 `userId` 필터 강제 적용 (타 사용자 데이터 접근 차단)
- `userVerified` 업데이트는 PUT 엔드포인트에서만 가능
- summary 집계: `GROUP BY month`, `GROUP BY category` Prisma 집계 쿼리
- 금액 정수 검증: Zod `z.number().int().positive()`

**파일 경로**
```
app/api/expenses/route.ts
app/api/expenses/[id]/route.ts
app/api/expenses/summary/route.ts
lib/validators/expense.ts
```

---

### BE-6. 신고서 생성 API (세금 계산 로직)

**설명**: 경비 + 소득 입력 → 종합소득세 계산 → 신고서 초안 생성 → PDF/Excel 생성

**엔드포인트**

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/api/tax-returns` [auth] | 신고서 목록 조회 |
| POST | `/api/tax-returns` [auth] | 신고서 생성 요청 |
| GET | `/api/tax-returns/[id]` [auth] | 신고서 상세 조회 |
| GET | `/api/tax-returns/[id]/download` [auth] | PDF 또는 Excel 다운로드 |
| DELETE | `/api/tax-returns/[id]` [auth] | 신고서 삭제 |

**입력 타입 (Zod 스키마 필수)**
```typescript
CreateTaxReturnInput: {
  taxYear: number,
  totalIncome: number,      // 연간 총 매출액 (양의 정수)
  otherIncome?: number,     // 기타 소득 (이자, 배당 등)
  dependents?: number       // 부양가족 수 (인적공제용)
}
```

**출력 타입**
```typescript
TaxReturnResult: {
  id: string,
  totalIncome: number,
  totalExpense: number,     // 인정된 총 경비
  standardDeduction: number, // 기본공제 합계
  taxBase: number,          // 과세표준
  estimatedTax: number,     // 예상 납부세액
  status: "DRAFT" | "READY"
}
```

**비즈니스 로직 요약**
- 신고서 생성 전 `userVerified: false` 항목 존재 시 → 400 에러 반환 (Rule 1 준수)
- 무료 플랜 한도 체크: `checkUsageLimit(userId, "TAX_RETURN_GENERATE")` → 초과 시 402
- 세금 계산 로직: `lib/tax-calculator.ts` 순수 함수로 분리, 단위 테스트 필수
  - 과세표준 = 총수입 - 총경비 - 기본공제
  - 세율 구간: 1,400만원 이하 6%, 5,000만원 이하 15%, 8,800만원 이하 24% 등 (2024년 기준)
- PDF 생성: `@react-pdf/renderer` 서버사이드 렌더링
- Excel 생성: `xlsx (SheetJS)`
- 생성된 파일: S3 임시 저장 → 다운로드 링크 반환 (Presigned URL, 1시간 만료)
- `@@unique([userId, taxYear])` — 연도별 1개 제한 (기존 있으면 덮어쓰기)

**파일 경로**
```
app/api/tax-returns/route.ts
app/api/tax-returns/[id]/route.ts
app/api/tax-returns/[id]/download/route.ts
lib/tax-calculator.ts               # 순수 함수, 단위 테스트 필수
lib/validators/tax-return.ts
```

---

### BE-7. 구독/결제 API (Stripe + 웹훅)

**설명**: Stripe 기반 월/연간 구독 결제 + 웹훅 수신 처리

**엔드포인트**

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/api/subscription` [auth] | 현재 구독 상태 조회 |
| POST | `/api/subscription/checkout` [auth] | Stripe Checkout 세션 생성 |
| POST | `/api/subscription/portal` [auth] | Stripe Customer Portal 세션 생성 |
| POST | `/api/subscription/cancel` [auth] | 구독 해지 예약 |
| POST | `/api/webhooks/stripe` | Stripe 웹훅 수신 (인증 없음, Stripe 서명 검증) |

**입력 타입**
```typescript
CheckoutInput: { plan: "MONTHLY" | "ANNUAL" }
WebhookEvent: Stripe.Event  // Stripe SDK 타입 사용
```

**출력 타입**
```typescript
CheckoutResult: { checkoutUrl: string }   // Stripe Checkout 리다이렉트 URL
SubscriptionStatus: {
  plan: "FREE" | "MONTHLY" | "ANNUAL",
  status: "ACTIVE" | "PAST_DUE" | "CANCELED" | "TRIALING",
  currentPeriodEnd: Date,
  cancelAtPeriodEnd: boolean
}
```

**비즈니스 로직 요약**
- Checkout: Stripe Customer 자동 생성 또는 기존 연결, 결제 완료 후 웹훅으로 플랜 활성화
- 웹훅 이벤트 처리:
  - `checkout.session.completed` → Subscription 레코드 생성, User.planStatus = PREMIUM
  - `invoice.payment_failed` → status = PAST_DUE
  - `customer.subscription.deleted` → planStatus = FREE
  - `customer.subscription.updated` → 갱신 처리
- 웹훅 보안: `stripe.webhooks.constructEvent()` 서명 검증 (STRIPE_WEBHOOK_SECRET)
- 구독 해지: `cancelAtPeriodEnd: true` (즉시 해지 아님, 기간 만료 후 해지)

**파일 경로**
```
app/api/subscription/route.ts
app/api/subscription/checkout/route.ts
app/api/subscription/portal/route.ts
app/api/subscription/cancel/route.ts
app/api/webhooks/stripe/route.ts
lib/stripe.ts                       # Stripe 클라이언트 싱글톤
```

---

### BE-8. 사용량 제한 미들웨어 (무료 한도 체크)

**설명**: 무료 플랜 사용량 추적 + API 레벨 하드 리밋 적용

**엔드포인트**

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/api/usage` [auth] | 현재 월 영수증 업로드 수, 이번 연도 신고서 생성 수 조회 |

**출력 타입**
```typescript
UsageSummary: {
  receipts: { used: number, limit: 20, resetAt: Date },
  taxReturns: { used: number, limit: 1, resetAt: Date },
  isPremium: boolean
}
```

**비즈니스 로직 요약**
- 무료 플랜 한도:
  - 영수증 업로드: 20건/월 (달력월 기준, 매월 1일 초기화)
  - 신고서 생성: 1회/연도 (연도 기준)
- `checkUsageLimit(userId, action)` 함수: `lib/usage.ts`에서 구현
  - UsageLog 집계: `WHERE userId = ? AND action = ? AND createdAt >= [월 시작일]`
  - 한도 초과 시 `{ allowed: false, message: "..." }` 반환 → API에서 HTTP 402 반환
- FE는 `/api/usage` 조회로 UI 비활성화 (UX 보조), 실제 차단은 BE에서만 (Rule 3 준수)
- 프리미엄 플랜: `checkUsageLimit` 호출 시 User.planStatus 확인 후 즉시 통과

**파일 경로**
```
app/api/usage/route.ts
lib/usage.ts                        # checkUsageLimit() 함수
```

---

## 3. 개발 우선순위

Must Have 기준 순서 정렬. 핵심 가치 제안(OCR + 신고서)을 최단 경로로 완성.

### Wave 1 — 기반 인프라 (모든 기능의 전제)
1. **BE-1** DB 스키마 + Prisma 셋업
2. **FE-1** 프로젝트 초기 셋업
3. **BE-2** NextAuth 인증 API

### Wave 2 — 사용자 진입 플로우
4. **FE-3** 회원가입/로그인 화면
5. **FE-4** 온보딩 화면
6. **BE-8** 사용량 제한 미들웨어

### Wave 3 — 핵심 기능 (Must Have #1, #2)
7. **BE-3** 영수증 업로드 API + S3 연동
8. **BE-4** OCR 파이프라인 (Google Vision + GPT-4o)
9. **FE-5** 대시보드 레이아웃 + 사이드바
10. **FE-7** 영수증 업로드 + OCR 결과 확인 화면

### Wave 4 — 경비 관리 (Must Have #2, #4)
11. **BE-5** 경비 항목 CRUD API
12. **FE-6** 대시보드 메인 (KPI 카드 + 차트)
13. **FE-8** 경비 목록 화면

### Wave 5 — 신고서 생성 (Must Have #3, #6)
14. **BE-6** 신고서 생성 API + 세금 계산 로직
15. **FE-9** 신고서 생성 Wizard

### Wave 6 — 수익 모델 (Must Have #7)
16. **BE-7** 구독/결제 API (Stripe)
17. **FE-10** 설정/구독 화면

### Wave 7 — 공개 페이지
18. **FE-2** 랜딩 페이지

---

## 4. 의존성 관계

```
BE-1 (DB) ──────────────┬──────► BE-2 (인증)
                         │              │
                         │              ▼
                         │        FE-3 (로그인/가입)
                         │              │
                         │              ▼
                         │        FE-4 (온보딩) ──► BE-2의 /api/profile POST
                         │
                         ├──────► BE-8 (사용량 제한) ─── BE-3, BE-6에서 의존
                         │
                         ├──────► BE-3 (영수증 업로드 API)
                         │              │
                         │              ▼
                         │        BE-4 (OCR 파이프라인) ──► BE-5 ExpenseItem 저장
                         │
                         └──────► BE-5 (경비 CRUD API)
                                        │
                                        ▼
                                  BE-6 (신고서 생성 API) ──► BE-7 (결제 한도 해제)
```

```
FE-1 (프로젝트 셋업) ──► FE-3 ──► FE-4 ──► FE-5 (사이드바 레이아웃)
                                              │
                              ┌───────────────┤
                              │               │
                              ▼               ▼
                        FE-6 (대시보드)   FE-7 (영수증 업로드)
                              │
                              ▼
                        FE-8 (경비 목록) ──► FE-9 (신고서 Wizard)
                                                    │
                                                    ▼
                                             FE-10 (설정/구독)
```

### 핵심 의존성 요약

| 태스크 | 선행 필수 태스크 |
|--------|-----------------|
| FE-3 (로그인) | BE-2 (NextAuth) |
| FE-4 (온보딩) | FE-3, BE-2 |
| FE-5, 6, 7, 8, 9, 10 (대시보드 전체) | FE-4, BE-1 |
| FE-7 (영수증 업로드 화면) | BE-3, BE-4 |
| FE-6 (대시보드 KPI 차트) | BE-5 (summary API) |
| FE-8 (경비 목록) | BE-5 |
| FE-9 (신고서 Wizard) | BE-5, BE-6 |
| FE-10 (설정/구독) | BE-7 |
| BE-3 (영수증 업로드) | BE-1, BE-8 |
| BE-4 (OCR 파이프라인) | BE-3 |
| BE-5 (경비 CRUD) | BE-1, BE-4 |
| BE-6 (신고서 생성) | BE-1, BE-5, BE-8 |
| BE-7 (결제) | BE-1, BE-2 |
| BE-8 (사용량 제한) | BE-1, BE-2 |

---

## 5. 공통 준수 사항 (Engineering Rules 요약)

모든 FE/BE 태스크에 예외 없이 적용.

| 규칙 | 내용 |
|------|------|
| Rule 1 — 세무 면책 문구 | 모든 신고 관련 화면에 `DisclaimerBanner` 고정. `userVerified: false` 항목 있으면 신고서 생성 API 차단. |
| Rule 2 — 개인정보 최소 수집 | S3 이미지 처리 후 즉시 삭제 옵션 필수. `ocrRawText` AES-256 암호화. 회원 탈퇴 시 전체 데이터 삭제. |
| Rule 3 — 무료 한도 API 레벨 강제 | FE 비활성화는 UX 보조. 실제 차단은 BE에서 `checkUsageLimit()` 호출, 초과 시 HTTP 402. |
| Rule 4 — 타입 안전성 | `tsconfig.json strict: true`. 모든 API body Zod 파싱. GPT-4o 응답 `json_object` 강제 + Zod 검증. |
| Rule 5 — 금액 정수 처리 | 모든 금액 `Int` (원 단위). OCR/AI 소수점 → `Math.round()`. 세금 계산은 `lib/tax-calculator.ts` 순수 함수. |

---

*본 문서는 PRD.md, wave_cto.md, DESIGN.md를 기반으로 PM이 작성한 FE/BE 개발 태스크 분해서입니다.*
*개발 시작 전 FE/BE 개발자 모두 이 문서와 Engineering Rules 5가지를 숙지하세요.*
