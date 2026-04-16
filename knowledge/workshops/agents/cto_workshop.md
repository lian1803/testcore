## ── 세계 최고 CTO 워크샵 — 10년차 테크 리더 마스터클래스 ──

### 🏗️ 아키텍처 의사결정 프레임워크

**핵심 원칙: 단순함이 먼저, 복잡함은 증명된 필요에 의해서만**

#### 언제 Monolith를 선택하나
- 팀 규모 5명 이하
- 도메인 경계가 아직 불명확할 때
- MVP / 시장 검증 단계
- 배포 복잡도를 최소화해야 할 때
- **결론:** 시작은 무조건 Monolith. Modular Monolith로 경계를 잡으면서 시작해라.

#### 언제 Microservices로 전환하나
- 특정 서비스만 독립적으로 스케일해야 할 때 (예: 이미지 처리, 결제)
- 팀이 도메인별로 명확히 분리될 때 (Conway's Law)
- 배포 주기가 서비스마다 완전히 달라야 할 때
- **경고:** Microservices는 네트워크 지연, 분산 트랜잭션, 운영 복잡도를 모두 감수해야 한다. 팀이 준비되지 않으면 독이다.

#### 언제 Serverless를 선택하나
- 이벤트 드리븐 작업 (이미지 리사이징, 이메일 전송, 웹훅 처리)
- 트래픽이 불규칙하고 예측 불가할 때
- 운영팀 없이 돌아가야 할 때
- **경고:** Cold start가 허용되지 않는 실시간 API에는 부적합. Cloudflare Workers는 V8 isolate 방식으로 cold start 없음 — 이 스택에서는 Serverless 최우선.

#### 트레이드오프 정리표
| | Monolith | Microservices | Serverless |
|---|---|---|---|
| 개발 속도 | 빠름 | 느림 | 빠름 (단순 기능) |
| 운영 복잡도 | 낮음 | 높음 | 낮음 |
| 스케일링 | 전체 단위 | 서비스 단위 | 함수 단위 |
| 트랜잭션 | 쉬움 | 어려움 (saga) | 어려움 |
| 비용 | 고정 | 고정+운영비 | 사용량 기반 |

**2025 현실:** 스타트업 99%는 Modular Monolith로 충분하다. Microservices는 Netflix가 아닌 이상 섣불리 시작하지 마라.

---

### 🗄️ SaaS 멀티테넌트 DB 설계 패턴

#### 3가지 모델 비교

**Pool 모델 (공유 DB + RLS)**
- 모든 테넌트가 같은 테이블, tenant_id 컬럼으로 구분
- PostgreSQL Row-Level Security로 DB 레벨 격리
- 장점: 운영 단순, 비용 효율, 쿼리 최적화 쉬움
- 단점: 테넌트 간 완전 격리 불가, 대형 테넌트가 전체에 영향
- **적합:** 초기 SaaS, SMB 타겟, 테넌트 수 많을 때

**Bridge 모델 (스키마 분리)**
- 테넌트마다 별도 PostgreSQL 스키마 (tenant_a.users, tenant_b.users)
- 장점: 스키마 레벨 격리, 테넌트별 백업 가능
- 단점: 마이그레이션 복잡 (스키마 수만큼 실행), 연결 풀 관리 복잡
- **적합:** 테넌트 수 100개 이하, 규제 요건 있을 때

**Silo 모델 (DB 분리)**
- 테넌트마다 독립 DB 인스턴스
- 장점: 완전 격리, 테넌트별 독립 스케일링, 컴플라이언스 대응
- 단점: 운영 복잡도 폭발, 비용 높음
- **적합:** Enterprise 고객, HIPAA/SOC2 필요 시, 고가 계약 테넌트

#### Prisma + PostgreSQL RLS 구현 (Pool 모델)

```sql
-- 모든 테이블에 tenant_id 컬럼 추가
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation ON users
  USING (tenant_id = current_setting('app.tenant_id')::uuid);

-- 인덱스는 반드시 tenant_id 포함
CREATE INDEX idx_users_tenant ON users(tenant_id, id);
```

```typescript
// Prisma middleware로 tenant context 자동 주입
const tenantClient = prisma.$extends({
  query: {
    $allModels: {
      async $allOperations({ args, query }) {
        const [, result] = await prisma.$transaction([
          prisma.$executeRaw`SET LOCAL app.tenant_id = ${tenantId}`,
          query(args),
        ]);
        return result;
      },
    },
  },
});
```

**핵심 규칙:**
- tenant_id는 애플리케이션 레이어에서 절대 신뢰하지 말 것 — DB 레벨에서 강제
- 모든 인덱스에 tenant_id를 첫 번째 컬럼으로
- Admin 쿼리용 별도 DB 역할(role) 관리

---

### ⚡ Next.js 프로덕션 아키텍처

#### App Router 컴포넌트 결정 트리

```
이 컴포넌트가 필요한 것:
├── 브라우저 API (window, localStorage) → Client Component
├── 이벤트 핸들러 (onClick, onChange) → Client Component
├── useState / useEffect → Client Component
├── DB / API 직접 접근 → Server Component ✅
├── 민감한 데이터 (API 키) → Server Component ✅
└── SEO 중요한 콘텐츠 → Server Component ✅
```

**원칙:** Server Component가 기본값. Client Component는 트리의 최말단(leaf)에만.

#### 캐싱 전략 4단계

```typescript
// 1. 정적 데이터 (빌드 타임 캐시)
fetch('/api/config', { cache: 'force-cache' })

// 2. 시간 기반 재검증 (ISR)
fetch('/api/posts', { next: { revalidate: 3600 } }) // 1시간

// 3. 태그 기반 온디맨드 재검증
fetch('/api/product', { next: { tags: ['product'] } })
// 업데이트 시: revalidateTag('product')

// 4. 완전 동적 (캐시 없음)
fetch('/api/realtime', { cache: 'no-store' })
```

#### Edge Runtime vs Node.js Runtime

| | Edge Runtime | Node.js Runtime |
|---|---|---|
| 콜드 스타트 | 없음 | 있음 |
| 실행 위치 | CDN 엣지 | 단일 리전 |
| 메모리 제한 | 128MB | 1GB+ |
| Node.js API | 제한적 | 완전 지원 |
| **적합** | 미들웨어, 인증, 리다이렉트 | DB 쿼리, 파일 처리 |

#### 프로덕션 필수 패턴

```typescript
// Parallel Data Fetching — 순차 말고 병렬로
const [user, posts, analytics] = await Promise.all([
  getUser(id),
  getPosts(userId),
  getAnalytics(userId),
]);

// Streaming으로 TTFB 개선
export default function Page() {
  return (
    <>
      <StaticHeader />           {/* 즉시 렌더 */}
      <Suspense fallback={<Skeleton />}>
        <SlowDataComponent />    {/* 스트리밍 */}
      </Suspense>
    </>
  );
}
```

---

### 🔒 보안 아키텍처 체크리스트

#### OWASP Top 10 대응 (SaaS 필수)

| 위협 | 대응 |
|------|------|
| Broken Access Control | 모든 API에 미들웨어 레벨 인가 체크. DB RLS 이중화. |
| Cryptographic Failures | 비밀번호 bcrypt(cost≥12). 민감 데이터 AES-256. HTTPS 강제. |
| Injection | Prisma ORM 사용 시 기본 방어. Raw query는 parameterized만. |
| Insecure Design | Threat modeling 초기 설계에 포함. |
| Security Misconfiguration | 환경변수 노출 금지. 에러 메시지에 스택 트레이스 금지 (프로덕션). |
| SSRF | 외부 URL 요청 시 allowlist 기반 검증. |

#### JWT 처리 원칙

```typescript
// Access Token: 짧게 (15~30분)
// Refresh Token: 길게 (7~30일), HttpOnly Cookie에만 저장

// 절대 금지
localStorage.setItem('token', accessToken); // ❌ XSS 취약

// 올바른 방법
// Access Token → 메모리 (변수)
// Refresh Token → HttpOnly Secure SameSite=Strict Cookie

// 알고리즘: RS256 또는 ES256 사용 (HS256은 secret 노출 시 전체 위험)
```

#### API 보안 필수 항목

```typescript
// 1. Rate Limiting (Cloudflare Workers에서)
const rateLimiter = new RateLimiter({
  requests: 100,
  window: '1m',
  key: (req) => req.headers.get('CF-Connecting-IP'),
});

// 2. Input Validation (Zod)
const schema = z.object({
  email: z.string().email().max(255),
  amount: z.number().positive().max(1000000),
});

// 3. CORS 명시적 설정
corsHeaders: {
  'Access-Control-Allow-Origin': process.env.ALLOWED_ORIGIN, // * 금지
}

// 4. Security Headers (Next.js)
// next.config.js에 X-Frame-Options, CSP, HSTS 설정
```

---

### 📈 스케일링 전략

#### 트래픽 증가 단계별 대응

**Phase 1: 0 → 1만 DAU**
- 단일 서버로 충분. Cloudflare CDN으로 정적 자산 캐시.
- 병목: 없음 (아직)

**Phase 2: 1만 → 10만 DAU**
- DB 연결 풀 설정 필수 (PgBouncer 또는 Prisma connection limit)
- Read replica 추가 (분석 쿼리 분리)
- Redis 캐싱 도입 (세션, 자주 읽히는 데이터)

```typescript
// DB Connection Pool 설정 (Prisma + PgBouncer)
datasource db {
  url = env("DATABASE_URL")
  // Pool mode: transaction (PgBouncer)
  directUrl = env("DIRECT_DATABASE_URL")
}
// Pool 사이즈 = (코어 수 * 2) + 유효 스핀들 수
```

**Phase 3: 10만+ DAU**
- 수평 스케일링 (stateless 서버 필수)
- Redis Cluster 전환
- DB sharding 또는 테넌트별 DB 분리 검토
- 메시지 큐 도입 (비동기 작업 분리)

#### Redis 캐싱 패턴

```typescript
// Cache-Aside Pattern (가장 일반적)
async function getUser(id: string) {
  const cached = await redis.get(`user:${id}`);
  if (cached) return JSON.parse(cached);

  const user = await db.user.findUnique({ where: { id } });
  await redis.setex(`user:${id}`, 3600, JSON.stringify(user)); // TTL 1시간
  return user;
}

// 캐시 무효화: 업데이트 시 즉시 삭제
async function updateUser(id: string, data: UpdateUser) {
  const user = await db.user.update({ where: { id }, data });
  await redis.del(`user:${id}`); // 캐시 삭제 (다음 읽기에서 재생성)
  return user;
}
```

#### Rate Limiting 구현

```typescript
// Sliding Window Counter (Redis)
async function rateLimit(key: string, limit: number, windowSec: number) {
  const now = Date.now();
  const windowStart = now - windowSec * 1000;

  await redis.zremrangebyscore(key, 0, windowStart);
  const count = await redis.zcard(key);

  if (count >= limit) throw new TooManyRequestsError();

  await redis.zadd(key, now, `${now}-${Math.random()}`);
  await redis.expire(key, windowSec);
}
```

---

### 🛠️ 기술 부채 관리 원칙

#### 부채 유형 분류

| 유형 | 설명 | 대응 |
|------|------|------|
| 의도적 부채 | 속도를 위해 의식적으로 선택 | TODO 주석 + 티켓 즉시 생성. 3개월 내 상환 계획. |
| 우발적 부채 | 몰라서 생긴 나쁜 코드 | 발견 즉시 리팩토링 or 티켓. |
| 환경 부채 | 구 버전 의존성, 구식 패턴 | 분기 1회 의존성 업데이트 스프린트. |
| 아키텍처 부채 | 잘못된 설계 결정 누적 | 가장 비쌈. 초기에 막아야 한다. |

#### 리팩토링 판단 기준

**지금 고쳐라:**
- 보안 취약점
- 데이터 무결성 위험
- 팀 전체 속도를 막는 공유 모듈의 문제
- 다음 기능 개발 시 무조건 건드려야 하는 부분

**나중에 고쳐라 (티켓만):**
- 성능에 영향 없는 코드 스타일
- 이미 잘 작동하는 레거시 기능
- 리팩토링 비용 > 비즈니스 가치인 경우

**그냥 둬라:**
- 변경될 가능성 거의 없는 안정된 코드
- 테스트가 완벽히 감싸고 있는 복잡한 코드
- 팀이 이해하고 있는 "이상하지만 동작하는" 코드

#### 실용적 운영 규칙

- **보이스카웃 규칙:** 건드린 파일은 건드리기 전보다 깨끗하게 두고 나와라.
- **스프린트 15~25% 배정:** 기술 부채 상환을 feature와 동등한 우선순위로.
- **부채 가시화:** 코드에 `// DEBT: [이유] [날짜] [담당자]` 주석 필수.
- **측정 지표:** 코드 복잡도(cyclomatic), 테스트 커버리지, 배포 시간. 수치가 악화되면 멈추고 고쳐라.

---

### 📋 코드 리뷰 기준 (시니어 레벨)

#### 리뷰 우선순위 (이 순서로 확인)

**1순위 — 반드시 차단 (Blocking)**
- 보안 취약점 (SQL injection, XSS, 인증 누락, 민감 데이터 노출)
- 데이터 손실 위험 (잘못된 트랜잭션, 경쟁 조건)
- 비즈니스 로직 오류 (요구사항과 다른 구현)
- 성능 시한폭탄 (N+1 쿼리, 인덱스 없는 대용량 테이블 풀스캔)

**2순위 — 강하게 제안 (Non-blocking but important)**
- 테스트 없는 핵심 로직
- 에러 처리 누락 (unhandled promise rejection, 빈 catch 블록)
- 확장 어렵게 만드는 하드코딩
- 과한 복잡도 (함수 50줄 초과, 중첩 3단계 초과)

**3순위 — 제안 (Nitpick)**
- 네이밍 개선
- 주석 추가
- 코드 스타일 (포맷터가 못 잡은 것만)

#### 시니어가 절대 하지 않는 것

- 포맷팅 지적 — 린터/포맷터의 일이다
- 개인 취향 강요 — "나라면 이렇게 안 했을 것" 같은 주관적 코멘트
- 설명 없는 변경 요구 — 왜 바꿔야 하는지 항상 이유 제시
- PR 24시간 넘게 방치 — 리뷰 지연은 팀 속도를 죽인다

#### 좋은 리뷰 코멘트 공식

```
[문제]: 이 쿼리는 users 테이블을 풀스캔합니다.
[이유]: 트래픽 증가 시 응답 시간이 O(n)으로 증가합니다.
[제안]: email 컬럼에 인덱스 추가하거나 WHERE 조건을 인덱스 컬럼으로 변경하세요.
[참고]: users 테이블이 현재 50만 행 → 인덱스 없으면 p99 500ms 예상.
```

#### Google Engineering Standards 핵심 원칙

> "코드 리뷰어는 PR이 **전체 시스템의 코드 건강도를 개선**하기만 하면 승인해야 한다. 완벽할 필요는 없다."

- 완벽한 코드보다 **작동하는 코드 + 개선 티켓**이 낫다
- 리뷰는 멘토링이기도 하다 — 이유를 가르쳐라, 변경만 강요하지 마라
- PR 크기는 400줄 이하가 적정. 그 이상이면 분리 요청.

#### Wave 4 통합 리뷰 체크리스트 (이 프로젝트 전용)

```
□ FE-BE 인터페이스 타입 일치 확인
□ 환경변수 하드코딩 없음
□ 에러 응답 형식 통일 (code, message, requestId)
□ 인증 미들웨어 모든 보호 라우트에 적용
□ DB 쿼리에 tenant_id 조건 누락 없음
□ console.log 프로덕션 코드에 없음
□ 비동기 에러 처리 (try-catch 또는 .catch())
□ 빌드 에러 없음 (tsc --noEmit 통과)
```
