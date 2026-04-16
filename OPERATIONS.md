# 리안 컴퍼니 운영 매뉴얼

> 이 문서는 Claude가 자율적으로 시스템을 운영하기 위한 완전한 매뉴얼이다.
> 리안이 "이거 해줘"라고 하면 이 문서를 보고 어떤 플로우를 태울지 스스로 판단해라.
> 마지막 업데이트: 2026-04-04

---

## 0. 빠른 시작 (리안용 치트시트)

### 새 프로젝트 시작 (자동파일럿)
```bash
cd company
./venv/Scripts/python.exe main.py "온라인 마케팅 대행 사업"
# → input() 없이 이사팀 자동 실행 → 보고서가 보고사항들.md에 저장됨
# → 리안은 보고서만 보고 "진행" 또는 "수정해" 한마디
```

### 새 프로젝트 시작 (대화형 — 시은과 대화)
```bash
cd company
./venv/Scripts/python.exe main.py
# → 시은이 질문하면서 명확화 → 이사팀 실행
```

### 매일 운영 루프 (콘텐츠 자동 생성)
```bash
cd company
./venv/Scripts/python.exe -m core.ops_loop daily "프로젝트명"
# → 인스타 캡션 + 블로그 제목 + 영업 DM 자동 생성 → 보고사항들.md
```

### 매주 성과 리뷰
```bash
cd company
./venv/Scripts/python.exe -m core.ops_loop weekly "프로젝트명" "이번 주 성과 데이터"
```

### 영업 결과 입력 (팀 학습)
```bash
cd company
python input_results.py "오늘 미용실 3곳 DM, 1곳 답장, 거절 이유 비싸다"
```

### 전체 팀 현황 확인 (2주마다)
```bash
python company/orchestrate.py
```

### 보고 확인
`보고사항들.md` 열어보기

### 직원 개별 호출
```bash
python company/ask.py 서윤 "양주 미용실 경쟁사 현황"
python company/ask.py 승현 "3차 메시지 개선 방향"
```

---

## 0-1. 이 시스템이 뭐냐

아이디어 하나 → AI 에이전트들이 자동으로 기획→팀 생성→실행→개발→마케팅→운영까지.
리안(CEO, 비개발자)의 개입을 최소화하는 것이 핵심 설계 원칙.
**만들고 끝이 아니라, 배포 후 매일 돌아가는 것이 목표.**

**네 개의 레이어:**
- **Layer 1: 리안 컴퍼니** (`company/`) = 기획 엔진. 아이디어 평가 + 팀 설계 + 지식 주입.
- **Layer 2: UltraProduct** (`.claude/commands/work.md`) = 실행 엔진. 코드 개발 + 배포.
- **Layer 3: 런칭 준비** (`core/launch_prep.py`) = 타겟/상품/가격/채널 구체화.
- **Layer 4: 운영 루프** (`core/ops_loop.py`) = 매일 콘텐츠 + 영업 + 성과 추적.

**핵심 인프라:**
- **회사 DNA** (`company_context.md`) = 모든 에이전트에 자동 주입. 회사가 뭐하는지 알고 일함.
- **리서치 루프** (`core/research_loop.py`) = 작업 전 최신 트렌드 자동 수집.
- **자료 라우팅** (`process_inbox.py`) = 자료 분석 후 해당 팀에 자동 배포.

---

## 1. 할 수 있는 것 전체 목록

리안이 뭘 시키면 아래에서 해당하는 걸 골라서 실행해라.

### 1-A. 새 아이디어 평가
```
"이거 될까?" / "아이디어 하나 있는데" / "시장조사 해줘"
→ 이사팀 파이프라인

자동파일럿 (CLI 인자):
→ python company/main.py "아이디어"
→ input() 없이 자동 실행 → 보고서 보고사항들.md에 저장

대화형 (인자 없이):
→ python company/main.py
→ 시은과 대화하며 명확화 → 이사팀 실행
```
- 시은이 아이디어 명확화 대화
- 태호+서윤 병렬로 트렌드+시장조사
- 민수 전략 수립 (GPT-4o)
- 하은 팩트 검증 (Gemini)
- 민수-하은 토론 + 시은 분석
- 준혁 GO/NO-GO 최종 판단 (Opus)
- GO → 시은이 팀 설계 → 교육팀 호출

### 1-B. 새 팀 만들기
```
"OO팀 만들어" / "이 일 할 팀 필요해"
→ 교육팀
→ python company/build_team.py "팀이름" "팀 목적 상세 설명"
```
**⚠️ 새 팀은 반드시 이 명령어로 만들어야 한다. 수동으로 .py 파일 직접 만들지 마라.**

교육팀이 하는 일:
1. 기존 knowledge/ 확인
2. Opus가 커리큘럼 설계 (에이전트 구성 + 필요 지식 쿼리 설계)
3. Perplexity가 쿼리 병렬 수집 (세계 최고 수준 전문 지식)
4. 수집된 지식을 knowledge/base/에 저장
5. 자동 생성:
   - `company/teams/{팀명}/` — 에이전트 .py + pipeline.py
   - `company/run_{팀명}.py` — 실행 진입점
   - `.claude/agents/{에이전트}.md` — Claude Code 에이전트 정의
   - `회사 조직도.md` — 자동 업데이트

**팀 목적은 최대한 상세하게 쓸수록 좋다.** 기획서가 있으면 기획서 내용을 요약해서 넘겨라.

### 1-C. 기존 팀 실행
```
"오프라인 영업 자료 만들어" / "영업 스크립트 새로 뽑아줘"
→ python company/offline_sales.py "업종"
```
```
"자료 분석해줘" / (자료들/ 폴더에 파일 있으면)
→ python company/process_inbox.py
```
```
온라인 영업 파이프라인 실행 (소상공인 타겟 온라인 영업):
→ python company/run_온라인영업팀.py "업무 내용"
```
```
온라인 콘텐츠 납품 파이프라인 실행 (블로그/인스타/광고 카피 등):
→ python company/run_온라인납품팀.py "업무 내용"
```
```
온라인 마케팅 전략/운영 파이프라인 실행:
→ python company/run_온라인마케팅팀.py "업무 내용"
```
```
교육팀이 만든 팀 실행:
→ python company/run_{팀명}.py "업무 내용"
```

### 1-D. 코드 개발 (UltraProduct)
```
"이거 만들어줘" / "개발해줘" / "앱 만들어" / "사이트 만들어"
→ team/{프로젝트}/ 폴더에서 /work 실행
```
Wave 3부터 시작 (Wave 1-2 기획은 이미 완료된 상태):
- CTO + CDO 병렬 설계
- PM 태스크 분해
- 🔴 리안 컨펌
- FE + BE 병렬 개발
- QA 테스트
- 배포 (상용화만)
- Gemini 독립 검증

**전제조건:** 해당 폴더에 CLAUDE.md + PRD.md 있어야 함.

### 1-E. 자료 처리
```
리안이 자료들/ 폴더에 파일 던져넣으면:
→ python company/process_inbox.py
```
- .txt .md .html → 도윤이 읽고 knowledge/base/ 저장 + 원본 삭제
- .png .jpg .webp .gif .bmp → 분석팀(Gemini) 이미지 분석
- .mp4 .mov .avi .mkv .webm → 분석팀(Gemini) 영상 분석
- .pdf → 현재 스킵 (pdfplumber 미설치)
- 처리 완료 → 보고사항들.md에 자동 보고

### 1-G. 직원 개별 호출

리안이 직원 이름을 부르면 → 해당 직원만 단독으로 스폰해라.

**Claude Code 에이전트 (UltraProduct팀) — Agent tool로 스폰:**
| 이름/키워드 | subagent_type |
|------------|---------------|
| 현우 / CTO / 아키텍처 / 기술 | cto |
| 나은 / CDO / 디자인 / UI | cdo |
| 민준 / FE / 프론트엔드 | fe |
| 정우 / BE / 백엔드 / API | be |
| 소연 / QA / 테스트 / 버그 | qa |
| 유진 / PM / 태스크 | pm |
| 재원 / 재원아 / 리서처 | 재원 (jaewon) |
| 승현 / 승현아 / 전략 | 승현 (seunghyun) |
| 예진 / 예진아 / 카피 | 예진 (yejin) |
| 영진 / 영진아 / 성과 | 영진 (youngjin) |

예시: 리안이 "현우야 이 코드 아키텍처 봐줘" → `Agent(subagent_type="cto", prompt="...")`

**온라인팀 에이전트 — run_{팀명}.py 직접 실행 또는 pipeline.py 임포트:**
| 팀 | 이름/역할 | 실행 방법 |
|----|----------|---------|
| 온라인영업팀 | 박탐정/이진단/김작가/최제안/정클로저/한총괄 | `python run_온라인영업팀.py "업무"` |
| 온라인납품팀 | 서진호/한서연/박지우/최도현/윤하은/정민재/김태리 | `python run_온라인납품팀.py "업무"` |
| 온라인마케팅팀 | 서진혁/한소율/윤채원/박시우/이도현/강하린 | `python run_온라인마케팅팀.py "업무"` |

**Python 에이전트 (이사팀) — ask.py로 호출:**
```bash
cd company
./venv/Scripts/python.exe ask.py "서윤" "네이버 플레이스 시장 규모 알려줘"
./venv/Scripts/python.exe ask.py "민수" "이 수익모델 분석해줘"
./venv/Scripts/python.exe ask.py "하은" "이 데이터 팩트체크 해줘"
./venv/Scripts/python.exe ask.py "준혁" "이 아이디어 GO/NO-GO 판단해줘"
./venv/Scripts/python.exe ask.py "태호" "요즘 SNS 마케팅 트렌드 알려줘"
./venv/Scripts/python.exe ask.py "시은" "이 아이디어 명확화 도와줘"
```

| 이름 | ask.py 키 |
|------|---------|
| 서윤 / 서윤아 / 시장조사 | 서윤 |
| 민수 / 민수야 / 전략 / 수익모델 | 민수 |
| 하은 / 하은아 / 팩트체크 / 검증 | 하은 |
| 준혁 / 준혁아 / GO판단 | 준혁 |
| 태호 / 태호야 / 트렌드 | 태호 |
| 시은 / 시은아 | 시은 |

**피드백 주기 (직원 성장):**
```bash
./venv/Scripts/python.exe ask.py --feedback "직원이름" "점수(1~5)" "피드백 내용"
```

**성과 현황 조회:**
```bash
./venv/Scripts/python.exe ask.py --performance
```

**자기 개발 실행 (낮은 평점 받은 분야 자동 학습):**
```bash
./venv/Scripts/python.exe ask.py --train "직원이름"   # 특정 직원
./venv/Scripts/python.exe ask.py --train all           # 전체 직원
```
→ Perplexity가 부족한 분야 리서치 → `knowledge/agents/{이름}/training/` 저장 → 다음 업무 시 자동 반영

---

### 1-F. 네이버 진단 도구 (오프라인 마케팅)
```
"진단 돌려줘" / "네이버 플레이스 분석" / "PPT 만들어"
→ team/[진행중] 오프라인 마케팅/소상공인_영업툴/naver-diagnosis/
→ python main.py (또는 uvicorn main:app --reload)
→ http://localhost:8000
```
- 소상공인 검색 → 네이버 플레이스 크롤링 → 7개 항목 점수화 → A~D 등급
- 자동 생성: 7슬라이드 PPT + 4단계 영업 메시지
- 배치 처리 (엑셀 업로드) 가능

---

## 2. 직원 목록 (에이전트)

### 이사팀 (company/agents/)
| 이름 | AI | 역할 | 파일 |
|------|-----|------|------|
| 시은 | Claude Sonnet | 오케스트레이터, 아이디어 명확화, 인터뷰, 팀 설계 | sieun.py |
| 태호 | Claude Haiku | 트렌드 스카우팅 | taeho.py |
| 서윤 | Perplexity | 실시간 시장조사, 지식 수집 | seoyun.py |
| 민수 | GPT-4o | 전략/수익모델 | minsu.py |
| 하은 | Gemini | 팩트 검증/반론 | haeun.py |
| 준혁 | Claude Opus | GO/NO-GO 최종 판단 | junhyeok.py |

### 교육팀 (company/teams/education/)
| 이름 | AI | 역할 | 파일 |
|------|-----|------|------|
| 도윤 | Claude Opus | 커리큘럼 설계 | curriculum_designer.py |
| 서윤 | Perplexity | 전문 지식 수집 (겸직) | trainer.py |

### 분석·마케팅팀 (company/teams/)
| 이름 | AI | 역할 | 파일 |
|------|-----|------|------|
| 지수 | Gemini Vision | 이미지/영상 분석 | analysis/analyzer.py |
| 재원 | Perplexity | 영업 자료 수집 (오프라인) | offline_marketing/researcher.py |
| 승현 | Claude Sonnet | 영업 전략 설계 (오프라인) | offline_marketing/strategist.py |
| 예진 | Claude Sonnet | DM/스크립트/카피 (오프라인) | offline_marketing/copywriter.py |

### 온라인영업팀 (company/teams/온라인영업팀/) — build_team.py 자동생성 2026-04-02
| 이름 | AI | 역할 | 파일 |
|------|-----|------|------|
| 박탐정 | Claude Sonnet | 잠재고객 분석·식별 기준 설계 | 박탐정.py |
| 이진단 | Claude Sonnet | 온라인 현황 무료 진단서 자동 생성 | 이진단.py |
| 김작가 | Claude Sonnet | 인스타DM·이메일 아웃리치 스크립트 | 김작가.py |
| 최제안 | Claude Sonnet | 맞춤 제안서 및 3Tier 가격표 | 최제안.py |
| 정클로저 | Claude Sonnet | 30분 미팅 대본 및 거절 대응 스크립트 | 정클로저.py |
| 한총괄 | Claude Sonnet | 전체 영업 파이프라인 품질 관리 | 한총괄.py |

### 온라인납품팀 (company/teams/온라인납품팀/) — build_team.py 자동생성 2026-04-02
| 이름 | AI | 역할 | 파일 |
|------|-----|------|------|
| 서진호 | Claude Sonnet | SEO 키워드 전략가 | 서진호.py |
| 한서연 | Claude Sonnet | 네이버 블로그 포스팅 작가 | 한서연.py |
| 박지우 | Claude Sonnet | 인스타그램 콘텐츠 크리에이터 | 박지우.py |
| 최도현 | Claude Sonnet | 퍼포먼스 광고 카피라이터 | 최도현.py |
| 윤하은 | Claude Sonnet | 상세페이지·스마트스토어 카피라이터 | 윤하은.py |
| 정민재 | Claude Sonnet | 성과 분석·리포트 매니저 | 정민재.py |
| 김태리 | Claude Sonnet | 납품 총괄 PM | 김태리.py |

### 온라인마케팅팀 (company/teams/온라인마케팅팀/) — build_team.py 자동생성 2026-04-02
| 이름 | AI | 역할 | 파일 |
|------|-----|------|------|
| 서진혁 | Claude Sonnet | 리드 헌터 — 잠재 셀러 발굴 | 서진혁.py |
| 한소율 | Claude Sonnet | 세일즈 매니저 — 콜드아웃리치·클로징 | 한소율.py |
| 윤채원 | Claude Sonnet | 마케팅 전략가 — 채널별 전략 | 윤채원.py |
| 박시우 | Claude Sonnet | 크리에이티브 디렉터 — 카피·콘텐츠 | 박시우.py |
| 이도현 | Claude Sonnet | 운영 매니저 — 납품·스케줄링·보고 | 이도현.py |
| 강하린 | Claude Sonnet | 그로스 애널리스트 — 성과·개선 | 강하린.py |

### UltraProduct 팀 (.claude/agents/)
| 이름 | AI | 역할 | 파일 |
|------|-----|------|------|
| 현우 | Sonnet | CTO — 기술 아키텍처 | cto.md |
| 나은 | Sonnet | CDO — Stitch 디자인 | cdo.md |
| 유진 | Haiku | PM — 태스크 분해 | pm.md |
| 민준 | Sonnet | FE — 프론트엔드 | fe.md |
| 정우 | Sonnet | BE — 백엔드 | be.md |
| 소연 | Sonnet | QA — 테스트 | qa.md |
| 재현 | Gemini | 독립 검증 | (Wave 7) |
| 도현 | Opus | 시스템 아키텍트 — CLAUDE.md/에이전트 수정 | architect.md |
| DevOps | Sonnet | 도구 수집가 — 패키지/MCP 자동 설치 (Wave 3.5) | devops.md |
| 지호 | Opus | 참모(CoS) — 전체 프로젝트 갭 분석, 빠진 것 찾기 | coos.md |

---

## 3. 의사결정 트리 — 리안이 뭘 시키면 어떻게 하냐

```
리안의 요청
    │
    ├─ "아이디어 평가해줘" / "이거 될까?"
    │   → 1-A. python main.py "아이디어"
    │
    ├─ "OO팀 만들어" / "이 일 할 사람 필요해"
    │   → 1-B. 기획서 작성 → python build_team.py
    │   ⚠️ 절대 수동으로 팀 코드 작성하지 마라
    │
    ├─ "개발해줘" / "사이트 만들어" / "앱 만들어"
    │   → 1-D. 해당 team/ 폴더에서 /work
    │   → PRD.md 없으면 먼저 1-A 또는 기획 필요
    │
    ├─ "영업 자료 만들어" / "스크립트 뽑아줘" / "DM 써줘"
    │   → 1-C. 해당 팀 파이프라인 실행
    │   오프라인: python offline_sales.py "업종"
    │   온라인영업: python run_온라인영업팀.py "업무"
    │   온라인납품: python run_온라인납품팀.py "업무"
    │   온라인마케팅: python run_온라인마케팅팀.py "업무"
    │
    ├─ "이 자료 분석해" / (자료들/ 폴더에 뭔가 있을 때)
    │   → 1-E. python process_inbox.py
    │
    ├─ "네이버 진단" / "PPT" / "소상공인 분석"
    │   → 1-F. naver-diagnosis 실행
    │
    ├─ "조직 변경" / "팀원 추가/삭제" / "모델 변경"
    │   → 회사 조직도.md + zip/src/App.tsx 동시 수정 + 빌드 배포
    │
    ├─ 직원 이름 + 업무 요청 ("현우야 이거 봐줘" / "서윤아 조사해줘" 등)
    │   → 1-G. 직원 개별 호출
    │
    ├─ "시스템 바꿔줘" / "에이전트 수정해줘" / "플로우 업그레이드해줘"
    │   → 1-H. 도현(아키텍트) 호출 → Agent(subagent_type="architect")
    │
    ├─ "전체 상황 봐줘" / "뭐 빠진 거 없어?" / "지호야 체크해줘"
    │   → 1-I. 지호(참모) 호출 → Agent(subagent_type="coos")
    │       또는 python company/watchdog.py
    │
    └─ 기타
        → CLAUDE.md 규칙에 따라 판단
        → 모르겠으면 리안에게 물어봐라
```

---

## 4. 지식 시스템

### 구조
```
knowledge/
├── manager.py       ← API (저장/검색/피드백/보고)
├── index.json       ← 전체 인덱스
├── base/            ← 공유 지식 (7개 문서, ~450KB)
│   ├── AI기초_비즈니스활용.md
│   ├── AI툴심화_자기강화루프.md
│   ├── UX_설계원칙_완전판.md
│   ├── 린스타트업_방법론_완전판.md
│   ├── 마케팅퍼널_완전가이드.md
│   ├── 서비스기획_원칙_완전판.md
│   └── 프로토타이핑_IA_UJ_PRD_가이드.md
├── teams/           ← 팀별 결과물 + 피드백
└── trends/          ← ❌ 미구현
```

### 지식 흐름
1. 교육팀이 Perplexity로 수집 → `knowledge/base/`에 저장
2. 팀 실행 결과물 → `knowledge/teams/{팀명}/`에 저장
3. 리안 피드백 → `knowledge/teams/{팀명}/feedback/`에 저장
4. 새 팀 생성 시 → 관련 지식 자동 검색 → 에이전트 프롬프트에 주입

### 사용 가능한 API (knowledge/manager.py)
```python
from knowledge.manager import (
    save_base_knowledge,      # 공유 지식 저장
    save_team_result,         # 팀 결과물 저장
    save_feedback,            # 피드백 저장
    get_knowledge_for_team,   # 팀 관련 지식 검색
    write_report,             # 보고사항들.md에 보고
    collect_feedback,         # 리안 피드백 수집
)
```

---

## 5. 실행 환경

### API 키 (.env)
```
위치: company/.env
상태: ✅ 전부 설정됨 (2026-04-01 확인)

ANTHROPIC_API_KEY    → Claude 모델 전체
OPENAI_API_KEY       → GPT-4o (민수)
GOOGLE_API_KEY       → Gemini (하은, 도윤, 지수)
PERPLEXITY_API_KEY   → Perplexity (서윤, 재원)
DISCORD_WEBHOOK_URL  → 디스코드 알림 (선택)
```

### Python 실행
```bash
# company 내 모든 스크립트:
cd company
./venv/Scripts/python.exe {스크립트}.py

# naver-diagnosis:
cd team/[진행중]\ 오프라인\ 마케팅/소상공인_영업툴/naver-diagnosis/
./venv/Scripts/python.exe main.py
```

### 모델 상수 (core/models.py)
```python
CLAUDE_OPUS   = "claude-opus-4-6"
CLAUDE_SONNET = "claude-sonnet-4-6"
CLAUDE_HAIKU  = "claude-haiku-4-5-20251001"
GEMINI_FLASH  = "gemini-2.5-flash"
GEMINI_PRO    = "gemini-2.5-pro"
GPT4O         = "gpt-4o"
SONAR_PRO     = "sonar-pro"
```
→ 모델 변경 시 여기만 수정하면 전체 반영.

### 자동 Git Hook
```
.claude/settings.json에 설정됨:
파일 Edit/Write 할 때마다 → git add -A → git commit → git push
```

---

## 6. 프로젝트 현황

| 프로젝트 | 위치 | 상태 |
|----------|------|------|
| 오프라인 마케팅 | `team/[진행중] 오프라인 마케팅/` | ✅ 진행중 (naver-diagnosis 운영중, 레퍼런스 클라이언트 대기) |
| 온라인 마케팅 (3팀 완성) | `company/teams/온라인{영업/납품/마케팅}팀/` | ✅ 팀 생성 완료 (2026-04-02), 실행 대기 중 |
| 혜경님 인하우스 마케터 (Lian Dash) | `team/[혜경님] 인하우스_마케터_및_프리랜서를_위한/lian-dash/` | ✅ Vercel 배포 완료 (https://lian-dash.vercel.app, mock 데이터) |
| 고객-마케터 플랫폼 | `team/[중단] 고객이랑 마케터랑 이어주는 플랫폼/` | ⏸️ 중단 |
| 구매대행 자동화 | `team/[중단] 구매대행 자동화/` | ⏸️ 중단 |
| 백로그 | `team/[중단] 나중에 할것들(지금 할거 아님)/` | ⏸️ 대기 |

---

## 7. 새 팀 만드는 전체 플로우 (상세)

이건 가장 중요한 플로우이므로 상세하게 기록한다.

### Step 1: 기획서 작성
- 리안이 "OO팀 만들어"라고 하면
- Claude가 먼저 Perplexity로 해당 도메인 조사
- 조사 결과를 바탕으로 `team/{팀명}/기획서.md` 작성
- 리안 검토 + 수정

### Step 2: 교육팀 실행
```bash
cd company
./venv/Scripts/python.exe build_team.py "팀이름" "팀 목적 (기획서 요약)"
```
- 팀 목적은 기획서 핵심을 요약한 텍스트. 길수록 좋다.
- Opus가 에이전트 구성 + 지식 쿼리 설계
- Perplexity가 지식 수집
- 코드 자동 생성

### Step 3: 자동 생성 결과물
```
company/teams/{팀명}/
├── __init__.py
├── pipeline.py           ← 팀 실행 로직
├── {에이전트1}.py        ← 지식 주입된 에이전트
├── {에이전트2}.py
└── ...

company/run_{팀명}.py   ← 실행 진입점
.claude/agents/{에이전트}.md  ← Claude Code 에이전트 정의
회사 조직도.md               ← 자동 업데이트됨
```

### Step 4: 팀 실행
```bash
cd company
./venv/Scripts/python.exe run_{팀명}.py "업무 내용"
```
- 팀 인터뷰 (리안한테 질문)
- 에이전트 순차 실행
- 결과물 `team/{팀명}/`에 저장
- 보고사항들.md에 자동 보고
- 리안 피드백 수집

---

## 8. 슬래시 커맨드

| 명령어 | 기능 | 위치 |
|--------|------|------|
| `/work` | UltraProduct Wave 3-7 실행 (Wave 3.5 DevOps 포함) | .claude/commands/work.md |
| `/setup` | 첫 설치 세팅 | .claude/commands/setup.md |
| `/save` | 세션 저장 | .claude/commands/save.md |
| `/shell` | /work와 동일 | .claude/commands/shell.md |
| `/brand-guidelines` | 브랜드 가이드라인 | .claude/commands/brand-guidelines.md |
| `/frontend-design` | 컴포넌트 구조 설계 | .claude/commands/frontend-design.md |
| `/theme-factory` | 컬러+폰트 확정 | .claude/commands/theme-factory.md |

---

## 9. 법적 제한 (마케팅 관련)

이 시스템으로 마케팅 팀을 만들 때 반드시 지켜야 할 법률:

| 항목 | 제한 | 안전한 대안 |
|------|------|-------------|
| 콜드 이메일 | 수신동의 없는 광고 메일 = 과태료 3천만원 (정보통신망법 50조) | 명함 교환 후 6개월 내만 / 정보 제공 형태 |
| 네이버 크롤링 | DB권 침해 + 개인정보보호법 위반 위험 | 수동 검색만, 자동 스크래핑 금지 |
| 인스타 DM 자동화 | 비공식 봇 = 계정 정지 | Manychat/소셜비즈 등 메타 공식 파트너만 |
| 카카오톡 | 스팸 발송 = 통신규제 위반 | 카카오 비즈메시지(채널 친구)만 |
| 블로그 자동 포스팅 | 네이버 API 없음, Selenium = 약관 위반 | AI 작성 + 수동 업로드 |

---

## 10. 트러블슈팅

| 문제 | 원인 | 해결 |
|------|------|------|
| main.py 실행 안 됨 | .env 없거나 키 오류 | company/.env 확인 |
| Perplexity 에러 | API 키 만료 or 한도 | PERPLEXITY_API_KEY 확인 |
| 교육팀 생성 실패 | Opus 호출 실패 | ANTHROPIC_API_KEY 확인 + 잔액 |
| naver-diagnosis 크롤링 실패 | Playwright 브라우저 없음 | `playwright install chromium` |
| Git push 실패 | 원격 연결 안 됨 | `git remote -v` 확인 |
| knowledge/base/ 비어있음 | 교육팀 미실행 | process_inbox.py 또는 build_team.py 실행 |

---

## 11. 이 문서 관리 규칙

> **2026-04-03 아키텍처 노트:**
> 에이전트 16명 워크샵 완료 — 온라인영업팀(6명), 온라인납품팀(7명), 온라인마케팅팀(6명) 모두 build_team.py로 자동 생성됨.
> 이 팀들은 `company/teams/` 아래에 있고 `run_{팀명}.py`로 실행.
> 조직도에 반영됨 (`회사 조직도.md` 2026-04-02 변경이력 참고).



- 새 팀이 생기면 → 2번(직원 목록) + 6번(프로젝트 현황) 업데이트
- 새 명령어가 생기면 → 1번(할 수 있는 것) + 8번(슬래시 커맨드) 업데이트
- 새 파이프라인이 생기면 → 3번(의사결정 트리) 업데이트
- 법적 제한 변경 → 9번 업데이트
- **이 문서가 코드와 불일치하면 → 코드가 진실, 문서를 수정해라**
