# PM 계획 — LLM 비용 서킷브레이커 (llm-guard)

> **PM: 리안** | 작성일: 2026-04-08
> Week 1~4 MVP 개발 태스크 분해

---

## 핵심 비전 (Week 1~4)
**"AI 에이전트가 수만 달러 태우기 전에 한 줄 코드로 잡아서 끊는다"**

- Week 1: Python SDK 배포 + 예산 차단 작동
- Week 2: 랜딩 + 대시보드 기본 구조 배포
- Week 3: 베타 10명 온보딩 + 실시간 알림
- Week 4: Stripe 결제 + 첫 유료 전환

---

## 1. User Stories (핵심 5개)

| ID | As a... | I want to... | So that... | 우선순위 |
|----|---------|-------------|------------|---------|
| US-001 | Python 개발자 | `pip install llm-guard` 후 3줄로 OpenAI 에이전트 보호 | 루프 돌다 갑자기 $5000 청구 안 됨 | Must |
| US-002 | SaaS 사업가 | 대시보드에서 오늘 비용/월 예산%/남은 예산 5초 안에 파악 | 뭔가 이상할 때 즉시 발견 | Must |
| US-003 | 개발팀 리더 | Slack에서 예산 50%, 80%, 100% 도달 시 자동 알림 받기 | 팀에서 먼저 알고 차단 | Must |
| US-004 | 스타트업 CEO | 프로젝트별로 예산 분리 (프로덕션 $100, 테스트 $10) | 프로덕션과 테스트 폭주 분리 | Should |
| US-005 | 꼼꼼한 개발자 | API 키 여러 개 발급 + 권한별 (읽기/쓰기) 관리 | 팀 확대될 때 보안 유지 | Could |

---

## 2. FE 태스크 (우선순위 순)

### Week 1 MVP

| # | 태스크 | 컴포넌트/페이지 | 설명 | 우선순위 | 예상 공수 |
|---|--------|-----------------|------|---------|---------|
| FE-001 | 랜딩페이지 기본 구조 | `app/page.tsx` | Three.js Hero + 섹션 레이아웃 (mock 콘텐츠) | Must | 2일 |
| FE-002 | Three.js 파티클 애니메이션 | `components/landing/hero-scene.tsx` | 비용 폭주($72K) 파티클 + 차단 이펙트 5초 루프| Must | 2일 |
| FE-003 | 랜딩 섹션들 | `app/page.tsx` | Problem($82K사례) + Solution(코드비교) + Features(Bento) | Should | 1.5일 |
| FE-004 | 대시보드 레이아웃 | `app/dashboard/layout.tsx` | Sidebar(240px) + Header(56px) + Content area | Must | 0.5일 |
| FE-005 | KPI 카드 4개 | `components/dashboard/kpi-card.tsx` | Today Cost / Budget% / Blocked / Remaining (mock) | Must | 1일 |
| FE-006 | Realtime 비용 차트 | `components/dashboard/cost-chart.tsx` | Recharts LineChart + Supabase Realtime 구독 (mock 데이터) | Must | 1.5일 |
| FE-007 | 로그인 게이트 | `middleware.ts` + Supabase Auth | 미인증자 / → /auth/login 리다이렉트 | Must | 0.5일 |
| FE-008 | 대시보드 Empty State | `components/dashboard/empty-state.tsx` | API 키 없을 때 Shield + CTA "Add API Key" | Should | 0.5일 |

### Week 2~3

| # | 태스크 | 컴포넌트/페이지 | 설명 | 우선순위 | 예상 공수 |
|---|--------|-----------------|------|---------|---------|
| FE-009 | 프로젝트 관리 페이지 | `app/dashboard/projects/page.tsx` | 프로젝트 카드 + 예산 inlineEdit + New Project 모달 | Should | 1.5일 |
| FE-010 | 알림 설정 페이지 | `app/dashboard/alerts/page.tsx` | 임계값 토글(50%/80%/100%) + Slack 연결 + 테스트 버튼 | Should | 1일 |
| FE-011 | 가격 페이지 | `app/pricing/page.tsx` | Free/Pro/Team 카드 + 월/연간 토글 + FAQ | Could | 1일 |

---

## 3. BE 태스크 (우선순위 순)

### Week 1 MVP

| # | 태스크 | 엔드포인트 | 설명 | 우선순위 | 예상 공수 |
|---|--------|-----------|------|---------|---------|
| BE-001 | Supabase 스키마 생성 | DB 초기화 | users / projects / api_keys / usage_logs / budgets / alerts 테이블 + RLS 정책 | Must | 0.5일 |
| BE-002 | SDK 예산 체크 API | `POST /api/v1/sdk/check` | Pre-call 토큰 추정 → 누적 비용 + 예상 비용 > 예산 ? 차단 : 허용 | Must | 1.5일 |
| BE-003 | SDK 사용량 기록 API | `POST /api/v1/sdk/report` | 실제 호출 후 토큰/비용 Supabase 기록 (비동기) | Must | 1일 |
| BE-004 | 유저 가입/로그인 | `POST /api/auth/signup` `POST /api/auth/login` | Supabase Auth + JWT 발급 | Must | 0.5일 |
| BE-005 | API 키 발급 | `POST /api/dashboard/api-keys` | 키 생성 + bcrypt 해시 + `lg_` 프리픽스 | Must | 1일 |
| BE-006 | API 키 조회 | `GET /api/dashboard/api-keys` | 사용자 본인의 키 목록 (원본 미노출, 프리픽스만) | Should | 0.5일 |
| BE-007 | 프로젝트 생성 | `POST /api/dashboard/projects` | 프로젝트명 + 월예산 저장 | Should | 0.5일 |
| BE-008 | 실시간 비용 조회 | `GET /api/dashboard/cost-today` | 오늘 누적 비용 JSON (차트 폴링용) | Must | 0.5일 |

### Week 2~3

| # | 태스크 | 엔드포인트 | 설명 | 우선순위 | 예상 공수 |
|---|--------|-----------|------|---------|---------|
| BE-009 | 프로젝트 업데이트 | `PATCH /api/dashboard/projects/:id` | 예산 변경 + 리셋 날짜 변경 | Should | 0.5일 |
| BE-010 | Slack 웹훅 전송 | `POST /api/webhooks/send-slack` | 임계값 도달 시 Slack 메시지 발송 (비동기) | Should | 0.5일 |
| BE-011 | SendGrid 이메일 알림 | `POST /api/webhooks/send-email` | 차단 이벤트 발생 시 이메일 즉시 | Should | 0.5일 |
| BE-012 | Stripe Webhook | `POST /api/webhooks/stripe` | subscription 생성/업데이트 → 유저 plan 변경 | Could | 1일 |
| BE-013 | 대시보드 차트 데이터 | `GET /api/dashboard/chart-data` | 7일 일별 비용 (line chart용) | Should | 0.5일 |

---

## 4. Python SDK 태스크 (`llm-guard` PyPI 패키지)

### Week 1 MVP 핵심

| # | 모듈 | 설명 | 예상 공수 |
|---|------|------|---------|
| SDK-001 | `llm_guard/__init__.py` | 패키지 진입점 | 0.5일 |
| SDK-002 | `llm_guard/openai.py` | OpenAI 클래스 래퍼 (chat.completions.create 오버라이드) | 1.5일 |
| SDK-003 | `llm_guard/token_estimator.py` | tiktoken 기반 토큰 사전 추정 (OpenAI/Google) | 0.5일 |
| SDK-004 | `llm_guard/budget_checker.py` | 누적 비용 + 예상 비용 계산 → BudgetExceededError 발생 로직 | 1일 |
| SDK-005 | `llm_guard/loop_detector.py` | 동일 컨텍스트 N회 반복 감지 (request_hash 기반) | 0.5일 |
| SDK-006 | `llm_guard/http_client.py` | llm-guard 백엔드 API 호출 (check + report) | 0.5일 |
| SDK-007 | `llm_guard/anthropic.py` | Anthropic 클래스 래퍼 (Optional Week 3) | 1일 |
| SDK-008 | `llm_guard/google.py` | Google Gemini 클래스 래퍼 (Optional Week 3) | 1일 |
| SDK-009 | `setup.py` + `pyproject.toml` | PyPI 배포 설정 | 0.5일 |
| SDK-010 | `tests/test_openai.py` | 단위 테스트 (예산 차단, 루프 감지) | 1일 |

**Week 1 배포 기준:**
- `llm_guard.openai.OpenAI` 완전 작동
- `BudgetExceededError` + 루프 감지 + 비동기 리포팅 완성
- PyPI에 v0.1.0 배포

---

## 5. 개발 우선순위 (Week 1 MVP 핵심)

### Week 1 Go-Live 필수 (7일)

**병렬 트랙:**

#### Backend (Day 1~3)
1. BE-001: Supabase 스키마 + RLS (Day 1)
2. BE-002: SDK /check 엔드포인트 (Day 2)
3. BE-003: SDK /report 엔드포인트 (Day 2)
4. BE-004: 회원가입/로그인 (Day 3)
5. BE-008: 비용 조회 API (Day 3)

#### Python SDK (Day 1~4)
1. SDK-001~004: Core (OpenAI + Token 추정 + 예산 판단) (Day 1~2)
2. SDK-005~006: Loop detector + HTTP 클라이언트 (Day 3)
3. SDK-010: 테스트 (Day 4)
4. SDK-009: PyPI 배포 (Day 4)

#### Frontend (Day 2~5)
1. FE-001~002: 랜딩페이지 + Three.js Hero (Day 2~3)
2. FE-004~008: 대시보드 + KPI + 차트 + 로그인 (Day 4~5)

#### QA (Day 5~6)
1. SDK OpenAI 래퍼 실제 동작 테스트
2. 대시보드 로그인 → 차트 표시 E2E 테스트
3. 예산 초과 시 실제 차단 확인

#### 배포 (Day 7)
1. Vercel에 FE + API 배포
2. PyPI SDK 배포 완료
3. 랜딩 웨이팅리스트 폼 활성화

---

### Week 2~3 추가 (Should 기능)

| 순서 | 기능 | 주담당 | 예상 일정 |
|------|------|--------|---------|
| 1 | 프로젝트 CRUD (FE-009 + BE-009) | FE/BE | Day 8~9 |
| 2 | 알림 설정 + Slack 연동 (FE-010 + BE-010) | FE/BE | Day 10~11 |
| 3 | Anthropic/Google SDK (SDK-007~008) | SDK | Day 12~13 |
| 4 | 차트 데이터 API (BE-013) | BE | Day 14 |
| 5 | 베타 10명 온보딩 | 마케팅팀 | Week 2 말 |

---

### Week 4 (Could 기능 + 유료화)

| # | 기능 | 팀 | 예상 공수 |
|---|------|-----|---------|
| 1 | Stripe 결제 연동 (FE-011 가격 페이지 + BE-012 webhook) | FE/BE | 1.5일 |
| 2 | Pro 기능 게이트 (Slack 알림, loop detection) | FE/BE | 0.5일 |
| 3 | 첫 유료 고객 온보딩 (영업) | 마케팅팀 | 내부 |
| 4 | NPS 피드백 수집 | 마케팅팀 | 내부 |

---

## 6. 완료 기준 (Definition of Done)

### Week 1 MVP
- [ ] Python SDK `llm_guard` v0.1.0 PyPI 배포 완료
- [ ] OpenAI 래퍼 3줄 코드 사용 → 실제 예산 차단 작동 확인
- [ ] 랜딩페이지 배포 (www.llm-guard.com)
- [ ] 대시보드 로그인 + 기본 KPI 4개 표시 + mock 차트
- [ ] Slack 알림 (테스트 1회 이상) 작동 확인
- [ ] 웨이팅리스트 첫 가입자 도달

### Week 2
- [ ] 베타 사용자 5명 이상 실제 SDK 사용 시작
- [ ] 프로젝트별 예산 분리 작동 확인
- [ ] Supabase Realtime 차트 실시간 업데이트 (지연 < 5초)

### Week 3
- [ ] Anthropic/Google 래퍼 PyPI v0.2.0 배포
- [ ] 베타 사용자 10명 도달 + NPS 측정

### Week 4
- [ ] Stripe 결제 첫 전환 1명 ($49 Pro)
- [ ] 랜딩 웨이팅리스트 100명 도달

---

## 7. 기술 제약 & 의존성

| 제약 | 영향 | 대응 |
|------|------|------|
| Supabase Free: 500MB DB | 베타 10명 이상 확장 시 문제 | Pro로 업그레이드 ($5/월) |
| Upstash Redis Free: 1만 req/day | 일일 활성사용자 100명 시 부족 | 문제 발생 시 Pro 업그레이드 |
| OpenAI ToS (프록시 금지) | SDK 래퍼 방식 검증 필요 | 클라이언트 사이드 래퍼 = 프록시 아님 → 합법 확인 |
| Stripe Webhook 신뢰성 | 결제 후 plan 미변경 위험 | Webhook 재시도 + 대시보드 수동 확인 (Week 4) |

---

## 8. 리스크 & 완화 전략

| 리스크 | 심각도 | 완화책 |
|--------|--------|--------|
| 토큰 카운팅 부정확 (예: 실제 $10.20 vs 추정 $9.80) | 중 | 오버 추정(±10%) + 이후 reconciliation 자동화 |
| SDK 호환성 문제 (OpenAI/Anthropic API 변경) | 중 | 2주마다 주요 라이브러리 버전 테스트 |
| Supabase 인증 토큰 탈취 | 높 | HTTPS 강제 + CSP 헤더 + refresh token 15분 |
| 경쟁사 빠른 모방 | 낮 | SDK 무료/오픈소스 vs 유료 SaaS 구분. 대시보드 UX 차별화 |

---

## 9. 마케팅 태스크 (병렬)

| 태스크 | 담당 | 예상 공수 | 완료 시점 |
|--------|------|---------|---------|
| 랜딩 카피 다듬기 + 사고사례 확보 | 마케팅팀 | 1일 | Week 1 말 |
| 웨이팅리스트 폼 → Discord/이메일 자동화 | 개발팀 | 0.5일 | Week 1 말 |
| 베타 사용자 리크루팅 (HN/Reddit/Twitter) | 마케팅팀 | 2일 | Week 2 초 |
| SDK 설치 가이드 작성 | 기술 라이터 | 1일 | Week 2 |
| 블로그 1호: "$72K 참사 어떻게 막았나" | 마케팅팀 | 1일 | Week 3 |

---

## 10. 성공 지표 (OKR)

### Week 1 (Go-Live)
- **O**: 안정적인 SDK + 대시보드 배포
- **KR1**: PyPI 다운로드 수 (관계없음, 시간 확인용) ≥ 1회
- **KR2**: 랜딩 웨이팅리스트 ≥ 10명

### Week 2~3 (베타)
- **O**: 실제 사용자가 SDK로 보호받기 시작
- **KR1**: 베타 가입자 ≥ 10명
- **KR2**: 실제 차단 이벤트 ≥ 1건 (누군가 루프 또는 예산 초과)
- **KR3**: NPS ≥ 40 (베타 사용자 설문)

### Week 4 (유료화)
- **O**: 첫 수익 창출
- **KR1**: 유료 전환자 ≥ 1명 ($49 Pro)
- **KR2**: 웨이팅리스트 ≥ 100명
- **KR3**: SDK Star ≥ 10 (GitHub, 있다면)

---

## 11. 리소스 배분

| 역할 | 담당자 | Week 1 | Week 2~3 | Week 4 |
|------|--------|--------|---------|--------|
| **BE Lead** | - | 풀타임 (API 3개 + Supabase) | 알림+Stripe | Stripe |
| **FE Lead** | - | 풀타임 (랜딩+대시보드) | 관리 페이지 | 가격 페이지 |
| **SDK Lead** | - | 풀타임 (OpenAI 래퍼) | Anthropic/Google | 유지보수 |
| **QA Lead** | - | 파트타임 (Day 5~6) | 풀타임 (통합테스트) | 회귀테스트 |
| **마케팅** | - | 웨이팅리스트 | 베타 리크루팅 | 유료화 |

---

**Document Status: READY FOR DEVELOPMENT**
생성일: 2026-04-08 | PM: 리안 | 다음 단계: Wave 3 FE/BE/SDK 에이전트 스폰
