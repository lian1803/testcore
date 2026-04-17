# BE 구현 완료 보고서 — LLM 비용 서킷브레이커

> **작성일**: 2026-04-08 | **상태**: Week 1 MVP 완료 (개발 준비됨)

---

## 구현된 파일 목록

### 타입 정의
- `src/types/index.ts` — 모든 API 요청/응답 타입 정의

### 라이브러리 & 유틸
- `src/lib/token-pricing.ts` — 모델별 단가 테이블 (OpenAI, Anthropic, Google)
- `src/lib/utils.ts` — API Key 생성, 해싱, 검증, 요청 ID, 날짜 계산 등
- `src/lib/supabase/client.ts` — 브라우저 클라이언트
- `src/lib/supabase/server.ts` — 서버/서비스 롤 클라이언트
- `src/lib/supabase/middleware.ts` — 세션 관리 미들웨어
- `src/lib/upstash.ts` — Redis 클라이언트 + 비용 카운터, 루프 감지

### DB 마이그레이션
- `supabase/migrations/001_init.sql` — 전체 DB 스키마 (users, projects, api_keys, usage_logs, budgets, alerts, stripe_events)

### API Routes

#### SDK 전용 (공개, API Key 검증)
- `src/app/api/v1/sdk/check/route.ts`
  - Pre-call 예산 체크
  - 루프 감지 (Redis)
  - 타임아웃 2초, allow-through on error
  
- `src/app/api/v1/sdk/report/route.ts`
  - 실제 토큰/비용 기록 (비동기)
  - Redis 비용 증액 + DB write

#### 대시보드 (인증 필수)
- `src/app/api/auth/signup/route.ts` — 회원가입 + 초기 프로젝트 생성
- `src/app/api/auth/signout/route.ts` — 로그아웃

- `src/app/api/dashboard/api-keys/route.ts` — GET (목록), POST (생성)
- `src/app/api/dashboard/api-keys/[id]/route.ts` — DELETE (비활성화)

- `src/app/api/dashboard/projects/route.ts` — GET (목록), POST (생성)

- `src/app/api/dashboard/usage/route.ts` — GET (현재 월 누적 비용)
- `src/app/api/dashboard/chart/route.ts` — GET (N일 일별 비용)

#### Webhooks
- `src/app/api/webhooks/slack-test/route.ts` — Slack 웹훅 테스트

### 환경 설정
- `.env.example` — 필요한 모든 환경변수 명시

### 미들웨어
- `src/middleware.ts` — Supabase Auth 세션 관리

---

## 핵심 설계 결정사항

### 1. 응답 타임아웃 & Allow-Through
- SDK check API: 2초 타임아웃 초과 시 `allowed: true` 반환 (가용성 우선)
- 서비스 장애가 사용자 LLM 호출을 중단시키면 안 됨

### 2. 비용 추적 이중 저장
- **Redis**: 빠른 조회용 (응답시간 p99 < 50ms)
- **Supabase**: 영구 저장 + 감사 추적
- Redis miss 시 DB fallback으로 일관성 보장

### 3. API Key 보안
- `lg_` 프리픽스 + 무작위 48자
- DB에는 bcrypt 해시만 저장, 원본은 발급 시 1회만 노출
- 타이밍 어택 방지: bcrypt.compare() 사용

### 4. 루프 감지
- 5분 윈도우 내 동일 request_hash 10회 이상 반복 = 루프
- Redis로 메모리 효율적 추적

### 5. 멀티테넌트 격리
- RLS (Row Level Security) 모든 테이블에 활성화
- user_id FK + RLS 정책으로 완전 격리

### 6. 에러 응답 표준화
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message",
    "requestId": "UUID"
  }
}
```

---

## 기술 스택 확정

| 영역 | 선택 | 이유 |
|------|------|------|
| 라우팅 | Next.js API Routes | Vercel 네이티브 배포 |
| 데이터베이스 | Supabase PostgreSQL | Auth + Realtime + RLS |
| 캐시/카운터 | Upstash Redis | Serverless HTTP 기반, 커넥션 풀 문제 없음 |
| 인증 | Supabase Auth | JWT 세션 관리 |
| 토큰 검증 | bcryptjs | 상수 시간 비교 |

---

## API 엔드포인트 요약

### SDK (공개)
| 메서드 | 경로 | 역할 | 인증 |
|--------|------|------|------|
| POST | `/api/v1/sdk/check` | 예산 체크 | API Key |
| POST | `/api/v1/sdk/report` | 사용량 기록 | API Key |

### 대시보드 (인증 필수, Supabase JWT)
| 메서드 | 경로 | 역할 |
|--------|------|------|
| POST | `/api/auth/signup` | 회원가입 |
| POST | `/api/auth/signout` | 로그아웃 |
| GET | `/api/dashboard/api-keys` | 키 목록 |
| POST | `/api/dashboard/api-keys` | 키 생성 |
| DELETE | `/api/dashboard/api-keys/[id]` | 키 삭제 |
| GET | `/api/dashboard/projects` | 프로젝트 목록 |
| POST | `/api/dashboard/projects` | 프로젝트 생성 |
| GET | `/api/dashboard/usage` | 현재 월 비용 |
| GET | `/api/dashboard/chart` | N일 차트 데이터 |
| POST | `/api/webhooks/slack-test` | Slack 테스트 |

---

## FE 연동 시 필요한 정보

### 1. SDK Check API 응답
```json
{
  "allowed": true,
  "current_spend_usd": 5.23,
  "budget_usd": 10.0,
  "remaining_usd": 4.77,
  "estimated_cost_usd": 0.0025,
  "reason": null  // null | "budget_exceeded" | "loop_detected"
}
```

### 2. API Key 발급 응답 (원본 1회만 노출)
```json
{
  "data": {
    "key": "lg_1a2b3c4d5e6f...",  // 이것만 저장하도록 FE에 가이드
    "prefix": "lg_1a2b3c4d",
    "message": "Save this key securely..."
  }
}
```

### 3. 대시보드 실시간 업데이트
- `/api/dashboard/usage` (폴링 또는 Supabase Realtime 구독)
- `/api/dashboard/chart` (매 5분 또는 수동)

### 4. 환경변수 필요
```
NEXT_PUBLIC_SUPABASE_URL=...
NEXT_PUBLIC_SUPABASE_ANON_KEY=...
SUPABASE_SERVICE_ROLE_KEY=... (서버만)
UPSTASH_REDIS_REST_URL=...
UPSTASH_REDIS_REST_TOKEN=...
```

---

## 다음 단계

### Week 2 (Should 기능)
1. 프로젝트 업데이트 (`PATCH /api/dashboard/projects/:id`)
2. 알림 설정 CRUD (`/api/dashboard/alerts`)
3. Slack 알림 자동 전송 (비용 50%, 80%, 100% 도달)
4. SendGrid 이메일 알림 (차단 이벤트 발생 시)

### Week 3
1. Anthropic/Google SDK 래퍼 (Python 패키지)
2. 베타 사용자 10명 온보딩
3. 실제 차단 이벤트 테스트

### Week 4
1. Stripe 결제 연동 (Free → Pro 업그레이드)
2. 유료 고객 첫 전환 1명
3. 랜딩 웨이팅리스트 100명+

---

## 테스트 체크리스트 (QA)

- [ ] SDK check API: 유효한 키로 정상 응답
- [ ] SDK check API: 무효한 키로 401 반환
- [ ] SDK check API: 예산 초과 시 `allowed: false`
- [ ] SDK check API: 루프 감지 시 차단
- [ ] SDK check API: 2초 타임아웃 후 allow-through
- [ ] SDK report API: 사용량 DB 기록 확인
- [ ] 대시보드: 회원가입 → 초기 프로젝트 생성
- [ ] 대시보드: API 키 생성 → prefix만 목록에 노출
- [ ] 대시보드: 현재 월 비용 조회 (Redis + DB 일관성)
- [ ] 대시보드: 7일 차트 데이터 정확성
- [ ] RLS: A 유저 토큰으로 B 유저 데이터 접근 불가
- [ ] Slack 웹훅: 테스트 메시지 전송 성공

---

## 주요 성능 지표

| 지표 | 목표 | 상태 |
|------|------|------|
| SDK check p99 | < 50ms | 설계됨 (Redis 캐시) |
| SDK overhead | < 10ms | 비동기 report 구현 |
| cold start | < 500ms | Vercel Fluid Compute 활용 가능 |
| Realtime 지연 | < 1초 | Supabase Realtime CDC |

---

## 주의사항

1. **Supabase Free Tier 제약**
   - DB 500MB, 월 50만 rows read
   - 베타 10명 * 100회/일 = 300만 rows/월 초과 가능
   - → usage_logs 30일 자동 삭제 또는 Pro 업그레이드 필요

2. **OpenAI ToS 확인**
   - llm-guard는 클라이언트 사이드 래퍼 (프록시 아님)
   - SDK 문서에 명시하여 법적 이슈 방지

3. **타이밍 어택 방지**
   - bcrypt.compare() 사용하여 상수 시간 비교 적용

---

## 배포 준비물

### Supabase
1. 프로젝트 생성
2. `supabase/migrations/001_init.sql` 실행
3. Auth 설정 (Google, GitHub 등 OAuth 선택사항)

### Upstash
1. Redis 데이터베이스 생성
2. REST URL + Token 환경변수에 추가

### Vercel
1. `.env.local` 또는 `vercel env` CLI로 환경변수 설정
2. `vercel deploy` 또는 Git push로 자동 배포

---

**상태**: ✅ Week 1 MVP 구현 완료  
**다음 리뷰**: FE 대시보드 구현 후 통합 테스트
