# BE 구현 완료

**작성자**: 정우 (BE Engineer)
**작성일**: 2026-04-03
**상태**: MVP 구현 완료 (의존성 설치 + DB 마이그레이션 필요)

---

## 구현된 API

| Method | Path | 설명 | 상태 |
|--------|------|------|------|
| POST | `/api/auth/register` | 이메일 회원가입 (bcrypt 12 rounds) | 완료 |
| POST | `/api/auth/[...nextauth]` | NextAuth Google + Credentials 로그인 | 완료 |
| POST | `/api/auth/forgot-password` | 비밀번호 재설정 메일 발송 (Resend) | 완료 |
| GET | `/api/profile` | 사업자 프로필 조회 | 완료 |
| POST | `/api/profile` | 온보딩 - 사업자 프로필 최초 생성 | 완료 |
| PATCH | `/api/profile` | 사업자 프로필 수정 | 완료 |
| GET | `/api/receipts` | 영수증 목록 (페이지네이션, 상태/날짜 필터) | 완료 |
| POST | `/api/receipts/upload` | 영수증 업로드 + OCR + AI 분류 | 완료 |
| GET | `/api/receipts/[id]` | 영수증 상세 + 연결 경비 항목 | 완료 |
| PATCH | `/api/receipts/[id]` | 영수증 수동 수정 (카테고리, 금액 등) | 완료 |
| DELETE | `/api/receipts/[id]` | 영수증 + S3 원본 삭제 | 완료 |
| POST | `/api/receipts/[id]/process` | OCR 재처리 (실패 재시도) | 완료 |
| GET | `/api/expenses` | 경비 목록 (연도/카테고리/월 필터, 정렬) | 완료 |
| POST | `/api/expenses` | 경비 수동 입력 | 완료 |
| GET | `/api/expenses/[id]` | 경비 상세 조회 | 완료 |
| PATCH | `/api/expenses/[id]` | 경비 수정 + 사용자 검증 완료 처리 | 완료 |
| DELETE | `/api/expenses/[id]` | 경비 삭제 | 완료 |
| GET | `/api/tax-return` | 신고서 목록 | 완료 |
| POST | `/api/tax-return` | 신고서 생성 (공제 계산 + 초안 생성) | 완료 |
| GET | `/api/tax-return/[id]` | 신고서 상세 | 완료 |
| GET | `/api/tax-return/[id]/download` | PDF/Excel 다운로드 | 완료 |
| POST | `/api/billing/checkout` | Stripe Checkout 세션 생성 | 완료 |
| POST | `/api/billing/portal` | Stripe Customer Portal | 완료 |
| POST | `/api/webhooks/stripe` | Stripe Webhook (서명검증 + 멱등성) | 완료 |
| GET | `/api/usage` | 무료 플랜 사용량 조회 | 완료 |

---

## 서비스 레이어

| 파일 | 역할 |
|------|------|
| `src/services/ocr.service.ts` | Google Vision API OCR + GPT-4o Vision 폴백 (신뢰도 0.7 기준) |
| `src/services/ai-classifier.service.ts` | GPT-4o 경비 분류 (세법 조항 매핑 포함) |
| `src/services/receipt.service.ts` | 영수증 업로드 파이프라인 + 재처리 |
| `src/services/expense.service.ts` | 경비 CRUD + 월별/카테고리 집계 |
| `src/services/tax-return.service.ts` | 종합소득세 계산 (누진세율, 인적공제, 사회보험료 공제) |
| `src/services/document.service.ts` | PDF (@react-pdf/renderer) + Excel (xlsx) 생성 |
| `src/services/billing.service.ts` | Stripe 구독 관리 + Webhook 처리 |
| `src/services/usage.service.ts` | 플랜 한도 체크 + 사용량 집계 |
| `src/services/s3.service.ts` | S3 presigned URL 생성 + 오브젝트 삭제 |

---

## 공통 라이브러리

| 파일 | 역할 |
|------|------|
| `src/lib/prisma.ts` | Prisma 클라이언트 싱글톤 |
| `src/lib/errors.ts` | AppError 계층 (NotFound, Validation, Unauthorized, Forbidden, Conflict, UsageLimit) |
| `src/lib/handle-error.ts` | 중앙 에러 핸들러 (RFC 9457 형식) |
| `src/lib/response.ts` | 일관된 응답 포맷 (ok, created, paginated, cursorPaginated) |
| `src/lib/middleware/auth.ts` | withAuth, withRole, requireAuth |
| `src/lib/middleware/validate.ts` | validateSchema (Zod), parseQueryParams |
| `src/lib/schemas/auth.ts` | RegisterSchema, ForgotPasswordSchema |
| `src/lib/schemas/receipt.ts` | UploadReceiptSchema, UpdateReceiptSchema, ReceiptListQuerySchema |
| `src/lib/schemas/expense.ts` | CreateExpenseSchema, UpdateExpenseSchema, ExpenseListQuerySchema |
| `src/lib/schemas/tax-return.ts` | CreateTaxReturnSchema, DownloadQuerySchema |

---

## 세법 로직 (tax-return.service.ts)

### 적용 법령
- 종합소득세 세율: 소득세법 §55 (7단계 누진세율, 2025년 귀속분)
- 지방소득세: 지방세법 §91 (소득세의 10%)
- 인적공제: 소득세법 §50 (기본공제 150만원/인), §51 (추가공제)
- 사회보험료 공제: 소득세법 §51의3
- 경비: 소득세법 시행령 §55 (업종별 단순경비율 + 실제 경비 중 큰 쪽 적용)

### 세율 구간 (소득세법 §55)
| 과세표준 | 세율 | 누진공제 |
|---------|------|--------|
| 1,400만원 이하 | 6% | 0 |
| 1,400만~5,000만원 | 15% | 84만원 |
| 5,000만~8,800만원 | 24% | 624만원 |
| 8,800만~1.5억원 | 35% | 1,536만원 |
| 1.5억~3억원 | 38% | 3,706만원 |
| 3억~5억원 | 40% | 9,406만원 |
| 5억원 초과 | 42% | 17,406만원 |

---

## 환경변수 목록

| 변수명 | 설명 | 필수 |
|--------|------|------|
| `NEXT_PUBLIC_APP_URL` | 앱 공개 URL | Y |
| `DATABASE_URL` | PostgreSQL 연결 문자열 | Y |
| `NEXTAUTH_SECRET` | NextAuth 서명 시크릿 (32자+) | Y |
| `NEXTAUTH_URL` | NextAuth 기본 URL | Y |
| `GOOGLE_CLIENT_ID` | Google OAuth Client ID | Y |
| `GOOGLE_CLIENT_SECRET` | Google OAuth Client Secret | Y |
| `GOOGLE_VISION_API_KEY` | Google Cloud Vision API Key | Y |
| `OPENAI_API_KEY` | OpenAI API Key (GPT-4o) | Y |
| `AWS_ACCESS_KEY_ID` | AWS IAM Access Key | Y |
| `AWS_SECRET_ACCESS_KEY` | AWS IAM Secret Key | Y |
| `AWS_REGION` | AWS 리전 (기본: ap-northeast-2) | Y |
| `AWS_S3_BUCKET_NAME` | S3 버킷명 | Y |
| `STRIPE_SECRET_KEY` | Stripe Secret Key | Y |
| `STRIPE_PUBLISHABLE_KEY` | Stripe Publishable Key | Y |
| `STRIPE_WEBHOOK_SECRET` | Stripe Webhook Signing Secret | Y |
| `STRIPE_PRICE_MONTHLY` | Stripe 월간 Price ID | Y |
| `STRIPE_PRICE_ANNUAL` | Stripe 연간 Price ID | Y |
| `RESEND_API_KEY` | Resend API Key (이메일) | 선택 |
| `RESEND_FROM_EMAIL` | 발신 이메일 주소 | 선택 |
| `SENTRY_DSN` | Sentry DSN (모니터링) | 선택 |

---

## 배포 전 필수 작업

```bash
# 1. 의존성 설치 (src/ 디렉토리에서)
cd src
npm install

# 2. Prisma 클라이언트 생성
npx prisma generate

# 3. DB 마이그레이션
npx prisma migrate dev --name init

# 4. Stripe Webhook 로컬 테스트
stripe listen --forward-to localhost:3000/api/webhooks/stripe

# 5. 개발 서버 실행
npm run dev
```

---

## FE에게 전달

### API 응답 형식
모든 성공 응답: `{ success: true, data: {...} }`
페이지네이션: `{ success: true, data: [...], pagination: { page, limit, total, totalPages, hasNext, hasPrev } }`
에러 응답 (RFC 9457): `{ type: "url", title: "ErrorName", status: 400, detail: "메시지", errors: {...} }`

### 인증
- NextAuth JWT 세션 사용
- `session.user.id`: userId
- `session.user.planStatus`: "FREE" | "PREMIUM" | "EXPIRED"
- 세션 갱신 필요 시: `useSession({ required: true })` + `update()` 호출

### 핵심 플로우
1. 회원가입 → `/api/auth/register` → NextAuth 로그인
2. 온보딩 → `/api/profile` POST
3. 영수증 업로드: 클라이언트에서 S3에 직접 업로드 → `/api/receipts/upload` POST로 imageKey 전달
4. 경비 확인 → PATCH `/api/expenses/[id]` with `userVerified: true`
5. 신고서 생성 → `/api/tax-return` POST → 결과 검토 → 다운로드
6. 결제 → `/api/billing/checkout` POST → Stripe URL로 리다이렉트

### 무료 플랜 한도 초과 시
HTTP 402 응답:
```json
{
  "status": 402,
  "title": "UsageLimitError",
  "detail": "무료 플랜 한도 초과: 영수증 업로드 20건 제한에 도달했습니다.",
  "errors": { "resource": "영수증 업로드", "limit": 20 }
}
```
FE에서 이 응답을 받으면 업그레이드 모달 표시.

### 법적 필수 UX
- 신고서 생성 API 응답에 `notice.disclaimer` 포함 → 반드시 UI에 표시
- 다운로드 파일명: `tax-return-{year}-draft.pdf/xlsx` (draft 명시)
- 모든 신고서 화면에 "참고용 초안" 워터마크 또는 배너 필수

### S3 이미지 업로드 순서
1. FE: 파일 선택 → FormData 또는 File 객체 확보
2. FE: `/api/receipts/upload-url` POST (현재 미구현, 추가 필요 시 요청)
3. 현재 MVP: S3 presigned URL 없이 imageKey를 직접 받는 방식
   → 실제 배포 시 `/api/receipts/upload-url` 엔드포인트 추가 필요
   → 또는 `/api/receipts/upload`에서 직접 multipart form 수신으로 변경

---

## 주의사항

1. **홈택스 자동 제출 없음**: 코드 어디에도 홈택스 API 연동 없음. PRD Must NOT 준수.
2. **세무 대행 아님**: 신고서는 참고용 초안. 모든 응답에 disclaimer 포함.
3. **보수적 경비 계산**: 불확실한 공제는 표준경비율 사용. 과소납부 리스크 방지.
4. **원본 삭제 옵션**: `deleteAfterProcessing: true` 시 OCR 완료 후 S3 원본 삭제.
5. **userVerified 레이어**: AI 분류 결과는 `userVerified: false`. 사용자 확인 후 true로 변경.
