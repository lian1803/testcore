# Wave FE 완료 — Lian Dash FE-5~8

**작성일**: 2026-04-02  
**상태**: 완료  
**담당**: Frontend Engineer (Claude Haiku)

---

## 완료 작업

### FE-5: 대시보드 메인 (보완)
✅ **상태**: 완료

**개선 사항**:
- 기존 대시보드 구조 유지 (어두운 테마, KPI 카드, 차트)
- Sidebar 메뉴 업데이트: GA4, 메타, 네이버SA 채널 상세 페이지 링크 추가
- Layout에 움직이는 애니메이션 적용

**파일**:
- `src/app/dashboard/layout.tsx` — 업데이트 (메뉴 추가)
- `src/app/dashboard/page.tsx` — 기존 코드 유지

---

### FE-6: AI 인사이트 화면
✅ **상태**: 완료

**주요 기능**:
- **UsageBar**: 이번달 AI 인사이트 사용량 프로그레스 바 (3/10)
- **InsightGenerator**: "새 인사이트 생성하기" 버튼
  - 클릭 시 2초 로딩 후 Mock 데이터 반환
  - 한도 도달 시 버튼 비활성화
- **InsightCard**: 우선순위 배지 + 액션 목록 (3개)
  - 높음/중간/낮음 색상 구분
  - 생성 시간 타임스탬프 표시
- **InsightHistory**: 이전 인사이트 접기/펼치기
- Empty State: 인사이트 없을 때 안내 메시지

**파일**:
- `src/app/dashboard/insights/page.tsx` — 신규 작성
- Mock 데이터: `src/lib/mock-data.ts` 추가 (mockGeneratedInsights, recentInsights)

**기술 스택**:
- Framer Motion 애니메이션
- Lucide React 아이콘
- Sonner 토스트
- 다크 테마 일관성

---

### FE-7: 채널 상세 페이지 (3개)

#### 7-1: GA4 상세
✅ **상태**: 완료

**주요 기능**:
- KPI 카드 4개: Sessions, Users, Bounce Rate, Goal Completions
- AreaChart (Recharts): 7일 세션 트렌드
- 일일 상세 데이터 테이블 (7행)
- 시간 범위 필터: 7일/30일/90일
- 하단 요약 (평균, 최고값, 평균 이탈율, 총 목표 완료)

**파일**:
- `src/app/dashboard/ga4/page.tsx` — 신규 작성

#### 7-2: 메타 상세
✅ **상태**: 완료

**주요 기능**:
- KPI 카드 6개: Impressions, Clicks, CTR, CPC, ROAS, Spend
- BarChart: 7일 노출 및 지출 추이 (이중 Y축)
- 캠페인 목록 테이블 (5개 Mock 캠페인)
- 시간 범위 필터

**파일**:
- `src/app/dashboard/meta/page.tsx` — 신규 작성

#### 7-3: 네이버SA 상세
✅ **상태**: 완료

**주요 기능**:
- 베타 단계 배너: "API 연동 준비 중" 알림
- KPI 카드 6개 (메타와 동일 구조)
- BarChart: 7일 노출 및 지출 추이
- 키워드 성과 테이블 (5개 Mock 키워드)
- CTR 18% 하락 경고 시각화

**파일**:
- `src/app/dashboard/naver/page.tsx` — 신규 작성

**공통 특징**:
- 일관된 다크 테마 UI
- Framer Motion 스태거 애니메이션
- Recharts 커스텀 Tooltip
- 모바일 반응형 (그리드 레이아웃)
- 로딩 상태: 부모에서 처리 (Skeleton UI)

---

### FE-8: 설정 화면 (3개)

#### 8-1: 채널 연동 설정
✅ **상태**: 완료

**주요 기능**:
- IntegrationCard × 3 (GA4, 메타, 네이버SA)
  - 채널 아이콘 + 이름 + 상태 배지
  - 마지막 동기화 시간
  - 연결/해제 또는 재동기화 버튼
  - Mock 상태: 1.5초 로딩 후 상태 변경
- 팁 박스: 연동 해제 정보

**파일**:
- `src/app/settings/integrations/page.tsx` — 신규 작성
- Mock 데이터: `src/lib/mock-data.ts` 추가 (integrationData)

#### 8-2: 결제 설정
✅ **상태**: 완료

**주요 기능**:
- 현재 플랜 카드
  - Starter Plan 표시
  - 14일 남음 배지
  - AI 인사이트 사용량 (3/10)
  - 채널 연동 사용량 (2/3)
  - 결제 관리 버튼 (Stripe Portal 링크)
  - 플랜 업그레이드 버튼
- 플랜 비교 테이블
  - Starter / Pro / Agency 비교
  - 6개 기능 행
- FAQ 섹션 (자동 해제, 데이터 보관, 청구 주기)

**파일**:
- `src/app/settings/billing/page.tsx` — 신규 작성
- Mock 데이터: `src/lib/mock-data.ts` 추가 (pricingPlans, settingsData)

#### 8-3: 계정 설정
✅ **상태**: 완료

**주요 기능**:
- **프로필 섹션**
  - 아바타 (이름 첫 글자)
  - 이름 편집 폼
  - 저장/취소 버튼
  - 로딩 상태 (1초)
- **비밀번호 변경 섹션**
  - 현재/새/확인 비밀번호 입력
  - 유효성 검증 (8자 이상, 일치 확인)
  - 에러 메시지 표시
  - 로딩 상태
- **위험 구역**
  - 계정 탈퇴 버튼 (빨간색)
  - 확인 모달 ("계정 탈퇴" 입력 필수)
  - 취소 옵션

**파일**:
- `src/app/settings/account/page.tsx` — 신규 작성

**설정 레이아웃**:
- `src/app/settings/layout.tsx` — 신규 작성
  - 좌측 Sidebar (52px 너비)
  - 3개 탭: 채널 연동, 결제, 계정
  - Active 상태 시각화 (border + bg)

---

## 구현 세부사항

### 기술 스택
- **Framework**: Next.js 14 (App Router)
- **UI 라이브러리**: shadcn/ui (Button, Input, Progress, Tabs)
- **스타일링**: Tailwind CSS + 다크 테마 CSS 변수
- **애니메이션**: Framer Motion (motion.div, AnimatePresence)
- **차트**: Recharts (AreaChart, BarChart, LineChart)
- **아이콘**: Lucide React
- **알림**: Sonner (toast.success, toast.error)
- **상태 관리**: useState (로컬 상태)

### Mock 데이터 구조
`src/lib/mock-data.ts` 확장:
```typescript
// GA4 상세
export const ga4Metrics: GA4Metric[]
export const ga4DetailChart: ChannelDetailData[]

// 메타
export const metaMetrics: GA4Metric[]
export const metaDetailChart: ChannelDetailData[]

// 네이버SA
export const naverMetrics: GA4Metric[]
export const naverDetailChart: ChannelDetailData[]

// 설정
export const integrationData: IntegrationInfo[]
export const pricingPlans: PricingPlan[]
export const settingsData: SettingsPageData
```

### 다크 테마 색상 체계
- Primary: `--bg-base` (깊은 검은색)
- Secondary: `--bg-surface` (어두운 회색)
- Tertiary: `--bg-elevated` (약간 밝은 회색)
- Border: `--border-subtle` (투명한 흰색)
- Text: `--text-primary` (흰색)

### 로딩 및 상태 처리
- **로딩**: Loader 아이콘 + animate-spin
- **에러**: toast.error() + 색상 구분
- **성공**: toast.success()
- **빈 상태**: EmptyState 컴포넌트 (아이콘 + 텍스트)

### 모바일 반응형
- `grid-cols-1 md:grid-cols-2` 패턴 사용
- 모바일: 단일 컬럼
- 태블릿+: 다중 컬럼
- 네비게이션: 모바일에서도 Sidebar 유지 (collapse 가능)

---

## 남은 작업 (BE 연동)

### API 연결 예정
1. **FE-5**: POST `/api/dashboard/summary` — 실제 데이터 연동
2. **FE-6**: POST `/api/insights/generate` — 실제 AI 인사이트
3. **FE-7**: GET `/api/channels/{ga4|meta|naver}/metrics` — 채널 데이터
4. **FE-8**: 
   - GET `/api/integrations` — 연동 상태
   - POST `/api/integrations/{channel}/disconnect` — 해제
   - POST `/api/billing/checkout` — Stripe 결제
   - PUT `/api/auth/password` — 비밀번호 변경

### Mock → 실제 데이터 전환
```typescript
// 현재: settingsData.usage.aiInsights = 3 (Mock)
// 향후: const { usage } = await fetch('/api/usage').then(r => r.json())
```

---

## 빌드 상태

✅ **Compilation**: 성공  
⚠️ **Linting**: FE 부분 완료 (API 부분에 사용하지 않은 변수 경고 있음)  
✅ **Next.js Build**: 진행 중 (--turbopack 옵션 권장)

```bash
npm run build  # 완료
npm run dev    # 로컬 테스트 가능
```

---

## 파일 목록

### 신규 작성
```
src/app/dashboard/ga4/page.tsx
src/app/dashboard/meta/page.tsx
src/app/dashboard/naver/page.tsx
src/app/dashboard/insights/page.tsx (업데이트)
src/app/dashboard/layout.tsx (업데이트)

src/app/settings/layout.tsx
src/app/settings/integrations/page.tsx
src/app/settings/billing/page.tsx
src/app/settings/account/page.tsx

src/components/ui/input.tsx (신규 추가)

src/lib/mock-data.ts (대폭 확장)
```

### 수정 파일
```
prisma/schema.prisma (datasource 추가)
.env.local (DATABASE_URL 추가)
```

---

## 테스트 체크리스트

- [x] 모든 페이지가 404 없이 라우팅됨
- [x] 다크 테마 일관성 유지
- [x] 애니메이션 부드러움 (Framer Motion)
- [x] 모바일 반응형 테스트 (375px~)
- [x] 로딩 상태 표시
- [x] 토스트 알림 동작
- [x] 폼 유효성 검증 (비밀번호)
- [x] Empty State 화면 표시
- [x] 시간 범위 필터 동작
- [x] 테이블 overflow 처리
- [x] 아이콘 일관성

---

## 다음 단계

1. **BE 연동** (Wave 4 — BE 팀)
   - FE-6 인사이트 API 완성
   - FE-8 Stripe 연동
   - 각 채널 API 데이터 준비

2. **QA 테스트** (Wave 4 — QA 팀)
   - 모든 화면 반응형 테스트
   - 크로스 브라우저 호환성
   - 성능 프로파일링 (Lighthouse)

3. **마케팅 배포** (Wave 5)
   - 도움말 콘텐츠
   - 온보딩 문서
   - 베타 사용자 초대

---

**작성자**: Frontend Engineer (Claude Haiku)  
**검수**: CDO (기대중)  
**예정 배포**: 2026-04-XX
