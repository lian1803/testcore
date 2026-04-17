# 테스트 시나리오 — AI 세금신고 도우미

**작성자**: 소연 (QA Engineer)
**작성일**: 2026-04-03

---

## TC-001 영수증 업로드 → OCR → 분류 정상 플로우

**목적**: 핵심 가치 제안(Must Have #1) 동작 검증

### 사전 조건
- 로그인 완료 (FREE 플랜, 이번 달 업로드 0건)
- `/api/receipts/upload` BE 동작 중
- Google Vision API 키 유효

### 테스트 단계
1. `/dashboard/receipts` 접근
2. 영수증 이미지(JPG, 5MB 이하) 드래그앤드롭
3. `OcrLoadingOverlay` 애니메이션 표시 확인
4. OCR 완료 후 `OcrResultEditor` 화면 전환 확인
5. 상호명/날짜/금액/카테고리 정확도 확인 (스타벅스 영수증 기준: MEAL 분류 예상)
6. 신뢰도 낮은 필드 노란 배경 표시 확인
7. 카테고리 수동 변경 (MEAL → OFFICE_SUPPLIES) 후 저장
8. 목록 화면으로 복귀 + 영수증 카드 표시 확인

### 합격 기준
- 3초~10초 내 OCR 결과 반환
- 상호명, 금액 정확도 90% 이상 (한국어 영수증 기준)
- 저장 후 `/api/expenses` 경비 항목 생성 확인 (DB)
- `userVerified: false` 상태로 저장됨

### 실패 시나리오
- 이미지 형식 오류 (PDF): "지원하지 않는 형식" 메시지
- OCR 완전 실패: FAILED 상태 저장, 재처리 버튼 표시
- 10MB 초과: 클라이언트 사이드 차단 (ReceiptUploader에 안내 텍스트 있음)

---

## TC-002 무료 플랜 한도 초과 시 차단

**목적**: 수익모델 보호 + PRD Must Have #7 검증

### 사전 조건
- 로그인 완료 (FREE 플랜)
- 이번 달 영수증 업로드 20건 완료 (DB usageLog 확인)

### 테스트 단계 — 영수증 업로드 차단
1. `/dashboard/receipts` 접근
2. 21번째 영수증 업로드 시도
3. BE에서 HTTP 402 응답 확인
4. FE에서 업그레이드 모달/안내 UI 표시 확인

### 테스트 단계 — 신고서 생성 차단
1. 해당 연도 신고서 1회 이미 생성된 상태 (FREE 플랜)
2. `/dashboard/tax-return` → 소득 입력 → "신고서 만들기" 클릭
3. BE에서 HTTP 402 응답
4. 페이지에서 "무료 플랜 한도 초과" 메시지 + "프리미엄 업그레이드" 링크 표시 확인
5. `/dashboard/settings` 링크로 정상 이동 확인

### 합격 기준
- 402 응답 시 업그레이드 안내 UI가 반드시 표시됨
- mock fallback으로 fake 성공 화면이 표시되지 않음
- 업그레이드 링크가 올바른 결제 페이지로 이동

---

## TC-003 Stripe 결제 성공/실패

**목적**: 수익모델 검증 + PRD Must Have #7

### 사전 조건
- Stripe 테스트 모드 키 설정
- STRIPE_WEBHOOK_SECRET 유효
- `stripe listen --forward-to localhost:3000/api/webhooks/stripe` 실행 중

### TC-003-A 결제 성공 플로우
1. FREE 플랜 사용자 로그인
2. `/dashboard/settings` → "프리미엄 업그레이드" 클릭
3. "월간 플랜" 선택 → `POST /api/billing/checkout` 호출
4. Stripe Checkout 페이지 리다이렉트 확인
5. 테스트 카드 4242 4242 4242 4242 입력
6. 결제 완료 → `/dashboard?upgrade=success` 리다이렉트
7. Stripe Webhook `checkout.session.completed` 수신 확인
8. DB: `subscription.status = ACTIVE`, `user.planStatus = PREMIUM` 확인
9. NextAuth 세션 갱신 후 UI에서 PREMIUM 상태 표시 확인

### TC-003-B 결제 실패 플로우
1. Stripe Checkout에서 취소 클릭
2. `/settings/billing?upgrade=canceled` 리다이렉트 확인
3. 취소 안내 메시지 표시 확인

### TC-003-C 결제 실패 (카드 거절) 플로우
1. 테스트 카드 4000 0000 0000 0002 (결제 거절) 입력
2. Stripe Checkout에서 오류 메시지 표시 확인
3. DB planStatus 변경 없음 확인

### TC-003-D Webhook 서명 검증
1. 잘못된 서명으로 POST /api/webhooks/stripe 직접 호출
2. HTTP 400 응답 확인
3. DB 변경 없음 확인

### 합격 기준
- Webhook 서명 검증이 반드시 동작 (stripe.webhooks.constructEvent)
- 결제 성공 후 즉시 PREMIUM 기능 활성화 (세션 갱신 포함)
- 멱등성: 동일 webhook 이벤트 2회 수신 시 DB 중복 처리 없음

---

## TC-004 신고서 PDF 생성 + 다운로드

**목적**: Must Have #3 + 법적 포지셔닝 검증

### 사전 조건
- 로그인 완료 (FREE 또는 PREMIUM 플랜)
- 경비 항목 최소 1건 존재
- PDF 생성 라이브러리 (@react-pdf/renderer) 설치됨

### 테스트 단계
1. `/dashboard/tax-return` 접근
2. 법적 고지 배너 표시 확인 ("신고 준비 도구 안내")
3. 연간 매출액 48,000,000원 입력 → "신고서 만들기" 클릭
4. 생성 로딩 화면 (최대 30초) 표시 확인
5. 신고서 미리보기 — 수입/경비/과세표준/세액 표시 확인
6. "PDF 다운로드" 클릭
7. 다운로드 파일명 확인: `tax-return-draft-{id}.pdf` (draft 명시)
8. PDF 열기 — "참고용 초안" 워터마크/배너 확인
9. "Excel 다운로드" 클릭 → `.xlsx` 파일 다운로드 확인
10. "홈택스 직접 입력 가이드 보기" 클릭 → 모달 6단계 확인

### 합격 기준
- PDF 파일명에 반드시 "draft" 포함
- disclaimer 문구 PDF 내 표시: "이 신고서는 참고용 초안입니다"
- 세액 계산 검증: 과세표준 38,535,000원 → 15% 구간 → 38,535,000 × 0.15 - 1,260,000 = 4,520,250원 (지방세 포함: 4,972,275원)
- 홈택스 링크 (hometax.go.kr) 동작 확인

### 실패 시나리오
- 경비 0건: 표준경비율 적용 결과 표시 (실제 경비 0 < 표준경비율 금액)
- 음수 과세표준: 0원으로 처리 (Math.max(0, ...))

---

## TC-005 인증 없이 보호된 경로 접근 차단

**목적**: 보안 — 미인증 사용자 데이터 접근 차단

### 사전 조건
- 로그아웃 상태 (세션 없음)

### 테스트 단계 — FE 라우팅
1. 브라우저에서 `/dashboard` 직접 접근
2. `/login?callbackUrl=/dashboard` 리다이렉트 확인
3. `/dashboard/receipts`, `/dashboard/expenses`, `/dashboard/tax-return` 반복
4. `/onboarding` 직접 접근 → `/login` 리다이렉트 확인

### 테스트 단계 — API 엔드포인트
1. 세션 없이 `GET /api/receipts` 호출 (curl 또는 Postman)
2. HTTP 401 응답 확인: `{ type, title: "UnauthorizedError", status: 401, detail: "인증이 필요합니다." }`
3. `GET /api/expenses` → 401 확인
4. `POST /api/tax-return` → 401 확인
5. `GET /api/profile` → 401 확인
6. `POST /api/billing/checkout` → 401 확인

### 테스트 단계 — 공개 경로 통과
1. `POST /api/auth/register` → 200 (인증 불필요)
2. `POST /api/webhooks/stripe` → 서명 없으면 400, 서명 있으면 처리 (인증 불필요)

### 테스트 단계 — 타인 데이터 접근 차단
1. 사용자 A로 로그인 후 사용자 B의 영수증 ID로 `GET /api/receipts/[B_receipt_id]` 접근
2. HTTP 403 또는 404 응답 확인
3. 사용자 B의 신고서 ID로 `GET /api/tax-return/[B_taxreturn_id]/download` 접근 → 403 확인

### 합격 기준
- 미인증 API 요청: 반드시 401
- 타인 데이터 접근: 반드시 403 또는 404 (데이터 존재 여부 노출 금지)
- 로그인 후 /login, /signup 접근 시 /dashboard로 리다이렉트

---

## TC-006 (추가) 영수증 원본 삭제 옵션 동작

**목적**: 개인정보보호 — deleteAfterProcessing 옵션 검증

### 테스트 단계
1. 영수증 업로드 시 `deleteAfterProcessing: true` 전달
2. OCR 완료 후 S3에서 해당 imageKey 오브젝트 삭제 확인 (AWS 콘솔)
3. DB Receipt.imageDeleted = true 확인
4. 삭제된 영수증 재처리 시도 → "원본 이미지가 삭제되어 재처리할 수 없습니다." 오류 확인

### 합격 기준
- 삭제 성공 시 S3 오브젝트 없음 확인
- DB에 삭제 여부 정확히 기록

---

## TC-007 (추가) 경비 수동 수정 + userVerified 처리

**목적**: Must Have #2 — OCR 오류 보정 레이어 검증

### 테스트 단계
1. OCR로 자동 생성된 경비 항목 조회 (userVerified: false)
2. `/dashboard/expenses` → 카테고리 변경 후 체크박스 클릭
3. `PATCH /api/expenses/[id]` 호출 + `{ userVerified: true }` 전달
4. DB에서 userVerified: true 확인
5. 신고서 생성 시 해당 경비 포함 여부 확인

### 합격 기준
- userVerified false 항목도 신고서 계산에는 포함됨 (isBusinessExpense: true 기준)
- userVerified 상태가 UI에 시각적으로 구분 표시됨
