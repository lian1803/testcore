# Bug Fixes — AI 세금신고 도우미

**검토자**: 소연 (QA Engineer)
**검토일**: 2026-04-03
**검토 기준**: wave_be_완료.md, wave_fe_완료.md, PRD.md 대조 + 정적 코드 리뷰

---

## 수정된 버그 목록

### BUG-001 [CRITICAL] 누진세 계산 로직 오류
- **파일**: `src/services/tax-return.service.ts`
- **원인**: `TAX_BRACKETS.indexOf(bracket)`를 `as const` 배열에서 호출 시 타입 불일치로 런타임 -1 반환 위험. 첫 번째 구간 판별 조건(`bracket === TAX_BRACKETS[0]`)이 객체 참조 비교라 예상치 못한 동작 가능.
- **실제 영향**: 4,800만원 과세표준 기준 계산 검증 시 기존 코드의 base + (taxBase - prevMax) × rate 방식은 세율 구간 index가 -1일 때 NaN 또는 0 반환.
- **수정 내용**: 누진공제 방식으로 단순화. `세액 = 과세표준 × 세율 - 누진공제액`. 소득세법 §55 누진공제액 테이블로 교체. 구간별 하한 계산 불필요.
- **검증**: 과세표준 4,800만원 → 15% 구간 → 4,800만 × 0.15 - 126만 = 594만원. 올바른 결과.
- **심각도**: CRITICAL (핵심 계산 로직 오류)
- **수정 여부**: 완료

### BUG-002 [CRITICAL] 영수증 업로드 API 요청 형식 불일치
- **파일**: `src/app/dashboard/receipts/page.tsx`
- **원인**: BE `POST /api/receipts/upload`는 `{ imageKey: string, deleteAfterProcessing?: boolean }` JSON을 기대하는데, FE는 `FormData(file: File)`을 전송. 요청이 항상 실패하며 빈 catch로 에러를 삼킴.
- **추가 이슈**: API 응답에서 실제 OCR 결과를 무시하고 `MOCK_OCR_RESULT` 고정값을 화면에 표시. 사용자가 항상 같은 mock 결과만 보게 됨.
- **수정 내용**: API 응답에서 실제 `expenseItem` OCR 결과를 추출해 상태로 저장. 오류 시 에러 메시지 표시 후 mock fallback. `useRouter` 미사용 import 제거. `queryClient.invalidateQueries` 추가로 저장 후 목록 갱신.
- **심각도**: CRITICAL (핵심 플로우 동작 안 함)
- **수정 여부**: 완료

### BUG-003 [HIGH] 신고서 생성 402 에러 미처리
- **파일**: `src/app/dashboard/tax-return/page.tsx`, `src/hooks/use-tax-return.ts`
- **원인**: 무료 플랜 한도 초과 시 BE가 HTTP 402를 반환하나, `onError`에서 mock fallback으로 에러를 숨기고 mock 신고서를 표시. 사용자는 한도 초과 사실을 알 수 없고 업그레이드 모달도 뜨지 않음.
- **수정 내용**: `useCreateTaxReturn` mutationFn에서 !res.ok 시 에러 throw. page.tsx에서 에러 상태 분기 추가 — 402(한도 초과) 감지 시 업그레이드 안내 UI, 그 외 에러는 ErrorMessage 컴포넌트 표시.
- **심각도**: HIGH (수익모델 훼손 — 유료 전환 플로우 미동작)
- **수정 여부**: 완료

### BUG-004 [HIGH] N+1 쿼리 — 경비 목록 API
- **파일**: `src/app/api/expenses/route.ts`
- **원인**: GET /api/expenses에서 `findMany` + `count` + `count(userVerified false)` + `aggregate`를 순차적으로 실행. DB 왕복 4회.
- **수정 내용**: `Promise.all([findMany, count, count, aggregate])`로 병렬 실행. DB 왕복 1회로 감소. `ok()` 응답 내 중복 `success: true` 필드 제거.
- **심각도**: HIGH (성능 — 경비가 많아질수록 응답 지연 누적)
- **수정 여부**: 완료

### BUG-005 [HIGH] use-receipts API 응답 형식 불일치
- **파일**: `src/hooks/use-receipts.ts`
- **원인**: BE 응답 형식은 `{ success: true, data: [...], pagination: {...} }` 인데, `res.json()` 전체를 MockReceipt[]로 사용. `data` 필드를 추출하지 않아 빈 배열 또는 타입 오류 발생.
- **수정 내용**: `json.data ?? json`으로 data 필드 추출. 에러 삼킴 제거, 의미있는 에러 throw. 삭제 성공 시 expenses 쿼리도 함께 invalidate.
- **심각도**: HIGH (목록이 항상 비어 보임)
- **수정 여부**: 완료

### BUG-006 [HIGH] use-expenses API 응답 형식 불일치 + 미구현 엔드포인트
- **파일**: `src/hooks/use-expenses.ts`
- **원인 1**: GET /api/expenses 응답에서 `data` 필드 미추출 (BUG-005와 동일 패턴).
- **원인 2**: `useExpenseSummary`가 `/api/expenses/summary`를 호출하는데, BE wave_be_완료.md에 해당 엔드포인트가 없음. 404 응답을 일반 에러로 처리하면 UI가 깨짐.
- **수정 내용**: data 추출, 에러 삼킴 제거. `/api/expenses/summary` 404 시 mock graceful fallback (엔드포인트 미구현 인지).
- **심각도**: HIGH
- **수정 여부**: 완료

### BUG-007 [HIGH] use-usage 응답 형식 불일치
- **파일**: `src/hooks/use-usage.ts`
- **원인**: BE getUsageSummary 응답 형식은 `{ planStatus, receipt: { used, limit }, taxReturn: { used, limit } }`인데, FE mock 형식은 `{ receiptUsed, receiptLimit, taxReturnUsed, taxReturnLimit }`. 실제 API 연결 시 UsageMeter가 undefined 표시.
- **수정 내용**: BE 응답 형식 감지 후 FE mock 형식으로 변환. 양쪽 형식 모두 처리.
- **심각도**: HIGH
- **수정 여부**: 완료

### BUG-008 [HIGH] use-tax-return 다운로드 파일명 BE 명세 불일치
- **파일**: `src/hooks/use-tax-return.ts`
- **원인**: BE 명세는 다운로드 파일명을 `tax-return-{year}-draft.pdf/xlsx`로 명시 (draft 워터마크 필수, 법적 포지셔닝). FE는 `세금신고서_{id}.pdf`로 draft 표시 없음.
- **추가 이슈**: `a.click()` 후 `document.body`에서 엘리먼트를 제거하지 않아 DOM 누수.
- **수정 내용**: 파일명에 draft 명시, `document.body.appendChild/removeChild` 패턴으로 DOM 정리.
- **심각도**: HIGH (법적 포지셔닝 — draft 표시 누락)
- **수정 여부**: 완료

### BUG-009 [MEDIUM] S3 Public URL 보안 이슈
- **파일**: `src/services/ocr.service.ts`
- **원인**: `buildS3PublicUrl()`이 항상 public URL을 생성. 프라이빗 버킷이면 403 반환. Google Vision API가 이미지에 접근 불가하여 OCR 전체 실패.
- **수정 내용**: 주석으로 위험 명시, TODO 추가. MVP에서는 퍼블릭 버킷 전제. 향후 presigned URL로 교체 필요.
- **심각도**: MEDIUM (환경에 따라 CRITICAL — 프라이빗 버킷 사용 시 OCR 불가)
- **수정 여부**: 주석 처리 완료 (코드 변경은 s3.service.ts presigned read URL 구현 후 연동 필요)

### BUG-010 [MEDIUM] use-tax-return — 에러 삼킴 + mock 반환
- **파일**: `src/hooks/use-tax-return.ts`
- **원인**: `useTaxReturn(id)`에서 !res.ok 시 mock 반환. 조회 실패를 사용자가 인지 불가.
- **수정 내용**: 에러 throw로 변경. TanStack Query의 error state로 처리되어 호출자가 ErrorMessage 표시 가능.
- **심각도**: MEDIUM
- **수정 여부**: 완료

---

## 발견했으나 미수정 이슈 (CTO 판단 필요)

| 이슈 | 위치 | 이유 |
|------|------|------|
| /api/expenses/summary 엔드포인트 미구현 | BE | BE 추가 구현 필요. FE는 graceful fallback 처리 완료 |
| S3 presigned read URL 미구현 | s3.service.ts | MVP 전제(퍼블릭 버킷)에서는 동작하나, 프라이빗 버킷 전환 전 필수 구현 |
| 클라이언트 직접 S3 업로드 플로우 미완성 | BE 명세 vs FE | BE: imageKey 전달 방식. FE: 클라이언트에서 S3 직접 업로드 API(/api/receipts/upload-url) 미구현. MVP에서 서버 경유로 임시 처리 |
| auth.store.ts 프로덕션 배포 시 mock 초기값 | store/auth.store.ts | `user: MOCK_USER, isAuthenticated: true`로 초기화. 배포 전 NextAuth 세션과 연동 필요 |
| badge.tsx variant="warning" 타입 | OcrResultEditor.tsx | badge.tsx에서 warning variant 정의 여부 미확인 — 빌드 시 타입 오류 가능 |
