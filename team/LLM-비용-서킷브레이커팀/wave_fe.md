# FE 구현 완료 보고 — LLM Guard (Cost Circuit Breaker)

**작성일:** 2026-04-08  
**담당:** 민준 (FE Engineer)  
**상태:** ✅ MVP 구현 완료 (Week 1)

---

## 구현 완료 내용

### 1. 랜딩페이지 (`src/app/page.tsx`)

**기술 스택:**
- Three.js + React Three Fiber — 파티클 시스템 히어로 (빨강→초록 전환 애니메이션)
- Framer Motion — 스크롤 페이드/카운트업 애니메이션
- Recharts 유사 구조 (차트는 대시보드에서만)

**구현된 섹션:**
1. **Hero Section** — Three.js 파티클 배경 + "$72,000 하룻밤에 날아갔다" 텍스트 + CTA 버튼
2. **Problem Section** — 실제 사고사례 카드 3개 ($82K, $72K, $47K)
3. **Solution Section** — Before/After 코드 비교 블록 (GitHub Dark 스타일)
4. **How It Works** — 3단계 설명 (Install → Detect → Block)
5. **Features** — 6가지 기능 리스트
6. **Waitlist CTA** — 이메일 입력 폼 (mock 데이터)
7. **Footer** — 링크 네비게이션

**Three.js 구현 상세:**
- `components/landing/particles.tsx` — 500개 파티클, 중력 시뮬레이션
- `components/landing/hero-scene.tsx` — Canvas + Scene + 조명 (빨강/초록 포인트라이트)
- `components/landing/code-compare.tsx` — 양쪽 코드 블록 with Framer Motion stagger
- `components/landing/number-counter.tsx` — IntersectionObserver 기반 카운트업

**색상:** 
- Background: `#0d1117` (GitHub Dark)
- Primary: `#00ff88` (초록 차단 신호)
- Alert: `#ff4444` (빨강 경보)
- Border: `#30363d`
- Text: `#e6edf3`

---

### 2. 대시보드 레이아웃 (`src/app/dashboard/layout.tsx`)

**구조:**
```
[Sidebar 240px fixed] | [Header 56px] [Main content area]
```

**Sidebar 기능:**
- 네비게이션 (Overview / Projects / Alerts / Keys / Billing)
- "Upgrade to Pro" 버튼
- 토글 가능한 모바일 메뉴

**Header:**
- Free/Pro 플랜 표시
- 프로필 아이콘 (placeholder)

---

### 3. 대시보드 메인 페이지 (`src/app/dashboard/page.tsx`)

**KPI Cards 4개 (실시간 업데이트 준비):**
| Card | 값 | 포인트 |
|------|-----|--------|
| Today Cost | $48.32 | 트렌드 화살표 |
| Budget Used | 62% | 프로그레스 바 (컬러: 초록→노랑→빨강) |
| Requests Blocked | 3 | "ACTIVE GUARD" 배지 |
| Remaining Budget | $451.68 | "resets in 19 days" |

**Recharts 라인 차트:**
- Mock 데이터 (7일 커브)
- LIVE 인디케이터 (pulsing dot)
- 초록 라인 (`#00ff88`)

**Block Events 테이블:**
- Time | Model | Reason | Cost | Status (BLOCKED/WARNED)
- Mock 3개 이벤트

**Upgrade CTA 배너:**
- 배경 그라디언트
- "Unlock Advanced Features" 메시지

---

### 4. 프로젝트 관리 (`src/app/dashboard/projects/page.tsx`)

**기능:**
- 프로젝트 카드 Grid (2열 반응형)
- "New Project" Dialog 모달
- 프로젝트별 예산 인라인 편집 (IKEA Effect: contentEditable)
- 상태 배지 (GUARDED/WARNING/AT_LIMIT)
- 경고 배너 (붉은 테두리, 빨강 배경)

**Card 요소:**
- 프로젝트 이름 + 상태 배지
- 예산 Progress Bar (컬러 분기)
- Requests / Avg Cost 통계
- "View Details" 버튼

---

### 5. 알림 설정 (`src/app/dashboard/alerts/page.tsx`)

**섹션:**
1. **Notification Channels** — Email (활성화) + Slack (연결 가능)
2. **Budget Thresholds** — 3단계 (50% 파랑 / 80% 노랑 / 100% 빨강)
3. **Agent Loop Detection** — PRO gate (blur overlay + upgrade CTA)
4. **Recent Alerts** — 3개 mock 알림 + 시간

**인터랙션:**
- Switch 토글 (shadcn)
- Slider (재시도 횟수 조정) — 1~20
- "Test Alerts" / "Save Changes" 버튼 → toast 알림

---

### 6. API 키 관리 (`src/app/dashboard/keys/page.tsx`)

**기능:**
- 키 목록 테이블 view
- "Create Key" Dialog 모달
- 키 표시/숨김 토글 (Eye icon)
- Copy to Clipboard 버튼
- 삭제 버튼 (Trash icon)
- 메타 정보 (Created / Last Used)

**Meta Info:**
- 생성일: "2 months ago"
- 마지막 사용: "2 hours ago"
- 활성 상태 배지

**Usage Example:**
- 코드 스니펫 (pre + font-mono)
- 설정 방법 (budget limit)

---

### 7. 빌링 페이지 (`src/app/dashboard/billing/page.tsx`)

**섹션:**
1. **Current Plan** — Free 플랜, API Requests 사용량, 다음 청구일
2. **Upgrade CTA** — "Unlock Advanced Features"
3. **Billing Information** — Email, Company, Tax ID, Address (편집 가능)
4. **Payment Method** — 카드 표시 + 업데이트 버튼
5. **Invoice History** — 테이블 (Invoice ID / Date / Amount / Status / Download PDF)

**Mock 인보이스 3개:**
- INV-2024-03, INV-2024-02, INV-2024-01
- 모두 $0.00 Paid (Free 플랜)

**Subscription Settings:**
- Email Receipts 토글
- Auto-Renew 토글
- "Cancel Subscription" 버튼 (위험 색)

---

### 8. 가격 페이지 (`src/app/pricing/page.tsx`)

**레이아웃:**
- Hero 헤더
- Monthly/Annual 토글 (20% off 배지)
- 3개 플랜 카드 (Free / **Pro** (featured) / Team)

**Pro 카드 (Featured):**
- 테두리 초록 (`#00ff88`)
- "Most Popular" 배지
- $49/month → $39/month (annual with 20% off)
- CTA: "Start 14-Day Free Trial"

**Feature Lists:**
- Free: 5개 기능
- Pro: 9개 기능 (Agent Loop Detection 포함)
- Team: 9개 기능 + Enterprise 추가

**FAQ:**
- 4개 아코디언 항목 (간단한 div 구조로 변환)

**Trust Signals:**
- No Proxy | Zero Latency | MIT License

---

### 9. 인증 페이지

#### 로그인 (`src/app/auth/login/page.tsx`)
- Email + Password 입력
- GitHub 로그인 옵션
- "Sign up" 링크
- Terms/Privacy 링크

#### 회원가입 (`src/app/auth/signup/page.tsx`)
- Name + Email + Password + Confirm Password
- GitHub 로그인 옵션
- Left: Features list (체크마크 + 텍스트)
- Right: 입력 폼
- "Sign in" 링크

---

## 주요 기술 결정

### 컴포넌트 라이브러리
- **shadcn/ui** — Card, Button, Badge, Input, Label, Dialog, Table, Progress, Switch, Slider
- **Recharts** — 라인 차트 (Dashboard에 mock 데이터)
- **Framer Motion** — 애니메이션 (Stagger, Scroll fade)
- **Lucide React** — 아이콘 (Copy, Eye, Trash, Menu, X, Check, Download)

### Dark Mode
- `next-themes`로 자동 dark mode 적용
- HTML에 `dark` 클래스 강제 설정
- Tailwind Dark mode override (globals.css)

### Three.js 최적화
- `dynamic(() => import(...), { ssr: false })` — SSR 오류 방지
- `<Suspense>` fallback with 스핀 로더
- Canvas `dpr={[1, 2]}` — 레티나 지원
- `performance={{ min: 0.5 }}` — 성능 저하 시 자동 DPR 감소

### 반응형 디자인
- `grid-cols-1 md:grid-cols-2 lg:grid-cols-4` — 모바일/태블릿/데스크톱
- Sidebar 토글 모바일 메뉴
- `clamp()` 반응형 타이포그래피 미적용 (px 고정)

---

## Mock 데이터 위치

### 대시보드
- **KPI 값:** `dashboard/page.tsx` (todayCost, budgetPercentage, requestsBlocked, remainingBudget)
- **차트 데이터:** `mockCostData` 배열
- **Block Events:** `mockBlockEvents` 배열

### 프로젝트
- **프로젝트 목록:** `mockProjects` 배열
- 상태: 동적 `useState`로 관리 (New Project 추가 가능)

### 알림
- **Threshold 설정:** 하드코딩된 3단계
- **Alert History:** `map()` mock 배열

### API 키
- **키 목록:** `useState` 초기값
- 생성/삭제 기능 포함

### 빌링
- **Current Plan:** Free, 18,420 API calls
- **인보이스:** 3개 mock 데이터

### 가격
- **플랜:** 3개 카드 배열
- **FAQ:** 4개 항목 배열

---

## BE 연동 시 변경할 부분

### API 엔드포인트 (현재 mock → 실제)
| 기능 | Endpoint | Mock 위치 |
|------|----------|---------|
| 대시보드 KPI | `GET /api/dashboard/usage` | 하드코딩 값 |
| 비용 차트 | `GET /api/dashboard/chart?period=7d` | mockCostData |
| 차단 이벤트 | `GET /api/dashboard/events` | mockBlockEvents |
| 프로젝트 목록 | `GET /api/dashboard/projects` | mockProjects |
| 프로젝트 생성 | `POST /api/dashboard/projects` | 현재 로컬 setState |
| 예산 업데이트 | `PATCH /api/dashboard/projects/:id` | contentEditable |
| API 키 목록 | `GET /api/dashboard/api-keys` | 하드코딩 array |
| 키 생성 | `POST /api/dashboard/api-keys` | random 생성 |
| 인보이스 목록 | `GET /api/dashboard/billing/invoices` | 하드코딩 array |

### 인증 연동
- **현재:** mock toast 알림
- **실제:** Supabase Auth / NextAuth.js
- 변경 파일: `auth/login/page.tsx`, `auth/signup/page.tsx`
- 미들웨어: 로그인 상태 확인 후 대시보드 리다이렉트

### Supabase Realtime (대시보드 라이브 업데이트)
- **현재:** mock 데이터 고정
- **실제:** `useEffect` → `supabase.channel('cost_events').on('*', ...).subscribe()`
- 파일: `dashboard/page.tsx` (KPI 업데이트)

### Stripe 결제 연동
- **현재:** "Upgrade to Pro" 클릭 → toast만
- **실제:** `@stripe/stripe-js` → Checkout Session 생성
- 파일: `dashboard/billing/page.tsx`, `pricing/page.tsx`

---

## 파일 구조

```
src/
├── app/
│   ├── page.tsx                          (랜딩페이지)
│   ├── layout.tsx                        (Root Layout)
│   ├── globals.css                       (GitHub Dark 테마)
│   ├── dashboard/
│   │   ├── layout.tsx                    (대시보드 레이아웃)
│   │   ├── page.tsx                      (메인 대시보드)
│   │   ├── projects/page.tsx
│   │   ├── alerts/page.tsx
│   │   ├── keys/page.tsx
│   │   └── billing/page.tsx
│   ├── pricing/page.tsx                  (가격 페이지)
│   └── auth/
│       ├── login/page.tsx
│       └── signup/page.tsx
├── components/
│   ├── landing/
│   │   ├── hero-scene.tsx                (Three.js 씬)
│   │   ├── particles.tsx                 (파티클 시스템)
│   │   ├── code-compare.tsx              (Before/After)
│   │   └── number-counter.tsx            (카운트업)
│   └── ui/                               (shadcn 컴포넌트)
└── lib/
    └── utils.ts                          (cn 함수 + 유틸)
```

---

## QA 필수 확인 사항

- [ ] Three.js 히어로 파티클 애니메이션 (브라우저 성능 → 낮은 fps 시 자동 감소)
- [ ] 대시보드 KPI 카드 로딩 상태 (skeleton? spin?)
- [ ] 반응형 테스트 (모바일 375px / 태블릿 768px / 데스크톱 1440px)
- [ ] 다크 모드 일관성 (모든 컬러 `#0d1117`/`#161b22` 범위)
- [ ] 버튼 hover/active 상태
- [ ] 모달 오버레이 닫기 (ESC 키)
- [ ] 폼 입력 유효성 검사
- [ ] 토스트 알림 자동 닫힘 (3초)

---

## Next Steps (Week 2-3)

1. **BE API 연동** — Supabase / Stripe 실제 구현
2. **Supabase Realtime** — 대시보드 라이브 업데이트
3. **인증 미들웨어** — 로그인 상태 보호
4. **모바일 최적화** — 모바일 대시보드 UX 개선
5. **성능 최적화** — 번들 사이즈, LCP 최적화
6. **에러 핸들링** — API 실패 시 재시도, 사용자 피드백

---

**빌드 상태:** ✅ 성공  
**배포 준비:** 준비 완료 (BE API 연동 대기 중)
