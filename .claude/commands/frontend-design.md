# /frontend-design — 컴포넌트 구조 + 레이아웃 설계

이 명령어가 실행되면 아래를 즉시 수행해라. 질문하지 마라.

---

## 입력 파악

현재 프로젝트 폴더에서 다음을 읽어라:
1. `wave1_cdo.md` — 화면 설계 스펙 (화면별 목적, CTA, 주요 요소)
2. `wave1_brand.md` — 브랜드 가이드라인 (컬러, 폰트, 컴포넌트 규칙)
3. `wave1_theme.md` — 테마 시스템 (Tailwind 설정값)
4. `wave2_pm_계획.md` (있으면) — PM 태스크 목록, 화면 우선순위

---

## 출력: 컴포넌트 구조 + 레이아웃

아래 형식으로 FE 구현 청사진을 출력해라.

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🖼️  Frontend Design — [프로젝트명]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 라우팅 구조

```
src/app/
├── layout.tsx              # 루트 레이아웃 (폰트, Provider)
├── page.tsx                # 랜딩 페이지
├── (auth)/
│   ├── login/page.tsx
│   └── register/page.tsx
├── (dashboard)/
│   ├── layout.tsx          # 사이드바 + 헤더
│   └── [각 화면]/page.tsx
└── api/                    # API routes (필요시)
```

## 화면별 컴포넌트 설계

### [화면명 1]
**레이아웃**: [2열 / 풀스크린 / 카드 그리드 등]
**Aceternity UI 컴포넌트**: [Hero Highlight / Spotlight / Bento Grid 등 — 해당 없으면 생략]
**Magic UI 컴포넌트**: [Shimmer Button / Animated Gradient Text / Number Ticker 등 — 해당 없으면 생략]
**shadcn/ui 컴포넌트**: [Button / Card / Input / Dialog 등]
**커스텀 컴포넌트**:
- `[컴포넌트명].tsx` — [역할]
- `[컴포넌트명].tsx` — [역할]

**인터랙션**:
- [액션] → [반응] (예: 버튼 클릭 → 로딩 스피너 → 성공 토스트)
- 빈 상태: [화면]
- 로딩 상태: [Skeleton 구조]
- 에러 상태: [메시지]

### [화면명 2]
...

## 공통 컴포넌트 목록

| 컴포넌트 | 위치 | 역할 | Props |
|----------|------|------|-------|
| [이름] | components/ui/ | [역할] | [주요 props] |
| [이름] | components/[기능]/ | [역할] | [주요 props] |

## 상태 관리

| 상태 | 라이브러리 | Store명 | 내용 |
|------|-----------|---------|------|
| 인증 | Zustand | useAuthStore | user, token, login(), logout() |
| [기능] | Zustand | use[기능]Store | [상태 항목] |
| 서버 데이터 | TanStack Query | - | [캐시 전략] |

## Aceternity UI 설치 및 사용법

```bash
npm install framer-motion clsx tailwind-merge
```

컴포넌트별 복사 위치: `src/components/ui/aceternity/`
소스: https://ui.aceternity.com/components — 각 컴포넌트 페이지에서 코드 복사

주요 컴포넌트 사용 화면:
- Hero Highlight: 랜딩 페이지 히어로 섹션
- Spotlight: 랜딩/온보딩 배경 효과
- Bento Grid: 기능 소개 섹션
- Card Hover Effect: 카드 리스트
- Tracing Beam: 스크롤 가이드
- Animated Tooltip: 아이콘 버튼 툴팁

## Magic UI 사용법

소스: https://magicui.design/docs — 각 컴포넌트 페이지에서 코드 복사
복사 위치: `src/components/ui/magic/`

주요 컴포넌트 사용 화면:
- Shimmer Button: CTA 버튼 (랜딩, 가입)
- Animated Gradient Text: 히어로 제목 강조
- Number Ticker: KPI 숫자 카운트업
- Border Beam: 카드 강조 효과
- Shine Border: 프리미엄 카드 테두리

## 애니메이션 규칙

- 진입 애니메이션: `framer-motion` animate={{ opacity: 1, y: 0 }} initial={{ opacity: 0, y: 20 }}
- 지연: 각 요소 0.1s 간격 staggerChildren
- hover: scale(1.02) 또는 brightness 변화 — 과하지 않게
- 페이지 전환: opacity fade 300ms
- CSS animation 최소화 — framer-motion 우선

## FE 구현 체크리스트

- [ ] 모든 버튼에 로딩 스피너 (disabled + spinner)
- [ ] 모든 데이터 목록에 빈 상태 UI
- [ ] 모든 fetch에 Skeleton 로딩
- [ ] 에러 메시지 사용자 친화적 (기술 용어 없음)
- [ ] 모바일 반응형 (375px 기준 확인)
- [ ] API 키 프론트 노출 없음 (서버사이드로 처리)
- [ ] 첫 화면 LCP 3초 이내

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

결과를 `wave3_frontend_design.md`에 저장해라.
FE 에이전트는 이 파일 기반으로 실제 코드를 작성해라.
