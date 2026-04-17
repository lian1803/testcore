# DESIGN.md — LLM Guard (Cost Circuit Breaker)

> CDO: 나은 | 작성일: 2026-04-08
> Hybrid 디자인 — 랜딩(Three.js 3D) + 대시보드(Stitch)

---

## 디자인 비전

**"터미널이 돈을 지킨다"**

개발자가 매일 쓰는 GitHub 다크 UI에서 출발, 빨간 경보와 초록 차단 신호가 금융 모니터링처럼 작동하는 SaaS. 화려함보다 신뢰. 숫자가 주인공.

---

## 디자인 구조 (Hybrid)

| 영역 | 스타일 | 담당 |
|------|--------|------|
| `/` 랜딩페이지 | Three.js 3D 임팩트 | FE(민준) 직접 구현 |
| `/pricing` 가격 | Stitch 생성 완료 | FE 핸드오프 |
| `/dashboard` 이하 | Stitch 생성 완료 | FE 핸드오프 |

---

## 컬러 시스템

### 랜딩용 (Three.js 3D 섹션)
```css
--bg-canvas:    #0d1117;   /* GitHub dark — 개발자에게 친숙 */
--bg-surface:   #161b22;
--bg-elevated:  #21262d;
--border:       #30363d;

--text-100:     #e6edf3;
--text-70:      rgba(230, 237, 243, 0.7);
--text-40:      rgba(230, 237, 243, 0.4);

--red-alert:    #ff4444;   /* 경보 — 비용 폭주 */
--green-safe:   #00ff88;   /* 차단 성공 — 터미널 그린 */
--yellow-warn:  #f0c040;   /* 임계값 경고 */
--blue-info:    #58a6ff;   /* 정보 / 차트 */

/* 랜딩 전용 글로우 */
--glow-red:   0 0 40px rgba(255,68,68,0.5), 0 0 120px rgba(255,68,68,0.15);
--glow-green: 0 0 40px rgba(0,255,136,0.5), 0 0 120px rgba(0,255,136,0.15);
```

### 대시보드용 (shadcn dark 오버라이드)
```css
/* globals.css에 적용 */
:root[class~="dark"] {
  --background: 216 28% 7%;        /* #0d1117 */
  --foreground: 210 40% 92%;       /* #e6edf3 */
  --card: 215 28% 11%;             /* #161b22 */
  --card-foreground: 210 40% 92%;
  --muted: 215 20% 16%;            /* #21262d */
  --muted-foreground: 210 30% 60%;
  --border: 215 14% 25%;           /* #30363d */
  --primary: 151 100% 50%;         /* #00ff88 */
  --primary-foreground: 216 28% 7%;
  --destructive: 0 100% 63%;       /* #ff4444 */
  --warning: 45 86% 60%;           /* #f0c040 */
  --ring: 210 100% 68%;            /* #58a6ff focus ring */
}
```

---

## 폰트 시스템

```css
/* Next.js에서 불러오기 */
import { Geist, Geist_Mono, IBM_Plex_Mono } from 'next/font/google'

/* 헤드라인/본문 */
--font-sans: 'GeistVF', system-ui;
font-weight: 700, letter-spacing: -0.03em  /* 헤드라인 */
font-weight: 400, font-size: 14-16px       /* 본문 */

/* 숫자/비용/코드 — 반드시 모노스페이스 */
--font-mono: 'Geist Mono', 'IBM Plex Mono';
font-feature-settings: "tnum" 1;   /* tabular numerals — 숫자 너비 고정 */
```

**왜 모노스페이스 숫자가 필수인가:**
실시간 비용 업데이트 시 `$12.48` → `$12.49`로 바뀔 때 레이아웃 시프트 발생 금지.
tabular numerals로 모든 숫자 너비를 동일하게 고정.

---

## 화면 명세

### Screen 1: Dashboard Main
**Stitch Screen ID:** `f99330ce140c47afbad92bcb8aef1722`
**Stitch Project:** `projects/10849739706536148905`

**목적:** 실시간 비용 상황을 5초 안에 파악. 이상 징후(루프, 한도 초과) 즉시 식별.

**레이아웃:**
```
[Sidebar 240px] | [Header 56px                                    ]
                | [KPI Cards Row: Today Cost | Budget% | Blocked | Remaining]
                | [Cost Over Time Chart — LIVE line chart          ]
                | [Block Events Table] | [Model Breakdown Bar     ]
```

**KPI 카드 4개:**
| 카드 | 수치 | 컬러 | 포인트 |
|------|------|------|--------|
| Today's Cost | `$12.48` | white | +$2.10 vs yesterday 트렌드 |
| Budget Used | `62%` | amber #f0c040 | progress bar + monthly 예산 레이블 |
| Requests Blocked | `3` | red #ff4444 | "ACTIVE GUARD" 배지 green |
| Remaining Budget | `$18.52` | green #00ff88 | "resets in 19 days" |

**실시간 차트:**
- Recharts `<LineChart>` — Supabase Realtime 구독
- 초록 선 `#00ff88` — 누적 비용
- 빨간 점선 — budget threshold
- "LIVE" pulsing dot: `animation: pulse 2s infinite`

**Empty State (API 키 미등록 시):**
```
[Shield icon large]
"No API key yet"
"Add your first LLM Guard key to start monitoring"
[+ Add API Key] — primary button
```

**CTA:** 우측 상단 "Upgrade to Pro" 항상 노출

---

### Screen 2: Projects Management
**Stitch Screen ID:** `01657d7472c844e6ad90480369107acc`

**목적:** 프로젝트별 예산 배분 관리. 어느 프로젝트가 위험한지 즉시 식별.

**레이아웃:**
```
[Sidebar] | [Header: "Projects"              [+ New Project btn]]
          | [Summary bar: 3 stat pills                          ]
          | [Project Cards Grid — 2 columns                     ]
          | [Budget Allocation stacked bar                      ]
```

**프로젝트 카드 상태 3가지:**
- GUARDED (green dot): 정상 운영 중
- WARNING (amber): 80%+ 사용
- AT LIMIT (red dot + banner): 한도 도달 / 루프 감지

**위험 배너 (red tint):**
```
bg: rgba(255, 68, 68, 0.1)
border-left: 3px solid #ff4444
텍스트: "Agent loop detected 3h ago — 12 retries blocked"
```

**Empty State (첫 방문):**
- 전체 영역에 온보딩 카드: "Create your first project" + 간단한 3단계 설명

**IKEA Effect 인터랙션:**
- 각 카드에서 예산 숫자를 인라인 클릭으로 직접 편집 가능
- `contentEditable` 스타일 또는 inline input — "내가 예산 설정했다"는 소유감

---

### Screen 3: Alerts Configuration
**Stitch Screen ID:** `69a513d264dd47e1b63eb2a2baffeb1b`

**목적:** 언제, 어디로 알림을 보낼지 설정. Slack/이메일 채널 연결.

**레이아웃:**
```
[Sidebar] | [Header: "Alert Settings"   [Test Alerts] [Save Changes]]
          | [Notification Channels card                              ]
          | [Budget Thresholds card                                  ]
          | [Agent Loop Detection card — PRO badge                  ]
          | [Alert History preview                                   ]
```

**임계값 3단계:**
| 임계값 | 채널 | 심각도 | 컬러 |
|--------|------|--------|------|
| 50% | Email | INFO | blue #58a6ff |
| 80% | Slack + Email | WARNING | amber #f0c040 |
| 100% | Slack + Email | CRITICAL | red #ff4444 + pulsing dot |

**Agent Loop Detection — PRO 게이트:**
- Free 플랜: 섹션 전체에 blur overlay + "Upgrade to Pro" 버튼
- Pro 플랜: 정상 접근, 재시도 횟수 슬라이더 (IKEA Effect — 직접 조절)

**Save Changes 피드백:**
- 저장 성공: green toast "Alert settings saved"
- Slack 연결 오류: red toast + retry 버튼

---

### Screen 4: Pricing Page
**Stitch Screen ID:** `3ed24de3a5b1485f860d49d750899a16`

**목적:** Free → Pro $49 전환 유도. 가격 저항 최소화.

**레이아웃:**
```
[Hero: 헤드라인 + 월/연간 토글]
[3 pricing cards: Free | Pro (highlighted) | Team]
[FAQ accordion 4개]
[Trust signals 3개]
```

**전환 최적화 포인트:**
1. "Most Popular" 배지 — Pro 카드만 `#00ff88` 테두리 + 배지
2. 연간 결제 토글 → Pro 가격이 `$49` → `$39.20`으로 변환 (20% off 배지)
3. Pro CTA: "Start 14-day Free Trial" — 카드 없이 시작 가능 강조
4. 신뢰 시그널: "No proxy. Zero latency." | "API keys never stored" | "MIT License SDK"

**가격 숫자 표시:**
```tsx
// 월간/연간 토글 시 가격 변환 애니메이션
<motion.span
  key={isAnnual ? 'annual' : 'monthly'}
  initial={{ opacity: 0, y: -10 }}
  animate={{ opacity: 1, y: 0 }}
  className="font-mono text-5xl font-bold"
>
  {isAnnual ? '$39' : '$49'}
</motion.span>
```

---

## 랜딩페이지 3D 스펙 (Three.js / React Three Fiber)

> FE(민준)에게: `Three.js + @react-three/fiber + @react-three/drei 사용. 아래 3D 스펙 구현해줘.`

### 배경 Three.js 씬

**오브젝트 1: 비용 폭주 파티클 시스템 (히어로 섹션)**
```
- 파티클 수: 500개
- 초기 상태: 빨간 파티클들이 화면 상단에서 아래로 급격히 쏟아짐
  - 색상: #ff4444, size 2px, 랜덤 속도 (비용 증가 시각화)
  - 움직임: gravity 적용, 가속하며 떨어짐
- 차단 이벤트 (3초 후): 파티클들이 중앙 수평선에서 멈추고
  - 색상이 #ff4444 → #00ff88으로 전환 (1.5초 tween)
  - 파티클이 정지하고 흩어지며 사라짐
  - 중앙에 녹색 shield 이펙트 flash
- 이 애니메이션이 5초 루프로 반복
```

**오브젝트 2: 배경 그리드 (터미널 느낌)**
```
- GridHelper 또는 커스텀 shader plane
- 색상: rgba(0, 255, 136, 0.06) — 매우 희미한 초록 그리드
- 카메라가 약간 앞으로 이동하는 느낌 (infinite forward motion)
- perspective: 45도 앵글
```

**오브젝트 3: 플로팅 코드 카드 (기능 섹션)**
```
- React Three Fiber + Html component로 코드 블록을 3D 공간에 배치
- 마우스 이동 시 parallax (depth 2-3레이어)
- Before 카드(빨간 glow) / After 카드(초록 glow)가 3D로 플로팅
```

### 카메라 & 조명
```
- Camera: PerspectiveCamera, fov 60, position z=5
- AmbientLight: intensity 0.2
- PointLight 1: #ff4444, intensity 2, position (−3, 2, 2) — 왼쪽 빨간 드라마틱 라이트
- PointLight 2: #00ff88, intensity 1.5, position (3, −1, 1) — 오른쪽 그린 차단 라이트
- 마우스 추적: camera rotation X/Y를 마우스 좌표에 부드럽게 연동 (lerp 0.05)
```

### 인터랙션 (스크롤)
```javascript
// useScroll from @react-three/drei
// 스크롤 0 → 0.3: 히어로 파티클 씬
// 스크롤 0.3 → 0.6: 그리드 배경 intensify
// 스크롤 0.6 → 1.0: 코드 카드 3D 등장
```

### 히어로 섹션 카피 (애니메이션 순서)
```
1. 붉은 텍스트 fade-in (0.5s delay):
   "$72,000"  ← 숫자 카운트업 애니메이션
   "하룻밤에 날아갔다"

2. 0.8s pause (파티클이 쏟아지는 동안)

3. 차단 이펙트와 동시에 초록 텍스트 등장:
   "한 줄로 막는다."
   [코드 스니펫 fade-in]
   from llm_guard.openai import OpenAI

4. CTA 버튼 등장 (1.2s delay):
   [Join Waitlist →] — 초록 glow 버튼
   [See How It Works ↓] — outline
```

---

## shadcn/ui 컴포넌트 목록

### 대시보드 공통
```
npx shadcn@latest add card
npx shadcn@latest add badge
npx shadcn@latest add button
npx shadcn@latest add separator
npx shadcn@latest add tooltip
npx shadcn@latest add avatar
npx shadcn@latest add dropdown-menu
npx shadcn@latest add sheet          # 모바일 사이드바
```

### 대시보드 메인
```
npx shadcn@latest add skeleton        # 로딩 상태
npx shadcn@latest add table
npx shadcn@latest add progress        # budget bar
```

### 프로젝트 관리
```
npx shadcn@latest add dialog          # New Project 모달
npx shadcn@latest add input
npx shadcn@latest add label
npx shadcn@latest add form
```

### 알림 설정
```
npx shadcn@latest add switch          # 임계값 토글
npx shadcn@latest add slider          # loop detection retry count
npx shadcn@latest add radio-group
npx shadcn@latest add toast
```

### 가격 페이지
```
npx shadcn@latest add accordion       # FAQ
npx shadcn@latest add tabs            # 월간/연간 토글 (또는 custom)
```

---

## 커스텀 컴포넌트 목록

| 컴포넌트 | 경로 | 설명 |
|---------|------|------|
| `KpiCard` | `components/dashboard/kpi-card.tsx` | 대형 숫자 + 트렌드 화살표 |
| `CostLineChart` | `components/dashboard/cost-chart.tsx` | Recharts + Supabase Realtime |
| `BlockEventTable` | `components/dashboard/block-table.tsx` | 차단 이벤트 로그 테이블 |
| `ProjectCard` | `components/projects/project-card.tsx` | 상태 배지 + 예산 bar + 인라인 편집 |
| `BudgetProgressBar` | `components/ui/budget-bar.tsx` | 색상 분기 (green/amber/red) |
| `StatusDot` | `components/ui/status-dot.tsx` | pulsing dot 애니메이션 |
| `ThresholdRow` | `components/alerts/threshold-row.tsx` | 임계값 설정 행 |
| `HeroScene` | `components/landing/hero-scene.tsx` | Three.js R3F 메인 씬 |
| `ParticleSystem` | `components/landing/particles.tsx` | 비용 폭주 → 차단 파티클 |
| `CodeComparison` | `components/landing/code-compare.tsx` | Before/After 코드 블록 |
| `PricingCard` | `components/pricing/pricing-card.tsx` | 플랜 카드 + 월/연간 토글 |

---

## Aceternity UI 적용

```
히어로 섹션:
- Spotlight effect — 마우스 따라 초록/빨간 스포트라이트
- Background Beams — 코드 섹션 뒤 빔 이펙트

피처 섹션:
- Bento Grid — 기능 설명 카드 (6개 피처를 벤토 레이아웃으로)
- Card Hover Effect — 카드에 마우스 올리면 3D tilt + glow

소셜 프루프:
- Infinite Moving Cards — 사고 사례 ($82K, $72K, $70K...) 좌우 스크롤
```

## Magic UI 적용

```
히어로 CTA 버튼:
- Shimmer Button — "Join Waitlist" 버튼에 shimmer 이펙트

사고 사례 숫자:
- Number Ticker — $82,000 카운트업 애니메이션

랜딩 배경:
- Animated Grid Pattern — 터미널 그리드 느낌 (Three.js와 병행)
```

---

## 랜딩 섹션 구조 (순서대로)

```
1. Hero              — 파티클 Three.js + "$72K" 카운트업 + CTA
2. Problem           — 실제 사고 사례 3건 (숫자 카드, Infinite Moving Cards)
3. Solution          — "한 줄 설치" 코드 비교 Before/After (코드 블록 3D)
4. How It Works      — 3단계 설명 (추정→차단→알림)
5. Features          — Bento Grid 6개 피처
6. Pricing Preview   — 3플랜 요약 + "Full pricing →" 링크
7. Waitlist CTA      — 이메일 입력 + "100명 달성 시 베타 오픈" 카운터
```

---

## 레이아웃 변수

```css
/* 대시보드 레이아웃 */
--sidebar-width: 240px;
--header-height: 56px;
--content-padding: 24px;
--card-gap: 16px;
--card-radius: 8px;

/* 랜딩 레이아웃 */
--section-py: clamp(80px, 10vw, 160px);
--content-max-width: 1200px;
--hero-min-height: 100svh;
```

---

## 애니메이션 스펙

```css
/* 기본 트랜지션 */
--ease-out: cubic-bezier(0.25, 0.1, 0.25, 1.0);
--ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);

/* 카드 호버 */
.card:hover {
  border-color: rgba(0, 255, 136, 0.3);
  box-shadow: 0 0 20px rgba(0, 255, 136, 0.08);
  transition: all 150ms var(--ease-out);
}

/* CRITICAL 배지 펄스 */
@keyframes pulse-red {
  0%, 100% { box-shadow: 0 0 0 0 rgba(255, 68, 68, 0.4); }
  50% { box-shadow: 0 0 0 6px rgba(255, 68, 68, 0); }
}

/* 숫자 카운트업 */
/* Number Ticker (Magic UI) 사용 — framer-motion 기반 */

/* 스크롤 진입 */
initial: { opacity: 0, y: 40 }
whileInView: { opacity: 1, y: 0 }
viewport: { once: true, margin: "-10%" }
transition: { duration: 0.6, ease: [0.25, 0.1, 0.25, 1.0] }
```

---

## Stitch 생성 결과

| 화면 | Screen ID | 상태 |
|------|-----------|------|
| Dashboard Main | `f99330ce140c47afbad92bcb8aef1722` | 완료 |
| Projects Management | `01657d7472c844e6ad90480369107acc` | 완료 |
| Alerts Configuration | `69a513d264dd47e1b63eb2a2baffeb1b` | 완료 |
| Pricing Page | `3ed24de3a5b1485f860d49d750899a16` | 완료 |

**Stitch Project ID:** `10849739706536148905`

Stitch 화면 코드는 아래 커맨드로 각각 fetch:
```
mcp__stitch__fetch_screen_code(projectId: "10849739706536148905", screenId: "<id>")
```

---

## FE(민준)에게

### 구현 우선순위

**Week 2 (랜딩 + 대시보드 껍데기):**
1. `app/page.tsx` — 랜딩페이지 (Three.js 히어로 + 섹션들)
2. `app/dashboard/page.tsx` — KPI 카드 4개 + 차트 레이아웃 (mock 데이터)
3. Supabase Auth 연동 (로그인 게이트)

**Week 3 (대시보드 기능화):**
4. `app/dashboard/projects/page.tsx` — 프로젝트 CRUD
5. `app/dashboard/alerts/page.tsx` — 알림 설정 + Slack webhook 테스트
6. Supabase Realtime 연결 → 차트 실시간 업데이트

**Week 4 (결제):**
7. `app/pricing/page.tsx` — Stripe Checkout 연동
8. `app/dashboard/billing/page.tsx` — 구독 상태

### Three.js 설치
```bash
npm install three @react-three/fiber @react-three/drei
npm install @types/three
```

### 차트 라이브러리
```bash
npm install recharts
```

### 애니메이션
```bash
npm install framer-motion
```

---

## CTO에게 요청

1. **Supabase Realtime 스키마 확인**: `cost_events` 테이블 channel 이름 → FE가 `useEffect`에서 구독
2. **Upstash Redis**: 토큰 카운터 read API endpoint → 대시보드 KPI 폴링 주기 결정 (500ms? 1s?)
3. **Stripe Webhook**: `/api/stripe/webhook` route에서 plan 업그레이드 시 `profiles` 테이블 업데이트 → FE에서 Pro feature gate 즉시 반영되게
4. **CORS**: Supabase anon key FE 노출 범위 — RLS 정책 확인 필요
5. **Three.js SSR**: `dynamic(() => import('./hero-scene'), { ssr: false })` 패턴 사용 — Next.js 서버사이드에서 Three.js canvas 렌더 불가
