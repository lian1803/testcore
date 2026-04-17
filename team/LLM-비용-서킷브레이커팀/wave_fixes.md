# Wave 7.5 — CRITICAL 자동 수정 내역

## CRITICAL 수정 (4건)

**[C-1] SDK check 서버사이드 타임아웃**
- `withTimeout()` 헬퍼 추가 (Promise.race + 1.8초)
- DB 쿼리 타임아웃 → catch에서 allow-through

**[C-2] 서킷브레이커 패턴**
- `upstash.ts`에 `incrementCircuitError`, `resetCircuitError`, `isCircuitOpen` 추가
- 5회 연속 오류 시 60초 allow-through
- check/route.ts 진입 시 circuit 상태 확인

**[C-3] API Key timing attack**
- prefix 불일치 시 `DUMMY_HASH`로 더미 bcrypt 실행
- `utils.ts`에 `DUMMY_HASH` 상수 추가

**[C-4] service client 싱글톤 제거**
- `server.ts` 모듈 레벨 캐싱 제거
- 매 호출마다 새 인스턴스 생성

## HIGH 수정 (H-2)
- `sdk/report/route.ts` — `call_count` 덮어쓰기 → SELECT 후 증분으로 수정
- `incrementSpent(id, 0)` → `getCurrentMonthSpent(id)` 로 대체

## 기타 수정
- ESLint 에러 0개 달성 (any→unknown, mounted 패턴 제거)
- 깨진 `[id` 폴더 삭제 → 빌드 오류 수정
- `DialogTrigger asChild` Radix 호환성 수정
- `fire-and-forget` `.then().catch()` → `void Promise.resolve().catch()` 변환

## 빌드 상태: ✅ 성공
