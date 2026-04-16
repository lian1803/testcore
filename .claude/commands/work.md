---
name: work
description: PRD.md + CLAUDE.md 읽고 Wave 3~6 자동 실행 (기획은 이미 완료됨)
---

# /work — UltraProduct 자동 실행

## 자동 실행 규칙

이 명령어의 모든 단계는 자동으로 진행한다.
리안 컨펌이 필요한 단계는 **딱 2개뿐**:

1. ⛔ Wave 3 설계 완료 후 (CTO+CDO+PM 결과 확인) → "진행해" 필요
2. ⛔ Wave 6 배포 전 → "배포해" 필요

나머지 모든 컨펌 요청:
- 디자인 전략 → 자동 결정값 그대로 진행
- 마케팅 사전 준비 → "나중에"로 자동 스킵 (배포 후 Wave 6.5에서 처리)
- Wave 3.5 DevOps → 자동 설치
- Wave 4 완료 후 → 자동으로 Wave 5 진행
- Wave 6.5 마케팅 → 자동 실행 후 결과만 보고사항들.md에 저장

---

이 명령어가 실행되면 아래를 즉시 수행해라. 질문하지 마라.

---

## Step 0: 컨텍스트 파악

**반드시 이 순서로 읽어라:**
1. `CLAUDE.md` — 프로젝트 배경, 이사팀 분석 요약, 실행 지시
2. `PRD.md` — 지훈이 작성한 PRD (Must Have, User Flow, 화면 목록, KPI)

파악할 것:
- **프로젝트 유형**: `상용화` → Wave 3~6 전부 / `개인 툴` → Wave 3~4 + Wave 6 (Wave 5 스킵)
- **Must Have 기능** (PRD.md에서)
- **화면 목록** (PRD.md에서)
- **기술 스택**: CLAUDE.md에 명시된 거 사용. 없으면 CTO가 결정.

⚠️ Wave 1~2 기획은 이미 완료됨. CPO/PM Agent 스폰 금지. Wave 3부터 시작.

---

## Step 1: 디자인 전략 자동 결정 + 레퍼런스 수집

CDO 부르기 전에, 디자인 라우터와 레퍼런스 분석기를 자동 실행해라.

**1-1. 디자인 라우터 실행:**
```python
import sys, os
_ROOT = os.popen("git rev-parse --show-toplevel").read().strip()
sys.path.insert(0, os.path.join(_ROOT, "company"))
os.chdir(os.path.join(_ROOT, "company"))
from dotenv import load_dotenv; load_dotenv()

from core.design_router import route
# PRD.md + CLAUDE.md에서 읽은 프로젝트 설명을 넣어라
design_plan = route("[PRD에서 읽은 프로젝트 설명 + 타겟 + 목적]")
```

**1-2. 레퍼런스 분석기 실행:**
```python
from core.reference_analyzer import analyze
refs = analyze("[프로젝트 설명]", design_plan)
```

**1-3. 결과를 리안에게 보여줘라:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
디자인 전략 (자동 분석)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

사이트 타입: [design_plan.site_type]
3D 레벨: [design_plan.3d_level]
스타일: [design_plan.style_family]

Stitch 담당: [design_plan.stitch_scope]
3D 담당: [design_plan.3d_scope]

참고 DESIGN.md: [refs.design_md_references]
참고 컴포넌트: [refs.component_references]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

자동 결정값 그대로 CDO에 전달. 컨펌 불필요.

**1-4. 3D 프로젝트면 SCENE.md 생성:**
`design_plan.3d_level`이 `none`이 아니면 → `templates/SCENE.md`를 복사해서 프로젝트 폴더에 `SCENE.md` 생성하고, design_plan 값으로 기본값 채워라.

---

## Wave 2.5: 마케팅 병렬 시작 (개발 전 즉시)

**개발 시작 전에 마케팅팀을 먼저 깨워라.** 개발하는 동안 콘텐츠 미리 쌓는다.

```
marketing_config.json에 이 프로젝트 설정이 있으면 → 팀 바로 활성화
없으면 → launch_prep.md 또는 PRD.md 읽고 plan_from_brief() 실행
```

**Agent — 마케팅 사전 준비 (Haiku, 백그라운드):**
`PRD.md`, `CLAUDE.md`, `launch_prep.md` (있으면)를 읽고:

```python
import sys, os
_ROOT = os.popen("git rev-parse --show-toplevel").read().strip()
sys.path.insert(0, os.path.join(_ROOT, "company"))
os.chdir(os.path.join(_ROOT, "company"))
from dotenv import load_dotenv; load_dotenv()
import anthropic
client = anthropic.Anthropic()

from core.marketing_planner import plan_from_brief, activate_teams, print_confirmation_prompt

# PRD에서 읽은 내용으로 context 구성
context = {
    "idea": "[PRD.md에서 읽은 프로젝트 설명]",
    "strategy": "[PRD.md에서 읽은 타겟/전략]",
}
plan = plan_from_brief(context, "[프로젝트명]", client)
print(print_confirmation_prompt("[프로젝트명]", plan))
```

마케팅 사전 준비는 자동 스킵 (배포 후 Wave 6.5에서 처리). 결과만 보고사항들.md에 저장.

---

## Wave 3 시작 전: Domain Architect → CTO + CDO 설계

### Wave 3-0: Domain Architect (CTO+CDO 전에 먼저 실행)

**Agent — Domain Architect (Sonnet):**
`PRD.md`를 읽고 `agents/domain-architect.md`의 10가지 규칙에 따라 `wave_domain.md`를 생성해라.
완료 기준: 엔티티 3~7개 / 유스케이스 5개 이상 / 워크 서피스 3개 이상 / 비즈니스 룰 3개 이상 / VERSION 블록 존재.

**Domain Architect 완료 확인 후 → CTO + CDO 병렬 스폰.**

---

## Wave 3: CTO + CDO 설계 (wave_domain.md 기반)

**⚙️ Wave 3 준비 시작** (Discord 알림)
```bash
curl -X POST "$DISCORD_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{"embeds":[{"title":"⚙️ UltraProduct 시작: CTO + CDO 설계","description":"PRD 기반 아키텍처 + 디자인 설계 중...","color":3447003}]}'
```

### CTO + CDO 병렬 스폰

**아래 Agent 2개를 동시에 스폰해라.**

**Agent 1 — CTO (Sonnet):**
`wave_domain.md`, `CLAUDE.md`, `PRD.md`, `agents/cto.md`를 읽고 기술 아키텍처(스택 확정, DB 설계, API 구조, 리스크, Engineering Rules)를 완성해서 `wave_cto.md`에 저장해라.
DB 스키마는 `wave_domain.md` 엔티티 기준으로 설계.

**Agent 2 — CDO 나은 (Sonnet):**
`wave_domain.md`, `CLAUDE.md`, `PRD.md`, `agents/cdo.md`를 읽고 Stitch MCP로 디자인을 생성해라.
`wave_domain.md`의 WORK SURFACES 섹션을 기준으로 화면 목록 결정.
1. PRD 화면 목록 + 이사팀 타겟 분석 기반으로 Phase 1~3 Stitch 프롬프트 작성
2. Stitch MCP 호출 → UI 생성
3. DESIGN.md 저장 (컬러/폰트/화면별 명세/shadcn 컴포넌트 목록)

**2개 모두 완료 확인 후 → PM 실행.**

### PM 유진 (Haiku) — CTO+CDO 완료 후 실행
`wave_domain.md`, `wave_cto.md`, `DESIGN.md`, `PRD.md`, `agents/pm.md`를 읽고
PRD Must Have 기능을 개발 태스크로 분해해서 `wave_pm.md`에 저장해라.
- User Story 작성 — **워크 서피스 기준으로 묶어라** (Main Listing / Detail / Create-Edit Form)
- 필수 워크 서피스 체크리스트 포함 (3개 없으면 wave_pm.md 미완성 처리)
- FE/BE 태스크 분리
- 개발 우선순위 정렬

---

## ⛔ 리안 컨펌 (Wave 3 설계 완료 후, 코딩 시작 전)

**⏸️ 설계 완료 — 리안 컨펌 대기** (Discord 알림)
```bash
curl -X POST "$DISCORD_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{"embeds":[{"title":"⏸️ 설계 완료 — 리안 컨펌 필요","description":"CTO/CDO/PM 설계 완료. 리안의 승인 대기 중...","color":16776960}]}'
```

**반드시 여기서 멈추고 리안에게 확인받아라. 자동으로 넘어가지 마라.**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 리안 컨펌 필요 — 설계 완료
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔹 PRD Must Have 기능
   [PRD.md에서 추출]

🔸 기술 스택 (CTO 확정)
   [wave_cto.md에서 추출]

🎨 디자인 방향 (CDO 확정)
   [DESIGN.md에서 추출]

📌 개발 태스크 수
   FE: [N]개 / BE: [N]개

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
수정할 거 있으면 말해. 없으면 "진행해" 입력.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

리안이 "진행해" 입력하면 → Wave 4 시작.

---

## Wave 3.5: DevOps 도구 준비 (FE/BE 시작 전)

**PM 완료 확인 후 → DevOps 에이전트 스폰.**

**Agent — DevOps (Sonnet):**
`wave_cto.md`, `DESIGN.md`, `wave_pm.md`, `PRD.md`, `agents/devops.md`를 읽고
FE/BE 개발에 필요한 모든 패키지/MCP/GitHub 소스를 파악해서 `wave_devops.md`에 설치 계획을 작성해라.
자동 설치 실행 (컨펌 불필요).

**완료 후 → Wave 4 시작.**

---

## Wave 4: 구현 — 순서 엄수 (BE 먼저)

**⚙️ Wave 4 시작: BE 먼저 → FE 연결** (Discord 알림)
```bash
curl -X POST "$DISCORD_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{"embeds":[{"title":"⚙️ Wave 4 시작: BE 구현 중 (FE는 BE 완료 후 시작)","description":"Backend API 구현 중...","color":3447003}]}'
```

### 개발 순서 절대 원칙
- FE가 먼저 예쁜 화면 만들고 "나중에 API 연결" → 절대 금지. 영원히 목업이 됨
- 하드코딩 mock 데이터로 대시보드 채우기 → 절대 금지
- "TODO: 백엔드 연결" 주석 남기고 끝내기 → 절대 금지

### Wave 4-1: 백엔드 먼저 (BE 에이전트)

**Agent — BE 정우 (Haiku):**
`wave_domain.md`, `wave_cto.md`, `wave_pm.md`, `PRD.md`, `agents/be.md`를 읽고
API 전체 구현, DB 스키마, 비즈니스 로직을 작성해서 `src/backend/`에 실제 코드를 생성해라.
- **wave_domain.md 엔티티 기준**으로 DB 스키마 작성. 새 필드 임의 추가 금지.

완료 기준 (이걸 통과해야 FE 시작 가능):
- 각 API 엔드포인트 curl 테스트 결과 첨부
- DB 스키마 마이그레이션 파일 존재 (wave_domain.md 엔티티 전부 포함)
- 인증 API (가입/로그인/토큰 검증) 실제 동작 확인

**BE 완료 확인 후 → Wave 4-2 시작.**

### Wave 4-2: 프론트엔드 (FE 에이전트) — BE 완료 후에만

**Agent — FE 민준 (Haiku):**
`wave_domain.md`, `wave_cto.md`, `DESIGN.md`, `wave_pm.md`, `PRD.md`, `agents/fe.md`를 읽고
4-1에서 구현된 실제 API에 연결하면서 UI를 구현해라.
- **반드시 3개 워크 서피스 구현** (Main Listing View + Detail View + Create/Edit Form)
- 모든 데이터는 API에서 fetch (하드코딩 금지). 워크 서피스 mock 데이터 = 구현 아님.
- 로그인/회원가입 → 실제 토큰 발급 확인
- 결제 → 실제 Stripe/토스 테스트모드 연결

**FE 완료 확인 후 → Wave 4.5 린터 실행.**

---

## Wave 4.5: 린터 + 정적 분석 (자동)

```bash
# Frontend 린터
cd src/frontend && npx eslint . --ext .ts,.tsx --fix 2>&1 | head -50

# Backend 린터
cd src/backend && python -m ruff check . --fix 2>&1 | head -50
```

결과 저장 → `qa/linter_results.md`
- 자동 수정 가능: 즉시 수정
- 수동 수정 필요: Wave 5 QA에 전달

---

## Wave 4.7: 시각 QA (3D/디자인 프로젝트일 때)

`design_plan.3d_level`이 `none`이 아닐 때만 실행. Stitch-only 프로젝트면 스킵.

```python
import sys, os
_ROOT = os.popen("git rev-parse --show-toplevel").read().strip()
sys.path.insert(0, os.path.join(_ROOT, "company"))
os.chdir(os.path.join(_ROOT, "company"))
from dotenv import load_dotenv; load_dotenv()

from core.visual_qa_loop import run_qa
# 로컬 dev 서버가 띄워져 있으면 URL로, 아니면 HTML 파일 경로로
result = run_qa("http://localhost:3000", "SCENE.md", max_iterations=3)
```

결과를 리안에게 보여줘라:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
시각 QA 결과
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
점수: [score]/100
통과: [passed]
이슈: [issues]
수정 제안: [suggestions]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

- 85점 이상: Wave 5로 진행
- 85점 미만: FE 에이전트에게 수정 제안 전달 → 재구현 → 재평가 (최대 3회)

---

## Wave 5: 검증 (QA + CTO 통합 리뷰)

**✅ Wave 5 시작: QA 검증** (Discord 알림)
```bash
curl -X POST "$DISCORD_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{"embeds":[{"title":"✅ Wave 5 시작: QA 검증","description":"코드 리뷰, 테스트, CTO 통합 리뷰 진행 중...","color":3447003}]}'
```

### Wave 5 — Agent 병렬 스폰 (QA + CTO리뷰 동시)

**Agent 1 — QA 소연 (Haiku):**
`src/` 코드 전체와 `agents/qa.md`를 읽고 코드 리뷰, 버그 수정, 테스트 시나리오 3개 이상을 작성해서 `qa/test_results.md`에 저장해라. 발견한 버그는 코드에서 직접 수정해라.

**Agent 2 — CTO 현우 통합 리뷰 (Sonnet):**
`src/` 코드 전체, `wave_cto.md`, `agents/cto.md`를 읽고 FE+BE 통합 검증, Engineering Rules 준수, 아키텍처 재검토를 수행해서 `qa/cto_review.md`에 저장해라.

**2개 완료 확인 후 → 워크 서피스 게이트 확인 후 → Wave 6 (상용화) 또는 Wave 7 (개인 툴) 진행.**

### Wave 5 워크 서피스 게이트 (자동 체크 — QA 완료 직후)

아래 3개가 **실제 API 연결된 상태**로 존재하는지 확인:
- [ ] Main Listing View: `wave_domain.md`의 핵심 엔티티 데이터 표시 (mock 아님)
- [ ] Detail View: 단일 레코드 전체 필드 + 액션
- [ ] Create/Edit Form: 저장 → DB 반영 확인

**3개 중 하나라도 없거나 mock 데이터면 → FE 에이전트에게 해당 서피스 재구현 지시 → Wave 5 재실행.**
전부 확인되면 → Wave 6 진행.

---

## Wave 6: 마케팅 실행 + 배포 (상용화만)

개인 툴이면 스킵 → Wave 7로.

**📣 Wave 6 시작: 마케팅 실행 + 배포** (Discord 알림)
```bash
curl -X POST "$DISCORD_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{"embeds":[{"title":"📣 Wave 6 시작: 마케팅 실행 + 배포","description":"분석·마케팅팀 연동 + 배포 준비 중...","color":3447003}]}'
```

마케팅은 분석·마케팅팀(승현+예진)이 담당. `offline_sales.py` 파이프라인 참고.

배포:
- Cloudflare Pages 배포 (프론트): `npx wrangler pages deploy`
- Cloudflare Workers 배포 (백엔드): `npx wrangler deploy`
- D1 마이그레이션: `npx wrangler d1 migrations apply DB`
- README.md 생성

### ⛔ Wave 6 리안 컨펌 (배포 전 필수)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📣 배포 컨펌 필요
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
배포 준비 완료. "배포해" 입력하면 실행.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Wave 6.5: 마케팅 자동 연결 (배포 완료 후 자동 실행)

배포가 성공적으로 완료되면 → 리안이 요청 안 해도 아래를 자동 실행.

**배포된 URL을 context에 저장하고 아래 실행:**

```python
# 배포 URL 확인 (Cloudflare Pages에서 받은 URL)
DEPLOYED_URL = "https://프로젝트명.pages.dev"  # 실제 배포된 URL로 교체
project_name = "프로젝트명"  # 실제 프로젝트명으로 교체

import sys, os, time
_ROOT = os.popen("git rev-parse --show-toplevel").read().strip()
sys.path.insert(0, os.path.join(_ROOT, "company"))
os.chdir(os.path.join(_ROOT, "company"))
from dotenv import load_dotenv; load_dotenv()

# 1. 랜딩페이지 QA 자동 실행 (배포 반영 5초 대기)
time.sleep(5)
from core.qa_loop import run_qa
qa_result = run_qa(DEPLOYED_URL, project_name)
print(f"\nQA 점수: {qa_result.get('score', '?')}/10")
# 7점 이하면 보고사항들.md에 자동 기록됨

# 2. 자동 마케팅 분석 + 전략 수립
import anthropic
client = anthropic.Anthropic()

from core.product_analyzer import analyze_product
from core.marketing_planner import plan_marketing, print_confirmation_prompt

analysis = analyze_product(DEPLOYED_URL, project_name, client)
plan = plan_marketing(analysis, project_name, client)
print(print_confirmation_prompt(project_name, plan))
```

**자동 실행:**
```python
from core.marketing_planner import activate_teams
activate_teams(project_name, plan)
```
결과만 보고사항들.md에 저장. 컨펌 불필요.

---

## Wave 7: Gemini 독립 검증 (자동 실행)

**🔍 Wave 7 시작: Gemini 독립 검증** (Discord 알림)
```bash
curl -X POST "$DISCORD_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{"embeds":[{"title":"🔍 Wave 7 시작: Gemini 최종 검증","description":"모든 산출물 독립 검증 중...","color":3447003}]}'
```

**Claude가 직접 검증하지 마라. 아래 명령어를 Bash로 실행해라.**

```bash
LIANCP_ROOT="$(cd ../.. 2>/dev/null && pwd || cd .. 2>/dev/null && pwd)"
"${LIANCP_ROOT}/company/venv/Scripts/python.exe" "${LIANCP_ROOT}/company/verify_gemini.py" "$(pwd)"
```

스크립트가 `final_report.md`를 현재 프로젝트 폴더에 자동 저장한다.

---

## Wave 7.5: CRITICAL 자동 수정 (1회만)

final_report.md를 읽고:
1. `[CRITICAL]` 태그 항목 추출
2. CRITICAL 있으면 → 코드 직접 수정 → `wave_fixes.md` 기록 → Gemini 재검증 1회
3. 재검증 후에도 CRITICAL 남으면 → 수동 확인 필요로 리안에게 알림
4. CRITICAL 없으면 → HIGH 이슈 목록만 리안에게 보여줘. 자동 수정 금지.

**재검증은 최대 1회만. 무한 루프 금지.**

---

## Wave 4 완료 후: 시은 자동 브리핑

**FE+BE 둘 다 완료되면 → 아래를 자동 실행해라. 리안이 요청 안 해도.**

```
프로젝트 폴더의 wave_fe_*.md, wave_be_*.md, wave_cto.md 읽고
리안에게 줄 CEO 브리핑을 보고사항들.md에 자동으로 추가해라.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
시은 Wave 4 완료 보고 — [프로젝트명] [날짜]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

완성된 것:
- FE: [완료된 화면 수]/[전체] 화면 (% 완성도)
- BE: [완료된 API 수]/[전체] API (% 완성도)

바로 테스트할 수 있는 것:
- [URL or 명령어]

아직 안 된 것:
- [미완성 항목]

리안이 확인해야 할 것:
- [QA 진행 전 결정사항이 있다면]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

작성 후 아래 메시지 리안에게 출력:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Wave 4 완료 — 시은 브리핑 완성
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FE [N]개 / BE [N]개 API 완성.
[한 줄 요약]

"계속해" → Wave 5 QA 자동 시작
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Wave 5 자동 시작. 컨펌 불필요.

---

## 최종 보고

**✅ UltraProduct 전체 완료** (Discord 알림)
```bash
curl -X POST "$DISCORD_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{"embeds":[{"title":"✅ UltraProduct 완료!","description":"모든 산출물 생성 완료. 최종 검증 리포트 완성!","color":65280}]}'
```

**Wave 7.5 완료 후 → 시은 + 지호 자동 최종 브리핑 실행. 리안이 요청 안 해도 자동으로.**

시은 역할: 프로젝트 최종 상태 요약 (뭐가 완성됐는지)
지호 역할: 전체 리안 컴퍼니 관점에서 갭/다음 액션 제안

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
리안 CEO 최종 브리핑 — [프로젝트명]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[시은 — 프로젝트 요약]
완성된 것: [목록]
품질 상태: Gemini 검증 [결과] / CRITICAL [N건] / HIGH [N건]
지금 당장 쓸 수 있나: [YES/NO + 이유]

[지호 — 다음 액션]
지금 해야 할 것 1: [무엇을, 왜]
지금 해야 할 것 2: [무엇을, 왜]
놓치고 있는 것: [있으면]

📁 산출물: [경로]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

이 브리핑을 보고사항들.md에도 자동 저장.
그리고 Discord 완료 알림도 이 내용 포함해서 보내.

**규칙: 리안이 "끝났어?" "다 됐어?" 같은 걸 물어보기 전에 먼저 내놔야 한다.**

---

## 모델 배정

| 역할 | 모델 | 이유 |
|------|------|------|
| CTO | Sonnet | 아키텍처 설계 |
| CDO 나은 | Sonnet | Stitch 프롬프트 정밀도 |
| PM 유진 | Haiku | 태스크 분해는 구조적 작업 |
| FE 민준 | Haiku | 코드 작성 |
| BE 정우 | Haiku | 코드 작성 |
| QA 소연 | Haiku | 버그 탐지 + 수정 |
| CTO 통합 리뷰 | Sonnet | 비용 최적화 (Opus 대비 ~$0.75 절감) |
| Wave 7 검증 | Gemini API | 진짜 독립 검증 |
