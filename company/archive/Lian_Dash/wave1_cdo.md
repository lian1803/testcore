# CDO 분석 — Lian Dash (마케팅 통합 데이터 분석 SaaS — UI 프로토타입)

> Wave 1 | 작성일: 2026-03-30 | 작성자: CDO | 범위: UI 프로토타입

---

## 1. 디자인 비전

**"데이터를 보는 즐거움" — 한국 중소기업 마케터를 위한 선제적 애널리틱스**

한국中小企业의 마케팅 데이터 흩어짐 문제를 해결하는 선제적 AI 대시보드. 데이터를 복잡하게 보여주는 기존 도구와 달리, 핵심 한 줄 인사이트를 먼저 전달. 차트는 배경이 되고,洞見가 주인공이 되는 UX.

### 비주얼 톤
- **분위기**: Professional but approachable. Notion의 깔끔함 + Linear의 정밀함 + 한국적 따뜻함
- **감성**: "마케터가 아침에を開きたくなる 대시보드" — 긴장감 없는 데이터 리뷰
- **광택/질감**: Flat design + 미세한 gradient. 3D 효과나 heavy shadow 금지

### 다크모드
**Light mode 단독.** 데이터 시각화는 밝은 배경에서 가독성이 높고, 한국中小企业 사용자가室内 조명 환경에서 업무하는实际情况에 맞춤. Dark mode는 Phase 2에서 고려.

---

## 2. 마케팅 채널 반영

Wave 1-0에서 수아 채널 판단 결과 없음 (프로토타입 단계). 따라서 **범용 B2B SaaS** 기준으로 설계.

다만 마케팅 채널(GA4/Meta/네이버SA) 특化和리があるため:
- 채널 색상体系을 시각적 언어의 핵심으로確立 (GA4=Blue, Meta=Purple, 네이버SA=Emerald)
- 채널 로고가 곧 브랜드 아이덴티티 — 랜딩 페이지 상단 신뢰 요소로 배치
- 온보딩 첫 화면에서 3개 채널 연결 = "우리 도구는Marketing 통합 플랫폼"이라는 가치 제안

---

## 3. UX 원칙 (이 프로젝트 맞춤)

1. **KPI 먼저, 차트 나중** — 사용자가 숫자要先 확인. 차트는 "왜 그런 숫자인지"를 설명하는 보조재
2. **전주 대비 % 한 눈에** — 모든 KPI 카드에 화살표 + % 표기. 숫자만으로는 모르는 "방향"을 즉시 전달
3. **날짜 필터 = 전역 네비게이션** — today/7d/30d切换가 대시보드 경험의 핵심. 스켈레톤 필수
4. **AI 인사이트는 방해하지 말고 도와준다** — 슬라이드아웃 패널, 현재 화면 가리지 않음
5. **"데모 모드"는 결점이 아니라 신뢰** — 프로토타입 한계를 숨기지 않고 공개. 사용자 기대치 관리

---

## 4. 디자인 시스템

### 4-1. 컬러 팔레트 (Tailwind 커스텀 값)

```typescript
// tailwind.config.ts — extend.colors에 추가

// === Base ===
background:     '#FFFFFF',   // main bg
backgroundSub:  '#F8FAFC',   // section bg, card bg
border:         '#E2E8F0',  // dividers, card borders
textPrimary:    '#0F172A',   // headings
textSecondary:  '#475569',   // body text
textMuted:      '#94A3B8',   // captions, placeholders

// === Brand Primary: Indigo ===
primary: {
  50:  '#EEF2FF',
  100: '#E0E7FF',
  200: '#C7D2FE',
  300: '#A5B4FC',
  400: '#818CF8',
  500: '#6366F1',  // main brand color
  600: '#4F46E5',
  700: '#4338CA',
  800: '#3730A3',
  900: '#312E81',
}

// === Semantic ===
success:  { DEFAULT: '#10B981', light: '#D1FAE5', dark: '#059669' }
warning:  { DEFAULT: '#F59E0B', light: '#FEF3C7', dark: '#D97706' }
danger:   { DEFAULT: '#EF4444', light: '#FEE2E2', dark: '#DC2626' }

// === Channel Colors ===
channelGA4: {
  DEFAULT: '#4285F4',  // Google Blue
  light:   '#DBEAFE',
  bg:      '#EFF6FF',
}
channelMeta: {
  DEFAULT: '#A855F7',  // Meta Purple
  light:   '#F3E8FF',
  bg:      '#FAF5FF',
}
channelNaver: {
  DEFAULT: '#10B981',  // Naver Green
  light:   '#D1FAE5',
  bg:      '#ECFDF5',
}
```

### 4-2. 타이포그래피

```
Title (H1):   Pretendard / Inter — 700 weight — 32px (mobile) / 48px (desktop)
Title (H2):   Pretendard / Inter — 700 weight — 24px
Title (H3):   Pretendard / Inter — 600 weight — 18px
Body:          Pretendard / Inter — 400 weight — 15px
Caption:       Pretendard / Inter — 400 weight — 13px
KPI Number:    'Plus Jakarta Sans', monospace — 700 weight — 28px
```

**Pretendard** 설치: `next/font`/google 또는 CDN. 없으면 system-ui fallback.

```html
<!-- app/layout.tsx — head에 추가 -->
<link rel="preconnect" href="https://cdn.jsdelivr.net" />
<link href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css" rel="stylesheet" />
```

**한국어 숫자 표기 규칙:**
- 금액: `38,080,000원` — Intl.NumberFormat('ko-KR', { style: 'currency', currency: 'KRW' })
- ROAS: `3.4x` — 소수 1자리 + 배율
- CTR: `4.2%` — 소수 1자리
- 전환수: `842건` — Intl.NumberFormat('ko-KR') + '건'
- 전주 대비: `+12.3%` (초록) / `-8.1%` (빨강) — +/- 부호 필수

### 4-3. 컴포넌트 시스템

**shadcn/ui 사용 컴포넌트:**
| 컴포넌트 | 용도 |
|----------|------|
| `Button` | Primary (indigo), Secondary (outline), Ghost |
| `Card` | KPI 카드, 채널 카드, 인사이트 카드 |
| `Badge` | 채널 배지, 데모 모드 배지 |
| `Tabs` | 채널 탭 (전체/GA4/Meta/네이버SA) |
| `Progress` | 온보딩 진행바 |
| `Separator` | 섹션 구분선 |
| `Skeleton` | 날짜 필터 전환 시 로딩 |
| `Dialog` | PDF 내보내기 모달 |
| `Select` | (미래: 채널 필터) |
| `Tooltip` | KPI 카드 아이콘 설명 |

**커스텀 컴포넌트:**
| 컴포넌트 | 설명 |
|----------|------|
| `KpiCard` | KPI 수치 + 전주 대비 % + 화살표 |
| `ChannelBadge` | 채널 색상 배지 (GA4/Meta/네이버SA) |
| `InsightCard` | AI洞見 카드 (빨강/노랑/초록 border-left) |
| `ConnectionCard` | 온보딩 채널 연결 카드 |
| `TrendArrow` | 초록↑ / 빨강↓ 화살표 아이콘 |
| `SlideOutPanel` | AI 인사이트 우측 슬라이드아웃 |
| `ShimmerSkeleton` | 스켈레톤 로딩 (KPI용 6개, 차트용 1개) |
| `ExportPreview` | PDF 미리보기 영역 |

---

## 5. 핵심 화면 흐름

```
[랜딩] → [온보딩 3단계] → [메인 대시보드]
                                ↓ (AI 인사이트 토글)
                          [AI 인사이트 슬라이드아웃 패널]
                                ↓ (PDF 내보내기)
                          [PDF 내보내기 모달]
```

**유저 저니 핵심:**
1. 랜딩 CTA 클릭 → 즉시 온보딩 시작 (저장/회원가입 없음)
2. 온보딩 3단계에서 채널 3개 모두 "연결" → 완료 → 대시보드
3. 대시보드 첫 진입: 30일 기준 데이터 기본 표시
4. 날짜 필터 변경 → 스켈레톤 0.5초 → 새 데이터
5. AI 인사이트 토글 → 패널 슬라이드 인 →洞見 확인 → 패널 닫기
6. PDF 내보내기 → 체크리스트 → 다운로드

---

## 6. 각 화면 상세 설계

### 화면 1: 랜딩 (`/`)

**목적:** 제품 가치를 5초 안에 전달. CTA 클릭 → 온보딩 이동.

#### 6.1.1 Hero Section

```
┌─────────────────────────────────────────────────────────────┐
│  [Logo: Lian Dash]                    [데모 요청] [로그인]  │  ← NavBar: sticky
├─────────────────────────────────────────────────────────────┤
│                                                             │
│        마케팅 데이터, 한눈에 끝내다                          │  ← H1, 32px(mobile)/48px
│                                                             │
│   GA4 · 메타 · 네이버SA 한 dashboard에서                    │  ← subheadline
│   파악하고, AI가 개선점을 제안합니다                        │
│                                                             │
│   [                                        ]                │  ← Primary CTA
│   [       무료로 시작하기 →              ]                │  ← Button size="lg"
│                                                             │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐                 │
│   │  GA4     │  │  Meta    │  │ 네이버SA  │  ← 3개 로고    │  ← grayscale 60%
│   └──────────┘  └──────────┘  └──────────┘     어울리게    │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  실제 사용사의 후기                                          │
│  ┌────────────────┐ ┌────────────────┐ ┌────────────────┐ │
│  │ ★★★★★          │ │ ★★★★★          │ │ ★★★★★          │ │
│  │ "한 달째 사..." │ │ "AI洞見이..."   │ │ "단순 ..."     │ │
│  │  이 Commerce   │ │  marketing..."  │ │  王도전자      │ │
│  └────────────────┘ └────────────────┘ └────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

**Grid:** 1열 (mobile) → Hero 컨텐츠 centered, max-width 640px
**CTA:** Primary Button (`bg-primary-600 hover:bg-primary-700 text-white`)
**채널 로고:** grayscale filter, opacity 0.6 → hover 시 opacity 1.0 transition 300ms
**NavBar:** `position: sticky top-0 bg-white/80 backdrop-blur-sm border-b border-border`

#### 6.1.2 Feature Section (스크롤 후)

```
┌─────────────────────────────────────────────────────────────┐
│  핵심 기능                                                   │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐  │
│  │ [Chart Icon]   │  │ [AI Icon]     │  │ [Export Icon] │  │
│  │ 채널 통합 보기  │  │ AI洞見 자동 제안 │  │ PDF 리포트    │  │
│  │ GA4, Meta,    │  │ 매일 아침 분석   │  │ 1-click      │  │
│  │ 네이버SA 한 곳에│  │ 요약을送达합니다  │  │ 내보내기      │  │
│  └───────────────┘  └───────────────┘  └───────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

**Grid:** 1열 (mobile) → 3열 (desktop ≥768px)
**Card:** `bg-backgroundSub border border-border rounded-xl p-6`

#### 6.1.3 Pricing Section (스크롤 후)

```
┌─────────────────────────────────────────────────────────────┐
│  간단한 가격                                                 │
│  ┌─────────────┐  ┌─────────────────┐  ┌─────────────┐     │
│  │ Starter     │  │ Professional ✓  │  │ Enterprise  │     │
│  │ 0원/월      │  │ 990,000원/월    │  │ 상담요청    │     │
│  │ ...         │  │ ...             │  │ ...         │     │
│  └─────────────┘  └─────────────────┘  └─────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

**Grid:** 1열 (mobile) → 3열 (desktop)
**Pro Card:** `border-primary-500 border-2 shadow-lg` — highlighted=true
**CTA Buttons:** Starter=Outline, Pro=Primary, Enterprise=Ghost

---

### 화면 2: 온보딩 (`/onboarding`)

**목적:** 채널 3개 연결 → 대시보드 이동. 3단계 이내.

#### 6.2.1 Progress Bar (상단)

```
┌─────────────────────────────────────────────────────────────┐
│  [1]────────[2]────────[3]                                    │
│  채널 선택      연결하기     완료                            │
│  ● Completed    ◐ Current    ○ Pending                      │
└─────────────────────────────────────────────────────────────┘
```

**컴포넌트:** `Progress` (shadcn) — value={step/3*100}
**색상:** step 완료 = `bg-primary-500`, 현재 = `bg-primary-200`, 남은 = `bg-border`
**Height:** 4px, rounded-full

#### 6.2.2 Step 1: 채널 선택

```
┌─────────────────────────────────────────────────────────────┐
│  분석할 채널을 선택하세요                                    │
│  복수 선택 가능 — 선택 후 "다음" 버튼 활성화                  │
│                                                             │
│  ┌─────────────────────┐  ┌─────────────────────┐         │
│  │ [GA4 Logo]           │  │ [Meta Logo]          │         │
│  │ Google Analytics     │  │ Meta Ads             │         │
│  │ 검색/오가닉 트래픽    │  │ Facebook + Instagram │         │
│  │          ☑ 선택됨     │  │          ☑ 선택됨     │         │
│  └─────────────────────┘  └─────────────────────┘         │
│  ┌─────────────────────┐                                   │
│  │ [NaverSA Logo]       │                                   │
│  │ 네이버 검색 광고      │                                   │
│  │ 국내 검색 전환 최적화  │                                   │
│  │          ☑ 선택됨     │                                   │
│  └─────────────────────┘                                   │
│                                                             │
│  [◀ 이전]              [다음 →]  (disabled: 0개 선택 시)    │
└─────────────────────────────────────────────────────────────┘
```

**Grid:** 1열 (mobile) → 3열 (desktop), 채널 카드 clickable (toggle)
**선택 시:** Card border → `border-primary-500 border-2`, checkmark Badge overlay
**Interaction:** 카드 클릭 → border + checkmark 토글, 200ms ease transition

#### 6.2.3 Step 2: 채널 연결 시뮬레이션

```
┌─────────────────────────────────────────────────────────────┐
│  채널을 연결하고 있습니다...                                 │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ [GA4 Logo]  Google Analytics                        │    │
│  │              ● ● ● 연결 중...  (pulsing dot)        │    │  ← 1.5s
│  │              ✓ 연결 완료                             │    │  ← 완료 후
│  └─────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ [Meta Logo]  Meta Ads                               │    │
│  │              ○ 준비 중                               │    │
│  └─────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ [Naver Logo]  네이버 검색 광고                      │    │
│  │              ○ 준비 중                               │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
│  [데모 모드] — 실제 OAuth 연동 없이 데모 데이터를 사용합니다   │  ← Badge
│                                                             │
│  [◀ 이전]                               [건너뛰기] [다음 →]  │
└─────────────────────────────────────────────────────────────┘
```

**로딩 애니메이션:** 순차 실행. GA4 완료 → 500ms → Meta → 500ms → 네이버SA
**Pulsing dot:** 세 개의 점(`● ● ●`)이 순서대로 커졌다 작아지는 animation
**체크 표시:** `text-success` green checkmark icon, scale in 200ms
**"데모 모드" Badge:** `bg-warning-100 text-warning-800 border border-warning-200`
**건너뛰기:** 온보딩 완료를 우회하고 대시보드로 바로 이동 ( 데모用户体验 continuity)

#### 6.2.4 Step 3: 완료

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│                    ✓                                        │  ← large checkmark
│                                                             │
│            대시보드 준비 완료!                               │
│                                                             │
│    3개 채널이 연결되었습니다. 이제 데이터를 확인하세요.        │
│                                                             │
│    [    대시보드 열기 →    ]                                │
│                                                             │
│    [← 온보딩 다시 시작]                                      │
└─────────────────────────────────────────────────────────────┘
```

**Centered layout, max-width 480px**
**Checkmark:** 80px green circle with white checkmark icon, scale animation on mount
**CTA:** Primary Button, full width

---

### 화면 3: 메인 대시보드 (`/dashboard`)

**목적:** 핵심 KPI 6개 + 트렌드 차트 + 채널별 테이블. 한 화면에 모든 것.

#### 6.3.1 Layout 구조 (Desktop 1280px 기준)

```
┌─────────┬──────────────────────────────────────────────────┐
│         │  [날짜 필터: Today | 7일 | 30일]  [PDF] [AI 토글]  │  ← DashboardHeader
│ 사이드바  ├──────────────────────────────────────────────────┤
│  240px  │  [KPI]  [KPI]  [KPI]  [KPI]  [KPI]  [KPI]        │  ← 3열 x 2줄
│         ├────────────────────────────┬─────────────────────┤
│ 대시보드 │                            │                     │
│ AI洞見  │    라인 차트 (시계열)        │  [AI洞見 토글 버튼]  │
│ 설정    │    7d/30d 추세선            │  ┌─────────────┐   │
│         │                            │  │ Toggle Btn  │   │
│         ├────────────────────────────┤  │  AI洞見 패널 │   │
│         │  [전체] [GA4] [Meta] [NSA]  │  │  열기 ↑      │   │
│         │  채널별 성과 테이블         │  └─────────────┘   │
└─────────┴────────────────────────────┴─────────────────────┘
```

**Grid:** `grid-cols-1fr 240px` — 대시보드 영역 + 사이드바
**Sidebar:** `w-[240px] min-h-screen bg-slate-900 text-white` — fixed
**Main area:** `flex-1 overflow-auto p-6`
**Header:** `sticky top-0 z-10 bg-white border-b border-border`

#### 6.3.2 DashboardHeader

```
┌──────────────────────────────────────────────────────────────┐
│  대시보드                         [Today][7일][30일] [PDF↓] [💡 AI] │
└──────────────────────────────────────────────────────────────┘
```

**날짜 필터:** `SegmentedControl` 또는 3개 `Button` group — `Today`/`7일`/`30일`
**활성 필터:** `bg-primary-500 text-white`, 비활성 = `bg-transparent text-textSecondary hover:bg-backgroundSub`
**PDF 버튼:** `Button variant="outline" size="sm"` — 아이콘: Download
**AI洞見 토글:** `Button variant="ghost" size="sm"` — 아이콘: Sparkles — 오른쪽 사이드바 패널 토글

#### 6.3.3 KPI 카드 그룹 (6개)

```
┌────────────────────┐ ┌────────────────────┐ ┌────────────────────┐
│ 总 매출             │ │ 广告费             │ │ ROAS               │
│ ₩38,080,000        │ │ ₩11,200,000        │ │ 3.4x               │
│ ↑ +12.3% 전주      │ │ ↑ +8.1% 전주       │ │ ↑ +0.2 전주        │
└────────────────────┘ └────────────────────┘ └────────────────────┘
┌────────────────────┐ ┌────────────────────┐ ┌────────────────────┐
│ 전환수               │ │ 平均 CPA           │ │ 平均 CTR            │
│ 842건               │ │ ₩13,301            │ │ 4.2%                │
│ ↑ +23건 전주        │ │ ↓ -5.2% 전주       │ │ ↑ +0.8%p 전주       │
└────────────────────┘ └────────────────────┘ └────────────────────┘
```

**Grid:** `grid grid-cols-2 md:grid-cols-3 gap-4`
**Card style:** `bg-white border border-border rounded-xl p-5 shadow-sm`
**KpiCard 내부:**
- 상단: caption `text-caption text-textMuted` (총 매출)
- 중앙: KPI number `font-mono text-[28px] font-bold text-textPrimary`
- 하단: 전주 대비 `text-[13px] font-medium` (초록=`text-success`, 빨강=`text-danger`)

**TrendArrow 컴포넌트:**
```tsx
// ↑ = 상승 (초록), ↓ = 하락 (빨강)
{change > 0 ? (
  <TrendingUp className="inline w-4 h-4 text-success mr-1" />
) : (
  <TrendingDown className="inline w-4 h-4 text-danger mr-1" />
)}
<span>{change > 0 ? '+' : ''}{change}% 전주</span>
```

**스켈레톤 상태 (날짜 필터 변경 시):**
```
┌────────────────────┐ ┌────────────────────┐ ┌────────────────────┐
│ ░░░░░░░░░░░░░░     │ │ ░░░░░░░░░░░░░░     │ │ ░░░░░░░░░░░░░░     │  ← h-24
│ ░░░░░░░░░░░░░░     │ │ ░░░░░░░░░░░░░░     │ │ ░░░░░░░░░░░░░░     │
│ ░░░░░░░░░░░        │ │ ░░░░░░░░░░░░        │ │ ░░░░░░░░░░░        │
└────────────────────┘ └────────────────────┘ └────────────────────┘
```
**Shimmer Skeleton 구현:**
```tsx
// src/components/ui/skeleton.tsx에 shimmer variant 추가
<div className="animate-pulse bg-gradient-to-r from-slate-200 via-slate-100 to-slate-200 bg-[length:200%_100%] animate-shimmer rounded" />
// globals.css에: @keyframes shimmer { 0% { background-position: 200% 0 } 100% { background-position: -200% 0 } }
```

#### 6.3.4 채널별 트렌드 라인 차트

```
┌──────────────────────────────────────────────────────────────┐
│  매출 추이                                          [범례]   │
│  ┃                                                      ┃   │
│  ┃        ╱╲    ╱╲                                      ┃   │
│  ┃   ╱╲  ╱  ╲  ╱  ╲  ╱╲   ╱╲                            ┃   │
│  ┃  ╱  ╲╱    ╲╱    ╲╱  ╲ ╱  ╲                           ┃   │
│  ┃╱                                         GA4 ————     ┃   │
│  ┃                                         Meta — — —    ┃   │
│  ┃                                         NaverSA ···  ┃   │
│  ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ (날짜)        ┃   │
└──────────────────────────────────────────────────────────────┘
```

**Recharts 사용:**
```tsx
<ResponsiveContainer width="100%" height={320}>
  <LineChart data={timeSeriesData}>
    <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
    <XAxis dataKey="date" tick={{ fontSize: 12, fill: '#94A3B8' }} />
    <YAxis tickFormatter={(v) => `₩${(v/1000000).toFixed(0)}M`} tick={{ fontSize: 12, fill: '#94A3B8' }} />
    <Tooltip formatter={(value) => [`₩${Number(value).toLocaleString('ko-KR')}`, '매출']} />
    <Line type="monotone" dataKey="ga4Revenue" stroke="#4285F4" strokeWidth={2} dot={false} />
    <Line type="monotone" dataKey="metaRevenue" stroke="#A855F7" strokeWidth={2} strokeDasharray="5 5" dot={false} />
    <Line type="monotone" dataKey="naverRevenue" stroke="#10B981" strokeWidth={2} strokeDasharray="2 2" dot={false} />
  </LineChart>
</ResponsiveContainer>
```

**채널 라인 스타일:**
- GA4: 실선 `#4285F4`
- Meta: 대시점선 `strokeDasharray="5 5"` `#A855F7`
- 네이버SA: 점선 `strokeDasharray="2 2"` `#10B981`

#### 6.3.5 채널별 성과 테이블

```
┌──────────────────────────────────────────────────────────────┐
│  [전체] [GA4] [Meta] [네이버SA]                              │  ← Tabs (shadcn)
├──────────────────────────────────────────────────────────────┤
│  채널     │ 광고비      │ 매출       │ ROAS  │ 전환수  │ CTR   │
│  ─────────┼─────────────┼────────────┼───────┼─────────┼───────│
│  GA4      │ ₩2,240,000  │ ₩17,136,000│ 7.7x  │ 423건   │ 5.1%  │
│  Meta     │ ₩3,920,000  │ ₩11,424,000│ 2.9x  │ 252건   │ 3.8%  │
│  네이버SA  │ ₩5,040,000  │ ₩9,520,000 │ 1.9x  │ 167건   │ 3.2%  │
└──────────────────────────────────────────────────────────────┘
```

**Tabs:** `variant="underline"` — shadcn `TabsList` + `TabsTrigger`
**테이블:** native `<table>` with Tailwind — `border-collapse`
**_ROAS 색상:_ ROAS ≥ 5 = `text-success`, 3-5 = `text-warning`, <3 = `text-danger`
**hover:** 행 highlight `bg-backgroundSub`

---

### 화면 4: AI 인사이트 슬라이드아웃 패널

**위치:** 대시보드 우측, 너비 320px, 높이 100vh (딱 붙음)
**오버레이:** 없음 ( dims 없이 슬라이드만)

#### 6.4.1 패널 열기/닫기 애니메이션

```tsx
// framer-motion 사용 시
<motion.div
  initial={{ x: 320 }}
  animate={{ x: 0 }}
  exit={{ x: 320 }}
  transition={{ duration: 0.3, ease: 'easeOut' }}
>
// 또는 CSS-only (Next.js limitation 고려)
className="transform transition-transform duration-300 translate-x-0"
className="transform transition-transform duration-300 translate-x-full"
```

#### 6.4.2 패널 레이아웃

```
┌────────────────────────────────────┐
│  💡 AI洞見              [✕ 닫기]   │  ← Header: sticky
├────────────────────────────────────┤
│  [전체 ▼]  필터: 전체/GA4/Meta/NSA  │  ← Select filter
├────────────────────────────────────┤
│  ┃ [빨강]  ⚠️ 네이버SA ROAS 낮음   │  ← border-left 4px danger
│  ┃ 채널: 네이버SA | 영향도: 높음    │
│  ┃ ROAS 1.9x — 업계 평균 이하     │
│  ┃ → 예산 20% GA4로 이동 검토     │
├────────────────────────────────────┤
│  ┃ [노랑]  ⚡ Meta 빈도수 주의     │  ← border-left 4px warning
│  ┃ 채널: Meta | 영향도: 중간       │
│  ┃ 광고 빈도 3.8회 — 창의력 저하   │
│  ┃ → 신규 타겟受众 추가 추천       │
├────────────────────────────────────┤
│  ┃ [초록]  ✓ GA4 개선趋势          │  ← border-left 4px success
│  ┃ 채널: GA4 | 영향도: 중간        │
│  ┃ 이탈률 4.2%p 개선              │
│  ┃ → 현재 전략 유지 권장          │
└────────────────────────────────────┘
```

**패널 스타일:** `bg-white border-l border-border w-[320px] h-screen sticky top-0 overflow-y-auto`
**Header:** `sticky top-0 bg-white border-b border-border p-4 flex justify-between items-center`

#### 6.4.3 InsightCard 상세 디자인

```tsx
// border-left 색상
danger:  'border-l-4 border-l-danger bg-danger-light'
warning: 'border-l-4 border-l-warning bg-warning-light'
success: 'border-l-4 border-l-success bg-success-light'

// 내부 구조
<div className="p-4 rounded-r-lg border border-l-0 border-border">
  <div className="flex items-start gap-2 mb-2">
    {insight.type === 'warning' && <AlertTriangle className="w-4 h-4 text-danger mt-0.5" />}
    {insight.type === 'opportunity' && <TrendingUp className="w-4 h-4 text-success mt-0.5" />}
    {insight.type === 'info' && <Info className="w-4 h-4 text-primary mt-0.5" />}
    <span className="font-semibold text-textPrimary">{insight.title}</span>
  </div>
  <div className="flex gap-2 mb-2">
    <ChannelBadge channel={insight.channel} />
    <Badge variant="outline" className="text-[11px]">
      영향도: {insight.impact === 'high' ? '높음' : insight.impact === 'medium' ? '중간' : '낮음'}
    </Badge>
  </div>
  <p className="text-[13px] text-textSecondary mb-2">{insight.description}</p>
  <p className="text-[13px] font-medium text-primary">
    → {insight.action}
  </p>
</div>
```

**카드 간격:** `gap-3` — 카드당 padding `p-4`
**스크롤:** 패널 내 scroll, Header sticky로 고정

---

### 화면 5: PDF 내보내기 모달

**트리거:** 대시보드 Header의 PDF 버튼
**스타일:** `Dialog` (shadcn) — `max-w-lg`

```
┌──────────────────────────────────────────────────────────────┐
│  리포트 내보내기                                      [✕]   │
├──────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────┐   │
│  │  📄 PDF 미리보기 영역                                  │   │
│  │  (data-export 속성 영역 — 회색 배경)                  │   │
│  │                                                      │   │
│  │  Lian Dash | 2026-03-30 | 30일 보고서                │   │
│  │  ─────────────────────────────────────               │   │
│  │  总 매출: ₩38,080,000 | ROAS: 3.4x | 전환: 842건    │   │
│  │  ─────────────────────────────────────               │   │
│  │  [차트 이미지]                                        │   │
│  └──────────────────────────────────────────────────────┘   │
├──────────────────────────────────────────────────────────────┤
│  ☑ KPI 요약                                                │
│  ☑ 채널별 성과                                             │
│  ☐ AI洞見 포함                                            │
├──────────────────────────────────────────────────────────────┤
│  파일명: LianDash_2026-03-30_30일.pdf          [취소]      │
│                                         [PDF 다운로드]      │
└──────────────────────────────────────────────────────────────┘
```

**미리보기:** `bg-slate-100 border-2 border-dashed border-slate-300 rounded-lg p-4`
**미리보기 내 `data-export` 영역:**
```tsx
<div data-export="kpi-summary">
  {/* KPI 6개 수치 */}
</div>
<div data-export="chart">
  {/* 라인 차트 이미지 (html2canvas 캡처) */}
</div>
<div data-export="channel-table">
  {/* 채널별 테이블 */}
</div>
```

**Checklist:** native checkbox + label — `gap-2 flex items-center`
**파일명 입력:** `Input` (shadcn) — 현재 날짜 + 기간 자동 입력
**토스트:** 다운로드 완료 시 `import { toast } from 'sonner'` — `toast.success('PDF가 다운로드되었습니다.')`

---

## 7. 반응형 설계

### 랜딩 + 온보딩 (모바일 퍼스트)

| Breakpoint | 레이아웃 |
|------------|---------|
| < 640px (mobile) | 1열, CTA full width, 채널 카드 세로 배치 |
| 640-1024px (tablet) | 2열 카드, CTA centered |
| ≥ 1024px (desktop) | 3열 카드 |

**모바일 온보딩:**
- Progress bar: `w-[60%] mx-auto`
- 채널 카드: 터치 영역 min 48px height
- Step 2 연결 카드: 세로 scroll, swipe navigation 비권장 (프로토타입)

### 대시보드 (데스크탑 우선)

| Breakpoint | 레이아웃 변경 |
|------------|-------------|
| ≥ 1280px | 전체 레이아웃 (사이드바 240px + 메인) |
| 1024-1279px | 사이드바 숨김, Mobile Header 표시 |
| < 1024px | 스택드 레이아웃, KPI 카드 2열 |

**사이드바 숨김 (1024px 이하):**
```tsx
// Sidebar.tsx
<div className="hidden lg:block w-[240px]" />  // 사이드바
<DashboardHeader /> // 모바일용 헤더 (햄버거 메뉴 포함)
```

---

## 8. 애니메이션 및 인터랙션 정의

### 8.1 날짜 필터 전환 (KPI 스켈레톤)

```tsx
// 상태: dateFilter 변경 → isLoading: true (0.5s minimum)
// Skeleton 표시: opacity 0 → 1, 150ms
// 데이터 도착: Skeleton → 실제 KPI Card, cross-fade 200ms

<DateFilterBar
  value={filter}
  onChange={async (f) => {
    setIsLoading(true);
    await new Promise(r => setTimeout(r, 500)); // 최소 로딩 시간
    setFilter(f);
    setIsLoading(false);
  }}
/>
```

### 8.2 AI 인사이트 패널 토글

```tsx
// DashboardHeader의 "AI洞見" 버튼 → isPanelOpen toggle
// 패널: translateX(320px → 0) duration-300 ease-out
// 토글 버튼: icon rotation 0° → 180° (빛나는 효과)
```

### 8.3 온보딩 채널 연결 순차 로딩

```tsx
// GA4 → Meta → 네이버SA 순서, 각 1.5s 간격
// 각 채널: ConnectingCard → (1.5s) → ConnectedCard
// 순차 완료 후: "다음" 버튼 fade in
```

### 8.4 KPI 카드 카운트업 (첫 로드)

```tsx
// 숫자가 0 → 실제값으로 800ms ease-out animation
// React: useEffect + requestAnimationFrame 또는 recharts 내장 animation
// Phase 2에서 구현, Phase 1은 instant display
```

---

## 9. 컴포넌트 상태 정의

### KpiCard 상태
| 상태 | 표현 |
|------|------|
| Default | 수치 + 전주 대비 |
| Loading | Shimmer skeleton (높이 96px) |
| Error | "데이터 로드 실패" + retry button |

### ConnectionCard 상태
| 상태 | 표현 |
|------|------|
| Ready | 로고 + 채널명 + "연결하기" 버튼 |
| Connecting | 로딩 스피너 + "연결 중..." |
| Connected | 체크 아이콘 + "연결 완료" (초록) |
| Error | 빨강 X 아이콘 + "재시도" |

### InsightCard 상태
| 상태 | 표현 |
|------|------|
| Opportunity | 초록 border-left, TrendingUp 아이콘 |
| Warning | 노랑 border-left, AlertTriangle 아이콘 |
| Info | 파랑 border-left, Info 아이콘 |

---

## 10. CTO에게 요청사항

1. **Shimmer Skeleton CSS** — `globals.css`에 `@keyframes shimmer` 정의 필요. `animate-shimmer` class로 적용.
2. **framer-motion 설치 여부** — AI 인사이트 패널 애니메이션에 framer-motion 사용 권장. 미설치 시 CSS transform으로 대체 (위 설계 참고).
3. **Pretendard 폰트 로딩** — `app/layout.tsx` head에 CDN link 추가 필요.
4. **Sonner 토스트** — `npm install sonner` — PDF 다운로드 완료 토스트에 사용.
5. **Recharts ResponsiveContainer** — 모든 차트 반드시 `ResponsiveContainer`로 감싸기.

---

## 11. FE 구현 체크리스트

```
CDO-FE-01: tailwind.config.ts — 커스텀 색상 (primary, channel*, semantic) 추가
CDO-FE-02: globals.css — @keyframes shimmer, Pretendard font-face
CDO-FE-03: app/layout.tsx — Pretendard CDN link, Sonner toast provider
CDO-FE-04: types.ts — KpiCardProps, InsightCardProps, ConnectionCardProps 타입
CDO-FE-05: KpiCard.tsx — 수치 + 전주 대비 % + TrendArrow
CDO-FE-06: KpiCardGroup.tsx — 6개 카드 3열 그리드 + Skeleton
CDO-FE-07: ChannelBadge.tsx — GA4/Meta/NSA 배지
CDO-FE-08: InsightCard.tsx — border-left 색상별 (danger/warning/success)
CDO-FE-09: SlideOutPanel.tsx — AI 인사이트 우측 패널 (320px)
CDO-FE-10: ConnectionCard.tsx — 연결 상태별 UI (ready/connecting/connected)
CDO-FE-11: DateFilterBar.tsx — today/7d/30d 토글 + isLoading 상태
CDO-FE-12: ExportModal.tsx — PDF 체크리스트 + 미리보기 + 다운로드
CDO-FE-13: 랜딩 page.tsx — HeroSection + FeatureSection + PricingSection
CDO-FE-14: 온보딩 page.tsx — Progress bar + Step 1/2/3
CDO-FE-15: 대시보드 page.tsx — KPI + 차트 + 테이블 + AI 패널 토글
CDO-FE-16: 반응형 검증 — 375px (mobile), 768px (tablet), 1280px (desktop)
```
