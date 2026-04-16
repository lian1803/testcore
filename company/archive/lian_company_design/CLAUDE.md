# 리안 컴퍼니 (LIAN COMPANY)

## 프로젝트 유형
개인 툴 (리안 본인 전용)

## 한 줄 정의
단편적인 아이디어를 넣으면, 이사팀이 기획·전략·검증을 자동 수행하고 UltraProduct용 설계서를 뽑아주는 AI 멀티에이전트 오케스트레이션 CLI 프로그램

## 핵심 Pain
아이디어는 계속 나오는데 혼자서 설계·개발·마케팅 전부 할 시간이 없음

## 핵심 가치
"대충 이런 거 만들고 싶어" → 5분 뒤 Claude Code 복붙용 설계서 + 마케팅 플랜 + 구현 지시서 자동 완성

---

## 기술 스택
- 언어: Python 3.11
- AI SDK: Anthropic Python SDK (claude-opus-4-5, claude-sonnet-4-5, claude-haiku-4-5)
- 실행 방식: CLI (python main.py "아이디어") 또는 대화형 (python main.py)
- 저장: outputs/ 폴더에 날짜별 마크다운 파일
- 환경변수: .env (ANTHROPIC_API_KEY)
- venv: lian_company/venv/ (이미 있음)

---

## 에이전트 구성 (9명)

### 오케스트레이터
- **시은 (Sieun)**: Gemini Pro 역할 → claude-sonnet-4-5. 아이디어를 받아 명확화 질문 → 이사팀/실행팀 흐름 총괄 → 리안에게 중간 확인 요청

### 이사팀 (아이디어 평가 → 설계서)
- **서윤 (Seoyun)**: claude-sonnet-4-5. 시장 조사 — 경쟁사, 타겟, Pain Point, 시장 규모
- **민수 (Minsu)**: claude-sonnet-4-5. 전략 수립 — 포지셔닝, 수익모델, 가격 전략
- **하은 (Haeun)**: claude-sonnet-4-5. 검증/반론 — "이미 있는 거 아니야?" 반박 + 차별점 확인
- **준혁 (Junhyeok)**: claude-opus-4-5. 최종 판단 — composite 점수 계산 → Go/No-Go

### 실행팀 (설계서 작성)
- **지훈 (Jihun)**: claude-sonnet-4-5. PRD 작성 — Must Have, User Flow, 화면 목록
- **종범 (Jongbum)**: claude-sonnet-4-5. 구현 지시서 — Claude Code 복붙용 설계서 (기술스택, API, DB 포함)
- **수아 (Sua)**: claude-sonnet-4-5. 마케팅 전략 — 채널, 카피 A/B, 48시간 검증 플랜
- **태호 (Taeho)**: claude-haiku-4-5. 트렌드 스카우팅 — GitHub/HN/ProductHunt 흐름 참조해 트렌드 인사이트 제공

---

## Must Have 기능

### 1. 대화형 아이디어 입력
- `python main.py` → 시은이 아이디어 받고 명확화 질문 (최대 3번)
- `python main.py "아이디어 문장"` → 바로 파이프라인 시작
- 리안이 "진행해" 또는 `[진행해]` 버튼(입력) 하면 이사팀 자동 실행

### 2. 이사팀 자동 실행 (순차)
- 서윤 → 민수 → 하은 → 준혁 순서로 실행
- 각 단계 완료 후 터미널에 실시간 출력
- 준혁의 Go 판단 시 → 실행팀 자동 실행

### 3. 실행팀 자동 실행 (순차)
- 지훈(PRD) → 종범(구현 지시서) → 수아(마케팅) 순서
- 태호는 실행 전 트렌드 인사이트 먼저 제공 (선택적)

### 4. 산출물 파일 자동 저장
```
outputs/YYYY-MM-DD_HHMMSS_[프로젝트명]/
├── 01_시장조사_서윤.md
├── 02_전략_민수.md
├── 03_검증_하은.md
├── 04_최종판단_준혁.json
├── 05_PRD_지훈.md
├── 06_구현지시서_종범.md   ← Claude Code 복붙용
├── 07_마케팅_수아.md
└── 08_트렌드_태호.md
```

### 5. 스트리밍 출력
- 각 에이전트 응답을 실시간으로 터미널에 스트리밍 (stream=True)
- 에이전트 이름 + 역할 헤더 출력 후 응답 스트리밍

---

## Must NOT (범위 외)
- 웹 UI 없음 (CLI만)
- 실제 웹 크롤링 없음 (태호는 LLM 기반 트렌드 분석)
- 자동 배포 없음 (설계서까지만, 실행은 UltraProduct가 함)
- 멀티유저 없음 (리안 혼자)
- DB 없음 (파일 저장만)

---

## 에이전트별 프롬프트 스타일
- 시은: 친근한 말투, 짧은 질문, 리안 스타일(비개발자 CEO)에 맞춤
- 이사팀: 전문적이지만 한국어 자연스럽게, 표 형식 결과
- 실행팀: 개발자가 바로 쓸 수 있는 구체적 출력
- 준혁: composite 점수 (수익성/경쟁/기술난이도/시장성) 테이블 + Go/No-Go 판정

---

## 파일 구조 목표
```
lian_company/
├── main.py              ← 진입점
├── .env                 ← ANTHROPIC_API_KEY
├── .env.example
├── requirements.txt
├── agents/
│   ├── sieun.py         ← 오케스트레이터
│   ├── seoyun.py        ← 시장조사
│   ├── minsu.py         ← 전략
│   ├── haeun.py         ← 검증
│   ├── junhyeok.py      ← 최종판단
│   ├── jihun.py         ← PRD
│   ├── jongbum.py       ← 구현지시서
│   ├── sua.py           ← 마케팅
│   └── taeho.py         ← 트렌드
├── core/
│   ├── pipeline.py      ← 파이프라인 오케스트레이션
│   └── output.py        ← 파일 저장 유틸
└── outputs/             ← 자동 생성
```
