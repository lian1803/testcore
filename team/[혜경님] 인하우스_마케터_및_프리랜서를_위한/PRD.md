# PRD — Lian Dash (인하우스 마케터·프리랜서용 통합 마케팅 대시보드)

## 프로젝트 유형
상용화 SaaS

## 한 줄 정의
GA4·메타·네이버SA 데이터를 한 화면에서 보고, AI가 "이번 주 뭘 고쳐야 하는지" 알려주는 툴

## 타겟
인하우스 마케터(중소기업 1~5인팀) + 프리랜서 마케터(월 3~10개 클라이언트)

---

## Must Have (MVP 1차)

| # | 기능 | 설명 |
|---|------|------|
| 1 | GA4 연동 | OAuth로 연결, 핵심 지표 자동 수집 |
| 2 | 메타(FB+IG) 연동 | 광고 성과 데이터 수집 |
| 3 | 네이버SA 연동 | 네이버 검색광고 데이터 수집 (Mock 폴백 허용) |
| 4 | 통합 대시보드 | 3채널 데이터 한 화면에서 비교 |
| 5 | AI 인사이트 | GPT-4o로 "이번 주 개선점 3가지" 자동 생성 (월 10회 제한) |
| 6 | Stripe 결제 | 14일 무료체험 → 결제 없으면 차단 |
| 7 | 회원가입/로그인 | NextAuth (이메일+구글) |
| 8 | 워크스페이스 | 단일 워크스페이스 (DB는 멀티 대비 설계) |

---

## 화면 목록

| 화면 | 경로 | 설명 |
|------|------|------|
| 랜딩페이지 | `/` | 3D 임팩트 랜딩. 타겟 Pain Point → 솔루션 → CTA |
| 회원가입 | `/signup` | 이메일 or 구글 가입 |
| 로그인 | `/login` | |
| 온보딩 | `/onboarding` | 첫 채널 연동 가이드 (3단계) |
| 대시보드 메인 | `/dashboard` | 3채널 통합 KPI 카드 + 트렌드 차트 |
| AI 인사이트 | `/dashboard/insights` | 이번 주 개선점 + 히스토리 |
| 채널 상세 — GA4 | `/dashboard/ga4` | GA4 전용 상세 지표 |
| 채널 상세 — 메타 | `/dashboard/meta` | 메타 광고 상세 |
| 채널 상세 — 네이버SA | `/dashboard/naver` | 네이버SA 상세 |
| 채널 연동 설정 | `/settings/integrations` | API 연결/해제 |
| 플랜/결제 | `/settings/billing` | Stripe 구독 관리 |
| 계정 설정 | `/settings/account` | |

---

## 디자인 스타일
**Hybrid** — 랜딩페이지(`/`)는 3D (Spline 감성, Three.js/React Three Fiber), 앱 내부(`/dashboard`, `/settings`)는 Stitch 스타일 깔끔한 SaaS UI

---

## KPI
- 14일 무료체험 → 유료 전환율 20% 이상
- 채널 연동 완료율 70% 이상 (온보딩에서 이탈 방지)
- AI 인사이트 월 사용량 제한 내 유지 (비용 통제)

---

## 기술 스택 (CLAUDE.md 기준)
- Frontend: Next.js 14 App Router + shadcn/ui + Tailwind
- 차트: Recharts
- 상태관리: Zustand + TanStack Query
- Backend: Next.js API Routes
- DB: PostgreSQL + Prisma
- 인증: NextAuth.js v5
- 결제: Stripe
- AI: OpenAI GPT-4o API
- 3D: Three.js + @react-three/fiber + @react-three/drei (랜딩만)
