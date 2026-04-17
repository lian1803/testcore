# Supabase/Upstash → Cloudflare D1/KV 마이그레이션 가이드

## 개요

llm-guard-app의 백엔드를 다음과 같이 전환했습니다:

| 기존 | 새것 |
|---|---|
| Supabase Auth (PostgreSQL) | JWT + Cloudflare D1 (SQLite) |
| Supabase Service Role | D1 HTTP API |
| Upstash Redis | Cloudflare KV (HTTP API) |
| `@supabase/ssr`, `@supabase/supabase-js` | 커스텀 D1/KV 클라이언트 |

---

## 설정 단계

### 1. Cloudflare D1 데이터베이스 생성

```bash
# Wrangler로 D1 데이터베이스 생성
wrangler d1 create llm-guard-app

# 응답에서 database_id와 account_id 메모
```

### 2. Cloudflare KV Namespace 생성

```bash
# KV 네임스페이스 생성
wrangler kv:namespace create llm-guard-app

# 응답에서 namespace_id 메모
```

### 3. 환경변수 설정

`.env.local` 또는 Vercel에서 다음 변수 설정:

```env
CF_ACCOUNT_ID=your-cloudflare-account-id
CF_D1_DATABASE_ID=your-d1-database-id
CF_API_TOKEN=your-cloudflare-api-token
CF_KV_NAMESPACE_ID=your-kv-namespace-id
JWT_SECRET=your-secure-jwt-secret-min-32-chars
NEXT_PUBLIC_APP_URL=https://yourdomain.com
NODE_ENV=production
```

### 4. D1 마이그레이션 실행

```bash
# SQL 스크립트로 D1 초기화
# d1-migrations/001_init.sql 파일 실행
wrangler d1 execute llm-guard-app --file ./d1-migrations/001_init.sql
```

또는 Vercel에서:

```bash
vercel env pull
# 로컬 .env 파일에서 D1 자격증명 사용
# 그런 다음 마이그레이션 실행
```

### 5. 패키지 설치

```bash
# Supabase 패키지 제거
npm uninstall @supabase/ssr @supabase/supabase-js @supabase/auth-helpers-nextjs @upstash/redis

# 새 패키지 설치
npm install jose
```

---

## 주요 변경 사항

### 인증 (Auth)

**기존:**
```typescript
import { createClient } from '@/lib/supabase/server';
const supabase = await createClient();
await supabase.auth.signUp({ email, password });
```

**새것:**
```typescript
import { signup, login, verifyJWT } from '@/lib/auth';
const { user, token } = await signup(email, password);
```

- JWT는 쿠키로 설정 (HttpOnly, Secure, SameSite=Strict)
- 비밀번호는 bcryptjs로 해싱
- `/middleware.ts`에서 JWT 검증

### 데이터베이스 (D1)

**기존:**
```typescript
const { data, error } = await supabase
  .from('users')
  .select('*')
  .eq('id', userId)
  .single();
```

**새것:**
```typescript
import { d1QueryOne } from '@/lib/d1';
const user = await d1QueryOne<User>(
  'SELECT * FROM users WHERE id = ?',
  [userId]
);
```

- 모든 쿼리는 SQL 문자열 + params로 전달
- D1 HTTP API 기반 (REST)
- 트랜잭션 지원 제한적

### 캐시 & 예산 추적 (KV)

**기존:**
```typescript
import { Redis } from '@upstash/redis';
const redis = getRedis();
await redis.incrbyfloat('budget:projectId:current', amount);
```

**새것:**
```typescript
import { incrementSpent } from '@/lib/cf-kv';
await incrementSpent(projectId, amount);
```

- CF KV는 Lua script 미지원 → 낙관적 잠금 사용
- 모든 KV 함수는 이미 Upstash 호환 인터페이스로 제공

---

## API 엔드포인트 호환성

| 엔드포인트 | 변경 |
|---|---|
| `POST /api/auth/signup` | ✅ 호환 (JWT 쿠키 기반) |
| `POST /api/auth/login` | ✅ 호환 (JWT 쿠키 기반) |
| `POST /api/auth/signout` | ✅ 호환 (쿠키 삭제) |
| `POST /api/v1/sdk/check` | ✅ 호환 (D1 + KV) |
| `POST /api/v1/sdk/report` | ✅ 호환 (D1 + KV, fire-and-forget) |
| `GET /api/dashboard/*` | 🔄 변경 예정 (D1 쿼리) |

---

## 마이그레이션 체크리스트

- [ ] Cloudflare 계정 생성 및 API 토큰 발급
- [ ] D1 데이터베이스 생성 및 마이그레이션 실행
- [ ] KV 네임스페이스 생성
- [ ] 환경변수 설정 (로컬 + Vercel)
- [ ] 패키지 설치 (`npm install`)
- [ ] 로컬 개발 서버 테스트 (`npm run dev`)
- [ ] 기존 사용자 데이터 마이그레이션 (필요시)
- [ ] API 테스트 (회원가입 → 로그인 → SDK check/report)
- [ ] 대시보드 라우트 테스트 (JWT 검증)
- [ ] 프로덕션 배포

---

## 기존 Supabase 데이터 마이그레이션

기존 Supabase에서 데이터를 내보내야 한다면:

1. Supabase Dashboard에서 데이터 Export
2. CSV/JSON → D1로 import

```bash
# 예: users 테이블 데이터 import
# supabase_users.json → D1로
wrangler d1 execute llm-guard-app --batch \
  "INSERT INTO users (id, email, plan, created_at, updated_at) VALUES (?, ?, ?, ?, ?)"
```

---

## 주의사항

### 1. SQLite vs PostgreSQL 문법

D1은 SQLite 기반이므로 PostgreSQL 문법이 다릅니다:

| PostgreSQL | SQLite |
|---|---|
| `UUID` | `TEXT` |
| `TIMESTAMPTZ` | `TEXT` (ISO 8601) |
| `NUMERIC(10, 4)` | `REAL` |
| `gen_random_uuid()` | 애플리케이션 코드에서 UUID 생성 |
| `ON CONFLICT ... DO UPDATE` | `INSERT OR REPLACE` |

### 2. KV의 제한사항

- Lua script 미지원 (race condition 방지는 낙관적 방식 사용)
- 크기 제한: 최대 25MB 값
- TTL 설정 시 GET → SET with expirationTtl

### 3. 성능

- D1은 HTTP API 기반이므로 레이턴시 증가 가능
- KV는 지역별 캐싱으로 빠름 (하지만 consistency 주의)

---

## 트러블슈팅

### "Missing Cloudflare credentials"

```
Error: Missing Cloudflare D1 credentials in environment variables
```

→ `.env.local`에 `CF_ACCOUNT_ID`, `CF_D1_DATABASE_ID`, `CF_API_TOKEN` 확인

### "D1 Query failed"

```
D1 Query failed: [{"message": "no such table: users"}]
```

→ `wrangler d1 execute llm-guard-app --file ./d1-migrations/001_init.sql` 실행

### JWT 검증 실패

```
JWT verification failed
```

→ `JWT_SECRET` 환경변수 확인 (최소 32자)

---

## 다음 단계

1. **대시보드 API** (`/api/dashboard/*`) 전환
   - 모든 쿼리를 D1으로 변경
   - 캐시 레이어 추가 (필요시 KV 사용)

2. **Middleware 마이그레이션** (Next.js 16)
   - `middleware.ts` → `proxy.ts` 이름 변경
   - Node.js 런타임 설정

3. **모니터링 & 로깅**
   - Cloudflare Analytics
   - D1 Query logs
   - KV access logs

---

## 유용한 링크

- [Cloudflare D1 Documentation](https://developers.cloudflare.com/d1/)
- [Cloudflare KV Documentation](https://developers.cloudflare.com/kv/)
- [Wrangler CLI](https://developers.cloudflare.com/workers/wrangler/)
- [SQLite Query Language](https://www.sqlite.org/lang.html)
