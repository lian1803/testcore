# Lian Dash — 풀 리디자인 설계서 v2.0

> CDO: 나은 | 작성일: 2026-04-03 | 대상: 민준(FE) 구현용

---

## 디자인 비전

**"데이터가 살아 숨쉬는 관제센터 — 처음 열면 '와', 매일 열면 '이게 없으면 못 살아'"**

기존 디자인의 문제: 평범한 dark SaaS. 어디서나 본 패턴.
새 방향: **Raycast 수준의 밀도감 + Linear 수준의 모션 + Vercel 수준의 미니멀** — 세 개를 한국 마케터 맥락에 합성.

타겟 마케터는 매일 아침 이 화면을 보며 "오늘 광고 어때?" 를 판단한다.
그 순간을 위해: 핵심 지표가 첫 시선에 들어오고, 이상 신호가 즉각 눈에 띄고, 다음 액션이 자연스럽게 유도되어야 한다.

---

## 레퍼런스 분석 — 훔쳐올 것

### Linear (linear.app)
- **훔칠 것**: 극단적 다크 배경(#07070a 수준), grain texture noise overlay, grid-dot 마이크로 애니메이션, 타이포그래피 계층의 정밀한 조정
- **적용 화면**: 전체 앱 배경 / 사이드바 / 대시보드 레이아웃
- **핵심 교훈**: "비어있는 것처럼 보이는데 꽉 찬 느낌" — 여백을 공간으로 쓰는 법

### Vercel (vercel.com)
- **훔칠 것**: 흑백 Hero + 한 줄 카피의 강력함, Geist 폰트 시스템, 이원 CTA 패턴(Primary + Outline), 스크롤 트리거 섹션 전환
- **적용 화면**: 랜딩페이지 Hero / CTA 버튼 시스템
- **핵심 교훈**: "설명하지 마라, 보여줘라" — 제품 스크린샷이 카피보다 강하다

### Resend (resend.com)
- **훔칠 것**: 코드 스니펫을 UI 요소로 쓰는 방식, 개발자 신뢰 구축 패턴, 좌우분할 Hero (텍스트 왼쪽 / 데모 오른쪽)
- **적용 화면**: 랜딩 기능 섹션 / 인테그레이션 화면
- **핵심 교훈**: "도구처럼 느껴지게 하라" — SaaS가 아닌 내 무기처럼

### Dribbble SaaS Dashboard 패턴 분석
- **공통 트렌드**: 사이드바 아이콘 탭 + 메인 콘텐츠 2단 레이아웃, KPI 카드 상단 배치 + 차트 하단, 채널별 컬러 코딩 일관성
- **차별화 기회**: 국내 경쟁사 없음. 글로벌 SaaS 미학 + 한국어 UX = 그 자체가 차별점

---

## 컬러 시스템

### 기반 철학
채널 브랜드 컬러(GA4 오렌지 / 메타 블루 / 네이버 그린)를 액센트로 쓰되,
베이스는 **Obsidian Black** — 채널 컬러가 더 빛나게 하는 배경.

### 서피스 토큰
```css
--bg-base:        #050507;   /* 최심층 배경. body. 기존보다 더 어둡게 */
--bg-surface:     #0a0a0e;   /* 사이드바, 카드 배경 */
--bg-elevated:    #111116;   /* 호버 상태, 드롭다운 */
--bg-overlay:     #17171d;   /* 모달, 팝오버 */
--bg-subtle:      #1c1c24;   /* 입력필드, 비활성 영역 */
```

### 보더 토큰
```css
--border-faint:   rgba(255,255,255,0.04);  /* 거의 안 보이는 구분선 */
--border-subtle:  rgba(255,255,255,0.07);  /* 기본 카드 테두리 */
--border-default: rgba(255,255,255,0.11);  /* 활성 요소 테두리 */
--border-strong:  rgba(255,255,255,0.18);  /* 강조 테두리 */
```

### 텍스트 토큰
```css
--text-primary:   #f2f2f5;   /* 헤딩, 핵심 값 */
--text-secondary: #8a8a96;   /* 레이블, 보조 설명 */
--text-muted:     #4a4a55;   /* 비활성, 힌트 */
--text-inverse:   #07070a;   /* 라이트 버튼 위 텍스트 */
```

### 채널 컬러 (브랜드 정확도 유지)
```css
--ch-ga4:        #E37400;    /* GA4 오렌지 */
--ch-ga4-dim:    rgba(227,116,0,0.15);
--ch-ga4-glow:   rgba(227,116,0,0.35);

--ch-meta:       #1877F2;    /* 메타 블루 */
--ch-meta-dim:   rgba(24,119,242,0.15);
--ch-meta-glow:  rgba(24,119,242,0.35);

--ch-naver:      #03C75A;    /* 네이버 그린 */
--ch-naver-dim:  rgba(3,199,90,0.15);
--ch-naver-glow: rgba(3,199,90,0.35);
```

### 시스템 컬러
```css
--color-success:  #22c55e;
--color-warning:  #f59e0b;
--color-danger:   #ef4444;
--color-info:     #6366f1;
```

### 액센트 — Primary UI
```css
--accent-primary:  #ffffff;              /* 버튼, 활성 상태 */
--accent-secondary: rgba(255,255,255,0.08); /* 서브 버튼, 호버 */
```

**컬러 원칙**: 보라색 액센트 제거. Lian Dash는 채널 컬러가 아이덴티티다.
흰색 = Primary UI 액센트. 채널 컬러 = 데이터 레이어 액센트. 섞지 않는다.

---

## 타이포그래피

### 폰트 패밀리
```
본문/UI: Geist (Vercel 폰트 — 한글 미지원이므로 영문/숫자용)
한글 UI: Pretendard (Variable)
숫자/코드: Geist Mono
```

**설치:**
```
next/font/google 대신 Geist는 next/font/local로 설치.
Pretendard: npm install pretendard 또는 CDN.
```

### 타입 스케일
```
--text-xs:   11px / line-height: 1.4 / letter-spacing: 0.02em  — 배지, 캡션
--text-sm:   13px / line-height: 1.5 / letter-spacing: 0.01em  — 사이드바 네비, 레이블
--text-base: 15px / line-height: 1.6                            — 본문, 카드 설명
--text-lg:   18px / line-height: 1.5 / font-weight: 500        — 섹션 제목
--text-xl:   24px / line-height: 1.3 / font-weight: 600        — 페이지 헤더
--text-2xl:  32px / line-height: 1.2 / font-weight: 700        — KPI 숫자
--text-3xl:  48px / line-height: 1.1 / font-weight: 800        — 랜딩 Hero 부제
--text-hero: 72px / line-height: 1.0 / font-weight: 900        — 랜딩 메인 헤드라인
```

### KPI 숫자 전용 스타일
```
font-family: Geist Mono
font-size: 28~36px
font-weight: 700
letter-spacing: -0.02em  (숫자는 tight하게)
color: var(--text-primary)
```

---

## 컴포넌트 시스템

### A. 공통 유틸 클래스 (globals.css에 추가)

**Surface 클래스**
```css
.surface-card {
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: 12px;
}

.surface-elevated {
  background: var(--bg-elevated);
  border: 1px solid var(--border-default);
  border-radius: 8px;
}
```

**Glass (기존 유지 + 강화)**
```css
.glass-panel {
  background: rgba(255,255,255,0.025);
  backdrop-filter: blur(24px) saturate(180%);
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: 16px;
}
```

**채널 배지**
```css
.badge-ga4   { background: var(--ch-ga4-dim);   color: var(--ch-ga4);   border: 1px solid rgba(227,116,0,0.2); }
.badge-meta  { background: var(--ch-meta-dim);  color: var(--ch-meta);  border: 1px solid rgba(24,119,242,0.2); }
.badge-naver { background: var(--ch-naver-dim); color: var(--ch-naver); border: 1px solid rgba(3,199,90,0.2); }
/* 전부 border-radius: 999px; padding: 2px 8px; font-size: 11px; font-weight: 600; */
```

**트렌드 배지 (상승/하락)**
```css
.trend-up   { color: #22c55e; background: rgba(34,197,94,0.1);  padding: 2px 6px; border-radius: 4px; font-size: 12px; font-weight: 600; }
.trend-down { color: #ef4444; background: rgba(239,68,68,0.1);  padding: 2px 6px; border-radius: 4px; font-size: 12px; font-weight: 600; }
.trend-flat { color: #8a8a96; background: rgba(138,138,150,0.1); padding: 2px 6px; border-radius: 4px; font-size: 12px; font-weight: 600; }
```

### B. KPI 카드 컴포넌트 (신규 설계)

기존 문제: 6개 동일 크기 카드 나열 → 감동 없음.
새 방향: **Featured KPI 1개 (크게) + 보조 KPI 5개 (작게)** 또는 **가로 스크롤 슬라이더형**

```
KpiCard props:
  - label: string
  - value: string (포맷된 값)
  - change: number (%)
  - channel: 'ga4' | 'meta' | 'naver' | 'total'
  - isBigCard: boolean (Featured 카드 여부)
  - sparklineData: number[] (미니 라인차트)
```

**Big Card (ROAS Featured)**:
- 크기: 전체 너비의 1/3, 높이 160px
- 왼쪽: 큰 숫자 (36px) + 채널 배지
- 오른쪽: 스파크라인 차트 (Recharts AreaChart, 높이 60px)
- 하단: 전일 대비 % 변화 badge

**Small Card**:
- 크기: 1/6씩 5개
- 숫자 28px, 레이블 12px, 트렌드 배지

### C. 사이드바 (완전 재설계)

**기존 문제**: collapse/expand는 좋으나 비어있는 느낌.
**새 방향**: 사이드바 자체가 Mini Dashboard — 워크스페이스 상태, 알림 도트, 실시간 상태를 표시.

구조:
```
┌─────────────────────────────┐
│ [L] Lian Dash    [←]        │  ← 로고 + collapse 버튼
├─────────────────────────────┤
│ ▾ 클라이언트 A  ●           │  ← 워크스페이스 드롭다운 + 활성 도트
├─────────────────────────────┤
│                             │
│  ○  개요                    │  ← 아이콘 + 레이블
│  ●  GA4         ⚡ 신호     │  ← 활성 + 알림 도트 (이상 감지 시)
│  ○  메타                    │
│  ○  네이버SA                │
│  ○  AI 인사이트  3          │  ← 배지 숫자 (미확인 인사이트 수)
│                             │
├─────────────────────────────┤
│  ○  연동 설정               │
│  ○  계정/결제               │
├─────────────────────────────┤
│  [업그레이드] 에이전시 플랜  │  ← Upgrade CTA (gradient border)
│  [아바타] 홍길동             │
└─────────────────────────────┘
```

스타일:
- 너비: 240px (expanded) / 56px (collapsed)
- 배경: var(--bg-surface) — 베이스보다 살짝 밝게
- 좌측 액티브 인디케이터: 2px solid white bar (layoutId 유지)
- 알림 도트: 채널 컬러 (GA4 = 오렌지 dot, 메타 = 파랑 dot)

### D. 탑바 (신규 추가 — 기존에 없음)

기존 문제: 탑바 없음 → 페이지 제목/필터 영역이 모호함.
새 방향: 사이드바 제외 영역 상단 고정 48px 탑바 추가.

```
[페이지 제목]                    [날짜 필터] [채널 필터] [새로고침] [내보내기]
 GA4 분석                         오늘 ▾     전체 ▾       ↻          ↓
```

스타일:
- height: 48px, border-bottom: var(--border-subtle)
- background: var(--bg-base) — 메인 영역과 동일 (분리감 없이)
- 오른쪽: 필터 버튼들 (border + rounded-lg, 13px)
- Sticky (position: sticky, top: 0, z-index: 30)

### E. 차트 스타일 가이드

**공통 규칙:**
- 배경: transparent (카드 배경 그대로 사용)
- Grid: `stroke="rgba(255,255,255,0.05)"` strokeDasharray="4 4"
- Axis 텍스트: 11px, fill: var(--text-muted)
- Tooltip: `surface-elevated` + 그림자

**AreaChart (트렌드용)**:
- Area fill: 채널 컬러 + opacity 0.1 그라디언트 (상단 0.2 → 하단 0.0)
- Stroke: 채널 컬러, strokeWidth: 1.5
- Dot: 없음 (호버 시만 표시, r=3)

**BarChart (비교용)**:
- Bar fill: 채널 컬러 + opacity 0.7
- Hover: opacity 1.0, 상단 채널 컬러 glow
- Bar radius: [4,4,0,0]

**PieChart → Donut으로 교체**:
- innerRadius: 55%, outerRadius: 80%
- 중앙에 총합 또는 선택 채널 값 표시
- 각 조각 사이 gap: 2px, 배경색과 같은 색

---

## 랜딩페이지 설계 (/)

### 전체 흐름
```
[Nav] → [Hero] → [Social Proof Bar] → [Problem Section] → [Features Bento] → [Product Preview] → [Pricing] → [Final CTA] → [Footer]
```

### 1. Nav
- height: 56px, position: sticky, top: 0
- `glass-nav` 클래스 (기존 유지)
- 좌: 로고 (Zap 아이콘 + "Lian Dash")
- 중앙: 링크 없음 (랜딩은 Simple Nav)
- 우: "로그인" (ghost) + "무료 시작" (white filled, 높이 32px)

### 2. Hero Section (완전 재설계)

**기존 문제**: 3D 씬은 있는데 카피가 너무 설명적. CTA가 묻힘.

**새 레이아웃**: 중앙 정렬 Full-viewport Hero

```
[배경: 극단적 다크 + hero-bg 그라디언트]
[HeroScene 3D — 전체화면 배경으로 배치, z-index: 0]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
         [배지] GA4 · 메타 · 네이버SA 통합
         
    마케터의 모든 데이터,
    하나의 화면에서.
    
    GA4·메타·네이버SA를 실시간으로 통합하고
    GPT-4o가 오늘 할 일을 알려줍니다.
    
    [무료로 시작하기 →]    [데모 보기]
    
         ⌄ 스크롤
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

카피:
- 메인 헤드라인: 2줄, 72px, font-weight: 900, text-gradient-white 적용
- 서브카피: 18px, var(--text-secondary), max-width: 480px
- 배지: "GA4 · 메타 · 네이버SA 통합" — 작은 pill, border + 아이콘

CTA 버튼:
- Primary: 흰색 배경 + 검은 텍스트, height: 48px, px: 28px, border-radius: 10px, shimmer-btn 효과
- Secondary: 투명 + 흰 테두리, 동일 크기
- 두 버튼 사이 gap: 12px, 가로 나열

HeroScene 방향 (Three.js):
- 기존: 파티클 구체 → 신규: **데이터 플로우 비주얼**
- 3개 채널 컬러 파티클이 중앙 허브로 흘러들어오는 형태
- GA4(오렌지), 메타(파랑), 네이버(초록) 파티클 스트림
- 배경 배치 (z-index: 0), 텍스트 위에 반투명 오버레이 없이

### 3. Social Proof Bar

```
[신뢰 숫자들 가로 나열 — marquee 또는 정적]
마케터 1,200+ 사용 중  |  월 평균 4.7시간 절약  |  리포트 자동화 89%  |  ★★★★★ 4.9/5
```

- 높이: 56px, border-top + border-bottom: var(--border-faint)
- 아이템 사이: | 구분자, 15px 폰트, var(--text-secondary)
- 배경: var(--bg-surface) — hero와 미세하게 구분

### 4. Problem Section (신규)

**"매일 이런 짓 하고 계신가요?"**

3개 Pain Point 카드, 가로 나열:
```
[GA4 탭 열기]   →   [메타 탭 열기]   →   [네이버 탭 열기]
   30분 소요           20분 소요           15분 소요
   
   "하루 1.5시간을 데이터 복붙에 씁니다"
```

스타일:
- 각 카드: surface-card, 회색 아이콘, 빨간 "소요 시간" 배지
- 하단 합산 카피: 18px, 굵게, text-gradient-white
- 섹션 배경: var(--bg-base)

### 5. Features Bento Grid (기존 구조 유지 + 비주얼 강화)

**2x2 + 1 wide** 레이아웃:
```
[AI 인사이트 — wide 2/3]   [실시간 통합 — 1/3]
[한국 최초 네이버SA — 1/2]  [보안 워크스페이스 — 1/2]
```

각 카드 개선:
- 상단: 채널 컬러 토핑 라인 (기존 유지)
- 배경: hover 시 채널 컬러 tint (기존 유지)
- **신규**: 카드 내부에 실제 UI 미니어처 (스크린샷 캡처 이미지 또는 SVG mock)
  - AI 인사이트 카드 → 인사이트 카드 3개 미니어처
  - 채널 통합 카드 → 3채널 배지 + 라인차트 미니어처
- 카드 크기: 패딩 28px, min-height 200px

### 6. Product Preview Section (신규 — 핵심 섹션)

**"실제 화면 보여주기"** — 가장 설득력 있는 섹션

레이아웃: 좌우 분할
- 왼쪽 40%: 탭 리스트 (대시보드 / GA4 / 메타 / AI 인사이트)
  - 탭 클릭 시 오른쪽 프리뷰 교체
  - 활성 탭: 채널 컬러 왼쪽 bar
- 오른쪽 60%: 실제 앱 스크린샷 (browser mock frame 안에)
  - Framer Motion으로 탭 전환 시 fade+slide

구현 방식: 실제 `/dashboard` 화면 스크린샷 PNG를 `public/screenshots/` 폴더에 저장 후 `<Image>` 컴포넌트로 표시. 개발 완료 후 교체 가능.

### 7. Pricing Section (기존 구조 유지 + 개선)

3가지 플랜: Starter / Pro / Agency

**레이아웃**: 3열 카드
- 중앙 Pro 카드: gradient border (기존 pricing-popular 유지) + 크기 살짝 크게 (scale-up)
- 연간 결제 토글: 상단에 배치, "2개월 무료" 뱃지

각 카드:
- 플랜명: 18px bold
- 가격: 36px, Geist Mono
- 기간: /월 (14px, muted)
- 기능 목록: 체크 아이콘 + 13px 텍스트
- CTA 버튼: Starter = outline / Pro = white filled / Agency = outline

### 8. Final CTA

```
모든 채널을 하나로.
지금 바로 시작하세요.

[14일 무료 체험 시작 →]
신용카드 필요 없음 · 설치 불필요 · 5분 셋업
```

- 배경: 미세한 채널 컬러 그라디언트 radial (기존 hero-bg와 유사하게)
- 버튼: 가장 큰 CTA (height: 52px, px: 36px)

---

## 대시보드 설계 (/dashboard)

### 레이아웃 구조

```
┌──────────────────────────────────────────────────────────────┐
│ SIDEBAR (240px)  │  MAIN AREA                                │
│                  │ ┌────────────────────────────────────────┐│
│ [Logo]           │ │ TOPBAR (48px sticky)                   ││
│ [Workspace]      │ │ 개요           [오늘▾] [전체▾] [↻] [↓]││
│                  │ └────────────────────────────────────────┘│
│ ● 개요           │                                            │
│ ○ GA4      ⚡   │  ┌─────┐ ┌──┐ ┌──┐ ┌──┐ ┌──┐             │
│ ○ 메타           │  │ROAS │ │  │ │  │ │  │ │  │  KPI Row    │
│ ○ 네이버SA       │  │ BIG │ │  │ │  │ │  │ │  │             │
│ ○ AI 인사이트 3  │  └─────┘ └──┘ └──┘ └──┘ └──┘             │
│                  │                                            │
│ ─────────────── │  ┌─────────────────┐ ┌──────────────────┐ │
│ ○ 설정           │  │  채널 트렌드    │ │  채널 분배       │ │
│ ○ 계정           │  │  (AreaChart)    │ │  (Donut)         │ │
│                  │  └─────────────────┘ └──────────────────┘ │
│ [업그레이드]     │                                            │
│ [유저 아바타]    │  ┌────────────────────────────────────────┐│
└──────────────────┘  │  채널별 성과 테이블                    ││
                      └────────────────────────────────────────┘
```

### KPI Row 상세

- 총 너비: 100%, 6열 CSS Grid
- ROAS 카드 (col-span-2): Featured. 큰 숫자 + 스파크라인
- 나머지 5개 (col-span-1 each): 총 광고비 / 전환 / CPA / CTR / 총 클릭

각 Small KPI Card:
```
[채널 배지 dot]  광고비 총합
₩12,450,000
▲ 8.3%  vs 전일
```

- padding: 20px
- 숫자: 28px Geist Mono bold
- 변화율: trend-up/down 배지

### 차트 영역 (2열)

**왼쪽 — 채널 트렌드 (2/3 너비)**:
- ResponsiveContainer height: 280px
- 3개 채널 AreaChart 겹치기 (세미 투명)
- 범례: 상단 우측, 채널 배지 형태
- Y축 오른쪽 배치, X축 날짜

**오른쪽 — 채널 분배 (1/3 너비)**:
- DonutChart height: 280px
- 중앙 텍스트: "총 광고비" + 합산 금액
- 범례: 하단, 채널 컬러 + 금액 + %

### 채널 성과 테이블

5열: 채널 / 광고비 / 전환 / ROAS / CTR / 상태
- 채널 컬럼: 채널 배지 컴포넌트
- 숫자: Geist Mono, 오른쪽 정렬
- 상태: "정상" (초록) / "주의" (노랑) / "경고" (빨강) 배지
- 호버: 행 전체 배경 rgba(255,255,255,0.03)
- 클릭: 해당 채널 상세 페이지로 이동

---

## 각 화면 설계

### 화면 1: 랜딩페이지 (/)

**목적**: 방문자가 "이거 나한테 필요하다"를 5초 안에 느끼고 가입 클릭.

**CTA**: "무료로 시작하기 →" — Hero 중앙, 화이트 필드 버튼

**핵심 컴포넌트**:
- HeroScene (Three.js) — 데이터 플로우 파티클
- 헤드라인 텍스트 (text-gradient-white, 72px)
- Social Proof Bar (marquee or static)
- Bento Grid (4개 feature 카드)
- Product Preview (탭 + 스크린샷)
- Pricing 카드 (3열)

**전환 포인트**:
- Hero CTA (최우선)
- Pricing 섹션 각 플랜 CTA
- Final CTA 섹션
- Nav 우측 "무료 시작" 버튼 (항상 노출)

---

### 화면 2: 로그인 (/login)

**목적**: 기존 사용자 빠른 로그인. 마찰 최소화.

**레이아웃**: 좌우 분할 (50/50)
- 왼쪽: 앱 스크린샷 or 인포그래픽 (랜딩에서 온 사람에게 확인감)
- 오른쪽: 로그인 폼

**CTA**: "로그인" 버튼 — 흰색 filled

**폼 구성**:
```
Lian Dash 로고
"다시 돌아오셨군요"

[구글로 계속하기]  ← 최우선 배치 (소셜 로그인)
─── 또는 ───
이메일
비밀번호 (보기 토글)
[로그인]
비밀번호 찾기
회원가입 링크
```

**스타일 특징**:
- 폼 배경: surface-card (메인 배경보다 살짝 밝게)
- 소셜 로그인 버튼: 흰색 테두리 + 구글 로고 아이콘
- 입력필드: bg-subtle + border-subtle, focus 시 border-default

---

### 화면 3: 회원가입 (/signup)

**목적**: 최대한 빠르게 가입 완료. 이탈 방지.

**레이아웃**: 로그인과 동일 (좌우)

**폼 구성**:
```
"마케터를 위한 분석 도구 시작"

[구글로 가입하기]
─── 또는 ───
이름
이메일
비밀번호 (강도 인디케이터)
[무료 체험 시작 →]

"이미 계정이 있으신가요? 로그인"
"14일 무료 · 신용카드 불필요"  ← 불안 해소
```

**특이사항**:
- 비밀번호 강도 바: 4단계, 채널 컬러 계열로 (약=빨강, 강=초록)
- 동의 체크박스 제거 (간결함 우선, 약관은 링크로)

---

### 화면 4: 온보딩 (/onboarding)

**목적**: 가입 후 첫 워크스페이스 + 채널 연동 완료까지 안내. 이탈 방지.

**레이아웃**: 중앙 집중형 (사이드바 없음), 상단 진행 바

**진행 단계 (3스텝)**:
```
Step 1: 워크스페이스 설정
  - 워크스페이스 이름
  - 용도 선택 (자사 마케팅 / 프리랜서 클라이언트 관리)

Step 2: 첫 채널 연동
  - GA4 / 메타 / 네이버SA 3개 카드
  - 각 카드: 채널 로고 + 연동하기 버튼 + "나중에 설정" 작은 링크
  - 최소 1개 연동 시 다음 가능

Step 3: 완료
  - 연동된 채널 확인
  - "대시보드 보기" → /dashboard 이동
  - 애니메이션 (confetti or 파티클 burst)
```

**진행 바**:
- 상단 center: 3개 dot + 연결선
- 완료된 스텝: 흰색 solid dot
- 현재 스텝: 흰색 dot + pulsing ring
- 미완료: muted dot

**채널 연동 카드**:
- 크기: 160x160px (정사각형)
- 채널 로고 중앙 (48px)
- 채널 이름 하단
- 연동 완료 시: 초록 체크 오버레이 + 채널 컬러 border

---

### 화면 5: 메인 대시보드 (/dashboard)

상단 "대시보드 설계" 섹션 참고.

**추가 디테일**:
- 페이지 로드 시: KPI 카드 staggered fade-up (0.06s 간격)
- 숫자 표시: CountUp 애니메이션 (0에서 목표값까지, 1.2s)
- 빈 상태 (채널 미연동 시): 연동 안내 카드 + "/settings/integrations" CTA

---

### 화면 6: GA4 상세 (/dashboard/ga4)

**목적**: GA4 데이터 심층 분석. 트래픽 소스, 페이지별 성과, 전환 경로.

**레이아웃**:
```
[탑바] GA4 분석  [날짜 필터] [속성 선택▾]

[KPI Row 4개] — 세션 / 신규 사용자 / 전환율 / 평균 세션 시간
              — GA4 오렌지 컬러 테마

[2열]
  [세션 트렌드 — AreaChart, 7일/30일]  [트래픽 소스 — DonutChart]

[페이지 성과 테이블]
  URL / 페이지뷰 / 평균 체류 / 이탈율 / 전환 기여

[전환 퍼널 (선택적)]
  방문 → 제품 조회 → 장바구니 → 결제 → 완료
  (BarChart 수평)
```

**GA4 전용 컬러**: #E37400 오렌지 계열 액센트 사용

---

### 화면 7: 메타 상세 (/dashboard/meta)

**목적**: 메타 광고 캠페인 성과 모니터링. ROAS, CTR, CPC 최적화 포인트 파악.

**레이아웃**:
```
[탑바] 메타 광고  [날짜 필터] [캠페인 필터▾] [오브젝티브 필터▾]

[KPI Row 5개] — 총 광고비 / ROAS / CPC / CTR / 전환
              — 메타 블루 컬러 테마

[2열]
  [광고비 vs 전환 — BarChart 이중축]  [오디언스 분포 — 연령/성별 HorizontalBar]

[캠페인 테이블]
  캠페인명 / 상태 / 노출 / 클릭 / CTR / 광고비 / 전환 / ROAS
  - 상태 배지: 활성(초록) / 일시중지(노랑) / 종료(회색)
  - 행 클릭: 광고 세트 드릴다운
```

**메타 전용 컬러**: #1877F2 파랑 계열 액센트

---

### 화면 8: 네이버SA 상세 (/dashboard/naver)

**목적**: 네이버 검색광고 키워드 성과 분석. CTR 하락 알림, 입찰가 최적화 신호 파악.

**레이아웃**:
```
[탑바] 네이버SA  [날짜 필터] [캠페인 필터▾]

[KPI Row 5개] — 총 광고비 / 클릭수 / CTR / 평균 CPC / 전환
              — 네이버 그린 컬러 테마

[2열]
  [CTR 트렌드 — 기간별 AreaChart]  [키워드 점유 — HorizontalBarChart Top10]

[키워드 성과 테이블]
  키워드 / 입찰가 / 노출 / 클릭 / CTR / CPC / 전환 / 품질지수
  - 품질지수: 1~10 별 or 숫자 배지 (7이상=초록, 4~6=노랑, 3이하=빨강)
  - 알림 아이콘: CTR 전주 대비 20% 이상 하락 시 ⚠️ 아이콘

[⚡ 알림 패널] (오른쪽 사이드 or 하단)
  이상 감지된 키워드 목록
  "상위 3개 키워드 CPC 급등 — 입찰가 재검토 권장"
```

**네이버 전용 컬러**: #03C75A 그린 계열 액센트

---

### 화면 9: AI 인사이트 (/dashboard/insights)

**목적**: GPT-4o가 생성한 오늘의 액션 포인트 3개를 확인하고 실행.

**레이아웃**:
```
[탑바] AI 인사이트  [마지막 분석: 오늘 오전 9:00]  [새 분석 생성]

[Hero 인사이트 카드 — 오늘의 TOP 인사이트]
  ┌──────────────────────────────────────────────────┐
  │ ⚡ 긴급  메타 광고 ROAS 개선 기회                 │
  │ 지난 7일 대비 CPC 23% 상승. 광고 소재 교체 권장.  │
  │                                                  │
  │ 액션 포인트:                                     │
  │  ① 오래된 크리에이티브(7일 이상) 교체            │
  │  ② 고성과 오디언스 lookalike 확장               │
  │  ③ 저성과 키워드 CPC 상한 낮추기                │
  │                                                  │
  │ [GA4로 확인] [메타로 확인]          [완료 표시] │
  └──────────────────────────────────────────────────┘

[이전 인사이트 목록 — 최근 5개]
  각 항목: 날짜 / 우선순위 배지 / 제목 / 액션 완료 여부

[분석 생성 모달 — "새 분석 생성" 클릭 시]
  로딩 애니메이션 (Brain 아이콘 + 스피너)
  "GA4, 메타, 네이버SA 데이터를 분석 중..."
  완료 시 새 인사이트 카드 슬라이드인
```

**Hero 인사이트 카드 스타일**:
- 배경: 우선순위에 따라 — 긴급=빨강 dim / 주의=노랑 dim / 일반=muted dim
- 왼쪽 border: 4px solid 우선순위 컬러
- padding: 24px
- 액션 포인트: 번호 + 텍스트, 각 항목 구분선

**월 10회 제한 표시**:
- 우측 상단: "이번 달 7/10 사용" — 진행 바
- 10회 소진 시: 업그레이드 CTA 오버레이

---

### 화면 10: 연동 설정 (/settings/integrations)

**목적**: 채널 연동 현황 확인, 신규 연동 추가, 연동 상태 관리.

**레이아웃**:
```
[탑바] 연동 설정

[연동된 채널]
  ┌──────┐ ┌──────┐ ┌──────┐
  │ GA4  │ │ META │ │NAVER │
  │ ✅   │ │ ✅   │ │ 연동 │
  │ 연결됨│ │ 연결됨│ │ 필요 │
  └──────┘ └──────┘ └──────┘
  
  각 카드: 채널 로고 + 연결 상태 + 마지막 동기화 시간 + [설정] 버튼

[사용 가능한 연동]
  2차 릴리즈 예정:
  카카오모먼트 / 구글 애즈 / 유튜브 애널리틱스
  → "Coming Soon" 배지, 클릭 불가 (muted 스타일)

[연동 상태 로그]
  최근 동기화 내역 (시간 / 채널 / 상태 / 레코드 수)
```

**채널 연동 카드**:
- 크기: 200x160px
- 연결됨 = border: 채널 컬러 1px, 좌상단 초록 dot
- 미연동 = border: border-subtle, "연동하기" 버튼 (채널 컬러)
- Coming Soon = opacity: 0.5, "곧 출시" pill 배지

---

## 민준에게 구현 지시

### 0. 시작 전 필수 작업

```bash
# Geist 폰트 설치
npm install geist

# Pretendard 설치
npm install pretendard
```

`app/layout.tsx`에 폰트 적용:
```tsx
import { GeistSans } from 'geist/font/sans';
import { GeistMono } from 'geist/font/mono';
```

`globals.css` 상단에 Pretendard 추가:
```css
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/variable/pretendardvariable.css');
```

body 폰트 스택:
```css
font-family: 'Pretendard Variable', 'GeistSans', system-ui, sans-serif;
```

숫자/코드 전용:
```css
.font-mono { font-family: 'GeistMono', 'JetBrains Mono', monospace; }
```

---

### 1. globals.css 교체

기존 CSS Variables를 아래로 교체:
- `--bg-base: #050507` (기존 #07070a에서 더 어둡게)
- 보라색 accent 변수 제거
- 채널 dim/glow 변수 추가 (위 컬러 시스템 참고)
- `surface-card`, `surface-elevated`, `badge-ga4/meta/naver`, `trend-up/down` 클래스 추가
- HeroScene 배경 그라디언트 — 보라색 제거, 채널 3색으로 재구성:
  ```css
  .hero-bg {
    background:
      radial-gradient(ellipse 80% 60% at 20% 40%, rgba(227,116,0,0.07) 0%, transparent 60%),
      radial-gradient(ellipse 80% 60% at 80% 40%, rgba(24,119,242,0.07) 0%, transparent 60%),
      radial-gradient(ellipse 60% 40% at 50% 80%, rgba(3,199,90,0.05) 0%, transparent 50%),
      var(--bg-base);
  }
  ```

---

### 2. HeroScene.tsx (Three.js 재설계)

**기존**: 파티클 구체
**신규**: 채널 데이터 플로우

구현 방향:
```tsx
// 3개 채널 소스 포인트 (화면 모서리 방향)
// GA4 파티클 (오렌지): 좌상단에서 중앙으로
// 메타 파티클 (파랑): 우상단에서 중앙으로
// 네이버 파티클 (초록): 하단에서 중앙으로
// 중앙에서 merge 후 위로 상승 (흰색으로 변환)

// 파티클 수: 각 채널 150개 = 총 450개
// 이동 속도: 0.003~0.008 랜덤
// 크기: 0.5~1.5px 랜덤
// 투명도: 중앙 근처에서 0.8 → 멀어지면 0

// 중앙 허브: 흰색 작은 구체 (radius: 0.1, 은은한 glow)
```

성능 주의:
- `useFrame` 내에서 geometry 재생성 금지
- `BufferGeometry + Float32Array positions` 사전 할당
- `useMemo`로 초기 파티클 위치 계산

---

### 3. 사이드바 개선 포인트

파일: `app/dashboard/layout.tsx`

추가할 것:
```tsx
// 1. 알림 도트 — navItems에 alert 프로퍼티 추가
const navItems = [
  { href: "/dashboard/ga4", ..., alertColor: "#E37400", alertCount: 1 },
  { href: "/dashboard/insights", ..., badgeCount: 3 },
  // ...
];

// 2. 사이드바 하단 업그레이드 카드
// 기존 유지 + gradient border 애니메이션 추가 (pricing-popular 클래스)

// 3. 워크스페이스 드롭다운
// 기존 구조 유지, 스타일만 개선 (surface-elevated 배경)
```

---

### 4. 탑바 컴포넌트 (신규 생성)

파일: `app/dashboard/components/TopBar.tsx`

```tsx
interface TopBarProps {
  title: string;
  titleKo?: string;
  filters?: {
    dateFilter?: boolean;    // 날짜 필터
    channelFilter?: boolean; // 채널 필터
  };
  actions?: React.ReactNode; // 우측 커스텀 액션
}
```

스타일:
```tsx
<div className="sticky top-0 z-30 flex items-center justify-between px-6 h-12 border-b"
     style={{ 
       background: 'var(--bg-base)', 
       borderColor: 'var(--border-subtle)' 
     }}>
  <h1 className="text-sm font-semibold text-white">{title}</h1>
  <div className="flex items-center gap-2">
    {/* 날짜 필터, 채널 필터 버튼들 */}
    {actions}
  </div>
</div>
```

---

### 5. KPI 카드 리팩토링

파일: `app/dashboard/components/KpiCard.tsx`

**Big Card** (ROAS Featured):
```tsx
// 스파크라인은 Recharts AreaChart, height: 56px
// ResponsiveContainer width: "100%"
// Area: strokeWidth 1.5, 채널 컬러, fill 그라디언트
// Axis 숨김, Grid 숨김, Tooltip 숨김
```

**Small Card**:
```tsx
// 기존 구조 유지, 폰트만 Geist Mono로 변경
// CountUp 애니메이션: react-countup 또는 직접 구현
// trend 배지: trend-up/trend-down 클래스
```

Grid 레이아웃 (dashboard/page.tsx):
```tsx
<div className="grid grid-cols-8 gap-3">
  <div className="col-span-3"> <KpiCard type="big" .../> </div>
  <div className="col-span-1"> <KpiCard .../> </div>
  <div className="col-span-1"> <KpiCard .../> </div>
  <div className="col-span-1"> <KpiCard .../> </div>
  <div className="col-span-1"> <KpiCard .../> </div>
  <div className="col-span-1"> <KpiCard .../> </div>
</div>
```

---

### 6. Donut 차트 (PieChart 교체)

기존 PieChart를 Donut으로:
```tsx
<PieChart>
  <Pie
    data={pieData}
    cx="50%"
    cy="50%"
    innerRadius="55%"    // ← 이게 핵심
    outerRadius="80%"
    paddingAngle={2}
    dataKey="value"
  >
    {pieData.map((entry, index) => (
      <Cell key={index} fill={entry.color} stroke="transparent" />
    ))}
  </Pie>
</PieChart>
// 중앙 텍스트는 SVG <text> 또는 absolute div로 오버레이
```

---

### 7. 랜딩 페이지 구조 변경

파일: `app/page.tsx`

**추가 섹션 순서**:
1. Nav (기존 유지 + CTA 버튼 추가)
2. Hero (헤드라인 + 3D + CTA)
3. Social Proof Bar (신규 — marquee 컴포넌트)
4. Problem Section (신규 — 3개 pain point 카드)
5. Bento Features (기존 유지 + 내부 미니어처 이미지 추가)
6. Product Preview (신규 — 탭 + 스크린샷)
7. Pricing (기존 유지)
8. Final CTA (기존 유지 + 개선)
9. Footer (신규 — 간단한 링크)

**Problem Section 구현 힌트**:
```tsx
const pains = [
  { icon: Chrome, time: "30분", label: "GA4 데이터 확인", sub: "필터 세팅, 보고서 내보내기..." },
  { icon: BarChart2, time: "20분", label: "메타 성과 취합", sub: "캠페인별 엑셀 정리..." },
  { icon: Search, time: "15분", label: "네이버SA 분석", sub: "키워드별 수동 확인..." },
];
// 오른쪽 화살표로 연결, 합산: "매일 1.5시간 낭비"
```

---

### 8. 애니메이션 가이드

**페이지 진입**: 모든 섹션 IntersectionObserver + `animate={{ opacity:1, y:0 }}`
- initial: `{ opacity: 0, y: 24 }`
- transition: `{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }`

**스태거**: 카드 리스트는 `staggerChildren: 0.07`

**카드 호버**: `whileHover={{ y: -3 }}` + CSS box-shadow 트랜지션

**숫자 카운트업**:
```tsx
// useEffect + requestAnimationFrame 직접 구현 or react-countup
// duration: 1.2s, easing: easeOutCubic
// 트리거: InView 진입 시 시작
```

**탭 전환 (Product Preview)**:
```tsx
<AnimatePresence mode="wait">
  <motion.div
    key={activeTab}
    initial={{ opacity: 0, x: 12 }}
    animate={{ opacity: 1, x: 0 }}
    exit={{ opacity: 0, x: -12 }}
    transition={{ duration: 0.25 }}
  >
    {/* 스크린샷 이미지 */}
  </motion.div>
</AnimatePresence>
```

---

### 9. shadcn 컴포넌트 목록

이미 설치된 컴포넌트 외 추가 필요:
```bash
npx shadcn@latest add progress      # AI 인사이트 사용량 바
npx shadcn@latest add tabs          # Product Preview 탭
npx shadcn@latest add separator     # 구분선
npx shadcn@latest add skeleton      # 로딩 상태
npx shadcn@latest add scroll-area   # 스크롤 영역
npx shadcn@latest add command       # 빠른 검색 (선택)
```

---

### 10. 파일 구조 정리

```
src/app/
├── components/
│   └── HeroScene.tsx         ← Three.js (재설계)
├── dashboard/
│   ├── components/
│   │   ├── TopBar.tsx         ← 신규
│   │   ├── KpiCard.tsx        ← 리팩토링
│   │   ├── ChannelBadge.tsx   ← 신규 (공통 채널 배지)
│   │   ├── TrendBadge.tsx     ← 신규 (상승/하락 배지)
│   │   ├── DonutChart.tsx     ← 신규 (PieChart 래퍼)
│   │   └── InsightCard.tsx    ← insights 화면용
│   ├── layout.tsx             ← Sidebar 포함 (개선)
│   ├── page.tsx               ← 메인 대시보드
│   ├── ga4/page.tsx
│   ├── meta/page.tsx
│   ├── naver/page.tsx
│   └── insights/page.tsx
├── (auth)/
│   ├── login/page.tsx
│   └── signup/page.tsx
├── onboarding/page.tsx
├── settings/
│   ├── account/page.tsx
│   ├── billing/page.tsx
│   └── integrations/page.tsx
├── globals.css                ← 컬러 시스템 교체
├── layout.tsx                 ← 폰트 추가
└── page.tsx                   ← 랜딩 재설계
```

---

### 11. 우선순위 구현 순서

**Phase 1 (필수, 가장 먼저)**:
1. `globals.css` — 컬러 시스템 교체 (보라 제거, 채널 컬러 정비)
2. `layout.tsx` — 폰트 교체 (Geist + Pretendard)
3. `dashboard/layout.tsx` — 탑바 추가 + 사이드바 알림 도트
4. `dashboard/page.tsx` — KPI Big Card + Donut 교체

**Phase 2 (시각적 임팩트)**:
5. `page.tsx` — Problem Section + Product Preview 섹션 추가
6. `HeroScene.tsx` — 데이터 플로우 파티클로 교체
7. 채널 상세 페이지 탑바 통일

**Phase 3 (완성도)**:
8. 애니메이션 정비 (CountUp, InView 트리거)
9. 빈 상태 (Empty States) 구현
10. Skeleton 로딩 상태 추가

---

## 기술 제약 및 주의사항

1. **Three.js**: `@react-three/fiber v8` + `@react-three/drei v9` + **React 18** 조합. React 19 올리지 말 것.
2. **Recharts**: ResponsiveContainer 안에서만 동작. SSR 시 `dynamic import + ssr:false` 필수.
3. **Framer Motion**: `layoutId` 사용 시 같은 컴포넌트 트리 내에서만 동작.
4. **Pretendard**: CDN 방식 사용 시 FOUT 발생 가능. `font-display: swap` 적용.
5. **KPI 숫자 포맷**: 한국어 포맷 — `toLocaleString('ko-KR')`. 단위: ₩ (광고비), % (비율), x (ROAS)
