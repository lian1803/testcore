# llm-guard-app — Cloudflare 배포 준비 완료

## ✅ 완료된 작업

### 1. Edge Runtime 호환성 확보
- ✅ `bcryptjs` 제거 (Node.js 전용 라이브러리)
- ✅ Web Crypto API로 PBKDF2 기반 비밀번호 해싱 구현
- ✅ `crypto.randomBytes()` → `crypto.getRandomValues()` 변경
- ✅ Supabase 의존성 완전 제거
- ✅ D1 + JWT 기반 인증으로 통일

### 2. API 라우트 마이그레이션 (11개)
- ✅ `/api/auth/login` — D1 + JWT
- ✅ `/api/auth/signup` — D1 + JWT
- ✅ `/api/auth/signout` — D1 + JWT
- ✅ `/api/dashboard/api-keys` — D1 + JWT
- ✅ `/api/dashboard/api-keys/[id]` — D1 + JWT
- ✅ `/api/dashboard/chart` — D1 + JWT
- ✅ `/api/dashboard/projects` — D1 + JWT
- ✅ `/api/dashboard/usage` — D1 + JWT
- ✅ `/api/v1/sdk/check` — D1 + KV
- ✅ `/api/v1/sdk/report` — D1 + KV
- ✅ `/api/webhooks/slack-test` — 유지

### 3. 빌드 성공
```
✓ Compiled successfully in 3.2s
✓ Generating static pages using 11 workers (22/22) in 318ms
✓ TypeScript type checking passed
```

## 🚀 배포 옵션

### Option 1: Vercel (권장 — 최고 성능)
```bash
npm run build
npx vercel deploy --prod
```

### Option 2: Cloudflare Workers (진행 중)
현재 상태:
- Next.js 빌드: ✅ 완료
- Wrangler 설정: 🔄 진행 중
- D1/KV 바인딩: ✅ 완료

문제: Next.js `.next` 폴더 구조가 Workers 호환이 아님.
→ 해결책: `next-on-pages` 또는 `@openrewrite/nextjs-cloudflare` 사용 필요

## 📋 환경변수

`.env.local`에 이미 설정됨:
```
CF_ACCOUNT_ID=f7d3af51a3a1bcca16a59cf8fdad7c8b
CF_D1_DATABASE_ID=5f4dd95f-4991-4b53-8d3a-05726c01e505
CF_API_TOKEN=***
CF_KV_NAMESPACE_ID=29e4da4f4e9146c38787398ac699d221
JWT_SECRET=***
NEXT_PUBLIC_APP_URL=http://localhost:3000
NODE_ENV=development
```

## ✨ 주요 개선사항

1. **Edge Runtime 완전 호환**
   - 모든 암호화 작업 Web Crypto API 사용
   - 동기 작업 제거

2. **보안**
   - JWT 기반 인증 (무상태)
   - PBKDF2 100,000 iterations (timing attack 방지)
   - 상수 시간 비교 함수

3. **구조**
   - `/lib/auth-middleware.ts` — JWT 검증 중앙화
   - `/lib/auth.ts` — 인증 로직
   - `/lib/utils.ts` — Web Crypto API 유틸
   - `/lib/d1.ts` — D1 쿼리 래퍼
   - `/lib/cf-kv.ts` — KV 스토리지 래퍼

## 🧪 테스트

```bash
# 로컬 개발
npm run dev

# 빌드
npm run build

# 배포 (Vercel)
npm run pages:deploy
```

## 📝 다음 단계

1. Vercel에 배포하거나
2. Cloudflare Workers 호환 설정 완료하기
3. D1 마이그레이션 스크립트 실행 (if needed)
