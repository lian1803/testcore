# CAPABILITIES — 내가 가진 모든 능력 (태스크 라우팅)

> **태스크 받으면 이 파일 먼저 읽고 관련 능력 쓰기.**
> 없으면 리안한테 "이런 거 설치할까요?" 제안.
> 마지막 스캔: 2026-04-17

---

## 🎯 트리거 매핑 — "리안이 말하면 → 내가 쓸 것"

### 디자인/UI
| 리안이 말하면 | 써야 할 것 | 호출 |
|---|---|---|
| "랜딩 만들어" / "홈페이지" / "사이트 만들어" | Skill: `landing` + director 에이전트 | `Skill("landing")` |
| "3D 히어로" / "R3F" / "3D로 돌려" | Skill: `r3f-hero` | `Skill("r3f-hero")` |
| "영상 히어로" / "Kling으로" | Skill: `kling-hero` | `Skill("kling-hero")` |
| "셰이더" / "GLSL" | Skill: `glsl-expert` | 참조 |
| "Three.js" / "3D 씬" | Skill: `threejs-*` (10개) | 관련 서브스킬 |
| "대시보드" / "관리자 UI" | CDO(나은) → Stitch MCP | `Agent(subagent_type="cdo")` |
| "프론트엔드 디자인 규칙" | Skill: `frontend-design` | 참조 |
| "마무리 다듬기" / "polish" | Skill: `polish` | 참조 |
| "테마" / "스타일 시스템" | Command: `/theme-factory` | 슬래시 |
| "브랜드 가이드라인" | Command: `/brand-guidelines` | 슬래시 |

### 마케팅/콘텐츠
| 리안이 말하면 | 써야 할 것 | 호출 |
|---|---|---|
| "카피 써줘" | Skill: `copywriting` | `Skill("copywriting")` |
| "마케팅 아이디어" | Skill: `marketing-ideas` + marketing 에이전트 | 자동 |
| "마케팅 심리학" | Skill: `marketing-psychology` | 자동 |
| "제품 마케팅 컨텍스트" | Skill: `product-marketing-context` | 자동 |
| "온라인 마케팅 돌려" | `run_온라인마케팅팀.py` | 터미널 |
| "온라인 영업 돌려" | `run_온라인영업팀.py` | 터미널 |
| "콘텐츠 납품 돌려" | `run_온라인납품팀.py` | 터미널 |
| "오프라인 영업/마케팅" | `offline_sales.py` | 터미널 |
| "카드뉴스 자동화" | `auto_trend_report.py` + `/trend` + html-to-png.js | 자동 |

### 인스타그램 / 리서치
| 리안이 말하면 | 써야 할 것 | 호출 |
|---|---|---|
| "인스타 링크 분석" / "인스타 분석해줘" | `analyze_instagram.py` (gallery-dl + Gemini + 딥다이브) | 스크립트 |
| "인스타 접속" / 단일 URL | `utils/insta_browse.py` (쿠키 주입) | 스크립트 |
| "경쟁사 감시" | Command: `/competitor-watch` + `auto_competitor_watch.py` | 자동 |
| "트렌드 리서치" | Command: `/trend` | 슬래시 |
| "Awwwards 스크랩" | `utils/awwwards_scraper.py` | 스크립트 |
| "Codepen 스크랩" | `utils/codepen_scraper.py` | 스크립트 |
| "네이버 크롤" | `utils/naver_crawler.py` + `utils/naver_auth.py` | 스크립트 |
| "Meta 광고 분석" | `utils/meta_ads.py` | 스크립트 |
| "이 영상/릴스 복제" / "HTML로 재현" | `utils/video_cloner.py` | 스크립트 |
| "이 웹페이지 분석" / "URL 스크랩" | `utils/web_scraper.py` | import |
| "팀 템플릿으로 저장" / "유사팀 생성" | `utils/team_templates.py` | import |
| "에이전트 상태 추적" | `utils/status_tracker.py` | import |

### 개발/코딩
| 리안이 말하면 | 써야 할 것 | 호출 |
|---|---|---|
| 새 API/백엔드 (100줄+) | `be` 에이전트 | `Agent(subagent_type="be")` |
| 프론트엔드 컴포넌트 | `fe` 에이전트 | `Agent(subagent_type="fe")` |
| 아키텍처 설계 | `cto` → `be`/`fe` | 순차 |
| 테스트/QA | `qa` 에이전트 | `Agent(subagent_type="qa")` |
| 도메인 모델링 | `domain-architect` | 스폰 |
| 태스크 분해 / User Story | `pm` | 스폰 |
| DevOps / 패키지 설치 | `devops` | 스폰 |

### 문서 생성 (Anthropic Skills)
| 리안이 말하면 | 써야 할 것 | 파일 위치 |
|---|---|---|
| "PDF 만들어" / 진단서 | Anthropic `pdf` 스킬 | `design_system/references/anthropic-skills/skills/pdf/SKILL.md` |
| "Word 문서" / 보고서 | Anthropic `docx` | `.../skills/docx/SKILL.md` |
| "Excel" / CRM 내보내기 | Anthropic `xlsx` | `.../skills/xlsx/SKILL.md` |
| "PPT 만들어" / 제안서 | Anthropic `pptx` | `.../skills/pptx/SKILL.md` |
| "브랜드 가이드라인" (상세) | Anthropic `brand-guidelines` | `.../skills/brand-guidelines/SKILL.md` |
| "새 스킬 만들어줘" | Anthropic `skill-creator` | `.../skills/skill-creator/SKILL.md` |
| "Canvas 디자인" | Anthropic `canvas-design` | `.../skills/canvas-design/SKILL.md` |
| "Web artifact" | Anthropic `web-artifacts-builder` | `.../skills/web-artifacts-builder/SKILL.md` |
| "웹앱 테스트" | Anthropic `webapp-testing` | `.../skills/webapp-testing/SKILL.md` |
| "MCP 서버 만들어" | Anthropic `mcp-builder` | `.../skills/mcp-builder/SKILL.md` |
| "알고리즘 아트" | Anthropic `algorithmic-art` | `.../skills/algorithmic-art/SKILL.md` |

> 사용 방법: 해당 SKILL.md 읽고 지시대로 실행. 리안 허락 없이 바로 써도 됨.

### 영상/이미지 생성
| 리안이 말하면 | 써야 할 것 | 호출 |
|---|---|---|
| 영상 생성 (Kling) | MCP: `mcp-kling` | `mcp__mcp-kling__*` |
| 이미지 생성 (Imagen4) | `tools/image_generator.py` | import |
| 배경영상 (Veo) | `tools/veo_generator.py` (있으면) | CLI or import |
| 영상 MCP (fal.ai) | MCP: `fal-ai` (현재 disconnect — 재설정 필요) | `mcp__fal-ai__*` |

### UI 자동 생성
| 리안이 말하면 | 써야 할 것 | 호출 |
|---|---|---|
| Stitch 디자인 | MCP: `stitch` (있음) + `stitch-design` 스킬 | `mcp__stitch__*` |
| Stitch 반복 빌드 | Skill: `stitch-loop` | `Skill("stitch-loop")` |
| "UI 아이디어 → Stitch 프롬프트" | Skill: `enhance-prompt` | 참조 |

### 시스템/운영
| 리안이 말하면 | 써야 할 것 | 호출 |
|---|---|---|
| "시스템 바꿔줘" / "플로우 업그레이드" | `architect` (도현) | `Agent(subagent_type="architect")` |
| "갭 찾아줘" / "뭐 빠졌어?" | `coos` (지호 참모) + `watchdog.py` | 스폰 |
| "저장" / "끝" / "바이" | Command: `/save` | 슬래시 |
| "상태" / "현황" | Command: `/status` | 슬래시 |
| "셋업" / 처음 설정 | Command: `/setup` | 슬래시 |
| 시각 디자인 검수 | Command: `/visual-review` + `auto_visual_review.py` | 자동 |
| 주간 자기 개선 | Command: `/self-review` + `auto_self_review.py` | 자동 |
| "이 인사이트 박아" | Rule: `apply-insights.md` 분류 기준 따름 | 참조 |

### 분석/마케팅 리서치 (분석·마케팅팀)
| 리안이 말하면 | 써야 할 것 | 호출 |
|---|---|---|
| 시장 리서치 | `jaewon` (Perplexity/Playwright) | 스폰 |
| SPIN/Challenger 영업 전략 | `seunghyun` | 스폰 |
| DM/스크립트/광고 카피 | `yejin` | 스폰 |
| 마케팅 성과 분석/루프 | `youngjin` | 스폰 |
| 마케팅 통합 실행 | `marketing` (오케스트레이터) | 스폰 |

---

## 📦 전체 설치 목록

### Skills (`.claude/skills/`) — 17개
- **범용 디자인/코딩**: `creative-coding`, `glsl-expert`, `polish`, `frontend-design`
- **히어로 자동화**: `r3f-hero` (Three.js 3D), `kling-hero` (AI 영상)
- **Three.js 11개**: `threejs-animation`, `threejs-fundamentals`, `threejs-geometry`, `threejs-interaction`, `threejs-lighting`, `threejs-loaders`, `threejs-materials`, `threejs-postprocessing`, `threejs-shaders`, `threejs-textures`, `webgpu-threejs-tsl`

### Skills (`.agents/skills/` — 심볼릭) — 7개
- `copywriting`, `enhance-prompt`, `marketing-ideas`, `marketing-psychology`, `product-marketing-context`, `stitch-design`, `stitch-loop`

### Agents (`.claude/agents/`) — 24개
- **C-level**: `cpo`, `cto`, `cdo`, `coos`
- **실행 엔지니어**: `be`, `fe`, `qa`, `pm`, `devops`, `architect`, `domain-architect`, `director`
- **분석·마케팅팀**: `analytics`, `marketing`, `jaewon`, `seunghyun`, `yejin`, `youngjin`
- **세금신고 프로젝트팀 (한시)**: `김태은`, `박소율`, `서진혁`, `이하린`, `정우진`, `한서윤`

### Commands (`.claude/commands/`) — 13개
- **세션/운영**: `/save`, `/setup`, `/status`, `/shell`
- **디자인**: `/landing`, `/brand-guidelines`, `/frontend-design`, `/theme-factory`
- **자동 리뷰**: `/self-review`, `/visual-review`, `/competitor-watch`, `/trend`
- **실행**: `/work`

### Rules (`.claude/rules/`) — 7개
- `triggers.md` — 리안 요청 → 시스템 실행 매핑
- `coding.md` — 코딩 작업 시 에이전트 스폰 기준
- `apply-insights.md` — "박아" 요청 시 분류 저장
- `instagram.md` — 인스타 접속/분석 규칙
- `test-folder.md` — 테스트 파일 위치
- `web-quality.md` — 웹 퀄리티 기준
- `org-change.md` — 조직/시스템 변경 규칙

### Python 툴 (`company/tools/` + `company/utils/`)
- **tools**: `design_scraper.py`, `image_generator.py`
- **utils 스크래핑**: `awwwards_scraper.py`, `codepen_scraper.py`, `insta_analyze.py`, `insta_browse.py`, `naver_crawler.py`, `naver_auth.py`, `web_scraper.py`
- **utils 분석/모니터**: `meta_ads.py`, `monitor.py`, `status_tracker.py`
- **utils 복제/템플릿**: `video_cloner.py` (인스타/유튜브 URL → HTML 재현), `team_templates.py` (기존 팀 저장/신규 팀 템플릿화)

### MCP 서버 (`.mcp.json`)
- `mcp-kling` — Kling AI 영상 생성
- `fal-ai` — fal.ai 통합 (nano-banana, kling-video 등) ⚠️ 현재 disconnect

### MCP (세션에 로드됨, 설정 외)
- `stitch` — Google Stitch UI 생성
- `nano-banana` — Gemini 이미지 편집
- `claude_ai_Google_Drive` — Google Drive 연동
- `plugin_vercel_vercel` — Vercel 배포

### GitHub 클론 레포 (`design_system/`, `team/`)
- `design_system/design-systems/` — 기업 DESIGN.md 58개 (VoltAgent)
- `design_system/references/` — Apple 3D, Awwwards Truus/Capsule, Codrops (5개)
- `design_system/references/anthropic-skills/` — **Anthropic 공식 Skills 17개** (pdf, docx, xlsx, pptx, brand-guidelines, skill-creator, canvas-design, frontend-design, theme-factory, mcp-builder, webapp-testing, web-artifacts-builder, algorithmic-art, claude-api, doc-coauthoring, internal-comms, slack-gif-creator)
- `team/LLM-비용-서킷브레이커팀/llm-guard-app` — SaaS 프로젝트

### 자동화 스크립트 (`company/`)
- `daily_auto.py` — 매일 08:00 (Task Scheduler)
- `weekly_runner.py` — 매주 월요일 10:00
- `auto_visual_review.py`, `auto_competitor_watch.py`, `auto_self_review.py`, `auto_trend_report.py`
- `watchdog.py` — 갭 분석 (지호)

---

## 🔄 자동 확장 규칙

**새 스킬/에이전트/MCP/툴 설치 시:**
1. 설치 완료 → 이 파일 트리거 매핑 + 전체 목록에 추가
2. `.claude/INSTALLED.md` 도 동기화
3. `devops` 에이전트 또는 설치한 Claude가 직접

**주기적 검증:**
- `weekly_runner.py`가 매주 월요일 스캔 → 차이 있으면 경고
- 새로 발견된 것 → 자동 등록 제안

**리안이 "이거 해줘" 했는데 매핑 없으면:**
1. 유사한 능력 탐색 (다른 트리거 키워드 매칭)
2. 없으면 → "이거 새로 설치할까요? 아니면 유사 대안으로 [X]를 쓸까요?" 제안
3. 리안 승인 후 설치 → 이 파일에 추가

---

## 📍 관련 파일
- `.claude/INSTALLED.md` — 설치 스냅샷 (인프라 관점)
- `CLAUDE.md` — 절대 규칙
- `OPERATIONS.md` — 운영 매뉴얼
- `.claude/rules/auto-discover.md` — 이 파일 사용 규칙
