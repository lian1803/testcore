# QA 검증 결과

**검토자**: 소연 (QA Engineer)
**검토일**: 2026-04-03
**검토 방식**: 정적 코드 리뷰 (wave_be_완료.md, wave_fe_완료.md, PRD.md 대조)
**검토 대상**: src/ 전체 TypeScript/TSX 파일 (101개)

---

## 발견된 버그

| # | 파일 | 버그 내용 | 심각도 | 수정 여부 |
|---|------|-----------|--------|-----------|
| BUG-001 | `services/tax-return.service.ts` | 누진세 계산 로직 오류 — indexOf 사용 시 런타임 -1 반환 위험, 올바른 누진공제 계산식 미적용 | CRITICAL | 완료 |
| BUG-002 | `app/dashboard/receipts/page.tsx` | 업로드 API 요청 형식 불일치 (FormData 전송 vs BE JSON 기대), 실제 OCR 결과 무시 후 mock 고정 표시 | CRITICAL | 완료 |
| BUG-003 | `app/dashboard/tax-return/page.tsx` + `hooks/use-tax-return.ts` | 신고서 생성 402 에러 미처리 — mock fallback으로 fake 성공 표시, 업그레이드 유도 없음 | HIGH | 완료 |
| BUG-004 | `app/api/expenses/route.ts` | N+1 쿼리 — count/aggregate 4회 순차 실행 | HIGH | 완료 |
| BUG-005 | `hooks/use-receipts.ts` | API 응답 형식 불일치 (data 필드 미추출), 에러 삼킴 | HIGH | 완료 |
| BUG-006 | `hooks/use-expenses.ts` | API 응답 형식 불일치, /api/expenses/summary 미구현 엔드포인트 호출 | HIGH | 완료 |
| BUG-007 | `hooks/use-usage.ts` | BE-FE 사용량 응답 형식 불일치 (UsageMeter undefined 표시) | HIGH | 완료 |
| BUG-008 | `hooks/use-tax-return.ts` | 다운로드 파일명 draft 표시 누락 (법적 포지셔닝), DOM 누수 | HIGH | 완료 |
| BUG-009 | `services/ocr.service.ts` | S3 프라이빗 버킷 사용 시 Public URL로 OCR 불가 | MEDIUM | 주석 처리 (TODO 명시) |
| BUG-010 | `hooks/use-tax-return.ts` | useTaxReturn — 에러 삼킴 + mock 반환 | MEDIUM | 완료 |

---

## 수정된 파일 목록

| 파일 | 수정 내용 |
|------|-----------|
| `src/services/tax-return.service.ts` | 누진세 계산 로직을 누진공제 방식으로 교체 (과세표준 × 세율 - 누진공제액) |
| `src/app/dashboard/receipts/page.tsx` | 업로드 플로우 수정 — 실제 OCR 결과 상태 관리, 에러 UI 추가, DOM 클린업, useRouter 제거 |
| `src/app/dashboard/tax-return/page.tsx` | 402 에러 감지 + 업그레이드 안내 UI 분기, ErrorMessage 컴포넌트 활용 |
| `src/app/api/expenses/route.ts` | N+1 쿼리를 Promise.all 병렬 실행으로 개선, 중복 success 필드 제거 |
| `src/hooks/use-receipts.ts` | BE 응답 형식 data 추출, 에러 throw, expenses 캐시 invalidate 추가 |
| `src/hooks/use-expenses.ts` | BE 응답 형식 data 추출, 에러 throw, /summary 404 graceful fallback |
| `src/hooks/use-usage.ts` | BE-FE 응답 형식 변환 로직 추가 |
| `src/hooks/use-tax-return.ts` | 에러 throw, 파일명 draft 명시, DOM 클린업, queryClient invalidate 추가 |
| `src/services/ocr.service.ts` | S3 공개 URL 보안 위험 주석 및 TODO 추가 |

---

## 테스트 시나리오 결과

| 시나리오 | 정적 분석 결과 | 비고 |
|----------|--------------|------|
| TC-001 영수증 업로드 → OCR → 분류 | BUG-002 수정 후 플로우 복원 | 실제 실행 테스트 필요 |
| TC-002 무료 플랜 한도 초과 차단 | BUG-003 수정 후 402 처리 가능 | Stripe 테스트 환경 필요 |
| TC-003 Stripe 결제 성공/실패 | webhook 서명 검증 코드 정상 | stripe listen 실행 필요 |
| TC-004 신고서 PDF 생성 + 다운로드 | BUG-001, BUG-008 수정 후 정상 | document.service.ts 실행 필요 |
| TC-005 인증 없이 보호 경로 접근 차단 | middleware.ts + requireAuth() 정상 구현 확인 | curl 테스트 필요 |
| TC-006 영수증 원본 삭제 옵션 | deleteAfterProcessing 로직 구현 확인 | S3 연동 테스트 필요 |
| TC-007 경비 수동 수정 + userVerified | PATCH /api/expenses/[id] 구현 확인 | DB 직접 확인 필요 |

---

## CTO에게 전달할 통합 이슈

### 즉시 배포 차단 이슈 (BLOCKING)

**1. 누진세 계산 오류 (BUG-001) — 수정 완료**
- 종합소득세 핵심 계산 로직에 런타임 오류 가능성 존재. 수정 후 과세표준별 세액 단위 테스트 필수.
- 검증 케이스: 1,400만 → 84만원 / 4,800만 → 594만원 / 8,800만 → 1,530만원

**2. 영수증 업로드 플로우 전체 미동작 (BUG-002) — 수정 완료**
- FE가 FormData를 전송하고 BE는 JSON imageKey를 기대. 핵심 기능이 처음부터 동작하지 않음.
- 수정 후에도 클라이언트 직접 S3 업로드 플로우가 미완성 상태. BE에서 presigned URL 엔드포인트(/api/receipts/upload-url) 추가 구현 필요.

**3. 무료 플랜 유료 전환 플로우 미동작 (BUG-003) — 수정 완료**
- 402 에러를 mock fallback으로 숨겨 사용자가 한도 초과를 알 수 없었음. 수익모델 훼손.

### 배포 전 추가 구현 필요 이슈 (REQUIRED)

**4. /api/expenses/summary 엔드포인트 미구현**
- FE useExpenseSummary가 호출하나 BE에 없음. 대시보드 KPI 카드, 월별 차트 데이터가 항상 mock.
- BE: GET /api/expenses/summary → { kpi: {...}, monthly: [...] } 구현 필요.

**5. auth.store.ts 프로덕션 mock 초기값**
- `user: MOCK_USER, isAuthenticated: true`로 초기화됨. 배포 시 NextAuth 세션과 동기화 로직 없으면 인증 우회처럼 동작할 수 있음.
- NextAuth `useSession()` 응답으로 Zustand 스토어 초기화 코드 추가 필요.

**6. badge.tsx variant="warning" 타입 미확인**
- OcrResultEditor.tsx에서 `<Badge variant="warning">` 사용. badge.tsx에 warning variant 미정의 시 빌드 타입 오류.
- 빌드 실행 후 확인 필요.

### 보안 이슈 (SECURITY)

**7. S3 Public URL 사용 (BUG-009)**
- 현재 OCR은 S3 Public URL로 이미지를 Google Vision에 전달. 버킷이 프라이빗으로 전환 시 즉시 OCR 불가.
- 영수증 원본 데이터가 공개 URL로 접근 가능한 것 자체가 개인정보 보호 위험.
- 배포 전 버킷 접근 정책 확인. 프라이빗이면 presigned read URL 구현 필수.

**8. 민감 정보 console.log 노출 확인**
- billing.service.ts: `console.log("[Stripe] 결제 완료: userId=...")`  — userId 노출. Sentry 연동 후 프로덕션에서는 로그 레벨 조정 필요.
- ocr.service.ts: Google Vision 실패 시 전체 오류 객체 console.error. API 응답에 키 정보 포함 가능성 있음.

### 성능 이슈 (PERFORMANCE)

**9. N+1 쿼리 수정 완료 (BUG-004)**
- 경비 목록 API에서 4개 병렬 쿼리로 개선 완료.
- 추가 검토: tax-return.service.ts의 expenseItem.aggregate 쿼리에 인덱스 설정 필요 (userId + taxYear + isBusinessExpense 복합 인덱스).

### 법적 포지셔닝 이슈 (LEGAL)

**10. 다운로드 파일명 draft 표시 — 수정 완료 (BUG-008)**
- BE 명세 준수: `tax-return-draft-{id}.pdf/xlsx`.

**11. MOCK_TAX_RETURN.status = "DRAFT" vs 실제 BE 응답 status = "READY"**
- BE tax-return.service.ts에서 status를 "READY"로 저장하나, mock 데이터는 "DRAFT". 불일치.
- UI에서 "READY"를 "참고용 초안"으로 표시해야 한서윤 컴플라이언스 기준 충족.

---

## 최종 평가

| 영역 | 상태 | 비고 |
|------|------|------|
| 핵심 기능 동작 | 수정 후 정상 | 실행 테스트 필요 |
| 보안 | 부분 이슈 | S3 Public URL, 로그 노출 |
| 법적 포지셔닝 | 수정 후 양호 | draft 파일명, disclaimer 포함 |
| 성능 | 수정 후 양호 | N+1 제거, 추가 인덱스 권장 |
| 타입 안전성 | 부분 이슈 | badge warning variant 확인 필요 |
| 에러 처리 | 수정 후 양호 | 에러 삼킴 패턴 10건 제거 |
| 미구현 기능 | 이슈 있음 | summary API, upload-url API |

**배포 권고**: CONDITIONAL — 위 BLOCKING 이슈 3건 수정 완료. REQUIRED 이슈 (#4~#6) 해결 후 배포 권장.
