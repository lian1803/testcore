# DESIGN.md — Lian Dash 디자인 시스템

작성일: 2026-04-02  
스타일: Hybrid (랜딩 3D / 앱 내부 Stitch)

---

## 디자인 철학

- **랜딩페이지 (`/`)**: 임팩트 우선. 3D 오브젝트와 다크 배경으로 "AI가 마케팅을 분석한다"는 인상 전달
- **앱 내부 (`/dashboard`, `/settings`, `/onboarding`)**: 데이터 가독성 우선. 깔끔한 Stitch 스타일 SaaS UI. 노이즈 제거, 정보 밀도 최적화

---

## 색상 시스템

### 랜딩페이지 (Dark)
```
배경 (Background):     #0A0A0F
보조 배경 (Surface):   #12121A
테두리 (Border):       #1E1E2E

포인트 1 (Purple):     #7C3AED
포인트 2 (Blue):       #2563EB
그라디언트:            linear-gradient(135deg, #7C3AED 0%, #2563EB 100%)

텍스트 주요:           #FFFFFF
텍스트 보조:           #94A3B8
텍스트 디밍:           #475569

성공/긍정:             #10B981
경고:                  #F59E0B
```

### 앱 내부 (Light / Stitch)
```
배경 (Background):     #F9FAFB
보조 배경 (Surface):   #FFFFFF
보더:                  #E5E7EB

사이드바 배경:         #111827
사이드바 텍스트:       #F9FAFB
사이드바 액티브:       #7C3AED (포인트 컬러 일관성)
사이드바 호버:         #1F2937

포인트 (Primary):      #7C3AED
포인트 호버:           #6D28D9
포인트 라이트:         #EDE9FE

텍스트 주요:           #111827
텍스트 보조:           #6B7280
텍스트 디밍:           #9CA3AF

성공:                  #10B981  (bg: #ECFDF5)
경고:                  #F59E0B  (bg: #FFFBEB)
에러:                  #EF4444  (bg: #FEF2F2)
차트 포인트:           #7C3AED
차트 보조:             #2563EB, #10B981, #F59E0B
```

---

## 타이포그래피

```
폰트 패밀리:
  - 한국어: Pretendard (Google Fonts fallback: Noto Sans KR)
  - 영문/숫자: Inter

랜딩페이지:
  Hero 타이틀:     72px / Bold / 라인하이트 1.1
  Sub 타이틀:      40px / SemiBold
  섹션 헤딩:       32px / SemiBold
  본문:            18px / Regular / 라인하이트 1.7

앱 내부:
  페이지 타이틀:   24px / SemiBold
  섹션 헤딩:       18px / SemiBold
  카드 타이틀:     14px / Medium
  수치 (KPI):      36px / Bold / tabular-nums
  수치 보조:       28px / SemiBold
  레이블:          12px / Medium / uppercase / letter-spacing 0.05em
  본문/설명:       14px / Regular
  캡션:            12px / Regular
```

---

## 랜딩페이지 3D 섹션 설계

### Hero 섹션
```
배경: #0A0A0F (풀스크린)
중앙: 3D 씬 (WebGL Canvas — Three.js)

3D 오브젝트 구성:
  1. 차트 큐브 (ChartCube)
     — 와이어프레임 정육면체 안에 막대 차트 형상
     — 머티리얼: MeshPhongMaterial, #7C3AED, 투명도 0.8
     — 애니메이션: 축 Y 기준 서서히 회전 (0.003 rad/frame)
     — 크기: 1.5 × 1.5 × 1.5, 중앙 좌상단 배치

  2. 데이터 구체 (DataSphere)
     — 구체 형태, 표면에 데이터 포인트 점들
     — 머티리얼: MeshStandardMaterial, #2563EB + emissive #1D4ED8
     — 애니메이션: 축 X/Y 복합 회전, Float (드라이 위아래 부유)
     — 크기: radius 1.0, 중앙 우하단 배치

  3. 숫자 파티클 시스템 (NumberParticles)
     — 500개 파티클, 각각 1~999 랜덤 숫자 텍스처
     — 색상: #7C3AED ~ #2563EB 그라디언트 랜덤
     — 애니메이션: 자체 공전 + 스크롤 시 흩날림

  4. 광원
     — AmbientLight: #FFFFFF, intensity 0.3
     — PointLight: #7C3AED, intensity 2.0, position (5, 5, 5)
     — PointLight: #2563EB, intensity 1.5, position (-5, -3, 3)

스크롤 반응:
  — ScrollControls (drei) 사용
  — 스크롤 0→1: 카메라 Z 15→30 (뒤로 물러남)
  — 파티클 opacity 1→0 (흩어져 사라짐)
  — 오브젝트 scale 1→0.5 + Y 위치 0→-5

CTA 오버레이 (HTML, 3D 위 absolute):
  타이틀:   "모든 마케팅 채널, 하나의 대시보드"
  부제:     "GA4·메타·네이버SA 데이터를 AI가 분석해 이번 주 개선점을 알려드립니다"
  버튼:     "무료로 시작하기" — 3D 오브젝트 사이로 빛나는 glow 효과
            배경: linear-gradient(135deg, #7C3AED, #2563EB)
            shadow: 0 0 40px rgba(124, 58, 237, 0.5)
            hover: shadow 강도 2배 + scale 1.02
```

### Feature 섹션
```
배경: #0A0A0F → #12121A 전환
레이아웃: 3열 그리드
카드 스타일:
  — border: 1px solid #1E1E2E
  — background: #12121A
  — hover: border-color #7C3AED + box-shadow 0 0 20px rgba(124,58,237,0.15)
  — 아이콘: 퍼플 그라디언트 원형 배경

피처 목록:
  1. GA4·메타·네이버SA 통합 — "7개 툴을 1개로"
  2. AI 자동 인사이트 — "이번 주 개선점 3가지 자동 생성"
  3. 워크스페이스 — "클라이언트별 데이터 완전 분리"
```

### Pricing 섹션
```
배경: #12121A
레이아웃: 2열 (Starter / Pro)
추천 카드 (Pro):
  — border: 2px solid #7C3AED
  — glow: box-shadow 0 0 30px rgba(124,58,237,0.2)
  — 뱃지: "인기" — #7C3AED 배경

스타터: ₩49,000/월 — 3채널, AI 10회/월, 단일 워크스페이스
프로: ₩99,000/월 — 5채널, AI 50회/월, 멀티 워크스페이스 (2차)
```

---

## 앱 내부 (Stitch 스타일)

### 레이아웃 구조
```
┌─────────────────────────────────────────┐
│ Sidebar (240px, #111827)                │
│  ┌───────────────────────────────────┐  │
│  │ Logo                              │  │
│  │ ─────────────────────             │  │
│  │ 대시보드           (NavItem)       │  │
│  │ AI 인사이트        (NavItem)       │  │
│  │ ─────────────────────             │  │
│  │ GA4               (NavItem)       │  │
│  │ 메타 광고          (NavItem)       │  │
│  │ 네이버SA           (NavItem)       │  │
│  │ ─────────────────────             │  │
│  │ 설정               (NavItem)       │  │
│  │                                   │  │
│  │ [하단] 워크스페이스 선택기          │  │
│  │        플랜 상태 뱃지              │  │
│  └───────────────────────────────────┘  │
│                                         │
│  Main Content (flex-1, #F9FAFB)         │
│  ┌─────────────────────────────────┐   │
│  │ Header: 페이지 타이틀 + 날짜범위  │   │
│  │ ────────────────────────────── │   │
│  │ Content Area                    │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

### 컴포넌트 스펙

#### Sidebar (사이드바)
```
width: 240px, fixed
background: #111827
padding: 24px 16px

NavItem:
  height: 40px, border-radius: 8px
  padding: 0 12px
  color: #9CA3AF → hover: #F9FAFB
  background: transparent → hover: #1F2937
  active: color #FFFFFF, background: rgba(124,58,237,0.15), 
          left-border: 3px solid #7C3AED

아이콘: 20px, Lucide React
```

#### MetricCard (KPI 카드)
```
background: #FFFFFF
border: 1px solid #E5E7EB
border-radius: 12px
padding: 20px 24px
shadow: 0 1px 3px rgba(0,0,0,0.06)

구조:
  [채널 아이콘 + 채널명]    [변화율 뱃지]
  [수치 — 36px Bold]
  [레이블 — 12px Gray]
  [스파크라인 — 40px 높이]

변화율 뱃지:
  상승: bg #ECFDF5, text #059669, "▲ 12.3%"
  하락: bg #FEF2F2, text #DC2626, "▼ 5.1%"
```

#### TrendChart (트렌드 차트)
```
Recharts LineChart + AreaChart 혼용
background: #FFFFFF, border-radius: 12px
padding: 24px

라인 색상:
  GA4:     #7C3AED (보라)
  메타:    #2563EB (파랑)
  네이버:  #10B981 (초록)

tooltip: 커스텀 — 배경 #111827, text #F9FAFB, border-radius 8px
grid: stroke #F3F4F6
```

#### InsightCard (AI 인사이트 카드)
```
background: linear-gradient(135deg, #EDE9FE 0%, #EFF6FF 100%)
border: 1px solid #DDD6FE
border-radius: 12px
padding: 20px 24px

상단: AI 스파크 아이콘 + "AI 인사이트" 레이블 + 생성 일시
본문: 인사이트 텍스트 (14px Regular)
하단: "개선 우선순위" 뱃지 3개 (High/Medium/Low)
```

#### ChannelTab (채널 탭)
```
shadcn Tabs 컴포넌트 기반
탭 바: border-bottom: 1px solid #E5E7EB
활성 탭: border-bottom: 2px solid #7C3AED, color #7C3AED
비활성: color #6B7280
```

---

## 화면별 컴포넌트 목록

### 랜딩페이지 (`/`)
| 컴포넌트 | 설명 |
|----------|------|
| `Hero3D` | Three.js 캔버스 + CTA 오버레이 전체 |
| `FloatingObject` | 개별 3D 오브젝트 (큐브/구체) |
| `ParticleField` | 숫자 파티클 시스템 |
| `FeatureCard` | 피처 섹션 카드 3개 |
| `PricingTable` | 스타터/프로 가격표 |
| `Footer` | 링크 + 저작권 |

### 대시보드 (`/dashboard`)
| 컴포넌트 | 설명 |
|----------|------|
| `Sidebar` | 좌측 고정 내비게이션 |
| `DateRangePicker` | 기간 선택 (7d/30d/custom) |
| `MetricCard` | KPI 수치 카드 (채널별) |
| `TrendChart` | 3채널 비교 라인 차트 |
| `ChannelTab` | 채널별 탭 전환 |
| `InsightCard` | 최신 AI 인사이트 미리보기 |
| `TrialBanner` | 14일 체험 D-Day 상단 배너 |

### AI 인사이트 (`/dashboard/insights`)
| 컴포넌트 | 설명 |
|----------|------|
| `InsightGenerator` | "인사이트 생성" 버튼 + 사용량 표시 (3/10) |
| `InsightCard` | 전체 인사이트 카드 |
| `InsightHistory` | 이전 인사이트 목록 |
| `UsageBar` | 월 사용량 프로그레스 바 |

### 온보딩 (`/onboarding`)
| 컴포넌트 | 설명 |
|----------|------|
| `StepProgress` | 3단계 진행 표시 (Step 1→2→3) |
| `IntegrationConnect` | 채널별 연동 카드 (Connect 버튼) |
| `SuccessAnimation` | 연동 완료 애니메이션 (Lottie 또는 CSS) |
| `SkipOnboarding` | "나중에 설정" 링크 |

### 설정 (`/settings/*`)
| 컴포넌트 | 설명 |
|----------|------|
| `IntegrationCard` | 채널 연동 상태 + 연결/해제 버튼 |
| `PlanCard` | 현재 플랜 + Stripe Portal 링크 |
| `AccountForm` | 이름/이메일 변경 폼 |

---

## 반응형 기준
```
Mobile:   320px~767px   — 사이드바 숨김 (햄버거 메뉴), 카드 1열
Tablet:   768px~1199px  — 사이드바 아이콘만 표시 (64px), 카드 2열
Desktop:  1200px+       — 사이드바 전체 표시 (240px), 카드 3~4열
```

---

## 접근성 기준
- 모든 인터랙티브 요소 키보드 접근 가능
- 색상 대비 WCAG AA 기준 (4.5:1 이상)
- 차트에 aria-label + 데이터 테이블 대안 제공
- 3D 캔버스에 `aria-hidden="true"` + 텍스트 대안 유지
