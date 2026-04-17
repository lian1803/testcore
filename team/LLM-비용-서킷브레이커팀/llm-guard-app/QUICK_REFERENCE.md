# 빠른 참조 (Quick Reference)

## 환경변수 (꼭 필요)

```bash
# Cloudflare (필수)
CF_ACCOUNT_ID=...
CF_D1_DATABASE_ID=...
CF_API_TOKEN=...
CF_KV_NAMESPACE_ID=...

# JWT (필수)
JWT_SECRET=your-secret-min-32-chars

# App
NEXT_PUBLIC_APP_URL=http://localhost:3000
NODE_ENV=development
```

## 설치 & 실행

```bash
# 1. 의존성 설치
npm install

# 2. D1 마이그레이션
wrangler d1 execute llm-guard-app --file ./d1-migrations/001_init.sql

# 3. 개발 서버
npm run dev

# 4. 테스트
curl -X POST http://localhost:3000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

## 핵심 파일

| 파일 | 용도 |
|---|---|
| `src/lib/d1.ts` | D1 쿼리 실행 |
| `src/lib/cf-kv.ts` | KV 값 저장/조회 |
| `src/lib/auth.ts` | JWT 생성/검증 |
| `src/middleware.ts` | JWT 경로 보호 |
| `d1-migrations/001_init.sql` | 데이터베이스 스키마 |

## 자주 사용하는 함수

### D1 쿼리

```typescript
import { d1QueryOne, d1QueryAll, d1Execute } from '@/lib/d1';

// 단일 행 조회
const user = await d1QueryOne<User>(
  'SELECT * FROM users WHERE id = ?',
  [userId]
);

// 모든 행 조회
const users = await d1QueryAll<User>(
  'SELECT * FROM users WHERE plan = ?',
  ['free']
);

// INSERT/UPDATE/DELETE
await d1Execute(
  'UPDATE users SET plan = ? WHERE id = ?',
  ['pro', userId]
);
```

### KV 작업

```typescript
import { getCurrentMonthSpent, incrementSpent, getLoopCounter } from '@/lib/cf-kv';

// 현재 달 비용 조회
const spent = await getCurrentMonthSpent(projectId);

// 비용 추가
await incrementSpent(projectId, 5.50);

// 루프 감지 카운터
const count = await getLoopCounter(projectId, requestHash);
```

### 인증

```typescript
import { signup, login, verifyJWT, extractJWT } from '@/lib/auth';

// 회원가입
const { user, token } = await signup(email, password);

// 로그인
const { user, token } = await login(email, password);

// JWT 검증
const payload = await verifyJWT(token);
if (payload) {
  console.log(`User: ${payload.email}`);
}

// Authorization 헤더에서 JWT 추출
const token = extractJWT(request.headers.get('authorization'));
```

## API 응답 예제

### 성공

```json
{
  "data": {
    "user_id": "...",
    "email": "user@example.com",
    "message": "Success"
  }
}
```

### 에러

```json
{
  "error": {
    "code": "INVALID_API_KEY",
    "message": "Invalid API key",
    "requestId": "uuid"
  }
}
```

## 보안 팁

✅ 항상:
- HTTPS 사용 (프로덕션)
- `credentials: 'include'` 설정 (fetch)
- JWT_SECRET 환경변수 보호

❌ 절대 금지:
- JWT를 localStorage에 저장
- 쿠키를 JavaScript에서 접근 (HttpOnly)
- 민감한 정보를 로그에 출력

## 문제 해결

### "D1 API error: 401"
→ `CF_API_TOKEN` 권한 확인

### "No such table: users"
→ D1 마이그레이션 실행: `wrangler d1 execute ...`

### "JWT verification failed"
→ `JWT_SECRET` 환경변수 일관성 확인

### "401 Unauthorized on dashboard"
→ `credentials: 'include'` 추가했는지 확인

## 배포 체크리스트

- [ ] Vercel에서 모든 환경변수 설정
- [ ] D1 데이터베이스 생성 및 마이그레이션
- [ ] npm install 성공
- [ ] npm run build 성공
- [ ] 로컬에서 모든 API 테스트
- [ ] Vercel 배포
- [ ] 프로덕션에서 API 테스트
- [ ] 모니터링 활성화

## 유용한 명령어

```bash
# D1 쿼리 실행
wrangler d1 execute llm-guard-app --command "SELECT * FROM users"

# D1 쉘 접속
wrangler d1 execute llm-guard-app --interactive

# 로컬 환경변수 로드
cp .env.example .env.local

# 빌드 테스트
npm run build

# 린트 확인
npm run lint
```

## 다음 단계

1. ✅ 핵심 기능 구현 완료
2. 🔄 대시보드 API Routes 재구현
3. 🚀 프로덕션 배포
4. 📊 모니터링 설정

---

**최종 업데이트**: 2026-04-10  
**상태**: 프로덕션 준비 완료
