# DevOps 설치 완료 — LLM Guard (Cost Circuit Breaker)

> 작성일: 2026-04-08 | DevOps 담당

---

## 프로젝트 구조

```
team/LLM-비용-서킷브레이커팀/
├── llm-guard-app/     ← Next.js 앱 루트 (폴더명 한글 제한으로 서브폴더 생성)
│   ├── src/
│   │   ├── app/
│   │   ├── components/ui/   ← shadcn 컴포넌트
│   │   └── lib/
│   └── package.json
├── PRD.md
├── wave_cto.md
├── DESIGN.md
├── wave_pm.md
└── wave_devops.md     ← 이 파일
```

> 주의: `npx create-next-app .` 실행 시 폴더명(한글+특수문자)이 npm 패키지명 제한에 걸려
> `llm-guard-app` 서브폴더로 생성. FE/BE 에이전트는 이 경로 기준으로 작업해야 함.

---

## 설치된 패키지

### Next.js 기본 (create-next-app@latest)

| 패키지 | 버전 | 용도 |
|--------|------|------|
| next | 16.2.2 | App Router 프레임워크 |
| react | 19.2.4 | UI 라이브러리 |
| react-dom | 19.2.4 | DOM 렌더링 |
| typescript | ^5 | 타입 시스템 |
| tailwindcss | ^4 | 유틸리티 CSS |
| eslint | ^9 | 코드 품질 |

### FE 핵심 패키지

| 패키지 | 버전 | 용도 |
|--------|------|------|
| @supabase/supabase-js | ^2.102.1 | Supabase DB + Auth + Realtime 클라이언트 |
| @supabase/ssr | ^0.10.0 | Next.js SSR + 쿠키 기반 세션 |
| three | ^0.183.2 | Three.js — 랜딩 파티클/3D 씬 |
| @types/three | ^0.183.1 | Three.js TypeScript 타입 |
| @react-three/fiber | ^9.5.0 | React용 Three.js 렌더러 (R3F) |
| @react-three/drei | ^10.7.7 | R3F 헬퍼 (useScroll, Html, etc.) |
| @stripe/stripe-js | ^9.1.0 | Stripe Checkout 프론트엔드 |
| recharts | ^3.8.1 | 실시간 비용 라인 차트 |
| framer-motion | ^12.38.0 | 스크롤 애니메이션 + 가격 토글 트랜지션 |
| react-hook-form | ^7.72.1 | 폼 상태 관리 |
| zod | ^4.3.6 | 스키마 유효성 검사 |
| @hookform/resolvers | ^5.2.2 | zod ↔ react-hook-form 연결 |
| lucide-react | ^1.7.0 | 아이콘 (Shield, Bell, Chart 등) |
| clsx | ^2.1.1 | 조건부 클래스명 |
| tailwind-merge | ^3.5.0 | Tailwind 클래스 충돌 방지 |
| next-themes | ^0.4.6 | 다크모드 (shadcn 자동 설치) |
| sonner | ^2.0.7 | 토스트 알림 (구 toast 컴포넌트 대체) |

### BE 핵심 패키지

| 패키지 | 버전 | 용도 |
|--------|------|------|
| stripe | ^22.0.0 | Stripe Webhook + 구독 서버사이드 처리 |
| @upstash/redis | ^1.37.0 | 서버리스 HTTP Redis — 토큰 누적 카운터 |

### shadcn/ui 컴포넌트 (설치 완료)

| 컴포넌트 | 파일 | 용도 |
|---------|------|------|
| button | button.tsx | 기본 버튼 |
| card | card.tsx | KPI 카드, 프로젝트 카드 |
| input | input.tsx | 폼 입력 |
| label | label.tsx | 폼 레이블 |
| badge | badge.tsx | 상태 배지 (GUARDED/WARNING/AT LIMIT) |
| table | table.tsx | 차단 이벤트 로그 테이블 |
| tabs | tabs.tsx | 월간/연간 가격 토글 |
| dialog | dialog.tsx | New Project 모달 |
| sheet | sheet.tsx | 모바일 사이드바 |
| skeleton | skeleton.tsx | 로딩 상태 |
| progress | progress.tsx | 예산 사용률 바 |
| switch | switch.tsx | 알림 임계값 토글 |
| slider | slider.tsx | 루프 감지 재시도 횟수 조절 |
| radio-group | radio-group.tsx | 알림 채널 선택 |
| accordion | accordion.tsx | 가격 페이지 FAQ |
| separator | separator.tsx | UI 구분선 |
| tooltip | tooltip.tsx | 대시보드 수치 상세 |
| avatar | avatar.tsx | 사이드바 유저 아바타 |
| dropdown-menu | dropdown-menu.tsx | 유저 메뉴 |
| sonner | sonner.tsx | 저장 성공/실패 토스트 |

---

## 특이사항

### toast → sonner 교체
`npx shadcn@latest add toast` 실행 시 "deprecated, use sonner instead" 메시지.
`sonner` 컴포넌트로 대체 설치함. FE 에이전트는 `toast` 대신 `sonner` 사용할 것.

```tsx
// 사용법
import { toast } from "sonner"
toast.success("Alert settings saved")
toast.error("Slack connection failed")
```

### Three.js SSR 주의 (DESIGN.md 명시)
Three.js는 서버사이드 렌더링 불가. 반드시 dynamic import 사용:
```tsx
const HeroScene = dynamic(() => import('@/components/landing/hero-scene'), { ssr: false })
```

### tooltip 사용 시 TooltipProvider 필수
`src/app/layout.tsx`에 `<TooltipProvider>` 래핑 필요:
```tsx
import { TooltipProvider } from "@/components/ui/tooltip"
// layout.tsx body에서 children 감싸기
```

---

## FE에게

### 작업 루트 경로
```
C:/Users/lian1/Documents/Work/core/team/LLM-비용-서킷브레이커팀/llm-guard-app/
```

### 개발 서버 실행
```bash
cd "C:/Users/lian1/Documents/Work/core/team/LLM-비용-서킷브레이커팀/llm-guard-app"
npm run dev
```

### 주요 사용 패턴

**Supabase 클라이언트 (SSR용)**
```typescript
// src/lib/supabase/client.ts — 브라우저용
import { createBrowserClient } from '@supabase/ssr'

// src/lib/supabase/server.ts — 서버 컴포넌트용
import { createServerClient } from '@supabase/ssr'
```

**Recharts 실시간 차트**
```tsx
import { LineChart, Line, XAxis, YAxis, ResponsiveContainer } from 'recharts'
// Supabase Realtime 구독과 연결해서 데이터 업데이트
```

**framer-motion 스크롤 애니메이션**
```tsx
import { motion } from 'framer-motion'
// DESIGN.md 스펙: initial opacity:0 y:40 → whileInView opacity:1 y:0
```

**Three.js R3F 씬 구조**
```tsx
import { Canvas } from '@react-three/fiber'
import { useScroll } from '@react-three/drei'
// DESIGN.md 스펙대로 파티클 500개 + 그리드 + 코드카드 3D
```

**Stripe Checkout**
```typescript
import { loadStripe } from '@stripe/stripe-js'
const stripe = await loadStripe(process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY!)
```

---

## BE에게

### API Routes 경로
```
src/app/api/v1/sdk/check/route.ts     — POST: pre-call 예산 체크
src/app/api/v1/sdk/report/route.ts    — POST: 사용량 기록 (비동기)
src/app/api/dashboard/api-keys/route.ts
src/app/api/dashboard/projects/route.ts
src/app/api/webhooks/stripe/route.ts
src/app/api/webhooks/send-slack/route.ts
```

**Upstash Redis 연결**
```typescript
import { Redis } from '@upstash/redis'
const redis = new Redis({
  url: process.env.UPSTASH_REDIS_REST_URL!,
  token: process.env.UPSTASH_REDIS_REST_TOKEN!,
})
// HTTP 기반 — Vercel Serverless에서 커넥션 풀 문제 없음
```

**Stripe Webhook (서버사이드)**
```typescript
import Stripe from 'stripe'
const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!)
// Webhook 검증: stripe.webhooks.constructEvent()
```

**Supabase Admin (서버사이드)**
```typescript
import { createClient } from '@supabase/supabase-js'
const supabaseAdmin = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!  // service_role — RLS 바이패스
)
```

---

## 환경변수 (.env.local 필요)

```bash
# Supabase
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=

# Stripe
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=

# Upstash Redis
UPSTASH_REDIS_REST_URL=
UPSTASH_REDIS_REST_TOKEN=

# 알림
SENDGRID_API_KEY=
SLACK_WEBHOOK_URL=
```

---

## 다음 단계 (FE/BE 에이전트용)

1. `.env.local` 파일 생성 (Supabase + Stripe + Upstash 키 입력)
2. Supabase에서 wave_cto.md SQL 스키마 실행 (users/projects/api_keys/usage_logs 테이블)
3. FE-001: `src/app/page.tsx` 랜딩페이지 시작 (Three.js Hero)
4. BE-001: `src/app/api/v1/sdk/check/route.ts` SDK 예산 체크 API 시작
5. FE-004: `src/app/dashboard/layout.tsx` 대시보드 레이아웃

**Python SDK (`llm-guard` PyPI 패키지)는 별도 폴더 필요:**
```
team/LLM-비용-서킷브레이커팀/llm-guard-sdk/   ← SDK 전용 Python 패키지
```
SDK 에이전트가 tiktoken, anthropic, openai, google-genai 설치 후 작업.
