━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🖼️  Frontend Design — Lian Dash
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

작성일: 2026-04-02
기반 문서: DESIGN.md, wave_pm.md, wave_cto.md

---

## 라우팅 구조

```
src/app/
├── layout.tsx                      # 루트 레이아웃 (Pretendard 폰트, Provider)
├── page.tsx                        # 랜딩페이지 (3D 히어로 + 피처 + 프라이싱)
├── (auth)/
│   ├── layout.tsx                  # 인증 페이지 레이아웃
│   ├── signup/page.tsx             # 회원가입
│   └── login/page.tsx              # 로그인
├── (app)/
│   ├── layout.tsx                  # 앱 메인 레이아웃 (Sidebar + Header)
│   ├── dashboard/
│   │   ├── page.tsx                # 대시보드 메인 (KPI + 트렌드 차트)
│   │   ├── insights/page.tsx       # AI 인사이트
│   │   ├── ga4/page.tsx            # GA4 상세
│   │   ├── meta/page.tsx           # 메타 상세
│   │   └── naver/page.tsx          # 네이버SA 상세
│   ├── onboarding/page.tsx         # 온보딩 (3단계)
│   └── settings/
│       ├── layout.tsx              # 설정 페이지 레이아웃 (좌측 탭)
│       ├── integrations/page.tsx   # 채널 연동 설정
│       ├── billing/page.tsx        # 플랜/결제 설정
│       └── account/page.tsx        # 계정 설정
└── api/
    ├── auth/[...nextauth]/route.ts
    ├── integrations/*/route.ts
    ├── dashboard/*/route.ts
    ├── channels/*/route.ts
    ├── insights/*/route.ts
    ├── billing/*/route.ts
    ├── webhooks/stripe/route.ts
    └── admin/*/route.ts
```

---

## 색상 시스템 (DESIGN.md 기준)

### 랜딩페이지 (Dark)
- 배경: `#0A0A0F`
- 보조 배경: `#12121A`
- 테두리: `#1E1E2E`
- 포인트 1 (Purple): `#7C3AED`
- 포인트 2 (Blue): `#2563EB`
- 그라디언트: `linear-gradient(135deg, #7C3AED 0%, #2563EB 100%)`
- 텍스트 주요: `#FFFFFF`
- 텍스트 보조: `#94A3B8`

### 앱 내부 (Light / Stitch)
- 배경: `#F9FAFB`
- 보조 배경: `#FFFFFF`
- 테두리: `#E5E7EB`
- 사이드바 배경: `#111827`
- 사이드바 텍스트: `#F9FAFB`
- 포인트 (Primary): `#7C3AED`
- 텍스트 주요: `#111827`
- 성공: `#10B981`
- 경고: `#F59E0B`
- 에러: `#EF4444`

---

## 화면별 컴포넌트 설계

### FE-1. 랜딩페이지 (`/`)

**레이아웃**: 풀스크린, 다크 배경, 섹션별 스크롤

**주요 섹션**:
1. Hero3D 섹션 (풀스크린)
2. Feature 섹션 (3열 그리드)
3. Pricing 섹션 (2열 카드)
4. CTA 섹션
5. Footer

**3D 컴포넌트** (Three.js + @react-three/fiber):
- `Hero3D.tsx` — 전체 3D 씬, dynamic import + `{ ssr: false }`
- `FloatingObject.tsx` — 차트 큐브 + 데이터 구체
- `ParticleField.tsx` — 500개 숫자 파티클 시스템
- 광원: AmbientLight + PointLight × 2 (퍼플/블루)
- ScrollControls 연동: 스크롤 시 카메라 후퇴 + 파티클 opacity 페이드

**CTA 오버레이** (HTML absolute positioned):
- 타이틀: "모든 마케팅 채널, 하나의 대시보드" (72px Bold)
- 부제: "GA4·메타·네이버SA 데이터를 AI가 분석..." (18px Regular)
- 버튼: "무료로 시작하기" (Shimmer Button — Magic UI 또는 Glow 효과)

**shadcn/ui 컴포넌트**:
- Button (CTA 버튼)
- Card (Feature/Pricing 카드)

**커스텀 컴포넌트**:
- `Hero3D.tsx` — Three.js 캔버스 풀스크린
- `FloatingObject.tsx` — ChartCube, DataSphere
- `ParticleField.tsx` — 파티클 시스템
- `FeatureCard.tsx` — Feature 섹션 카드 (3개)
- `PricingTable.tsx` — Starter/Pro 카드
- `CTASection.tsx` — 최하단 "지금 시작" 섹션
- `Footer.tsx` — 서비스명, 링크

**인터랙션**:
- 3D 오브젝트 마우스 따라 천천히 회전
- 스크롤 시 카메라 후퇴 + 파티클 흩어짐
- 버튼 hover: scale(1.02) + glow 강도 2배
- Feature 카드 hover: 테두리 퍼플 색상 + box-shadow glow

**로딩 상태**: 랜딩 자동 로드 (3D 번들 지연 로드)

**빈 상태**: N/A

---

### FE-2. 회원가입/로그인 (`/(auth)/signup`, `/(auth)/login`)

**레이아웃**: 중앙 정렬 카드 (max-width: 400px)

**배경**: `#F9FAFB` (라이트 모드로 전환되는 포인트)

**shadcn/ui 컴포넌트**:
- Input (이메일, 비밀번호)
- Button (Submit)
- Checkbox (동의)
- Alert (에러 메시지)

**커스텀 컴포넌트**:
- `AuthForm.tsx` — 이메일 + 비밀번호 폼
  - Props: `type: 'signup' | 'login'`, `onSubmit`, `isLoading`
  - 이메일 유효성 검사 (실시간)
  - 에러 메시지 표시 (NextAuth 에러 코드 → 한국어)
- `SocialAuthButton.tsx` — "구글로 계속하기"
  - Google OAuth 트리거

**인터랙션**:
- 이메일 입력 시 실시간 유효성 검사 표시
- 구글 버튼 클릭 → Google OAuth 팝업
- Submit 버튼 → 로딩 스피너
- 성공 → `/onboarding` 또는 `/dashboard` 리다이렉트 (이미 채널 연동 여부)
- 실패 → 에러 메시지 표시 (e.g., "이미 가입된 이메일입니다", "비밀번호가 틀렸습니다")

**빈 상태**: N/A

**에러 상태**:
- 이메일 이미 존재
- 비밀번호 불일치
- 네트워크 오류

---

### FE-3. 온보딩 (`/(app)/onboarding`)

**레이아웃**: 중앙 정렬, 3단계 진행 바

**Step 1: 워크스페이스 설정**
- 이름 입력 필드
- "다음" 버튼

**Step 2: 채널 연동 선택**
- GA4 카드 (로고 + "연결" 버튼)
- 메타 카드 (로고 + "연결" 버튼)
- 네이버SA 카드 (로고 + "연결" 버튼 또는 "Mock" 배지)
- "나중에 설정" 스킵 링크

**Step 3: 완료 요약**
- 연동된 채널 확인 체크 목록
- "대시보드 시작" 버튼
- 성공 애니메이션 (파티클 이펙트 또는 confetti)

**shadcn/ui 컴포넌트**:
- Input (워크스페이스 이름)
- Button (진행/완료)
- Card (채널 카드)
- Badge (Mock 상태)

**커스텀 컴포넌트**:
- `StepProgress.tsx` — 3단계 진행 바
  - Props: `currentStep: 1|2|3`, `steps: [{label, completed}]`
- `WorkspaceForm.tsx` — 워크스페이스 이름 입력
- `IntegrationConnect.tsx` — 채널 카드 그리드
  - Props: `channel: 'GA4' | 'META' | 'NAVER'`, `status: 'connected' | 'pending' | 'mock'`, `onConnect`
- `SuccessAnimation.tsx` — 완료 애니메이션
  - Framer Motion staggerChildren 또는 Lottie

**인터랙션**:
- 각 단계 폼 유효성 검사 후 "다음" 활성화
- 채널 "연결" 버튼 → OAuth 팝업 또는 리다이렉트
- 연동 성공 → 채널 카드 체크 표시 + 상태 업데이트
- "다음" → Step 진행 (Step 1 → 2 → 3)
- Step 3 완료 → `/dashboard` 리다이렉트

**로딩 상태**: 채널 연동 중 "연결 중..." 스피너

**빈 상태**: "채널을 선택하지 않으면 나중에 설정할 수 있습니다" (선택사항)

---

### FE-4. 대시보드 메인 (`/(app)/dashboard`)

**레이아웃**: 2열 (사이드바 240px 고정 + 메인 콘텐츠 flex)

**사이드바** (240px, #111827):
- Logo + 서비스명
- 구분선
- NavItem × 5:
  - 🏠 대시보드
  - ✨ AI 인사이트
  - ─────
  - 📊 GA4
  - 📱 메타 광고
  - 🔍 네이버SA
  - ─────
  - ⚙️ 설정
- 하단:
  - Workspace Selector (dropdown)
  - Plan Badge ("Trial 7일 남음" 등)

**메인 콘텐츠**:
- TrialBanner: 상단 (14일 체험 D-Day 카운트다운, EXPIRED 시 결제 안내)
- DateRangePicker: "7일 | 30일 | 사용자 정의" (shadcn Popover + Calendar)
- MetricCard 그리드 (4~6개):
  - Sessions (GA4)
  - Impressions (메타 + 네이버)
  - Clicks (3채널 합계)
  - Conversions (GA4)
  - ROAS (메타)
  - Spend (메타 + 네이버)
  - 각 카드: 채널 아이콘 + 채널명 + 수치 + 변화율 뱃지 + 스파크라인
- TrendChart: Recharts LineChart (3채널 비교, 퍼플/파랑/초록)
- ChannelTab: GA4 / 메타 / 네이버SA 탭 전환

**shadcn/ui 컴포넌트**:
- Sidebar/Navigation
- Card (MetricCard)
- Tabs (ChannelTab)
- Popover + Calendar (DateRangePicker)
- Badge (변화율, Plan 상태)

**커스텀 컴포넌트**:
- `Sidebar.tsx` — 좌측 네비게이션 고정 바
  - Props: `currentPath`, `user`, `workspaces`, `planStatus`
  - NavItem hover: 배경색 #1F2937, 텍스트 밝음
  - Active: 좌측 테두리 3px 퍼플 + 배경 rgba(124,58,237,0.15)
- `MetricCard.tsx` — KPI 카드
  - Props: `channel`, `label`, `value`, `change`, `sparklineData`
  - 변화율: 상승(초록) / 하락(빨강) 뱃지
- `TrendChart.tsx` — Recharts LineChart
  - Props: `data`, `channels: ['GA4', 'META', 'NAVER']`, `dateRange`
  - 라인 색상: 퍼플/파랑/초록
  - Tooltip 커스텀 (배경 #111827, 텍스트 흰색)
- `ChannelTab.tsx` — shadcn Tabs 래퍼
- `TrialBanner.tsx` — 상단 배너
  - Props: `daysRemaining`, `planStatus`
  - EXPIRED 상태: "결제하기" 링크 → `/settings/billing`
- `DateRangePicker.tsx` — 기간 선택
  - Props: `selectedRange`, `onChange`

**인터랙션**:
- 날짜 범위 변경 → TanStack Query 리페칭 (5분 캐시)
- 채널 탭 전환 → 해당 채널 상세 데이터 표시
- MetricCard 클릭 → 채널 상세 페이지 이동
- Sidebar NavItem 클릭 → 해당 페이지 네비게이션

**로딩 상태**: Skeleton UI
- MetricCard Skeleton: 4~6개 회색 박스 (각 20px 높이)
- TrendChart Skeleton: 차트 영역 회색 박스

**빈 상태**: "채널을 연동해주세요" (한 개도 연동 안 된 경우)

**에러 상태**: "데이터를 불러올 수 없습니다. 다시 시도해주세요." + Retry 버튼

---

### FE-5. AI 인사이트 (`/(app)/dashboard/insights`)

**레이아웃**: 메인 + 사이드바 (대시보드와 동일)

**상단 섹션**:
- UsageBar: 진행 바 (e.g., "3/10 사용함")
- "인사이트 생성하기" 버튼 (Shimmer Button)
  - 10회 도달 시: 비활성화 + "Pro 플랜으로 업그레이드" 링크

**생성 상태 (버튼 클릭 후)**:
- 로딩 스피너: "AI가 데이터를 분석 중입니다..." (최대 10초)
- 완료 후: 새 InsightCard 맨 위에 추가

**현재 인사이트** (최신 1개):
- InsightCard:
  - 배경: linear-gradient(135deg, #EDE9FE 0%, #EFF6FF 100%)
  - 상단: ✨ 아이콘 + "AI 인사이트" + 생성 일시 (e.g., "2시간 전")
  - 본문: 개선점 텍스트 (예: "이번 주 GA4 전환율이 12% 하락했습니다. 메타 광고 CPC를 3% 낮추는 것을 추천합니다.")
  - 하단: 뱃지 3개 ("우선순위: 높음", "원인: CPC 상승", "액션: 입찰가 조정")

**히스토리 섹션**:
- InsightHistory: 이전 인사이트 목록 (최근 10개)
  - 각 항목: 생성 일시 + 요약 미리보기 (2줄) + 클릭하면 전문 표시

**shadcn/ui 컴포넌트**:
- Button (생성 버튼)
- Card (InsightCard)
- Badge (우선순위, 원인, 액션)
- Progress (UsageBar)

**커스텀 컴포넌트**:
- `InsightGenerator.tsx` — 생성 버튼 + 사용량 표시
  - Props: `usageCount`, `maxUsage`, `isGenerating`, `onGenerate`
- `InsightCard.tsx` — 인사이트 카드
  - Props: `insight: { title, description, priority, metric, createdAt }`, `isNew: boolean`
  - isNew 시 상단 강조 + 배경 밝음
- `InsightHistory.tsx` — 인사이트 목록
  - Props: `insights: InsightLog[]`
  - 각 항목 hover: 배경색 변화 + 확장 버튼
- `UsageBar.tsx` — 월 사용량 프로그레스 바
  - Props: `used`, `max`

**인터랙션**:
- "인사이트 생성하기" 클릭:
  - POST `/api/insights/generate` 호출
  - 로딩: 스피너 표시, 버튼 비활성화
  - 성공: 새 카드 추가, UsageBar 업데이트, 토스트 "인사이트가 생성되었습니다"
  - 실패: 토스트 "생성에 실패했습니다. 다시 시도해주세요."
- 10회 도달: 버튼 비활성화 + "Pro 플랜으로 업그레이드하세요" 링크

**로딩 상태**: 생성 버튼 → 스피너 "분석 중..."

**빈 상태**: "아직 인사이트가 없습니다. 생성해보세요"

---

### FE-6. GA4 상세 (`/(app)/dashboard/ga4`)

**레이아웃**: 메인 + 사이드바

**메인 콘텐츠**:
- MetricCard × 4 (우상단):
  - Sessions
  - Users
  - Bounce Rate
  - Goal Completions
- TrendChart: AreaChart (세션 추이, 7일/30일)
- DataTable: 날짜별 상세 데이터
  - 컬럼: 날짜, 세션, 사용자, 전환율, 목표 달성

**shadcn/ui 컴포넌트**:
- Card (MetricCard)
- Table (DataTable, shadcn Table)

**커스텀 컴포넌트**:
- `MetricCard.tsx` (재사용)
- `GADetailChart.tsx` — GA4 전용 차트
  - Props: `data: GaMetric[]`, `dateRange`

**인터랙션**:
- 날짜 범위 변경 → 데이터 갱신
- 테이블 정렬 (컬럼 헤더 클릭)

**로딩 상태**: Skeleton (MetricCard + 테이블)

**빈 상태**: "GA4를 연동해주세요"

**에러 상태**: "GA4 데이터를 불러올 수 없습니다"

**Error Boundary**: 이 화면만 에러 시 격리 (앱 전체 다운 방지)

---

### FE-7. 메타 상세 (`/(app)/dashboard/meta`)

**레이아웃**: 메인 + 사이드바

**메인 콘텐츠**:
- MetricCard × 6 (우상단):
  - Impressions
  - Clicks
  - CTR
  - CPC
  - ROAS
  - Spend
- BarChart: 캠페인별 ROAS 비교 (Recharts)
- DataTable: 캠페인별 성과 상세
  - 컬럼: 캠페인명, 노출, 클릭, CTR, CPC, ROAS, 지출

**shadcn/ui 컴포넌트**:
- Card (MetricCard)
- Table (DataTable)

**커스텀 컴포넌트**:
- `MetaDetailChart.tsx` — 메타 전용 BarChart

**인터랙션**:
- BarChart 바 클릭 → 해당 캠페인 상세 (테이블에서 하이라이트)

**로딩 상태**: Skeleton

**빈 상태**: "메타 광고를 연동해주세요"

**Error Boundary**: 활성화

---

### FE-8. 네이버SA 상세 (`/(app)/dashboard/naver`)

**동일 구조**: GA4, 메타와 동일

**메인 콘텐츠**:
- MetricCard × 5:
  - Impressions
  - Clicks
  - CTR
  - CPC
  - Conversions
- LineChart: 일일 추이
- DataTable: 키워드별 성과

**Mock 상태 배너**:
- 네이버SA가 Mock 상태인 경우: 상단에 배너 "데이터 연동을 준비 중입니다. 현재 샘플 데이터를 보고 있습니다."

**Error Boundary**: 활성화

---

### FE-9. 설정 — 연동 (`/(app)/settings/integrations`)

**레이아웃**: 좌측 탭 + 우측 콘텐츠 (shadcn Tabs)

**좌측 탭**:
- 연동 설정
- 결제 관리
- 계정 설정

**우측 콘텐츠**:
- IntegrationCard × 3:
  - GA4
  - 메타
  - 네이버SA
  - 각 카드: 채널 로고 + 상태 ("연결됨" / "연결 필요" / "오류") + 마지막 동기화 시각 + "연결" 또는 "해제" 버튼

**shadcn/ui 컴포넌트**:
- Card (IntegrationCard)
- Button (연결/해제)
- Badge (상태)
- Tabs (설정 탭)

**커스텀 컴포넌트**:
- `IntegrationCard.tsx` — 채널 카드
  - Props: `channel`, `status`, `lastSynced`, `onConnect`, `onDisconnect`
- `SettingsTabs.tsx` — 설정 탭 네비게이션

**인터랙션**:
- "연결" 버튼 → OAuth 팝업/리다이렉트
- "해제" 버튼 → 확인 다이얼로그 → DELETE `/api/integrations/{channel}/disconnect`
  - 성공: 토스트 "연동이 해제되었습니다", 카드 상태 업데이트
  - 실패: 토스트 "해제에 실패했습니다"

**로딩 상태**: 버튼 비활성화 + 스피너

**빈 상태**: N/A

---

### FE-10. 설정 — 결제 (`/(app)/settings/billing`)

**레이아웃**: 좌측 탭 + 우측 콘텐츠

**우측 콘텐츠**:
- 현재 플랜 카드:
  - 플랜명 ("Trial" 또는 "Pro")
  - 구독 상태 ("활성" / "체험 중" / "만료됨")
  - 갱신 날짜 또는 체험 만료 D-Day
  - "플랜 관리" 버튼 → Stripe Customer Portal 새창 열기
- 플랜 비교 테이블 (선택사항, 업그레이드 유도):
  - Starter: ₩49,000/월
  - Pro: ₩99,000/월
  - 각각 포함 사항 (채널 수, AI 횟수, 워크스페이스)

**shadcn/ui 컴포넌트**:
- Card (플랜 카드)
- Button (플랜 관리)
- Table (플랜 비교)
- Badge (플랜 상태)

**커스텀 컴포넌트**:
- `PlanCard.tsx` — 현재 플랜 표시
  - Props: `planStatus`, `renewalDate`, `onManage`
- `PlanComparison.tsx` — 플랜 비교 테이블

**인터랙션**:
- "플랜 관리" 버튼 → GET `/api/billing/portal` → Stripe Portal URL 받아 새창 열기
- 플랜 비교 테이블의 "업그레이드" 버튼 → Stripe Checkout 시작

**로딩 상태**: 버튼 로딩 스피너

---

### FE-11. 설정 — 계정 (`/(app)/settings/account`)

**레이아웃**: 좌측 탭 + 우측 콘텐츠

**우측 콘텐츠**:
- 프로필 섹션:
  - 이름 입력 필드
  - 이메일 (읽기 전용)
  - 저장 버튼
- 비밀번호 섹션 (이메일 가입자만):
  - 현재 비밀번호 입력
  - 새 비밀번호 입력
  - 확인 비밀번호 입력
  - 변경 버튼
- 위험 영역:
  - "계정 탈퇴" 버튼 → 확인 다이얼로그 → 계정 삭제

**shadcn/ui 컴포넌트**:
- Input (이름, 비밀번호)
- Button (저장, 변경, 탈퇴)
- AlertDialog (확인)

**커스텀 컴포넌트**:
- `AccountForm.tsx` — 이름 변경
  - Props: `user`, `onUpdate`
- `PasswordForm.tsx` — 비밀번호 변경
  - Props: `onUpdate`, `isEmailAuth`

**인터랙션**:
- 저장 버튼 → PATCH 요청 → 성공 토스트
- 비밀번호 변경 → PATCH 요청 → 성공 토스트
- 계정 탈퇴 → 확인 다이얼로그 → DELETE 요청 → `/login` 리다이렉트

---

## 공통 컴포넌트 목록

| 컴포넌트 | 위치 | 역할 | 주요 Props |
|----------|------|------|-----------|
| Button | shadcn/ui | 버튼 | variant, size, disabled, onClick, isLoading |
| Card | shadcn/ui | 카드 래퍼 | — |
| Input | shadcn/ui | 입력 필드 | type, placeholder, value, onChange, error |
| Table | shadcn/ui | 데이터 테이블 | columns, data, sorting, pagination |
| Tabs | shadcn/ui | 탭 전환 | defaultValue, onValueChange |
| Popover | shadcn/ui | 팝오버 | — |
| AlertDialog | shadcn/ui | 확인 다이얼로그 | open, onOpenChange, onConfirm |
| Badge | shadcn/ui | 뱃지/태그 | variant, children |
| Progress | shadcn/ui | 진행 바 | value, max |
| Skeleton | shadcn/ui | 로딩 스켈레톤 | className |
| Sidebar | shadcn/ui | 사이드바 | (또는 커스텀) |
| NavigationMenu | shadcn/ui | 네비게이션 메뉴 | (또는 커스텀) |
| Toast | sonner | 알림 메시지 | toast.success/error/loading |
| LineChart | Recharts | 라인 차트 | data, dataKey, stroke |
| AreaChart | Recharts | 면적 차트 | data, dataKey, fill |
| BarChart | Recharts | 막대 차트 | data, dataKey |
| Sidebar | 커스텀 | 좌측 고정 네비 | currentPath, user, planStatus |
| MetricCard | 커스텀 | KPI 카드 | channel, label, value, change, sparklineData |
| TrendChart | 커스텀 | 트렌드 차트 | data, channels, dateRange |
| Hero3D | 커스텀 | 3D 히어로 섹션 | (Three.js, dynamic import) |
| ParticleField | 커스텀 | 3D 파티클 | (Three.js) |
| InsightCard | 커스텀 | AI 인사이트 카드 | insight, isNew |
| IntegrationCard | 커스텀 | 채널 연동 카드 | channel, status, onConnect, onDisconnect |

---

## 상태 관리

| 상태 | 라이브러리 | Store명 | 내용 |
|------|-----------|---------|------|
| 인증 | NextAuth.js | useSession() | user, session, status |
| 대시보드 필터 | Zustand | useDashboardStore | dateRange, selectedChannels, setDateRange, setChannels |
| UI 상태 | Zustand | useUIStore | sidebarOpen, toastQueue, openDialog, closeDialog |
| 서버 데이터 | TanStack Query | useQuery | 대시보드 요약, 채널별 지표, 인사이트 히스토리 |

**주요 Query Keys**:
```typescript
// TanStack Query
['dashboard', 'summary', { workspaceId, dateRange }]
['channels', 'ga4', { workspaceId, startDate, endDate }]
['channels', 'meta', { workspaceId, startDate, endDate }]
['channels', 'naver', { workspaceId, startDate, endDate }]
['insights', 'history', { workspaceId }]
['integrations', { workspaceId }]
```

---

## Tailwind CSS 커스텀 설정

```typescript
// tailwind.config.ts
module.exports = {
  theme: {
    extend: {
      colors: {
        // 랜딩 다크
        'landing-bg': '#0A0A0F',
        'landing-surface': '#12121A',
        'landing-border': '#1E1E2E',
        // 포인트
        'primary': '#7C3AED',
        'primary-light': '#EDE9FE',
        'secondary': '#2563EB',
        // 앱 라이트
        'app-bg': '#F9FAFB',
        'app-surface': '#FFFFFF',
        'app-border': '#E5E7EB',
        'sidebar-dark': '#111827',
        'sidebar-hover': '#1F2937',
        // 상태
        'success': '#10B981',
        'success-light': '#ECFDF5',
        'warning': '#F59E0B',
        'warning-light': '#FFFBEB',
        'error': '#EF4444',
        'error-light': '#FEF2F2',
      },
      fontFamily: {
        sans: ['Pretendard', 'Noto Sans KR', 'system-ui', 'sans-serif'],
        mono: ['Fira Code', 'monospace'],
      },
      fontSize: {
        'hero-title': ['72px', { lineHeight: '1.1', fontWeight: '700' }],
        'hero-sub': ['40px', { lineHeight: '1.2', fontWeight: '600' }],
        'section-heading': ['32px', { lineHeight: '1.3', fontWeight: '600' }],
        'page-title': ['24px', { lineHeight: '1.4', fontWeight: '600' }],
        'card-title': ['14px', { lineHeight: '1.5', fontWeight: '500' }],
        'label': ['12px', { lineHeight: '1.5', fontWeight: '500', letterSpacing: '0.05em' }],
      },
      animation: {
        'float': 'float 3s ease-in-out infinite',
        'glow': 'glow 2s ease-in-out infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-20px)' },
        },
        glow: {
          '0%, 100%': { boxShadow: '0 0 20px rgba(124, 58, 237, 0.5)' },
          '50%': { boxShadow: '0 0 40px rgba(124, 58, 237, 0.8)' },
        },
      },
    },
  },
}
```

---

## 애니메이션 규칙

### 진입 애니메이션
```typescript
// Framer Motion
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.4, delay: 0.1 }}
/>
```

### Stagger (자식 순차 애니메이션)
```typescript
<motion.div
  variants={{
    container: {
      hidden: { opacity: 0 },
      show: {
        opacity: 1,
        transition: {
          staggerChildren: 0.1,
        },
      },
    },
    item: {
      hidden: { opacity: 0, y: 20 },
      show: { opacity: 1, y: 0 },
    },
  }}
  initial="hidden"
  animate="show"
>
  {items.map((item) => (
    <motion.div key={item.id} variants={variants.item}>
      {item.content}
    </motion.div>
  ))}
</motion.div>
```

### Hover 효과
```typescript
// 과하지 않게
<motion.div
  whileHover={{ scale: 1.02 }}
  whileTap={{ scale: 0.98 }}
  transition={{ duration: 0.2 }}
/>
```

### 로딩 스피너 (Framer Motion)
```typescript
<motion.div
  animate={{ rotate: 360 }}
  transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
/>
```

---

## 반응형 기준 (Tailwind Breakpoints)

| 구간 | 너비 | Tailwind | 레이아웃 |
|------|------|----------|----------|
| 모바일 | 320px ~ 767px | `sm` ~ `md` | 사이드바 숨김 (햄버거 메뉴), 카드 1열 |
| 태블릿 | 768px ~ 1199px | `md` ~ `lg` | 사이드바 아이콘만 표시 (64px), 카드 2열 |
| 데스크탑 | 1200px+ | `lg`+ | 사이드바 전체 표시 (240px), 카드 3~4열 |

---

## 모바일 터치 규칙

- 모든 터치 영역 최소 44x44px
- 버튼: `min-w-[44px] min-h-[44px]`
- 본문 텍스트: `text-base` (16px) 이상

---

## 접근성 기준

- **색상 대비**: WCAG AA 기준 (4.5:1 이상)
- **키보드 네비게이션**: 모든 버튼/입력 필드 `tab` 가능
- **Screen Reader**: Semantic HTML + `aria-label`, `aria-describedby` 필수
- **3D 캔버스**: `aria-hidden="true"` + 텍스트 대안 제공

---

## FE 구현 체크리스트

- [ ] 모든 버튼에 로딩 스피너 (disabled + spinner)
- [ ] 모든 데이터 목록에 빈 상태 UI
- [ ] 모든 fetch에 Skeleton 로딩
- [ ] 에러 메시지 사용자 친화적 (기술 용어 없음)
- [ ] 모바일 반응형 (375px 기준 확인)
- [ ] API 키 프론트 노출 없음 (서버사이드 처리)
- [ ] 첫 화면 LCP 3초 이내
- [ ] 3D 번들 dynamic import + `{ ssr: false }` (앱 번들 격리)
- [ ] Sidebar active 상태 시각적 명확 (퍼플 좌측 테두리)
- [ ] Trial 만료 D-Day 배너 상단 고정
- [ ] 10회 AI 제한 UI 명확 (버튼 비활성화 + 메시지)
- [ ] OAuth 팝업 handling (에러, 취소, 성공)
- [ ] Stripe Portal 새창 열기
- [ ] NextAuth 세션 자동 갱신 (JWT 전략)
- [ ] Mock 데이터 폴백 (네이버SA)

---

## Mock 데이터 파일 구조

```
src/lib/
├── mock-data.ts        # 모든 Mock 데이터 중앙 관리
└── channels/
    ├── ga4.mock.ts     # GA4 Mock
    ├── meta.mock.ts    # 메타 Mock
    └── naver.mock.ts   # 네이버SA Mock
```

**사용 방식**:
- 개발 시 `NEXT_PUBLIC_USE_MOCK=true` 환경변수로 제어
- 네이버SA는 API 연동 실패 시 자동 폴백

---

## 구현 우선순위 (FE-PM 기준)

1. **FE-1, FE-2**: 랜딩페이지 (의존성 없음, 병렬 가능)
2. **FE-3**: 인증 화면 (BE-2 완료 후)
3. **FE-4**: 온보딩 (BE-3 완료 후)
4. **FE-5**: 대시보드 메인 (BE-6, BE-8 완료 후)
5. **FE-6**: AI 인사이트 (BE-7 완료 후)
6. **FE-7, FE-8**: 채널 상세 (BE-3, BE-4, BE-5 완료 후)
7. **FE-9, FE-10, FE-11**: 설정 페이지 (BE 마무리 후)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
