# FE 통합 가이드 — Cloudflare D1/KV 백엔드

## 📍 API 엔드포인트 변경 사항

**좋은 소식**: 모든 API 응답이 **동일하게 유지**됩니다. FE 코드 변경 불필요!

---

## 인증 (Auth)

### 회원가입

```bash
POST /api/auth/signup
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**응답** (동일):
```json
{
  "data": {
    "user_id": "uuid-...",
    "email": "user@example.com",
    "plan": "free",
    "message": "Signup successful"
  }
}
// Set-Cookie: auth_token=jwt-token; HttpOnly; Secure; SameSite=Strict
```

### 로그인

```bash
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**응답** (동일):
```json
{
  "data": {
    "user_id": "uuid-...",
    "email": "user@example.com",
    "plan": "free",
    "message": "Login successful"
  }
}
// Set-Cookie: auth_token=jwt-token; HttpOnly; Secure; SameSite=Strict
```

### 로그아웃

```bash
POST /api/auth/signout
```

**응답**:
```json
{
  "data": {
    "message": "Signout successful"
  }
}
// Set-Cookie: auth_token=; expires=...
```

---

## 쿠키 기반 인증

JWT는 **HttpOnly 쿠키**로 설정됩니다:

```typescript
// 자동으로 쿠키에 포함됨 (fetch/axios)
fetch('/api/dashboard/api-keys', {
  credentials: 'include'  // 쿠키 전달 필수
})
```

### 커스텀 헤더 (선택사항)

API 키 업데이트 또는 프로그래매틱 접근:

```bash
Authorization: Bearer <jwt-token>
```

**쿠키에서 JWT 추출** (필요시):

```typescript
// JavaScript
const token = document.cookie
  .split(';')
  .find(c => c.trim().startsWith('auth_token='))
  ?.split('=')[1];

// React Hook
export function useAuthToken() {
  const [token, setToken] = useState<string | null>(null);
  useEffect(() => {
    const token = document.cookie
      .split(';')
      .find(c => c.trim().startsWith('auth_token='))
      ?.split('=')[1] || null;
    setToken(token);
  }, []);
  return token;
}
```

---

## SDK 체크 & 보고

### SDK Check (API 키 검증)

```bash
POST /api/v1/sdk/check
X-LLM-Guard-Key: lg_...
Content-Type: application/json

{
  "model": "gpt-4o",
  "provider": "openai",
  "estimated_tokens": 1000,
  "request_hash": "sha256-hash-of-prompt",
  "context_count": 0
}
```

**응답** (동일):
```json
{
  "allowed": true,
  "current_spend_usd": 5.50,
  "budget_usd": 10.0,
  "remaining_usd": 4.50,
  "estimated_cost_usd": 0.01
}
```

또는 거부된 경우:
```json
{
  "allowed": false,
  "current_spend_usd": 10.0,
  "budget_usd": 10.0,
  "remaining_usd": 0,
  "estimated_cost_usd": 0.01,
  "reason": "budget_exceeded"
}
```

### SDK Report (사용량 기록)

```bash
POST /api/v1/sdk/report
X-LLM-Guard-Key: lg_...
Content-Type: application/json

{
  "model": "gpt-4o",
  "provider": "openai",
  "input_tokens": 900,
  "output_tokens": 150,
  "cost_usd": 0.01234,
  "latency_ms": 450,
  "is_blocked": false,
  "request_hash": "sha256-hash-of-prompt"
}
```

**응답** (fire-and-forget):
```json
{
  "received": true
}
```

---

## 대시보드 경로 (JWT 보호)

모든 대시보드 경로는 JWT 검증됩니다:

```typescript
// ✅ 자동으로 작동 (쿠키 포함)
fetch('/api/dashboard/api-keys', {
  credentials: 'include'  // 쿠키 전달
})

// ❌ 실패 (인증 없음)
fetch('/api/dashboard/api-keys')
// → 401 Unauthorized
```

**미들웨어**가 다음을 자동으로 처리:

1. 쿠키에서 JWT 추출
2. JWT 서명 검증
3. 사용자 ID를 `x-user-id` 헤더로 추가
4. 인증 실패 시 `/auth/login` 리다이렉트

---

## 에러 처리

### 응답 형식 (변경 없음)

```json
{
  "error": {
    "code": "INVALID_REQUEST" | "INVALID_API_KEY" | "PROJECT_NOT_FOUND" | ...,
    "message": "Human-readable error message",
    "requestId": "uuid-for-debugging"
  }
}
```

### HTTP 상태 코드

| 상태 | 의미 |
|---|---|
| 200 | 성공 |
| 201 | 리소스 생성됨 (회원가입) |
| 400 | 잘못된 요청 |
| 401 | 인증 실패 |
| 403 | 권한 없음 (비활성 API 키) |
| 404 | 리소스 없음 |
| 500 | 서버 오류 |

---

## 마이그레이션 영향 (FE 관점)

### ✅ 변경 없음

- 모든 API 응답 형식
- HTTP 상태 코드
- 에러 메시지 구조
- 쿠키 기반 인증

### 🔄 내부 구현 (FE는 무시해도 됨)

- Supabase → D1 (데이터베이스)
- Upstash → Cloudflare KV (캐시)
- Auth0 → JWT + bcryptjs (인증)

### 📝 권장 업데이트 (선택사항)

```typescript
// 환경변수 정리 (더 이상 필요 없음)
// .env.local에서 제거
// NEXT_PUBLIC_SUPABASE_URL
// NEXT_PUBLIC_SUPABASE_ANON_KEY
// NEXTAUTH_URL
// NEXTAUTH_SECRET

// 유지하면 되는 것
// NEXT_PUBLIC_APP_URL
// NODE_ENV
```

---

## 개발 환경 설정 (FE)

### 로컬 개발

```bash
# BE 서버 시작 (다른 터미널)
npm run dev  # http://localhost:3000

# FE 테스트 (axios/fetch)
curl http://localhost:3000/api/auth/login \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

### 프로덕션

BE가 Vercel에 배포되면, FE도 자동으로 같은 Origin에서 요청:

```typescript
// ✅ 자동으로 작동
fetch('/api/auth/login')

// ❌ 수동 URL 불필요
fetch('https://yourdomain.com/api/auth/login')
```

---

## 테스트 시나리오 (FE)

### 1️⃣ 회원가입 → 로그인 → 대시보드

```typescript
// 1. 회원가입
const signupRes = await fetch('/api/auth/signup', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'password123'
  }),
  credentials: 'include'
});

// 2. 자동으로 쿠키 설정됨
// → 이제 대시보드 접근 가능

// 3. 대시보드 접근
const dashRes = await fetch('/api/dashboard/api-keys', {
  credentials: 'include'  // 쿠키 포함
});
```

### 2️⃣ JWT 만료 처리

```typescript
// JWT는 7일 후 만료
// 자동으로 /auth/login으로 리다이렉트됨
fetch('/api/dashboard/...')
  .then(res => {
    if (res.status === 401) {
      window.location.href = '/auth/login';
    }
  })
```

### 3️⃣ SDK 체크 & 보고

```typescript
// SDK Check
const checkRes = await fetch('/api/v1/sdk/check', {
  method: 'POST',
  headers: {
    'X-LLM-Guard-Key': 'lg_...',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    model: 'gpt-4o',
    provider: 'openai',
    estimated_tokens: 1000,
    request_hash: '...',
    context_count: 0
  })
});

const checkResult = await checkRes.json();
if (checkResult.allowed) {
  // 진행
} else {
  // 예산 초과
  console.log(`Budget exceeded. Remaining: $${checkResult.remaining_usd}`);
}

// SDK Report
await fetch('/api/v1/sdk/report', {
  method: 'POST',
  headers: {
    'X-LLM-Guard-Key': 'lg_...',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    model: 'gpt-4o',
    provider: 'openai',
    input_tokens: 900,
    output_tokens: 150,
    cost_usd: 0.01234,
    latency_ms: 450,
    is_blocked: false,
    request_hash: '...'
  })
});
```

---

## 주의사항

### ⚠️ 쿠키 설정 필수

```typescript
// ❌ 틀린 방법
fetch('/api/dashboard/api-keys')

// ✅ 올바른 방법
fetch('/api/dashboard/api-keys', {
  credentials: 'include'  // 쿠키 포함
})

// ✅ axios
axios.defaults.withCredentials = true;
```

### ⚠️ CORS 설정

BE와 FE가 다른 도메인이면, BE에서 CORS 설정 필요:

```typescript
// BE: src/middleware.ts 또는 route.ts에서
response.headers.set('Access-Control-Allow-Origin', process.env.NEXT_PUBLIC_APP_URL);
response.headers.set('Access-Control-Allow-Credentials', 'true');
response.headers.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE');
response.headers.set('Access-Control-Allow-Headers', 'Content-Type, Authorization');
```

---

## 문제 해결

### "401 Unauthorized on `/api/dashboard/api-keys`"

→ `credentials: 'include'` 추가했는지 확인

### "Cookie not being set"

→ HTTPS에서만 Secure 쿠키 설정 (로컬: HTTP 가능)

### "CORS error"

→ BE에서 `Access-Control-Allow-Credentials: true` 설정 확인

---

## 연락처

**BE 팀**: 정우  
**문제 신고**: GitHub Issues  
**Slack**: #backend-team
