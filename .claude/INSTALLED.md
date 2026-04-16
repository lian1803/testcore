# 설치된 외부 리소스 전체 목록
> 리안 시스템에 설치/클론/연결된 모든 외부 도구. Claude가 항상 참조.
> 마지막 업데이트: 2026-04-11

---

## Skills (슬래시 커맨드 / 에이전트 능력 확장)

### `.agents/skills/` — 범용 마케팅/카피/디자인 (7개)
| 스킬명 | 용도 | 파이프라인 연결 |
|---|---|---|
| `copywriting` | 랜딩/홈페이지/CTA 마케팅 카피 작성 | 수동 `/copywriting` |
| `enhance-prompt` | UI 아이디어 → Stitch 최적화 프롬프트 변환 | 수동 |
| `marketing-ideas` | SaaS 마케팅 아이디어/전략 생성 | ✅ offline_marketing + 온라인마케팅팀 pipeline |
| `marketing-psychology` | 심리학 원칙 기반 마케팅 설계 | ✅ offline_marketing + 온라인마케팅팀 pipeline |
| `product-marketing-context` | 제품 마케팅 컨텍스트 문서 생성/업데이트 | ✅ offline_marketing + 온라인마케팅팀 pipeline |
| `stitch-design` | Stitch 디자인 작업 통합 진입점 | 수동 |
| `stitch-loop` | Stitch로 반복적 웹사이트 빌드 루프 | 수동 |

> 심볼릭 링크: `C:/Users/lian1/.claude/skills/` → `.agents/skills/` 동일

### `.claude/skills/` — 로컬 스킬 (13개)
| 스킬명 | 용도 |
|---|---|
| `frontend-design.md` | GLSL 셰이더/Lenis/SplitText 등 고급 프론트엔드 디자인 규칙 + 디자인 분기/레시피 |
| `threejs-fundamentals/` | Three.js 씬 설정, 카메라, 렌더러, Object3D 계층 |
| `threejs-shaders/` | GLSL, ShaderMaterial, 커스텀 이펙트 |
| `threejs-postprocessing/` | EffectComposer, Bloom, DOF, 화면 이펙트 |
| `threejs-materials/` | PBR, 셰이더 머티리얼 |
| `threejs-geometry/` | BufferGeometry, 커스텀 지오메트리, 인스턴싱 |
| `threejs-animation/` | 키프레임, 스켈레탈, 모프 타겟 |
| `threejs-interaction/` | 레이캐스트, 마우스/터치 인풋 |
| `threejs-lighting/` | 조명, 그림자, IBL |
| `threejs-loaders/` | GLTF, 텍스처, HDR 로딩 |
| `threejs-textures/` | UV 매핑, 큐브맵, 환경맵 |
| `webgpu-threejs-tsl/` | WebGPU + TSL(Three.js Shading Language) |

### `.claude/commands/` — 슬래시 커맨드 (13개)
| 커맨드 | 용도 | 자동화 연결 |
|---|---|---|
| `/work` | PRD.md + CLAUDE.md 읽고 Wave 3~6 자동 실행 | 수동 (팀 프로젝트 시작 시) |
| `/self-review` | 지호 COO 주간 시스템 자기 개선 리뷰 | ✅ daily_auto.py 4.5단계 (일요일) |
| `/visual-review` | Lian Dash 시각 디자인 자동 검수 (Playwright + Gemini Vision) | ✅ daily_auto.py 4.5단계 (수요일) |
| `/competitor-watch` | 경쟁사 자동 모니터링 (웹 스크랩 → 변경 감지) | ✅ daily_auto.py 4.5단계 (월요일) |
| `/brand-guidelines` | 브랜드 가이드라인 생성 | 수동 |
| `/landing` | 랜딩 페이지 설계/작성 | 수동 |
| `/save` | 세션 저장 (memory + git commit) | 수동 (세션 종료 시) |
| `/setup` | 프로젝트 초기 셋업 | 수동 |
| `/shell` | 쉘 명령 실행 | 수동 |
| `/status` | 시스템 현황 보고 | 수동 |
| `/theme-factory` | 테마/스타일 시스템 생성 | 수동 |
| `/trend` | 트렌드 리서치 자동 실행 | ✅ daily_auto.py 4.5단계 (매일) |
| `/frontend-design` | 프론트엔드 디자인 규칙 참조 | 수동 |

---

## MCP Servers

### 현재 활성 (`.mcp.json`)
| 서버명 | 상태 |
|---|---|
| (없음) | — |

---

## GitHub 클론된 레포

### 코드/시스템
| 레포 | 위치 | 용도 |
|---|---|---|
| `lian1803/test` | `/core` (메인) | 전체 시스템 레포 |
| `lian1803/llm-guard-app` | `team/LLM-비용-서킷브레이커팀/llm-guard-app` | LLM 비용 서킷브레이커 SaaS |

### 디자인 리소스
| 레포 | 위치 | 용도 |
|---|---|---|
| `VoltAgent/awesome-design-md` | `design_system/design-systems` | DESIGN.md 58개 (기업별 디자인 토큰) |
| `codebucks27/3D-Landing-page-for-Apple-iPhone` | `design_system/references/apple-3d-landing` | Three.js+GSAP Apple 풀 구현 |
| `Thakuma07/Truus.co-Awwward-Website` | `design_system/references/awwwards-truus` | CursorBubble, DoubleMarquee, MotionCards |
| `ShowravKormokar/capsule` | `design_system/references/awwwards-capsule` | Awwwards 클론 Vite 기반 |
| `codrops/ScrollBasedLayoutAnimations` | `design_system/references/codrops-scroll-animations` | GSAP Flip+Lenis+ScrollTrigger |
| `codrops/ImageTrailEffects` | `design_system/references/codrops-image-trail` | 마우스 트레일 이미지 6변형 |
| `codrops/OnScrollTypographyAnimations` | `design_system/references/codrops-typo-scroll` | 스크롤 타이포그래피 |
| `abi/screenshot-to-code` | `design_system/references/screenshot-to-code` | 스크린샷→코드 변환 |
| (로컬) | `team/디자인팀/demo` | 디자인 데모 (리모트 없음) |

---

## 자동화 스크립트

### `company/auto_*.py` (4개) — daily_auto.py 4.5단계에 전부 연결됨
| 스크립트 | 용도 | 자동 실행 주기 |
|---|---|---|
| `auto_visual_review.py` | 배포된 사이트 스크린샷 + Gemini Vision 검수 | ✅ 매주 수요일 |
| `auto_competitor_watch.py` | 경쟁사 웹 모니터링 + 변경 감지 | ✅ 매주 월요일 |
| `auto_self_review.py` | 시스템 자기 개선 리뷰 | ✅ 매주 일요일 |
| `auto_trend_report.py` | 트렌드 자동 리포트 | ✅ 매일 |

---

## Hooks (자동 실행)

| 트리거 | 파일 | 동작 |
|---|---|---|
| PreToolUse (Bash/Write/Edit) | `.claude/hooks/pre_tool_safety.sh` | 안전 체크 |
| PostToolUse (Edit/Write) | settings.json 인라인 | git 자동 커밋 |
| Stop | settings.json 인라인 | work_log.md 기록 |

---

## 디자인 자동화 파이프라인 (코어)

| 모듈 | 파일 | 용도 | 연결 |
|---|---|---|---|
| 디자인 라우터 | `company/core/design_router.py` | 프로젝트 설명 → 디자인 전략 자동 결정 | ✅ /work Step 1-1 |
| 레퍼런스 분석기 | `company/core/reference_analyzer.py` | design_system에서 유사 레퍼런스 자동 검색 | ✅ /work Step 1-2 |
| 시각 QA 루프 | `company/core/visual_qa_loop.py` | 스크린샷 + Gemini Vision 자동 평가 | ✅ /work Wave 4.7 |
| 랜딩 QA 루프 | `company/core/qa_loop.py` | PC/모바일 스크린샷 + Claude 평가 + 보고 | ✅ /work Wave 6.5 + launch_prep.py |

---

## SaaS 모니터링 자동화

| 프로젝트 | 파일 | 용도 | 자동화 |
|---|---|---|---|
| llm-guard-app | `e2e/monitor.spec.ts` | Playwright E2E 테스트 (14개 시나리오) | ✅ GitHub Actions 매일 09:00 KST |
| llm-guard-app | `.github/workflows/monitor.yml` | 실패 → Issue 생성 → Claude 자동 수정 → PR | ✅ `anthropics/claude-code-action@beta` |

---

## 전체 자동화 스케줄

### Windows Task Scheduler
| 작업 | 스크립트 | 주기 |
|---|---|---|
| LianCompany_DailyAuto | `daily_auto.py` | 매일 08:00 |
| LianCompany_WeeklyReview | `weekly_runner.py` | 매주 월요일 10:00 |

### daily_auto.py 실행 순서
| 단계 | 내용 | 자동 여부 |
|---|---|---|
| 0단계 | Git 리뷰 (core-shell 변경사항 확인) | ✅ |
| 1단계 | 디자인 트렌드 수집 (Awwwards) | ✅ |
| 1.5단계 | 디자인스카우팅팀 실행 | ✅ |
| 2단계 | 전 팀 학습 (continuous_learning) | ✅ |
| 3단계 | 일일 콘텐츠 생성 (ops_loop) | ✅ |
| 4단계 | 보고 저장 (보고사항들.md) | ✅ |
| 4.5단계 | 트렌드(매일) / 경쟁사(월) / 시각QA(수) / 자기개선(일) | ✅ |
| 5단계 | 대시보드 데이터 생성 | ✅ |

---

## 미연결 (수동 전용) — 의도적

### 팀 run 스크립트 (태스크 입력 필요)
| 스크립트 | 이유 |
|---|---|
| `run_온라인영업팀.py` | 영업 태스크 입력 필요 |
| `run_온라인납품팀.py` | 콘텐츠 태스크 입력 필요 |
| `run_온라인마케팅팀.py` | 마케팅 태스크 입력 필요 |
| `run_인스타분석팀.py` | 링크 파일 입력 필요 |
| 기타 프로젝트팀 run_*.py | 프로젝트별 태스크 입력 필요 |

### 추가 연결 완료
| 파일 | 용도 | 연결 |
|---|---|---|
| `watchdog.py` | 지호 참모 전체 프로젝트 갭 분석 | ✅ weekly_runner.py 매주 월요일 |
| `core/kpi.py` | KPI 동기화 + 주간 리포트 | ✅ daily_auto.py 3.5단계(매일 sync) + weekly_runner.py(주간 리포트) |

---

## 분류 요약

| 분류 | 항목 수 |
|---|---|
| Skills | 21개 (자동 3개 + 수동 18개) |
| MCP | - |
| GitHub 레포 | 4개 (core, llm-guard-app, awesome-design-md, demo) |
| 자동화 스크립트 | 4개 (전부 daily_auto.py 연결 완료) |
| 코어 자동화 모듈 | 15개+ (pipeline 연결) |
| SaaS 모니터링 | 1개 (llm-guard-app, 자동 수정 포함) |
