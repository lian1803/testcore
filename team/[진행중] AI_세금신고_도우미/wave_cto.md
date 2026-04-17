# AI 세금신고 도우미 — CTO 기술 아키텍처 설계서 v1.0

**작성자**: CTO (Wave 시스템)
**작성일**: 2026-04-03
**기반 문서**: CLAUDE.md v1.0, PRD.md v1.0
**프로젝트 상태**: CONDITIONAL_GO (5.25/10) — MVP 범위 엄수 필수

---

## 1. 기술 스택 결정

| 항목 | 선택 | 이유 |
|------|------|------|
| Framework | Next.js 14 (App Router) | Server Component + Route Handler 통합, SEO 필수인 랜딩 페이지 SSR, Vercel 최적 배포 궁합 |
| UI 컴포넌트 | shadcn/ui + Tailwind CSS | 접근성 내장, 커스터마이징 자유도 높음, 1인 팀 속도 극대화 |
| 차트 | Recharts | 경비 대시보드 월별/카테고리 시각화에 충분, shadcn/ui와 통합 잘 됨 |
| 상태관리 | Zustand + TanStack Query | 클라이언트 전역 상태(Zustand) + 서버 데이터 캐싱/동기화(TanStack Query) 역할 분리 |
| DB | PostgreSQL + Prisma ORM | 관계형 데이터 모델 최적, Prisma 타입 안전성, Vercel Postgres 또는 Supabase 연동 용이 |
| 인증 | NextAuth.js v5 | 카카오/구글 소셜 로그인, 세션/JWT 관리, App Router 완전 지원 |
| OCR (1차) | Google Cloud Vision API | 한글 인식 정확도 우수, REST API 연동 간단, 비용 대비 성능 검증됨 |
| OCR (2차 보완) | GPT-4o Vision | Vision API 실패/저신뢰도 케이스 폴백, 복잡한 영수증 레이아웃 처리 |
| AI 분류 | OpenAI GPT-4o | OCR 결과 → 경비 카테고리 자동 분류, 종합소득세 공제 항목 매핑 |
| 결제 | Stripe | 월/연간 구독, 웹훅 안정성, 국내 카드 지원 (토스페이먼츠는 2차 검토) |
| 스토리지 | AWS S3 (또는 Vercel Blob) | 영수증 원본 이미지 저장, 처리 후 삭제 옵션 대응, presigned URL로 직접 업로드 |
| 배포 | Vercel | Next.js 최적 환경, Edge Function 활용, CI/CD 자동화, Preview 배포 |
| PDF 생성 | @react-pdf/renderer | 신고서 초안 PDF 출력, 서버사이드 렌더링 지원 |
| Excel 생성 | xlsx (SheetJS) | 신고서 초안 Excel 출력, 경량 라이브러리 |
| 이메일 | Resend | 이메일 인증, 결제 확인 알림, React Email 템플릿 통합 |
| 모니터링 | Sentry | 에러 추적, OCR 실패율 모니터링 |

---

## 2. DB 스키마

> 모든 모델은 Prisma ORM으로 관리. `schema.prisma` 기준으로 작성.

```prisma
// ──────────────────────────────────────────────
// User: 회원 기본 정보 + 플랜 상태
// ──────────────────────────────────────────────
model User {
  id             String    @id @default(cuid())
  email          String    @unique
  name           String?
  emailVerified  DateTime?
  image          String?
  passwordHash   String?                         // 소셜 로그인은 null
  planStatus     PlanStatus @default(FREE)       // FREE | PREMIUM
  trialStartedAt DateTime?                       // 무료 체험 시작일
  createdAt      DateTime  @default(now())
  updatedAt      DateTime  @updatedAt

  // Relations
  accounts        Account[]
  sessions        Session[]
  businessProfile BusinessProfile?
  receipts        Receipt[]
  expenseItems    ExpenseItem[]
  taxReturns      TaxReturn[]
  subscription    Subscription?
  usageLogs       UsageLog[]
}

enum PlanStatus {
  FREE
  PREMIUM
  EXPIRED
}

// ──────────────────────────────────────────────
// BusinessProfile: 사업자 프로필
// 업종/과세유형에 따라 공제 항목 계산이 달라지므로 필수
// ──────────────────────────────────────────────
model BusinessProfile {
  id                 String       @id @default(cuid())
  userId             String       @unique
  businessType       String       // 국세청 업종코드 (예: "940909" 프리랜서)
  businessTypeLabel  String       // 사람이 읽을 수 있는 업종명 (예: "프리랜서/IT")
  taxationType       TaxationType // 과세유형
  registrationNumber String?      // 사업자등록번호 (선택, 미입력 시 null)
  taxYear            Int          // 신고 대상 연도 (기본값: 전년도)
  createdAt          DateTime     @default(now())
  updatedAt          DateTime     @updatedAt

  user User @relation(fields: [userId], references: [id], onDelete: Cascade)
}

enum TaxationType {
  GENERAL    // 일반과세자
  SIMPLIFIED // 간이과세자
  TAX_FREE   // 면세사업자
  INCOME_ONLY // 소득세만 해당 (프리랜서)
}

// ──────────────────────────────────────────────
// Receipt: 영수증 원본 메타데이터
// 이미지는 S3에 저장, imageUrl은 presigned URL 또는 S3 키
// ──────────────────────────────────────────────
model Receipt {
  id           String        @id @default(cuid())
  userId       String
  imageUrl     String        // S3 Object Key (만료 후 접근 불가 처리)
  imageDeleted Boolean       @default(false) // 원본 삭제 옵션 반영
  ocrRawText   String?       // Google Vision API 원본 응답 텍스트
  ocrConfidence Float?       // OCR 신뢰도 점수 (0~1)
  ocrEngine    OcrEngine     @default(GOOGLE_VISION)
  status       ReceiptStatus @default(PENDING)
  uploadedAt   DateTime      @default(now())
  processedAt  DateTime?     // OCR 완료 시각

  user         User          @relation(fields: [userId], references: [id], onDelete: Cascade)
  expenseItems ExpenseItem[]
}

enum OcrEngine {
  GOOGLE_VISION
  GPT4O_VISION  // 폴백 엔진
}

enum ReceiptStatus {
  PENDING    // 업로드됨, OCR 미처리
  PROCESSING // OCR 진행중
  COMPLETED  // OCR + AI 분류 완료
  FAILED     // OCR 실패
  MANUAL     // 수동 입력
}

// ──────────────────────────────────────────────
// ExpenseItem: AI 분류된 경비 항목
// 사용자 최종 확인(userVerified) 레이어가 법적 책임 분산의 핵심
// ──────────────────────────────────────────────
model ExpenseItem {
  id                String   @id @default(cuid())
  receiptId         String?  // 수동 입력 시 null 가능
  userId            String
  date              DateTime // 영수증 날짜
  amount            Int      // 원 단위 (소수점 제거, 반올림)
  merchantName      String   // 상호명
  category          ExpenseCategory
  isBusinessExpense Boolean  @default(true)  // 업무 관련 경비 여부
  userVerified      Boolean  @default(false) // 사용자가 최종 확인했는지
  memo              String?  // 사용자 메모
  taxYear           Int      // 귀속 연도
  createdAt         DateTime @default(now())
  updatedAt         DateTime @updatedAt

  receipt Receipt? @relation(fields: [receiptId], references: [id], onDelete: SetNull)
  user    User     @relation(fields: [userId], references: [id], onDelete: Cascade)
}

enum ExpenseCategory {
  OFFICE_SUPPLIES    // 사무용품
  COMMUNICATION      // 통신비
  TRANSPORTATION     // 교통비
  MEAL               // 식비/접대비
  EDUCATION          // 교육/도서비
  EQUIPMENT          // 장비/소프트웨어
  RENT               // 임차료
  INSURANCE          // 보험료
  ADVERTISING        // 광고/마케팅
  PROFESSIONAL_FEE   // 전문가 수수료 (세무사, 변호사 등)
  OTHER              // 기타
}

// ──────────────────────────────────────────────
// TaxReturn: 종합소득세 신고서 초안
// status: DRAFT(생성중) → READY(완료) → DOWNLOADED(다운로드됨)
// ──────────────────────────────────────────────
model TaxReturn {
  id              String          @id @default(cuid())
  userId          String
  taxYear         Int
  totalIncome     Int             // 연간 총 수입 (원)
  totalExpense    Int             // 인정된 총 경비 (원)
  estimatedTax    Int             // 예상 납부세액 (원)
  standardDeduction Int          // 기본 공제 합계
  taxBase         Int             // 과세표준 (totalIncome - totalExpense - standardDeduction)
  status          TaxReturnStatus @default(DRAFT)
  generatedAt     DateTime        @default(now())
  downloadedAt    DateTime?
  pdfUrl          String?         // 생성된 PDF S3 키 (임시 저장)
  excelUrl        String?         // 생성된 Excel S3 키 (임시 저장)

  user User @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@unique([userId, taxYear]) // 연도별 1개 제한
}

enum TaxReturnStatus {
  DRAFT       // 생성 중
  READY       // 완료, 다운로드 가능
  DOWNLOADED  // 사용자가 다운로드함
}

// ──────────────────────────────────────────────
// Subscription: Stripe 구독 정보
// ──────────────────────────────────────────────
model Subscription {
  id                   String             @id @default(cuid())
  userId               String             @unique
  plan                 SubscriptionPlan
  stripeCustomerId     String             @unique
  stripeSubscriptionId String?            @unique
  stripePriceId        String?
  status               SubscriptionStatus @default(ACTIVE)
  currentPeriodEnd     DateTime
  cancelAtPeriodEnd    Boolean            @default(false)
  createdAt            DateTime           @default(now())
  updatedAt            DateTime           @updatedAt

  user User @relation(fields: [userId], references: [id], onDelete: Cascade)
}

enum SubscriptionPlan {
  MONTHLY // 월 9,900원
  ANNUAL  // 연 79,200원
}

enum SubscriptionStatus {
  ACTIVE
  PAST_DUE    // 결제 실패
  CANCELED
  TRIALING
}

// ──────────────────────────────────────────────
// UsageLog: 무료 플랜 한도 추적 + 감사 로그
// ──────────────────────────────────────────────
model UsageLog {
  id        String     @id @default(cuid())
  userId    String
  action    UsageAction
  metadata  Json?      // 추가 컨텍스트 (예: receiptId, taxYear 등)
  createdAt DateTime   @default(now())

  user User @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@index([userId, action, createdAt]) // 한도 집계 쿼리 최적화
}

enum UsageAction {
  RECEIPT_UPLOAD    // 영수증 업로드 (무료: 20건/월 제한)
  TAX_RETURN_GENERATE // 신고서 생성 (무료: 1회/년 제한)
  PDF_DOWNLOAD
  EXCEL_DOWNLOAD
}

// ──────────────────────────────────────────────
// NextAuth.js v5 필수 모델 (변경 금지)
// ──────────────────────────────────────────────
model Account {
  id                String  @id @default(cuid())
  userId            String
  type              String
  provider          String
  providerAccountId String
  refresh_token     String?
  access_token      String?
  expires_at        Int?
  token_type        String?
  scope             String?
  id_token          String?
  session_state     String?

  user User @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@unique([provider, providerAccountId])
}

model Session {
  id           String   @id @default(cuid())
  sessionToken String   @unique
  userId       String
  expires      DateTime

  user User @relation(fields: [userId], references: [id], onDelete: Cascade)
}

model VerificationToken {
  identifier String
  token      String   @unique
  expires    DateTime

  @@unique([identifier, token])
}
```

---

## 3. API 엔드포인트 구조

> 모든 엔드포인트는 `app/api/` 하위 Route Handler로 구현. 인증 필요 엔드포인트는 `[auth]` 표시.

### 인증 (NextAuth.js)
| 메서드 | 경로 | 설명 |
|--------|------|------|
| POST | `/api/auth/[...nextauth]` | NextAuth.js 소셜/이메일 로그인 처리 |
| POST | `/api/auth/register` | 이메일 회원가입 (비밀번호 해싱 후 DB 저장) |
| POST | `/api/auth/verify-email` | 이메일 인증 토큰 확인 |
| POST | `/api/auth/forgot-password` | 비밀번호 재설정 메일 발송 |
| POST | `/api/auth/reset-password` | 토큰 검증 후 비밀번호 변경 |

### 사업자 프로필
| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/api/profile` [auth] | 내 사업자 프로필 조회 |
| POST | `/api/profile` [auth] | 온보딩 시 최초 프로필 생성 |
| PUT | `/api/profile` [auth] | 프로필 수정 (업종/과세유형/신고연도) |

### 영수증 & OCR
| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/api/receipts` [auth] | 영수증 목록 조회 (페이지네이션, 날짜 필터) |
| POST | `/api/receipts/upload-url` [auth] | S3 presigned upload URL 발급 (직접 업로드용) |
| POST | `/api/receipts` [auth] | 업로드 완료 후 Receipt DB 레코드 생성 + OCR 큐 등록 |
| GET | `/api/receipts/[id]` [auth] | 영수증 상세 + OCR 결과 조회 |
| DELETE | `/api/receipts/[id]` [auth] | 영수증 + S3 이미지 삭제 (개인정보 삭제 옵션) |
| POST | `/api/receipts/[id]/process` [auth] | OCR 재처리 요청 (실패한 영수증 재시도) |

### 경비 항목
| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/api/expenses` [auth] | 경비 목록 조회 (연도/카테고리/월 필터) |
| POST | `/api/expenses` [auth] | 경비 수동 추가 (영수증 없이) |
| PUT | `/api/expenses/[id]` [auth] | 경비 항목 수정 (카테고리 보정, 금액 수정, 검증 완료) |
| DELETE | `/api/expenses/[id]` [auth] | 경비 항목 삭제 |
| GET | `/api/expenses/summary` [auth] | 연간/월별 경비 집계 (대시보드용) |

### 신고서
| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/api/tax-returns` [auth] | 신고서 목록 조회 |
| POST | `/api/tax-returns` [auth] | 신고서 생성 요청 (소득 입력 포함) |
| GET | `/api/tax-returns/[id]` [auth] | 신고서 상세 조회 |
| GET | `/api/tax-returns/[id]/download` [auth] | PDF 또는 Excel 다운로드 (query: `?format=pdf|excel`) |
| DELETE | `/api/tax-returns/[id]` [auth] | 신고서 삭제 |

### 구독 & 결제 (Stripe)
| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/api/subscription` [auth] | 현재 구독 상태 조회 |
| POST | `/api/subscription/checkout` [auth] | Stripe Checkout 세션 생성 (월/연간 플랜) |
| POST | `/api/subscription/portal` [auth] | Stripe Customer Portal 세션 생성 (구독 관리) |
| POST | `/api/subscription/cancel` [auth] | 구독 해지 예약 (기간 만료 후 해지) |
| POST | `/api/webhooks/stripe` | Stripe 웹훅 수신 (결제 완료/실패/구독 갱신) — 인증 없음, Stripe 서명 검증 |

### 사용량 조회
| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/api/usage` [auth] | 현재 월 영수증 업로드 수, 이번 연도 신고서 생성 수 조회 |

---

## 4. OCR 파이프라인

### 전체 플로우

```
[사용자]
   │
   │ 1. 영수증 촬영 or 갤러리 선택
   ↓
[FE: ReceiptUploader 컴포넌트]
   │
   │ 2. POST /api/receipts/upload-url 호출
   │    → 무료 플랜 한도 체크 (UsageLog 집계)
   │    → 한도 초과 시 페이월 반환 (402)
   ↓
[BE: S3 Presigned URL 발급]
   │
   │ 3. FE가 S3에 이미지 직접 업로드 (서버 메모리 우회)
   ↓
[FE → BE]
   │
   │ 4. POST /api/receipts (S3 Key 전달)
   │    → Receipt DB 레코드 생성 (status: PENDING)
   │    → UsageLog 기록
   ↓
[BE: OCR Worker (Route Handler 또는 Vercel Edge Function)]
   │
   │ 5. 전처리
   │    - 이미지 크기 검증 (최대 10MB)
   │    - 이미지 포맷 정규화 (JPEG/PNG/WEBP → JPEG)
   │    - 해상도 보정 (최소 300dpi 권장)
   │    → status: PROCESSING 업데이트
   │
   │ 6. Google Cloud Vision API 호출 (TEXT_DETECTION)
   │    - 전체 텍스트 추출
   │    - 신뢰도 점수(ocrConfidence) 저장
   │    - 신뢰도 < 0.7이면 GPT-4o Vision으로 폴백
   │
   │ 7. GPT-4o Vision 폴백 (필요 시)
   │    - Vision API 실패 or 저신뢰도 케이스
   │    - 한글 손글씨, 열감지 영수증 등 처리
   │    - ocrEngine: GPT4O_VISION 기록
   ↓
[BE: AI 분류 (GPT-4o)]
   │
   │ 8. OCR 텍스트 → 구조화된 데이터 추출
   │    프롬프트 입력:
   │    - OCR 원본 텍스트
   │    - 사용자 업종코드 + 과세유형
   │    - 국세청 경비 카테고리 목록
   │
   │    출력 (JSON):
   │    {
   │      date: "2025-03-15",
   │      amount: 45000,
   │      merchantName: "스타벅스 강남점",
   │      category: "MEAL",
   │      isBusinessExpense: true,
   │      confidence: 0.92
   │    }
   │
   │ 9. ExpenseItem DB 저장
   │    - userVerified: false (사용자 확인 대기)
   │    → status: COMPLETED 업데이트
   ↓
[FE: 결과 표시]
   │
   │ 10. TanStack Query 폴링 or 웹소켓으로 상태 감지
   │     - 분류 결과 카드 표시
   │     [날짜 | 금액 | 상호명 | 카테고리]
   │
   │ 11. 사용자 검토 & 수정
   │     - 카테고리 드롭다운 변경 가능
   │     - "사업 관련 경비 맞음" 토글
   │     - 금액/날짜 직접 수정 가능
   │
   │ 12. 저장 버튼 클릭
   │     → PUT /api/expenses/[id] (userVerified: true)
   ↓
[완료]
   - 대시보드 경비 집계 자동 반영
   - 원본 이미지 삭제 요청 옵션 제공 (개인정보 보호)
```

### OCR 엔진 선택 기준

| 상황 | 엔진 | 이유 |
|------|------|------|
| 일반 영수증 (인쇄체) | Google Cloud Vision | 빠르고 저렴함 (1,000건당 $1.5) |
| 신뢰도 < 0.7 | GPT-4o Vision 폴백 | 복잡한 레이아웃, 손글씨 처리 |
| Vision API 타임아웃 | GPT-4o Vision 폴백 | 장애 대응 |

### 에러 처리

- OCR 실패 시: `status: FAILED` 기록, FE에서 수동 입력 안내
- AI 분류 실패 시: OCR 텍스트는 저장, category: OTHER로 기본 분류, 사용자에게 수동 수정 유도
- 10초 타임아웃: 처리 중 상태 유지, 비동기 폴링으로 완료 감지

---

## 5. Engineering Rules

다음 5가지 규칙은 FE/BE 모든 코드에 예외 없이 적용한다.

### Rule 1. 세무 면책 문구 모든 UI에 강제 표시
**배경**: 홈택스 자동 제출 금지, 세무 대리 행위 아님을 법적으로 명확히 해야 함.
- 모든 신고서 관련 페이지에 고정 배너 표시: *"이 서비스는 신고 준비 도구입니다. 최종 신고 책임은 사용자에게 있습니다."*
- ExpenseItem의 `userVerified: false` 항목이 있으면 신고서 생성 불가 — 반드시 사용자가 모든 경비를 확인해야 함.
- API 레벨에서도 `userVerified` 검사 후 TaxReturn 생성 허용.

### Rule 2. 개인정보 최소 수집 + 즉시 삭제 옵션 필수
**배경**: 영수증에는 개인 거래 정보가 담겨 있음. 한서윤 보안 아키텍처 반영.
- 영수증 원본 이미지는 OCR 처리 완료 후 사용자 선택에 따라 S3에서 즉시 삭제 가능 (`imageDeleted: true`).
- S3 Bucket에 수명 주기 정책 설정: 기본 90일 후 자동 삭제 (유료 플랜은 연장 가능).
- OCR 원본 텍스트(`ocrRawText`)는 암호화 저장 (Prisma 레벨 AES-256 또는 PostgreSQL 컬럼 암호화).
- 회원 탈퇴 시 모든 영수증, 경비 항목, 신고서, S3 이미지 즉시 삭제 (`onDelete: Cascade` 적용됨).

### Rule 3. 무료 플랜 한도는 API 레벨에서만 검증
**배경**: FE에서만 막으면 우회 가능. 수익 모델 검증의 핵심.
- `/api/receipts`, `/api/tax-returns` POST 핸들러에서 반드시 `checkUsageLimit()` 함수 호출.
- 한도 초과 시 HTTP 402 반환 + 페이월 유도 메시지 포함.
- FE는 `/api/usage` 조회 결과로 UI 비활성화 표시 (UX 보조), 실제 차단은 BE에서.
- 한도 기준: 영수증 20건/월(달력월 기준), 신고서 1회/년(연도 기준).

### Rule 4. 타입 안전성 — `any` 금지, Zod 스키마 의무화
**배경**: OCR/AI 응답은 불확실함. 타입 오류가 세금 계산 버그로 이어질 수 있음.
- `tsconfig.json`: `"strict": true`, `"noImplicitAny": true` 필수.
- 모든 API Route Handler의 request body는 Zod 스키마로 파싱 (`z.parse()` or `z.safeParse()`).
- GPT-4o 응답은 반드시 JSON Schema 명세 후 `response_format: { type: "json_object" }` 사용.
- Prisma 반환 타입 직접 사용 (`Prisma.ExpenseItemGetPayload<...>`), 별도 인터페이스 중복 선언 금지.

### Rule 5. 금액 계산은 정수(원 단위)로만, 부동소수점 금지
**배경**: 세금 계산에서 `0.1 + 0.2 = 0.30000000000000004` 같은 부동소수점 오류는 치명적.
- 모든 금액은 원(KRW) 단위 정수로 저장 (`Int` 타입, 소수점 없음).
- OCR/AI가 소수점 금액 반환 시 `Math.round()` 처리 후 저장.
- 세금 계산 로직은 별도 `lib/tax-calculator.ts`에 분리, 순수 함수로 작성, 단위 테스트 필수.
- 화면 표시 시만 `toLocaleString('ko-KR')` 포맷팅 적용.

---

## 6. 기술 리스크

### Risk 1. 세무사법 위반 — 세무 대리 행위 경계선
| 항목 | 내용 |
|------|------|
| 리스크 | 홈택스 자동 제출, 실시간 세무 상담 챗봇 기능이 세무사법 제2조(세무 대리) 위반으로 해석될 수 있음 |
| 발생 시 영향 | 서비스 강제 중단, 형사 처벌 (2년 이하 징역 또는 2,000만 원 이하 벌금) |
| 완화 전략 | MVP에서 홈택스 자동 제출/챗봇 기능 절대 금지 (PRD Must NOT 준수). 모든 UI 문구 "신고 준비 도구", "참고용", "최종 책임은 사용자에게" 명시. 법무법인 자문 후 서비스 오픈. |
| 담당 | 한서윤(컴플라이언스) + 외부 세무사법 전문 법무법인 |

### Risk 2. OCR 정확도 — AI 분류 오류로 인한 세금 신고 오류
| 항목 | 내용 |
|------|------|
| 리스크 | Google Vision API 한글 인식률 실제 운영 환경에서 90% 미만 가능. 열감지 영수증, 손글씨, 저해상도 이미지에서 오류 빈발. AI 분류 오류가 잘못된 공제 항목으로 이어짐. |
| 발생 시 영향 | 사용자 신뢰 손상, 잘못된 세금 신고로 인한 가산세 → 법적 책임 클레임 가능성 |
| 완화 전략 | 하이브리드 OCR (Google Vision 주, GPT-4o 폴백). `userVerified: false` 항목은 신고서 생성 차단. 신뢰도 낮은 항목 강조 표시 (빨간 테두리). 이미지 업로드 가이드 UX (밝은 조명, 평평하게 찍기). Sentry로 OCR 실패율 모니터링, 월 5% 초과 시 알림. |
| 목표 정확도 | 1차 MVP: 85% 이상 (수동 수정 허용) → 2차: 97% 목표 (서진혁 OCR 설계 반영) |

### Risk 3. API 비용 — GPT-4o / Google Vision 비용 폭증
| 항목 | 내용 |
|------|------|
| 리스크 | 무료 플랜 사용자가 대량의 영수증을 업로드하면 GPT-4o Vision 비용이 수익보다 커짐. GPT-4o Vision 1회 처리 비용 약 $0.02~0.05 (이미지 크기 의존) |
| 발생 시 영향 | API 비용 > 구독 수익 → 사업 지속 불가 |
| 완화 전략 | 무료 플랜 영수증 20건/월 하드 리밋. Google Vision을 1차 엔진으로 사용 (GPT-4o 대비 약 10배 저렴). GPT-4o 폴백은 신뢰도 0.7 미만 케이스에만 적용 (예상 폴백률 15~20%). 월별 API 비용 대시보드 모니터링, 임계값 초과 시 Slack 알림. 장기적으로 Fine-tuned 경량 모델로 분류 비용 절감 검토. |
| 비용 추정 | 무료 사용자 1명: Google Vision $0.03 + GPT-4o 분류 $0.01 × 20건 = 월 $0.8. 유료 전환율 5%라면 1,000 무료 사용자 기준 월 $800 API 비용 vs 50명 유료 수익 495,000원(약 $375) → 초기 적자 구간 인식하고 무료 한도 조정 레버 확보 필수. |

### Risk 4. 데이터 보안 — 영수증/소득 정보 유출
| 항목 | 내용 |
|------|------|
| 리스크 | 영수증 원본 이미지, 사업자등록번호, 연간 소득/경비 데이터는 민감 개인정보. S3 버킷 설정 오류, SQL 인젝션, 세션 하이재킹 시 대규모 개인정보 유출 가능. |
| 발생 시 영향 | 개인정보보호법 위반 과징금 (매출의 3% 이하). 서비스 신뢰 붕괴. |
| 완화 전략 | S3 Presigned URL 방식으로 서버 직접 업로드 차단 (URL 만료: 5분). S3 Bucket: 퍼블릭 액세스 완전 차단, 서버사이드 암호화 (SSE-S3). PostgreSQL 민감 컬럼 (ocrRawText, registrationNumber) AES-256 암호화. NextAuth.js 세션 토큰 HTTPS 전용 쿠키. Rate Limiting 적용 (Upstash Redis): 로그인 10회/분, 업로드 5회/분. 환경변수 `.env` 절대 커밋 금지, Vercel 환경변수로만 관리. 한서윤 보안 아키텍처 문서 기반 침투 테스트 오픈 전 필수. |

---

## 부록: 프로젝트 디렉토리 구조

```
ai-tax-assistant/
├── app/
│   ├── (auth)/
│   │   ├── login/page.tsx
│   │   ├── signup/page.tsx
│   │   └── onboarding/page.tsx
│   ├── (dashboard)/
│   │   ├── dashboard/page.tsx         # 경비 대시보드
│   │   ├── receipts/page.tsx          # 영수증 목록
│   │   ├── receipts/[id]/page.tsx     # 영수증 상세
│   │   ├── expenses/page.tsx          # 경비 항목 관리
│   │   ├── tax-return/page.tsx        # 신고서 생성/목록
│   │   └── settings/page.tsx          # 계정/구독 설정
│   ├── api/
│   │   ├── auth/[...nextauth]/route.ts
│   │   ├── auth/register/route.ts
│   │   ├── profile/route.ts
│   │   ├── receipts/
│   │   │   ├── route.ts               # GET(목록), POST(생성)
│   │   │   ├── upload-url/route.ts    # S3 presigned URL 발급
│   │   │   └── [id]/
│   │   │       ├── route.ts           # GET, DELETE
│   │   │       └── process/route.ts   # OCR 재처리
│   │   ├── expenses/
│   │   │   ├── route.ts
│   │   │   ├── summary/route.ts
│   │   │   └── [id]/route.ts
│   │   ├── tax-returns/
│   │   │   ├── route.ts
│   │   │   └── [id]/
│   │   │       ├── route.ts
│   │   │       └── download/route.ts
│   │   ├── subscription/
│   │   │   ├── route.ts
│   │   │   ├── checkout/route.ts
│   │   │   ├── portal/route.ts
│   │   │   └── cancel/route.ts
│   │   ├── usage/route.ts
│   │   └── webhooks/stripe/route.ts
│   ├── page.tsx                       # 랜딩 페이지
│   └── layout.tsx
├── components/
│   ├── ui/                            # shadcn/ui 기본 컴포넌트
│   ├── receipt/
│   │   ├── ReceiptUploader.tsx        # 영수증 업로드 + OCR 트리거
│   │   ├── ReceiptCard.tsx
│   │   └── OcrResultEditor.tsx        # 분류 결과 수정 UI
│   ├── expense/
│   │   ├── ExpenseTable.tsx
│   │   ├── ExpenseSummaryChart.tsx    # Recharts 월별/카테고리
│   │   └── CategorySelector.tsx
│   ├── tax-return/
│   │   ├── TaxReturnForm.tsx          # 소득 입력 폼
│   │   └── TaxReturnPreview.tsx
│   └── shared/
│       ├── DisclaimerBanner.tsx       # 세무 면책 문구 고정 배너
│       ├── PaywallModal.tsx           # 무료 한도 초과 페이월
│       └── UsageMeter.tsx             # 이번 달 사용량 표시
├── lib/
│   ├── auth.ts                        # NextAuth.js 설정
│   ├── db.ts                          # Prisma Client 싱글톤
│   ├── s3.ts                          # S3 클라이언트 + presigned URL
│   ├── ocr/
│   │   ├── google-vision.ts           # Google Cloud Vision API 래퍼
│   │   ├── gpt4o-vision.ts            # GPT-4o Vision 폴백
│   │   └── pipeline.ts                # OCR 파이프라인 오케스트레이터
│   ├── ai/
│   │   └── expense-classifier.ts      # GPT-4o 경비 분류
│   ├── tax-calculator.ts              # 종합소득세 계산 순수 함수
│   ├── stripe.ts                      # Stripe 클라이언트
│   ├── usage.ts                       # 무료 플랜 한도 체크
│   └── validators/                    # Zod 스키마 모음
│       ├── receipt.ts
│       ├── expense.ts
│       └── tax-return.ts
├── prisma/
│   └── schema.prisma
├── .env.local                         # 절대 커밋 금지
└── tsconfig.json                      # strict: true 필수
```

---

> 이 문서는 Wave 시스템 CTO 역할이 PRD.md + CLAUDE.md를 기반으로 설계한 기술 아키텍처 설계서입니다.
> 구현 시작 전 반드시 이 문서를 기준으로 FE/BE 개발자와 공유하고 Engineering Rules 5가지를 팀 전체가 숙지해야 합니다.
