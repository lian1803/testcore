# CTO 분석 — Lian Dash (마케팅 통합 데이터 분석 SaaS — UI 프로토타입)

> Wave 1 | 작성일: 2026-03-30 | 범위: UI 프로토타입 (Mock 데이터, 실제 API 연동 없음)

---

## 기술 스택 결정

| 항목 | 선택 | 이유 |
|------|------|------|
| 프레임워크 | Next.js 14 (App Router) | 지시서 기준. 파일 기반 라우팅으로 5개 화면 구조화 용이 |
| 스타일 | Tailwind CSS 3.4.x | shadcn/ui 기본 전제 조건. utility-first로 빠른 프로토타이핑 |
| UI 컴포넌트 | shadcn/ui | Radix 기반, copy-paste 방식으로 번들 최소화 |
| 차트 | Recharts 2.12.x | React 네이티브, 커스터마이징 쉬움. 대시보드 차트에 최적 |
| 상태관리 | Zustand 4.5.x | 날짜 필터 전역 상태 관리. Redux 대비 보일러플레이트 없음 |
| 데이터패칭 | TanStack Query 5.x | Mock 데이터지만 인터페이스 구조 실제와 동일하게 유지 (나중에 실제 API로 교체 용이) |
| 언어 | TypeScript 5.x (strict) | 지시서 규칙. Mock 데이터 타입 안정성 |
| 패키지 매니저 | npm | Next.js 기본값 |
| PDF 내보내기 | jspdf + html2canvas | 모달 UI만 구현, 실제 PDF 렌더링까지 포함 (서버 불필요) |

**백엔드/DB/인증: 없음.** 프로토타입 범위 초과이므로 전부 제외.

---

## 아키텍처

```
[브라우저]
    |
    | npm run dev (localhost:3000)
    |
[Next.js 14 App Router]
    |
    ├── app/
    │   ├── page.tsx              → 랜딩 페이지 (/)
    │   ├── onboarding/           → 온보딩 (/onboarding)
    │   ├── dashboard/            → 메인 대시보드 (/dashboard)
    │   ├── insights/             → AI 인사이트 (/dashboard — 패널로 포함)
    │   └── layout.tsx            → 공통 레이아웃
    |
    ├── [Zustand Store]           → dateFilter (today/7d/30d) 전역 상태
    │       |
    │       ↓ 상태 변경 시
    ├── [TanStack Query]          → useMockQuery() 훅
    │       |
    │       ↓ 데이터 요청
    └── [src/lib/mock-data.ts]    → 날짜 필터별 데이터 반환 (단일 진실 공급원)
            |
            ↓ 데이터
    [Recharts 차트 컴포넌트들]    → 시각화
```

**데이터 흐름 원칙:**
- 모든 데이터는 `mock-data.ts` → TanStack Query → 컴포넌트 단방향
- Zustand는 UI 상태(날짜 필터, 온보딩 스텝, 모달 open/close)만 관리
- 나중에 실제 API 연동 시 TanStack Query의 `queryFn`만 교체

---

## 폴더 구조

```
lian-dash/
├── src/
│   ├── app/
│   │   ├── layout.tsx                    ← 루트 레이아웃 (폰트, Provider)
│   │   ├── globals.css                   ← Tailwind base + 커스텀 변수
│   │   ├── page.tsx                      ← 화면1: 랜딩 페이지
│   │   ├── onboarding/
│   │   │   └── page.tsx                  ← 화면2: 온보딩 3단계
│   │   └── dashboard/
│   │       ├── layout.tsx                ← 사이드바 + 헤더 공통 레이아웃
│   │       ├── page.tsx                  ← 화면3: 메인 대시보드
│   │       └── insights/
│   │           └── page.tsx              ← 화면4: AI 인사이트 (전용 페이지)
│   │
│   ├── components/
│   │   ├── ui/                           ← shadcn/ui 컴포넌트 (Button, Card, Dialog 등)
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── dialog.tsx
│   │   │   ├── select.tsx
│   │   │   ├── badge.tsx
│   │   │   ├── tabs.tsx
│   │   │   ├── progress.tsx
│   │   │   ├── separator.tsx
│   │   │   └── skeleton.tsx
│   │   ├── layout/
│   │   │   ├── Sidebar.tsx               ← 사이드바 네비게이션
│   │   │   ├── DashboardHeader.tsx       ← 날짜 필터 + 알림 헤더
│   │   │   └── Providers.tsx             ← QueryClientProvider + 전역 Provider
│   │   ├── landing/
│   │   │   ├── HeroSection.tsx           ← 히어로 + CTA
│   │   │   ├── FeatureSection.tsx        ← 기능 3열 카드
│   │   │   └── PricingSection.tsx        ← 플랜 카드
│   │   ├── onboarding/
│   │   │   ├── OnboardingStep1.tsx       ← 채널 선택 (GA4/Meta/네이버SA)
│   │   │   ├── OnboardingStep2.tsx       ← 연결 시뮬레이션 (OAuth UI only)
│   │   │   └── OnboardingStep3.tsx       ← 완료 + 대시보드 이동
│   │   ├── dashboard/
│   │   │   ├── KpiCardGroup.tsx          ← 상단 KPI 카드 4개 묶음
│   │   │   ├── KpiCard.tsx               ← 개별 KPI 카드 (추이 화살표 포함)
│   │   │   ├── ChannelOverviewChart.tsx  ← 채널별 통합 라인 차트
│   │   │   ├── MetricsTable.tsx          ← 채널별 상세 지표 테이블
│   │   │   ├── DateFilterBar.tsx         ← 오늘/7일/30일 토글
│   │   │   └── ExportModal.tsx           ← 화면5: PDF 내보내기 모달
│   │   └── insights/
│   │       ├── InsightCard.tsx           ← 개별 인사이트 카드
│   │       ├── InsightFeed.tsx           ← 인사이트 목록 피드
│   │       └── ChannelBreakdownChart.tsx ← 채널별 파이/바 차트
│   │
│   ├── lib/
│   │   ├── mock-data.ts                  ← Mock 데이터 단일 진실 공급원
│   │   ├── utils.ts                      ← cn() + 공통 유틸
│   │   └── types.ts                      ← TypeScript 인터페이스 전체
│   │
│   ├── store/
│   │   ├── useDateFilterStore.ts         ← 날짜 필터 전역 상태
│   │   └── useOnboardingStore.ts         ← 온보딩 스텝 상태
│   │
│   └── hooks/
│       ├── useDashboardData.ts           ← TanStack Query 대시보드 데이터 훅
│       ├── useInsightsData.ts            ← TanStack Query 인사이트 데이터 훅
│       └── useChannelData.ts             ← TanStack Query 채널별 데이터 훅
│
├── public/
│   ├── logo.svg
│   └── channel-icons/                    ← GA4, Meta, NaverSA 아이콘
│
├── package.json
├── tailwind.config.ts
├── tsconfig.json
├── next.config.ts
├── components.json                       ← shadcn/ui 설정
└── .env.local.example                    ← 나중에 실제 API 키 넣을 자리
```

---

## Mock 데이터 설계

### 타입 구조 (`src/lib/types.ts`)

```typescript
// 날짜 필터 타입
export type DateFilter = 'today' | '7d' | '30d';

// 채널 타입
export type Channel = 'ga4' | 'meta' | 'naver_sa';

// 채널별 지표
export interface ChannelMetrics {
  channel: Channel;
  channelName: string;
  // 공통 지표
  impressions: number;
  clicks: number;
  ctr: number;          // %
  conversions: number;
  cost: number;         // KRW
  revenue: number;      // KRW
  roas: number;         // 소수 (예: 3.2 = 320%)
  // 채널 고유 지표
  sessions?: number;    // GA4
  bounceRate?: number;  // GA4, %
  reach?: number;       // Meta
  frequency?: number;   // Meta
  qualityScore?: number; // 네이버SA
}

// KPI 카드 데이터
export interface KpiSummary {
  totalRevenue: number;
  totalCost: number;
  totalRoas: number;
  totalConversions: number;
  revenueChange: number;   // 전기 대비 % (양수=상승, 음수=하락)
  costChange: number;
  roasChange: number;
  conversionChange: number;
}

// 시계열 데이터 포인트
export interface TimeSeriesPoint {
  date: string;         // 'MM/DD' 형식
  ga4Revenue: number;
  metaRevenue: number;
  naverRevenue: number;
  totalRevenue: number;
}

// AI 인사이트
export interface AiInsight {
  id: string;
  type: 'opportunity' | 'warning' | 'info';
  channel: Channel | 'all';
  title: string;
  description: string;
  impact: 'high' | 'medium' | 'low';
  metric?: string;
  value?: string;
}

// 대시보드 전체 데이터
export interface DashboardData {
  kpi: KpiSummary;
  channels: ChannelMetrics[];
  timeSeries: TimeSeriesPoint[];
  insights: AiInsight[];
  lastUpdated: string;
}
```

### Mock 데이터 함수 설계 (`src/lib/mock-data.ts`)

날짜 필터마다 다른 수치를 반환하는 **한국 중소기업 현실 벤치마크** 기준:

| 필터 | 총 광고비 | 총 매출 | ROAS | 전환수 |
|------|-----------|---------|------|--------|
| today | 380,000원 | 1,140,000원 | 3.0 | 28건 |
| 7d | 2,650,000원 | 8,745,000원 | 3.3 | 196건 |
| 30d | 11,200,000원 | 38,080,000원 | 3.4 | 842건 |

**채널 비중 (한국 중소기업 평균)**:
- GA4 (SEO/오가닉): 매출 45%, 비용 20% (ROAS 높음)
- Meta 광고: 매출 30%, 비용 35% (ROAS 중간)
- 네이버 SA: 매출 25%, 비용 45% (ROAS 낮음, but 전환 품질 높음)

```typescript
// mock-data.ts 핵심 구조

const BASE_DATA: Record<DateFilter, DashboardData> = {
  today: { /* 위 수치 기반 */ },
  '7d': { /* 위 수치 기반 */ },
  '30d': { /* 위 수치 기반 */ },
};

// 날짜 필터로 데이터 반환하는 메인 함수
export function getMockDashboardData(filter: DateFilter): DashboardData {
  return BASE_DATA[filter];
}

// 시계열 데이터 생성 (날짜 수만큼 포인트 생성)
export function getMockTimeSeries(filter: DateFilter): TimeSeriesPoint[] {
  const days = filter === 'today' ? 24 : filter === '7d' ? 7 : 30;
  // days만큼 배열 생성, 약간의 랜덤 변동 포함 (seed 고정으로 재렌더 시 동일값)
}

// 채널별 데이터
export function getMockChannelData(filter: DateFilter): ChannelMetrics[] {
  return BASE_DATA[filter].channels;
}

// AI 인사이트 (날짜 무관, 고정)
export function getMockInsights(): AiInsight[] {
  return STATIC_INSIGHTS;
}
```

**시계열 수치 (7일 기준, 일별 매출 분포 예시)**:
```
월: 1,050,000 / 화: 980,000 / 수: 1,320,000 / 목: 1,180,000
금: 1,580,000 / 토: 1,390,000 / 일: 1,245,000
```
주중 대비 금요일 피크, 일요일 소폭 감소 — 한국 이커머스 패턴 반영.

**AI 인사이트 예시 (정적, 5개)**:
```
1. [opportunity/high] 네이버SA ROAS 2.1배 → Meta 예산 15% 이동 시 월 +3.2M 예상
2. [warning/medium] Meta 광고 빈도수 3.8회 초과 → 광고 소재 교체 필요
3. [info/low] GA4 이탈률 전주 대비 4.2%p 개선 → 랜딩 페이지 효과
4. [opportunity/medium] 네이버SA 품질지수 7점 → 광고문구 수정으로 CPC 12% 절감 가능
5. [warning/high] 이번 주 전환비용(CPA) 전월 대비 18% 상승
```

---

## 컴포넌트 목록 및 Props 구조

### 화면1: 랜딩 (`app/page.tsx`)

```typescript
// HeroSection.tsx
interface HeroSectionProps {
  // props 없음 — 정적 콘텐츠
}

// FeatureSection.tsx
interface Feature {
  icon: React.ReactNode;
  title: string;
  description: string;
}
interface FeatureSectionProps {
  features?: Feature[]; // 기본값 내장
}

// PricingSection.tsx
interface PricingPlan {
  name: string;
  price: number;       // 월 KRW
  features: string[];
  highlighted: boolean;
}
interface PricingSectionProps {
  plans?: PricingPlan[]; // 기본값 내장
}
```

### 화면2: 온보딩 (`app/onboarding/page.tsx`)

```typescript
// OnboardingStep1.tsx — 채널 선택
interface ChannelOption {
  id: Channel;
  name: string;
  icon: string;
  description: string;
}
interface OnboardingStep1Props {
  selectedChannels: Channel[];
  onToggle: (channel: Channel) => void;
  onNext: () => void;
}

// OnboardingStep2.tsx — 연결 시뮬레이션
interface OnboardingStep2Props {
  channels: Channel[];
  onNext: () => void;
  onBack: () => void;
}
// 내부에서 연결 중 로딩 애니메이션 (setTimeout 2초) 시뮬레이션

// OnboardingStep3.tsx — 완료
interface OnboardingStep3Props {
  connectedChannels: Channel[];
  onGoToDashboard: () => void;
}
```

### 화면3: 메인 대시보드 (`app/dashboard/page.tsx`)

```typescript
// DateFilterBar.tsx
interface DateFilterBarProps {
  value: DateFilter;
  onChange: (filter: DateFilter) => void;
}

// KpiCard.tsx
interface KpiCardProps {
  title: string;
  value: string;          // 포맷된 값 (예: "38,080,000원")
  change: number;         // % (양수: 상승, 음수: 하락)
  icon: React.ReactNode;
  description?: string;
}

// KpiCardGroup.tsx
interface KpiCardGroupProps {
  data: KpiSummary;
}

// ChannelOverviewChart.tsx
interface ChannelOverviewChartProps {
  data: TimeSeriesPoint[];
  filter: DateFilter;
}

// MetricsTable.tsx
interface MetricsTableProps {
  channels: ChannelMetrics[];
}

// ExportModal.tsx — 화면5
interface ExportModalProps {
  open: boolean;
  onClose: () => void;
  filter: DateFilter;
  data: DashboardData;
}
```

### 화면4: AI 인사이트 (`app/dashboard/insights/page.tsx`)

```typescript
// InsightCard.tsx
interface InsightCardProps {
  insight: AiInsight;
}

// InsightFeed.tsx
interface InsightFeedProps {
  insights: AiInsight[];
  filter?: AiInsight['type'] | 'all';
}

// ChannelBreakdownChart.tsx
interface ChannelBreakdownChartProps {
  channels: ChannelMetrics[];
  metric: keyof Pick<ChannelMetrics, 'revenue' | 'cost' | 'conversions'>;
}
```

### 공통 레이아웃

```typescript
// Sidebar.tsx
interface SidebarProps {
  currentPath: string;
}
// 네비게이션 항목: 대시보드, AI 인사이트, 설정 (비활성)

// DashboardHeader.tsx
interface DashboardHeaderProps {
  title: string;
  onExport?: () => void;   // PDF 내보내기 버튼 (대시보드에서만)
}
```

---

## Engineering Rules (이 프로젝트 필수 준수)

1. **TypeScript strict 모드 강제** — `tsconfig.json`에 `"strict": true`. `any` 타입 사용 금지. 타입 미확정 시 `unknown` 사용 후 타입가드 처리.

2. **컴포넌트당 파일 1개** — `components/dashboard/KpiCard.tsx`에 `KpiCard` 컴포넌트 하나만 존재. 같은 파일에 다른 컴포넌트 추가 금지.

3. **Mock 데이터 단일 진실 공급원** — `src/lib/mock-data.ts` 외 어디에서도 하드코딩된 숫자/문자열 데이터 없음. 컴포넌트 내부에 `const data = [{ ... }]` 형태 금지.

4. **실제 API 호출 코드 없음** — `fetch()`, `axios`, `http.get()` 등 네트워크 호출 코드 작성 금지. TanStack Query의 `queryFn`은 반드시 `mock-data.ts`의 함수를 호출.

5. **TanStack Query 인터페이스 유지** — 나중에 실제 API 교체 시 `queryFn`만 바꾸면 되도록. 훅 시그니처(`useDashboardData`, `useInsightsData`)는 실제 API 쓸 때도 동일하게 유지.

6. **서버 컴포넌트 vs 클라이언트 컴포넌트 명시** — 상태/이벤트 필요한 컴포넌트 최상단에 `'use client'` 명시. 정적 컴포넌트는 기본(서버) 유지.

7. **절대 경로 import** — `../../components/ui/button` 대신 `@/components/ui/button`. `tsconfig.json`의 `@/*` alias 활용.

8. **숫자 포맷 통일** — 금액은 `Intl.NumberFormat('ko-KR', { style: 'currency', currency: 'KRW' })`. 컴포넌트마다 직접 포맷 금지. `src/lib/utils.ts`의 `formatKRW()` 사용.

---

## 기술 리스크

| 리스크 | 심각도 | 해결 방법 |
|--------|--------|-----------|
| shadcn/ui 초기 설정 복잡 | 낮음 | `npx shadcn-ui@latest init` 후 필요한 컴포넌트만 추가 |
| Recharts 반응형 처리 | 낮음 | `ResponsiveContainer` 래퍼 필수 사용. width="100%" |
| TanStack Query v5 API 변경 | 낮음 | v5는 `useQuery(options)` 단일 객체 인자. v4 문법 혼용 금지 |
| jspdf + html2canvas PDF 한글 깨짐 | 중간 | 구글 폰트 Noto Sans KR 임베딩 또는 `html2canvas` 스케일 조정 |
| Next.js 14 App Router hydration 불일치 | 낮음 | Zustand persist 사용 시 `skipHydration: true` 설정 |

---

## package.json dependencies

```json
{
  "name": "lian-dash",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "next": "14.2.5",
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "typescript": "^5.5.4",

    "tailwindcss": "^3.4.6",
    "autoprefixer": "^10.4.19",
    "postcss": "^8.4.40",

    "@radix-ui/react-dialog": "^1.1.1",
    "@radix-ui/react-select": "^2.1.1",
    "@radix-ui/react-tabs": "^1.1.0",
    "@radix-ui/react-separator": "^1.1.0",
    "@radix-ui/react-progress": "^1.1.0",
    "@radix-ui/react-slot": "^1.1.0",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.1.1",
    "tailwind-merge": "^2.4.0",
    "lucide-react": "^0.408.0",

    "recharts": "^2.12.7",

    "zustand": "^4.5.4",

    "@tanstack/react-query": "^5.51.21",
    "@tanstack/react-query-devtools": "^5.51.21",

    "jspdf": "^2.5.1",
    "html2canvas": "^1.4.1"
  },
  "devDependencies": {
    "@types/node": "^20.14.12",
    "@types/react": "^18.3.3",
    "@types/react-dom": "^18.3.0",
    "eslint": "^8.57.0",
    "eslint-config-next": "14.2.5"
  }
}
```

---

## 빌드/실행 명령어

처음 세팅하는 사람이 따라할 단계별 명령어:

```bash
# 1. 프로젝트 생성 (기존 폴더에 새 Next.js 앱 생성)
npx create-next-app@14 lian-dash \
  --typescript \
  --tailwind \
  --eslint \
  --app \
  --src-dir \
  --import-alias "@/*" \
  --no-turbopack

cd lian-dash

# 2. shadcn/ui 초기화
npx shadcn-ui@latest init
# 물음에 답변:
# Style: Default
# Base color: Slate
# CSS variables: Yes

# 3. shadcn/ui 컴포넌트 추가 (필요한 것만)
npx shadcn-ui@latest add button card dialog select badge tabs progress separator skeleton

# 4. 추가 패키지 설치
npm install recharts zustand @tanstack/react-query @tanstack/react-query-devtools jspdf html2canvas lucide-react

# 5. 개발 서버 실행
npm run dev
# → http://localhost:3000 에서 확인
```

---

## 파일 생성 우선순위 (FE 작업 순서 권장)

FE가 작업할 때 이 순서로 진행하면 의존성 충돌 없음:

```
1단계 (기반): types.ts → utils.ts → mock-data.ts
2단계 (상태): useDateFilterStore.ts → useOnboardingStore.ts
3단계 (훅):   useDashboardData.ts → useInsightsData.ts → useChannelData.ts
4단계 (레이아웃): globals.css → layout.tsx → Providers.tsx → Sidebar.tsx → DashboardHeader.tsx
5단계 (화면 순서): 랜딩 → 온보딩 → 대시보드 → AI 인사이트 → ExportModal
```

---

## CDO에게 요청

1. **차트 빈 상태 디자인** — 날짜 필터 전환 시 로딩 스켈레톤 디자인 필요. Recharts는 데이터 로딩 중 빈 차트가 깜빡일 수 있음. 스켈레톤 shimmer 패턴 지정 요청.

2. **ExportModal PDF 레이아웃** — jspdf+html2canvas는 DOM을 캡처하는 방식. PDF에 들어갈 요소의 `id` 또는 `data-export` 속성을 디자인 시 미리 지정해주면 구현 용이.

3. **모바일 대시보드 우선순위** — 5개 화면 중 랜딩/온보딩은 모바일 퍼스트 필수. 대시보드/인사이트는 데스크톱 우선 후 태블릿 지원 수준으로 조율.

## CPO에게 피드백

1. **온보딩 3단계 중 Step2 (OAuth 시뮬레이션)** — 실제 OAuth 없이 "연결 중..." 로딩만 보여주는 방식으로 구현. 사용자가 실제 연결된다고 오해할 수 있으므로 UI에 "프로토타입 데모 모드" 배지 표시 권장.

2. **AI 인사이트 패널 vs 독립 페이지** — 지시서에는 "패널"로 명시되었으나 인사이트 콘텐츠 양 감안 시 `/dashboard/insights` 독립 페이지가 UX 상 유리. 대시보드 우측 슬라이드아웃 패널과 독립 페이지 중 최종 확정 요청.

3. **PDF 내보내기 범위** — 현재 설계는 현재 화면(대시보드) 기준 PDF 1장. 다중 채널 리포트(채널별 상세 + 인사이트 포함) 요구사항이면 개발 복잡도가 3배 증가. MVP에서는 단일 페이지 캡처로 확정 권장.
