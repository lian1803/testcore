# CTO 통합 리뷰 — LLM 비용 서킷브레이커 (llm-guard)

리뷰 일자: 2026-04-08
리뷰어: CTO (Sonnet)
대상 브랜치: worktree agent-a8e5bbcb

---

## 설계 준수율

**전체: 72%**

| 항목 | 준수 여부 | 비고 |
|------|----------|------|
| DB 스키마 6개 테이블 | 준수 (+ stripe_events 추가됨) | |
| RLS 정책 | 준수 | |
| SDK check API 2초 타임아웃 + allow-through | 부분 준수 | 서버 내부 타임아웃 없음 |
| Upstash Redis HTTP 기반 카운터 | 준수 | |
| bcrypt API Key 해싱 | 준수 | |
| 에러 응답 통일 형식 | 준수 | |
| 서킷브레이커 패턴 (5회 오류 → 60초 allow-through) | 미구현 | |
| 대시보드 Supabase Realtime 연결 | 미구현 | Mock 데이터 사용 중 |
| Stripe Webhook | 미구현 | |
| 인증 미들웨어 dashboard 보호 | 준수 | |
| 환경변수 zod 검증 lib/env.ts | 미구현 | process.env 직접 접근 |
| 플랜 제한 (Free=1 프로젝트 등) | 미구현 | |

---

## 발견한 구조적 문제 목록

### CRITICAL

**[C-1] SDK /check API — 타임아웃 미구현**

설계 명세: SDK 타임아웃 2초 초과 시 allow-through. 서버사이드에서도 DB/Redis 쿼리에 타임아웃 적용 필요.

현재 구현은 `try/catch`로 예외를 잡아 allow-through 응답을 반환하지만, DB 쿼리나 bcrypt 검증이 hanging 상태에 빠지면 Vercel Function 기본 타임아웃(10~60초)까지 블록킹된다. SDK 클라이언트가 2초 컷을 해도 서버 리소스는 낭비된다.

수정 방법:
```typescript
// /api/v1/sdk/check 내부에 AbortController 적용
const controller = new AbortController();
const timeoutId = setTimeout(() => controller.abort(), 1800); // 1.8초 (SDK 2초보다 짧게)
try {
  // DB 쿼리에 signal 전달
} finally {
  clearTimeout(timeoutId);
}
```

**[C-2] 서킷브레이커 패턴 미구현**

설계 명세(Engineering Rules BE 5번): "연속 5회 DB 오류 시 60초간 allow-through 모드 전환". 현재는 단순 catch → allow-through이며, 연속 오류 카운터가 없다. DB 완전 장애 시 매 요청마다 DB 연결 시도 → 타임아웃 대기가 반복된다. Upstash에 circuit breaker 상태를 저장하거나 인메모리 카운터로 구현해야 한다.

**[C-3] API Key 검증 로직 — timing attack 취약성**

`/api/v1/sdk/check`와 `/api/v1/sdk/report` 모두:
```typescript
.eq('key_prefix', apiKey.substring(0, 13))
.single()
```
prefix로 1차 조회 후 `bcrypt.compare`를 호출한다. prefix가 틀리면 bcrypt 단계에 도달하지 않아 응답 시간이 달라진다. 공격자가 prefix brute-force 후 bcrypt 단계를 확인하는 side-channel이 생긴다.

완전한 timing-safe 구현은 어렵지만, prefix 불일치 시에도 더미 bcrypt 비교를 추가해야 한다:
```typescript
if (keyError || !apiKeyRecord) {
  await bcrypt.compare(apiKey, '$2b$10$invalidhashplaceholder00000000000000000000000000000000');
  return 401;
}
```

**[C-4] service client 싱글톤 — 메모리 누수 위험**

`src/lib/supabase/server.ts`:
```typescript
let serviceClient: ReturnType<typeof createServerClient> | null = null;

export async function createServiceClient() {
  if (serviceClient) {
    return serviceClient;
  }
  serviceClient = createServerClient(...);
  return serviceClient;
}
```

Vercel Serverless Function은 warm 재사용 시 모듈 레벨 변수가 유지된다. `serviceClient` 싱글톤이 이전 요청의 상태를 오염시킬 수 있고, 특히 Service Role Key를 사용하는 클라이언트를 공유하면 보안 격리가 깨진다. 요청마다 새 인스턴스를 생성해야 한다.

```typescript
// 싱글톤 제거, 매 호출마다 새 클라이언트
export function createServiceClient() {
  return createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_ROLE_KEY!,
    { cookies: { getAll: () => [], setAll: () => {} } }
  );
}
```

---

### HIGH

**[H-1] 대시보드 page.tsx — 완전 Mock 데이터**

`/dashboard/page.tsx`가 실제 API 연결 없이 하드코딩된 Mock 데이터만 사용한다. Supabase Realtime 구독도 없다. 설계 명세 핵심 기능(실시간 비용 차트)이 구현되지 않았다.

```typescript
// 현재
const [todayCost] = useState(48.32);
const mockCostData = [...];

// 필요한 것
useEffect(() => {
  fetchUsageData(projectId);
  const channel = supabase.channel('usage_logs').on('postgres_changes', ...).subscribe();
  return () => supabase.removeChannel(channel);
}, []);
```

**[H-2] budgets 테이블 업데이트 로직 버그**

`/api/v1/sdk/report` report route에서:
```typescript
call_count: body.is_blocked ? 0 : 1, // 증가시키는 로직은 trigger로 처리
```
이는 잘못된 로직이다. `call_count`를 1로 설정하는 것이 아니라 기존 값에 +1을 해야 한다. 현재는 매 호출마다 call_count가 0 또는 1로 덮어써진다. Supabase RPC나 DB trigger가 없는 상태에서 이렇게 작성하면 데이터가 오염된다.

수정:
```typescript
// supabase.rpc('increment_budget', { p_project_id, p_cost, p_is_blocked }) 사용
// 또는 raw SQL: UPDATE budgets SET call_count = call_count + 1, spent_usd = spent_usd + $cost
```

**[H-3] Stripe Webhook 엔드포인트 미구현**

설계 명세에 `POST /webhooks/stripe` 명시. 현재 `/api/webhooks/slack-test`만 존재하며 Stripe webhook이 없다. 결제 플로우가 완전히 누락됐다. Pro 업그레이드가 불가능한 상태다.

**[H-4] 프로젝트 생성 시 period_start 계산 버그**

`/api/dashboard/projects` POST:
```typescript
const periodStart = new Date();
periodStart.setDate(body.reset_day);
if (periodStart < new Date()) {
  periodStart.setMonth(periodStart.getMonth() + 1);
}
```

오늘 날짜가 reset_day보다 크면 다음 달로 설정하는 의도인데, `setDate`와 `setMonth`를 순서대로 호출할 때 날짜 overflow가 발생한다. 예: 1월 31일에 reset_day=5 설정 시 `setDate(5)` → 1월 5일, `setMonth(1)` → 2월 5일. 이 경우는 맞지만, 2월에 reset_day=31 설정 시 3월 3일로 날짜가 밀린다. 이미 구현된 `getMonthPeriodStart()` 유틸을 써야 한다.

**[H-5] dashboard layout.tsx — 'use client' 전체 적용**

`dashboard/layout.tsx`가 `'use client'`로 선언되어 있다. 레이아웃 전체가 클라이언트 컴포넌트가 되면 하위 Server Component들의 이점이 사라진다. `useState`가 필요한 사이드바 토글 부분만 별도 Client Component로 분리해야 한다.

Engineering Rules FE 1번 위반: "Server Component 기본값. 'use client'는 인터랙션이 있는 leaf 컴포넌트에만."

**[H-6] Slack Webhook URL — 평문 저장**

`alerts` 테이블의 `slack_webhook` 컬럼이 암호화 없이 평문으로 저장된다. 설계 명세 보안 규칙 3번: "Slack Webhook URL은 DB에 암호화 저장 (Supabase Vault 또는 AES-256 + 서버 키)". 현재 미구현 상태다.

**[H-7] 환경변수 zod 검증 미구현**

Engineering Rules FE 6번: "환경변수는 `lib/env.ts`에서 zod로 검증 후 export. 컴포넌트에서 `process.env` 직접 접근 금지."

현재 전체 코드베이스에서 `process.env.NEXT_PUBLIC_SUPABASE_URL!` 등 직접 접근이 다수 존재한다. 빌드 타임에 환경변수 누락을 감지하지 못한다.

**[H-8] 루프 카운터 증가 누락**

`/api/v1/sdk/check`에서 `getLoopCounter`로 현재 카운트를 조회하지만, `incrementLoopCounter`를 호출하지 않는다. 카운터가 항상 0에서 시작해 루프 감지가 동작하지 않는다.

```typescript
// 현재: 조회만 함
const loopCount = await getLoopCounter(project.id, body.request_hash);

// 필요: 조회 + 증가
const loopCount = await incrementLoopCounter(project.id, body.request_hash);
```

---

### MEDIUM

**[M-1] bcrypt cost factor — 10은 SDK 핫패스에 부적합**

`hashApiKey`에 `bcrypt.hash(key, 10)` 사용. 키 발급 시(1회)는 문제없지만, `/sdk/check`와 `/sdk/report` 매 요청마다 `bcrypt.compare`가 호출된다. bcrypt cost=10은 약 100~300ms 소요. SDK check가 p99 < 50ms 목표(Engineering Rules BE 2번)를 달성할 수 없다.

권장: SDK API용 빠른 검증에는 HMAC-SHA256 서명 비교를 추가하고, bcrypt는 발급 시만 사용. 또는 Redis에 prefix→hash 캐시를 두어 bcrypt 횟수를 줄인다.

**[M-2] `/api/v1/sdk/*` 미들웨어 제외 설정 — 맞지만 주의 필요**

`middleware.ts`:
```typescript
'/((?!api/v1/sdk|_next/static|...).*)'
```
SDK 엔드포인트가 미들웨어에서 제외되는 것은 의도된 설계다. 하지만 `/api/v1/` 하위에 나중에 추가되는 엔드포인트가 실수로 인증 없이 공개될 수 있다. `/api/v1/sdk/`만 제외하고 나머지는 명시적으로 보호하는 allowlist 방식을 권장한다.

**[M-3] `@supabase/auth-helpers-nextjs` 미사용 패키지 포함**

`package.json`에 `@supabase/auth-helpers-nextjs`(v0.15.0)와 `@supabase/ssr`(v0.10.0)이 모두 포함. `auth-helpers-nextjs`는 deprecated이며 `ssr` 패키지로 이미 이전됐다. 미사용 패키지로 번들 크기만 증가한다.

**[M-4] `next-auth` 미사용 패키지 포함**

`package.json`에 `next-auth`(v4.24.13)가 있으나 코드에서 사용하지 않는다. Supabase Auth를 사용하므로 불필요. 제거 필요.

**[M-5] `/sdk/report` 비동기 처리 — Vercel 제약 위험**

```typescript
(async () => {
  // DB write 로직
})();
return response; // 즉시 반환
```
Vercel Serverless Function은 응답 반환 후 실행이 중단될 수 있다. 백그라운드 IIFE가 완료되기 전에 함수가 종료될 위험이 있다. `waitUntil`을 지원하는 환경(Edge Runtime)이 아닌 Node.js Runtime에서는 `waitUntil` 없이 fire-and-forget이 불안정하다.

권장: Vercel의 `waitUntil` API 사용 또는 응답 반환 전에 완료되도록 처리.

**[M-6] chart API — usage_logs 직접 풀스캔**

`/api/dashboard/chart`에서 N일치 `usage_logs`를 전량 조회 후 애플리케이션 레벨에서 집계한다. `budgets` 테이블이 일별 집계 캐시 역할로 설계됐으나 활용하지 않는다. 로그가 많아질수록 느려지는 O(n) 쿼리다.

**[M-7] `requestId`가 일부 에러 응답에 누락**

`/api/webhooks/slack-test` 에러 응답에 `requestId`가 없다. Engineering Rules에서 "모든 API 응답에 requestId 포함" 명시. 일관성 깨짐.

---

## 항목별 요약

| 우선순위 | ID | 항목 | 파일 위치 |
|----------|-----|------|----------|
| CRITICAL | C-1 | SDK check 서버사이드 타임아웃 미적용 | `src/app/api/v1/sdk/check/route.ts` |
| CRITICAL | C-2 | 서킷브레이커 패턴 미구현 | `src/lib/upstash.ts` + `check/route.ts` |
| CRITICAL | C-3 | API Key prefix 조회 timing attack | `src/app/api/v1/sdk/check/route.ts`, `report/route.ts` |
| CRITICAL | C-4 | service client 싱글톤 보안 격리 위반 | `src/lib/supabase/server.ts` |
| HIGH | H-1 | 대시보드 Mock 데이터 + Realtime 미연결 | `src/app/dashboard/page.tsx` |
| HIGH | H-2 | budgets call_count 증가 로직 버그 | `src/app/api/v1/sdk/report/route.ts` |
| HIGH | H-3 | Stripe Webhook 엔드포인트 미구현 | 없음 |
| HIGH | H-4 | 프로젝트 생성 period_start 날짜 버그 | `src/app/api/dashboard/projects/route.ts` |
| HIGH | H-5 | dashboard layout 전체 use client | `src/app/dashboard/layout.tsx` |
| HIGH | H-6 | Slack Webhook URL 평문 저장 | `alerts` 테이블 |
| HIGH | H-7 | 환경변수 zod 검증 미구현 | 전체 |
| HIGH | H-8 | 루프 카운터 증가 누락 — 루프 감지 불동작 | `src/app/api/v1/sdk/check/route.ts` |
| MEDIUM | M-1 | bcrypt cost=10 SDK 핫패스 성능 문제 | `src/lib/utils.ts` |
| MEDIUM | M-2 | 미들웨어 allowlist 설계 취약 | `src/middleware.ts` |
| MEDIUM | M-3 | auth-helpers-nextjs deprecated 패키지 | `package.json` |
| MEDIUM | M-4 | next-auth 미사용 패키지 | `package.json` |
| MEDIUM | M-5 | Vercel fire-and-forget 불안정 | `src/app/api/v1/sdk/report/route.ts` |
| MEDIUM | M-6 | chart API O(n) 풀스캔 | `src/app/api/dashboard/chart/route.ts` |
| MEDIUM | M-7 | requestId 누락 에러 응답 | `src/app/api/webhooks/slack-test/route.ts` |

---

## 즉시 수정 필수 (배포 전 블로커)

1. **H-8 루프 카운터 증가 누락** — 핵심 기능(루프 감지)이 완전히 동작하지 않음. 1줄 수정.
2. **H-2 call_count 버그** — budgets 테이블 데이터가 오염됨. DB 신뢰성 문제.
3. **C-4 service client 싱글톤** — 서로 다른 요청 간 Service Role 클라이언트 공유. 보안 위험.
4. **C-3 timing attack** — 더미 bcrypt 비교 추가로 방어 가능.

---

## 잘 구현된 부분 (통과)

- Zod 스키마로 모든 API 입력 검증
- 에러 응답 형식 통일 (code, message, requestId)
- bcrypt로 API Key 원본 비저장 (발급 시 1회만 노출)
- Upstash Redis HTTP 기반 카운터 (incrbyfloat, expire 정상 사용)
- RLS 정책 6개 테이블 전부 적용
- DB 스키마가 설계 명세와 거의 일치 (stripe_events 테이블 추가는 플러스)
- `X-LLM-Guard-Key` 헤더 기반 SDK 인증 분리
- bcrypt.compare의 상수 시간 특성을 활용한 기본 timing-safe 비교
- 미들웨어에서 /dashboard 보호 + /api/v1/sdk 제외 설계
- get_current_spend, get_month_period_start DB 함수 구현

---

## QA에게 전달

테스트 우선순위:
1. SDK check API에서 루프 카운터가 실제로 증가하는지 확인 (H-8 수정 후)
2. budgets.call_count가 호출마다 정확히 +1 되는지 확인 (H-2 수정 후)
3. 예산 초과 시 allowed=false 응답 + 실제 LLM 호출 차단 E2E 테스트
4. API Key 발급 → SDK check 인증 → report 전체 플로우 통합 테스트
