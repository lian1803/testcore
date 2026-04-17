# FE 구현 완료

**작성자**: FE 민준
**완료일**: 2026-04-03
**구현 범위**: FE-1 ~ FE-12 전 태스크

---

## 완성된 화면

| 화면 | 경로 | 상태 |
|------|------|------|
| 랜딩 페이지 | `/` | 완료 |
| 로그인 | `/login` | 완료 |
| 회원가입 | `/signup` | 완료 |
| 온보딩 (3단계 Wizard) | `/onboarding` | 완료 |
| 대시보드 홈 | `/dashboard` | 완료 |
| 영수증 업로드 | `/dashboard/receipts` | 완료 |
| 경비 목록 | `/dashboard/expenses` | 완료 |
| 신고서 생성 | `/dashboard/tax-return` | 완료 |
| 설정 / 결제 | `/dashboard/settings` | 완료 |

---

## 완성된 컴포넌트

### shadcn/ui 기반 UI 컴포넌트 (src/components/ui/)
- `button.tsx` — variant: default/accent/destructive/outline/secondary/ghost/link, loading 상태 포함
- `input.tsx` — error 상태 (border-error 적용)
- `card.tsx` — Card/CardHeader/CardTitle/CardDescription/CardContent/CardFooter
- `badge.tsx` — 카테고리별 컬러 variant (meal/transportation/communication/office/education)
- `progress.tsx` — Radix Progress, primary 컬러
- `label.tsx` — Radix Label
- `select.tsx` — Radix Select (SelectTrigger/SelectContent/SelectItem/SelectLabel)
- `dialog.tsx` — Radix Dialog (모달 오버레이)
- `switch.tsx` — Radix Switch, accent 체크 컬러
- `tabs.tsx` — Radix Tabs
- `radio-group.tsx` — Radix RadioGroup
- `toast.tsx` — Radix Toast (default/success/error variant)

### 랜딩 (src/components/landing/)
- `Navbar.tsx` — sticky, 스크롤 backdrop-blur, 모바일 메뉴
- `HeroSection.tsx` — primary 배경, 영수증→분류 결과 목업 카드
- `FeatureCards.tsx` — 3개 카드 grid
- `TrustSection.tsx` — 3개 수치 (97%/10초/40만원)
- `PricingSection.tsx` — 무료/프리미엄, ring-accent 강조
- `Footer.tsx` — 법적 고지 문구 포함

### 인증 (src/components/auth/)
- `LoginForm.tsx` — 이메일/비밀번호, 실시간 유효성 검사, 로딩 버튼
- `SignupForm.tsx` — 이름/이메일/비밀번호/이용약관, 특수문자 검증
- `SocialLoginButtons.tsx` — 구글(#FEE500), 카카오
- `PasswordInput.tsx` — 눈 아이콘 토글

### 온보딩 (src/components/onboarding/)
- `OnboardingWizard.tsx` — 3단계, 슬라이드 전환, API POST /api/profile
- `StepIndicator.tsx` — Progress 바 + 완료/현재/미완료 스텝 시각화
- `Step1BusinessType.tsx` — 업종 드롭다운, 공제 항목 힌트 동적 표시
- `Step2TaxationType.tsx` — 과세유형 RadioGroup, 사업자등록번호
- `Step3TaxYear.tsx` — 연도 선택, 신고 기간 안내 박스

### 레이아웃 (src/components/layout/)
- `Sidebar.tsx` — 데스크탑 w-64 고정, 로고/네비/사용량/유저프로필
- `SidebarNav.tsx` — 5개 메뉴, 활성 상태 primary 배경
- `HeaderBar.tsx` — 모바일 드로어 (Sheet 패턴)
- `UserProfile.tsx` — 이니셜 아바타, hover 시 로그아웃 버튼
- `UsageMeter.tsx` — Progress 바, 80% 이상 error 컬러

### 대시보드 (src/components/dashboard/)
- `KpiCards.tsx` — 4개 KPI (총경비/세액/영수증수/절세액), accent border
- `MonthlyExpenseChart.tsx` — Recharts StackedBarChart, 카테고리 컬러, 커스텀 Tooltip
- `RecentReceiptsList.tsx` — 최근 5건, 카테고리 뱃지, 상대시간

### 영수증 (src/components/receipt/, src/components/receipts/)
- `ReceiptUploader.tsx` — 드래그앤드롭 + 클릭, isDragOver 상태
- `OcrLoadingOverlay.tsx` — scan-line 애니메이션, 5단계 진행 텍스트
- `OcrResultEditor.tsx` — 날짜/금액/상호명/카테고리 수정, 신뢰도 낮은 필드 노란 배경
- `ReceiptCard.tsx` — 카드 형태, 신뢰도 아이콘, 삭제 버튼

### 경비 (src/components/expenses/)
- `ExpenseTable.tsx` — 테이블 (날짜/상호명/분류/금액/확인/삭제), 합계 row
- `ExpenseRow.tsx` — 카테고리 뱃지, userVerified 체크 아이콘
- `ExpenseFilters.tsx` — 카테고리 + 날짜 범위 필터, 초기화

### 신고서 (src/components/tax-return/)
- `TaxReturnForm.tsx` — 매출액/기타소득 입력, 법적 고지 배너
- `TaxReturnPreview.tsx` — 수입/경비/과세표준/세액 테이블, 카테고리별 내역
- `DownloadButtons.tsx` — PDF/Excel, 홈택스 입력 가이드 모달 (6단계)

### 공통 (src/components/common/)
- `LegalBanner.tsx` — warning 배너, 모든 대시보드 페이지 상단 고정
- `LoadingSpinner.tsx` — sm/md/lg 사이즈
- `ErrorMessage.tsx` — 아이콘 + 제목 + 재시도 버튼
- `EmptyState.tsx` — 아이콘 + 설명 + CTA 버튼
- `ConfirmDialog.tsx` — destructive 지원, loading 상태

### 상태관리 / 훅 (src/store/, src/hooks/, src/providers/)
- `auth.store.ts` — Zustand (user, isAuthenticated)
- `receipt.store.ts` — Zustand (uploadStatus, ocrStage, progress)
- `use-receipts.ts` — TanStack Query (GET receipts, DELETE)
- `use-expenses.ts` — TanStack Query (GET list, summary, PATCH, DELETE)
- `use-tax-return.ts` — TanStack Query (POST 생성, GET, 다운로드)
- `use-usage.ts` — TanStack Query (GET /api/usage, 1분 refetch)
- `query-provider.tsx` — QueryClientProvider

---

## BE에게 필요한 것

### API 엔드포인트 목록

| 메서드 | 경로 | 요청 바디 | 응답 |
|--------|------|-----------|------|
| POST | /api/auth/register | `{name, email, password}` | `{user}` |
| POST | /api/auth/login | `{email, password}` | `{user, token}` |
| GET | /api/auth/signin/google | - | redirect |
| POST | /api/profile | `{businessType, taxationType, registrationNumber, taxYear}` | `{profile}` |
| POST | /api/receipts/upload | `FormData(file: File)` | `{receipt, ocrResult}` |
| GET | /api/receipts | - | `MockReceipt[]` |
| DELETE | /api/receipts/[id]` | - | `{ok}` |
| GET | /api/expenses | `?category&dateFrom&dateTo` | `MockExpenseItem[]` |
| GET | /api/expenses/summary | - | `{kpi: MockKpiData, monthly: MockMonthlyData[]}` |
| POST | /api/expenses | `{...OcrResult, isBusinessExpense, memo}` | `{expense}` |
| PATCH | /api/expenses/[id] | `Partial<MockExpenseItem>` | `{expense}` |
| DELETE | /api/expenses/[id] | - | `{ok}` |
| POST | /api/tax-return | `{totalIncome, otherIncome, taxYear}` | `MOCK_TAX_RETURN 형태` |
| GET | /api/tax-return/[id] | - | `MOCK_TAX_RETURN 형태` |
| GET | /api/tax-return/[id]/download | `?format=pdf|excel` | `Blob` |
| GET | /api/usage | - | `{receiptUsed, receiptLimit, taxReturnUsed, taxReturnLimit}` |
| POST | /api/billing/checkout | `{plan: "monthly"|"annual"}` | `{url: string}` (Stripe URL) |

### OCR 결과 응답 형식 (POST /api/receipts/upload)
```json
{
  "receipt": { "id": "...", "imageUrl": "...", "status": "COMPLETED" },
  "ocrResult": {
    "merchantName": "스타벅스 강남역점",
    "date": "2025-03-20",
    "amount": 15500,
    "category": "MEAL",
    "confidence": 0.94,
    "lowConfidenceFields": ["date"],
    "classificationReason": "상호명 기반 자동 분류"
  }
}
```

### 중요 사항
- 모든 API는 인증된 사용자만 접근 가능 (NextAuth 세션 검증)
- 영수증 원본 이미지는 S3 presigned URL로 직접 업로드 또는 API Route를 통해 전달
- 신고서 다운로드 응답은 Content-Type: application/pdf 또는 application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
- 결제는 Stripe Checkout Session 생성 후 redirect URL 반환
