---
name: shell
description: PRD.md + CLAUDE.md 읽고 Wave 3~6 자동 실행 (기획은 이미 완료됨)
---

# /work — UltraProduct 자동 실행

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

## Step 1: 디자인 스타일 선택 (리안 컨펌)

CDO 부르기 전에 리안에게 물어봐라.

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎨 디자인 스타일 선택
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[프로젝트명] 어떤 느낌으로 만들까?

1. Stitch 스타일 — 깔끔한 SaaS UI. 빠르고 안정적. (기본값)
2. 3D 웹 스타일 — Spline 감성. 임팩트 있는 랜딩페이지. 마케팅/브랜딩 사이트에 적합.
3. 둘 다 — 메인 랜딩은 3D, 앱 내부는 Stitch

숫자 입력 or "알아서 해줘" (→ 타겟/목적 기반 CDO가 판단)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

리안 답변에 따라:
- `1` 또는 "알아서" → CDO가 Stitch로 진행 (기존 방식)
- `2` → CDO에게 `design_style: "3D (Three.js / React Three Fiber, Spline 감성)"` 전달
- `3` → CDO에게 `design_style: "hybrid — 랜딩 3D + 내부 Stitch"` 전달

---

## Wave 3 시작 전: CTO + CDO 설계 (PRD 기반)

**⚙️ Wave 3 준비 시작** (Discord 알림)
```bash
curl -X POST "$DISCORD_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{"embeds":[{"title":"⚙️ UltraProduct 시작: CTO + CDO 설계","description":"PRD 기반 아키텍처 + 디자인 설계 중...","color":3447003}]}'
```

### CTO + CDO 병렬 스폰

**아래 Agent 2개를 동시에 스폰해라.**

**Agent 1 — CTO (Sonnet):**
`CLAUDE.md`, `PRD.md`, `agents/cto.md`를 읽고 기술 아키텍처(스택 확정, DB 설계, API 구조, 리스크, Engineering Rules)를 완성해서 `wave_cto.md`에 저장해라.

**Agent 2 — CDO 나은 (Sonnet):**
`CLAUDE.md`, `PRD.md`, `agents/cdo.md`를 읽고 Stitch MCP로 디자인을 생성해라.
1. PRD 화면 목록 + 이사팀 타겟 분석 기반으로 Phase 1~3 Stitch 프롬프트 작성
2. Stitch MCP 호출 → UI 생성
3. DESIGN.md 저장 (컬러/폰트/화면별 명세/shadcn 컴포넌트 목록)

**2개 모두 완료 확인 후 → PM 실행.**

### PM 유진 (Haiku) — CTO+CDO 완료 후 실행
`wave_cto.md`, `DESIGN.md`, `PRD.md`, `agents/pm.md`를 읽고
PRD Must Have 기능을 개발 태스크로 분해해서 `wave_pm.md`에 저장해라.
- User Story 작성
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
리안 컨펌 후 설치 실행.

**완료 후 → Wave 4 시작.**

---

## Wave 4: 구현 (FE + BE 병렬)

**⚙️ Wave 4 시작: FE + BE 구현** (Discord 알림)
```bash
curl -X POST "$DISCORD_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{"embeds":[{"title":"⚙️ Wave 4 시작: FE + BE 구현","description":"Frontend와 Backend 코드 생성 중... (병렬)","color":3447003}]}'
```

### Wave 4 — Agent 병렬 스폰 (FE + BE 동시)

**아래 Agent 2개를 동시에 스폰해라. 절대 순서대로 하지 마라.**

**Agent 1 — BE 정우 (Haiku):**
`wave_cto.md`, `wave_pm.md`, `PRD.md`, `agents/be.md`를 읽고
API 전체 구현, DB 스키마, 비즈니스 로직을 작성해서 `src/backend/`에 실제 코드를 생성해라.

**Agent 2 — FE 민준 (Haiku):**
`wave_cto.md`, `DESIGN.md`, `wave_pm.md`, `PRD.md`, `agents/fe.md`를 읽고
UI 전체 구현, 컴포넌트, 상태관리, 백엔드 API 연결을 작성해서 `src/frontend/`에 실제 코드를 생성해라.

**2개 모두 완료 확인 후 → Wave 4.5 린터 실행.**

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

**2개 완료 확인 후 → Wave 6 (상용화) 또는 Wave 7 (개인 툴) 진행.**

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

## 최종 보고

**✅ UltraProduct 전체 완료** (Discord 알림)
```bash
curl -X POST "$DISCORD_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{"embeds":[{"title":"✅ UltraProduct 완료!","description":"모든 산출물 생성 완료. 최종 검증 리포트 완성!","color":65280}]}'
```

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ UltraProduct 완료
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Gemini 검증 결과: [준비 완료 / 조건부 준비 / 미준비]
🔧 자동 수정한 CRITICAL 이슈: X건
⚠️ 남은 HIGH 이슈: X건 (리안 확인 필요)
📁 산출물 위치: [경로]

🚀 다음 단계: [배포 가이드 or 수정 필요 사항]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

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
