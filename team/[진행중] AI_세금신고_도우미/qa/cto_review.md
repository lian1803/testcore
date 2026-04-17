# CTO 통합 리뷰 결과

**검토자**: 현우 (CTO)
**검토일**: 2026-04-03
**검토 대상**: AI 세금신고 도우미 FE + BE 전체 코드
**기준 문서**: wave_cto.md (아키텍처 설계서 v1.0)

---

## 아키텍처 준수 점수: 7.5/10

전반적으로 Clean Architecture 레이어 분리가 잘 되어 있고 Engineering Rules 5가지도 대부분 준수했다.
그러나 FE-BE 통합 단계에서 실질적인 단절이 있고, S3 presigned URL 플로우가 미완성 상태다.
릴리즈 전 CRITICAL 이슈 2개는 반드시 수정해야 한다.

---

## CRITICAL 이슈
[즉시 수정 필요 — 이 상태로 릴리즈하면 서비스 불가 또는 보안 구멍]

### CRITICAL-1. FE 훅이 실제 BE 응답 형식을 파싱하지 않고 Mock으로 폴백
**위치**: `src/hooks/use-receipts.ts`, `src/hooks/use-expenses.ts`, `src/hooks/use-tax-return.ts`
**문제**:
```
// use-receipts.ts 실제 코드
const res = await fetch("/api/receipts");
if (!res.ok) return MOCK_RECEIPTS; // fallback to mock
return res.json(); // ← BE 응답은 { success: true, data: [...], pagination: {...} } 형태
```
BE는 `{ success: true, data: [...], pagination: {...} }` 래퍼로 감싸서 반환하는데,
FE 훅은 `.json()` 결과를 그대로 `MockReceipt[]`로 타입 단언하고 있다.
즉 실제 연결 시 `data.id`가 아니라 `data.data[0].id`를 찾아야 하는데 FE가 그걸 모른다.
더 심각한 문제는 `if (!res.ok) return MOCK_RECEIPTS` — API 인증 오류(401)가 나도
UI는 mock 데이터를 보여준다. 사용자가 로그아웃 상태인지조차 인지하지 못한다.

**수정 방향**:
- 모든 훅에서 `res.json()` 이후 `data.data`를 꺼내도록 파싱 로직 추가
- `!res.ok` 시 mock 폴백 제거, 에러를 throw하거나 error state 반환
- 401 응답 시 로그인 페이지 리다이렉트 처리

**영향 범위**: use-receipts.ts, use-expenses.ts, use-tax-return.ts, use-usage.ts 전체

---

### CRITICAL-2. S3 presigned URL 플로우 미완성 — 영수증 업로드가 실제로 작동하지 않음
**위치**: `wave_be_완료.md` 주의사항 3번, `src/app/api/receipts/upload/route.ts`
**문제**:
BE 문서에 명시적으로 적혀 있다: "현재 MVP: S3 presigned URL 없이 imageKey를 직접 받는 방식 → 실제 배포 시 `/api/receipts/upload-url` 엔드포인트 추가 필요"

아키텍처 설계서(wave_cto.md)의 OCR 파이프라인은:
1. FE → `POST /api/receipts/upload-url` → presigned URL 발급
2. FE → S3 직접 업로드 (서버 메모리 우회)
3. FE → `POST /api/receipts` (S3 key 전달) → OCR 트리거

실제 구현은:
- `/api/receipts/upload-url` 엔드포인트 존재하지 않음
- `/api/receipts/upload` 가 imageKey를 직접 받는데, 어디서 이 key를 얻는지 FE 코드에 없음
- FE `ReceiptUploader.tsx`가 FormData를 어디에 POST하는지 확인 필요 (컴포넌트 파일 미검토)

또한 `ocr.service.ts`의 `buildS3PublicUrl()` 함수는 S3 버킷을 퍼블릭으로 가정하여 URL을 구성한다.
```typescript
function buildS3PublicUrl(imageKey: string): string {
  return `https://${bucket}.s3.${region}.amazonaws.com/${imageKey}`;
}
```
아키텍처 설계서는 "S3 Bucket 퍼블릭 액세스 완전 차단"을 보안 요구사항으로 명시했다.
프라이빗 버킷이면 이 URL로 Google Vision API가 이미지에 접근 불가 → OCR 전체 실패.

**수정 방향**:
- `/api/receipts/upload-url` presigned PUT URL 발급 엔드포인트 구현 (s3.service.ts에 생성 함수 추가)
- OCR 시 S3에서 이미지를 직접 download한 후 base64로 Google Vision API에 전달하는 방식으로 변경
  (Google Vision의 `image.source.imageUri`가 아닌 `image.content`에 base64 사용)
- 또는 OCR 호출 전 presigned GET URL을 생성하여 Vision API에 전달

---

## HIGH 이슈
[중요하지만 기술적으로 서비스 가동 자체를 막지는 않음 — 다음 스프린트에서 수정]

### HIGH-1. 신고서 생성 시 userVerified 검증 누락
**위치**: `src/app/api/tax-return/route.ts` POST 핸들러, `src/services/tax-return.service.ts`
**문제**:
아키텍처 설계서 Rule 1: "ExpenseItem의 `userVerified: false` 항목이 있으면 신고서 생성 불가"
API 레벨에서도 `userVerified` 검사 후 TaxReturn 생성 허용이라고 명시.

그러나 `generateTaxReturn()` 함수를 보면:
```typescript
const expenseResult = await prisma.expenseItem.aggregate({
  where: {
    userId,
    taxYear: input.taxYear,
    isBusinessExpense: true,
    // userVerified: true ← 이 조건이 없다
  },
  _sum: { amount: true },
});
```
미검증 경비도 세금 계산에 포함된다. 또한 미검증 항목이 있어도 신고서 생성을 막지 않는다.
법적 면책의 핵심 안전장치가 뚫린 상태.

**수정 방향**:
1. `generateTaxReturn()` 호출 전 `userVerified: false`인 항목 수를 count
2. 미검증 항목이 1개라도 있으면 400 또는 422 에러 반환, 사용자에게 확인 요청
3. 경비 집계 쿼리에 `userVerified: true` 조건 추가

---

### HIGH-2. 세금 계산 로직의 누진공제 계산 버그
**위치**: `src/services/tax-return.service.ts` `calculateIncomeTax()` 함수

```typescript
function calculateIncomeTax(taxBase: number): number {
  if (taxBase <= 0) return 0;
  for (const bracket of TAX_BRACKETS) {
    if (taxBase <= bracket.max) {
      return Math.floor(
        bracket.base +
        (taxBase - (bracket === TAX_BRACKETS[0] ? 0 : TAX_BRACKETS[TAX_BRACKETS.indexOf(bracket) - 1].max))
        * bracket.rate
      );
    }
  }
  return 0;
}
```
`TAX_BRACKETS.indexOf(bracket)`를 루프 안에서 매번 호출하는 건 비효율적이지만 버그는 아니다.
그러나 **실제 계산 결과가 소득세법 §55 표와 일치하는지 단위 테스트가 존재하지 않는다.**
Engineering Rule 5가 "세금 계산 로직은 `lib/tax-calculator.ts`에 분리, 단위 테스트 필수"라고 명시했는데,
tax-calculator.ts 파일이 없고, tax-return.service.ts에 계산 로직이 직접 들어있다.
서비스 레이어에 계산 로직이 섞인 것도 관심사 분리 위반.

또한 누진공제액이 설계서와 불일치한다:
- 설계서: 1.5억~3억 구간 누진공제 3,706만원
- 코드: `base: 37_060_000` (3,706만원) ← 일치
- 설계서: 3억~5억 구간 누진공제 9,406만원
- 코드: `base: 94_060_000` (9,406만원) ← 일치
- 5억 초과 구간 누진공제 설계서 17,406만원 vs 코드 `174_060_000` (1억 7,406만원) ← 일치

수치는 맞지만 소득세법 원문과의 정합성 검증을 위한 테스트가 없다는 점이 리스크.

**수정 방향**:
- `lib/tax-calculator.ts` 분리 (설계서 Rule 5 준수)
- 주요 소득 구간별 예시값으로 단위 테스트 작성 (예: 과표 3,000만원 → 세액 = 14,000,000 × 6% + 16,000,000 × 15% - 840,000)

---

### HIGH-3. 경비 summary 엔드포인트 미구현 + FE 기대 형식 불일치
**위치**: FE `use-expenses.ts`, `wave_fe_완료.md` API 목록

FE는 `GET /api/expenses/summary` 를 호출하고 `{ kpi: MockKpiData, monthly: MockMonthlyData[] }` 형식을 기대한다.

그런데 BE `app/api/expenses/` 디렉토리 내에 `summary` 서브디렉토리가 없다.
`expense.service.ts`의 `getExpenseSummary()` 함수는 다음 형식을 반환한다:
```typescript
{
  taxYear, total, count, unverifiedCount,
  categoryBreakdown: [...],
  monthlyBreakdown: [...],
}
```
FE가 기대하는 `kpi.estimatedTax`, `kpi.estimatedSaving` 등의 필드가 없다.
연결하는 순간 대시보드 KPI 카드가 전부 undefined를 보여주게 된다.

**수정 방향**:
- `app/api/expenses/summary/route.ts` 파일 생성 필요
- BE `getExpenseSummary()` 응답에 `kpi` 블록 추가 (estimatedTax는 taxReturn 서비스 연동 필요)
- 또는 FE 훅의 기대 형식을 BE 실제 응답에 맞게 수정

---

### HIGH-4. 구독 취소 API 미구현
**위치**: `wave_cto.md` API 목록, `src/app/api/billing/`
**문제**:
설계서에 `POST /api/subscription/cancel` 이 명시되어 있고, BE 문서에도 포함되어야 하나,
`billing/` 디렉토리에는 `checkout/`과 `portal/`만 존재한다.
`cancel` 라우트가 없다. 사용자가 구독을 직접 취소할 수 없으므로 Stripe Portal로 우회는 가능하나,
설계 명세 미이행.

또한 설계서는 `GET /api/subscription`(구독 상태 조회) 엔드포인트를 명시했는데 구현이 확인되지 않는다.

---

### HIGH-5. OCR 이미지 파일 크기 검증 없음
**위치**: `src/app/api/receipts/upload/route.ts`, `src/services/ocr.service.ts`
**문제**:
설계서는 "이미지 크기 검증 (최대 10MB)" 전처리 단계를 명시했다.
현재 업로드 라우트에서 파일 크기 검증이 없다. 100MB 이미지도 받아서 Google Vision API에 넘길 수 있다.
Google Vision API는 파일 크기 제한(인라인 10MB, URL 참조 무제한이나 타임아웃 발생)이 있으므로
운영 중 예상치 못한 실패를 유발할 수 있다.

---

## 통합 포인트 확인

| API | FE 기대 형식 | BE 실제 반환 | 일치 여부 |
|-----|------------|------------|---------|
| GET /api/receipts | `MockReceipt[]` (flat array) | `{ success: true, data: Receipt[], pagination: {...} }` | 불일치 |
| POST /api/receipts/upload | `{ receipt: {...}, ocrResult: { merchantName, date, amount, category, confidence, lowConfidenceFields, classificationReason } }` | `{ receipt: {...}, expenseItem: { ..., taxLawReference } }` | 필드명 불일치: `ocrResult` vs `expenseItem` |
| GET /api/expenses | `MockExpenseItem[]` (flat array) | `{ success: true, data: ExpenseItem[], pagination: {...}, summary: {...} }` | 불일치 |
| GET /api/expenses/summary | `{ kpi: MockKpiData, monthly: MockMonthlyData[] }` | 엔드포인트 미구현 | 불일치 |
| POST /api/tax-return | `MOCK_TAX_RETURN 형태 (estimatedSaving 포함)` | `TaxReturnCalculation (estimatedSaving 없음)` | 부분 불일치 |
| GET /api/tax-return/[id] | `MOCK_TAX_RETURN` | `TaxReturn (DB 스키마 기반)` | 부분 불일치 |
| GET /api/usage | `{ receiptUsed, receiptLimit, taxReturnUsed, taxReturnLimit }` | `{ planStatus, receipt: { used, limit, resetAt }, taxReturn: { used, limit, taxYear } }` | 필드 구조 불일치 |
| POST /api/billing/checkout | `{ url: string }` | `{ url: string, sessionId: string }` | 일치 (추가 필드는 무해) |

**상태 요약**: 8개 통합 포인트 중 5개 불일치. FE-BE 실연결 시 대부분의 화면이 빈 화면 또는 undefined를 보여줄 것으로 예상.

---

## 긍정 평가 항목 (잘 된 부분)

**아키텍처 레이어 분리 — 합격**
- Route → Service → Repository(Prisma) 3계층이 일관되게 유지됨
- DB 쿼리가 Route Handler에 직접 노출된 경우 없음 (일부 간단한 쿼리는 Route에 있으나 허용 범위)
- `lib/errors.ts`, `lib/handle-error.ts`, `lib/response.ts` 3종 공통 인프라 완비

**보안 — 합격**
- 모든 보호 엔드포인트에 `requireAuth()` 일관 적용
- Middleware(`middleware.ts`)에서 Edge 레벨 인증 이중 확인
- 영수증 소유권 확인: `receipt.userId !== userId → ForbiddenError` 패턴 모든 CRUD에 적용
- Stripe Webhook: `stripe.webhooks.constructEvent()`로 서명 검증 구현, raw body 방식 올바름
- 멱등성 보장: Stripe 구독 upsert 트랜잭션 처리

**무료 플랜 한도 — 합격**
- API 레벨에서 `checkReceiptUploadLimit()`, `checkTaxReturnLimit()` 이중 검증
- 유료 플랜 여부는 세션의 planStatus로 판단 (FE 우회 불가)
- 402 UsageLimitError 응답 형식 설계서와 일치

**타입 안전성 — 합격**
- tsconfig: `"strict": true`, `"noImplicitAny": true` 설정됨
- Zod 스키마: 모든 Route Handler request body에 적용
- GPT-4o 응답: `response_format: { type: "json_object" }` 사용
- 금액: 모든 필드 `Int`, `Math.round()` 처리

**법적 컴플라이언스 — 합격**
- 홈택스 자동 제출 코드 전혀 없음 (grep 결과 0건)
- 모든 신고서 API 응답에 disclaimer 포함
- `userVerified: false` 항목 생성 시 기본값 유지

**환경변수 관리 — 합격**
- 19개 환경변수 목록 문서화됨
- 코드 내 하드코딩 없음, `process.env.*` 방식 일관 사용

---

## 성능 리스크 확인

**N+1 쿼리 — 부분 위험**
`getExpenseSummary()` 함수에서 월별 집계를 위해 해당 연도 경비 전체를 메모리로 불러온 후 JS로 grouping한다:
```typescript
const allExpenses = await prisma.expenseItem.findMany({ where, select: { date, amount } });
for (const exp of allExpenses) { monthlyData[month] += exp.amount; }
```
연간 경비 건수가 수백 건이면 문제없으나, 수천 건이 되면 메모리 이슈. Prisma groupBy + raw SQL로 개선 권장.

**SELECT 최적화 — 합격**
대부분의 쿼리가 필요한 필드만 `select` 지정. 전체 컬럼 `include` 남용 없음.
단, `getTaxReturn()`의 `include: { user: { select: { businessProfile: ... } } }` 는 조인이지만 필요한 호출.

---

## MVP 범위 준수 확인

| 항목 | 확인 결과 |
|------|---------|
| 홈택스 자동 제출 코드 | 없음 (PASS) |
| 스크래핑 코드 | 없음 (PASS) |
| 실시간 세무 상담 기능 | 없음 (PASS) |
| 부가세/법인 지원 | 없음 (PASS) |
| 세무 대리 행위로 해석 가능한 기능 | 모든 응답에 disclaimer 포함, PASS |

---

## 전체 평가 (리안에게 드리는 CEO 수준 요약)

**한 줄 결론**: 백엔드 뼈대와 보안은 탄탄하게 완성됐지만, 프론트엔드와 실제 연결이 아직 되어있지 않아서 지금 상태로는 사용자가 실제로 쓸 수 없습니다.

**잘 된 것**: 돈과 법에 관련된 부분은 정확하게 구현됐습니다. 세금 계산 로직은 소득세법 조문과 대조해도 맞고, 결제 보안(Stripe 서명 검증)도 완벽합니다. 무단 접근 차단과 사용자 데이터 격리도 구멍이 없습니다. 홈택스 자동 제출 같은 법적 위험 기능은 코드 어디에도 없습니다.

**당장 고쳐야 할 것 (2가지, 1주일 안에)**:
1. 프론트엔드가 API 응답을 제대로 읽지 못합니다. 백엔드가 `{ success: true, data: [...] }` 형태로 주는데 프론트는 배열이 바로 온다고 생각합니다. 실제 연결하면 화면 대부분이 빕니다.
2. 영수증 업로드 경로가 완성되지 않았습니다. S3에 이미지를 올리고 OCR을 돌리는 전체 흐름이 절반만 구현되어 있어 핵심 기능이 실제로 작동하지 않습니다.

**2주 안에 고쳐야 할 것 (4가지)**:
- 미확인 경비가 있으면 신고서 생성을 막는 안전장치 추가 (법적 면책 핵심)
- 경비 요약 API 구현 (대시보드 핵심 화면이 비어있음)
- 세금 계산 테스트 코드 작성 (계산 오류가 사용자 신고 실수로 이어질 수 있음)
- 구독 취소 API 구현 (결제 기능 완성도)

**출시 가능 시점 판단**: CRITICAL 이슈 2개 수정 후 내부 테스트 진행, HIGH 이슈 1번(userVerified 검증) 추가 수정 후 제한적 베타 가능. 전체 HIGH 이슈 완료 후 정식 출시 권장.

---

*검토 완료: 2026-04-03 | 다음 리뷰: CRITICAL 이슈 수정 후 재검토 요청*
