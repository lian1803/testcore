# PM 계획 — 리안 컴퍼니

## User Stories

| ID | As a... | I want to... | So that... | 우선순위 |
|----|---------|-------------|------------|---------|
| US-01 | 리안 (CEO) | 터미널에 아이디어를 입력하면 | 5분 안에 에러 없이 설계서가 나온다 | Must |
| US-02 | 리안 (CEO) | 각 에이전트 실행 진행상황을 확인하고 | 어디까지 진행됐는지 알 수 있다 | Must |
| US-03 | 리안 (CEO) | 한글 출력이 깨지지 않고 | 결과를 바로 읽을 수 있다 | Must |
| US-04 | 리안 (CEO) | 에러 발생 시 한국어로 메시지를 보고 | 무엇이 문제인지 즉시 파악한다 | Should |
| US-05 | 리안 (CEO) | outputs 폴더에 저장된 파일을 열면 | 각 에이전트 결과가 정리되어 있다 | Should |

---

## 화면 목록 + 라우트

N/A (CLI 프로그램)

---

## API 엔드포인트

| API | 모델 | 사용처 |
|-----|------|--------|
| Perplexity API | sonar-pro | seoyun.py (시장조사) |
| OpenAI API | gpt-4o | minsu.py (전략) |
| Google Generative AI | gemini-2.0-flash | haeun.py (검증) |
| Anthropic API | claude-sonnet-4-6 | sieun.py, jihun.py, jongbum.py, sua.py, taeho.py |
| Anthropic API | claude-opus-4-6 | junhyeok.py (최종판단) |

---

## 개발 태스크 (우선순위 순)

### Backend — P0 (즉시 수정, 없으면 실행 불가)

#### TASK-01: seoyun.py Perplexity 스트리밍 문법 수정
- 파일: `lian_company/agents/seoyun.py` (50-61행)
- 현재 문제: `with` 문법이 Perplexity API와 호환되지 않음
- 수정 내용:
  ```python
  # 현재 (잘못됨)
  with perplexity.chat.completions.create(..., stream=True) as stream:
      for chunk in stream:

  # 수정 후 (올바름)
  stream = perplexity.chat.completions.create(
      model=MODEL,
      messages=[...],
      stream=True
  )
  for chunk in stream:
      text = chunk.choices[0].delta.content or ""
      print(text, end="", flush=True)
      full_response += text
  ```
- 참고: minsu.py의 48-59행과 동일한 방식 적용
- 의존성: 없음
- 예상 소요: 5분

#### TASK-02: main.py Windows UTF-8 인코딩 강제 설정
- 파일: `lian_company/main.py` (상단, 1-14행 사이)
- 현재 문제: Windows에서 한글 출력 시 깨짐
- 수정 내용:
  ```python
  #!/usr/bin/env python3
  """
  리안 컴퍼니 — AI 멀티에이전트 기획 자동화 시스템
  ...
  """
  import sys
  import io
  import os

  # Windows UTF-8 인코딩 강제 설정
  sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
  sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

  # 프로젝트 루트를 경로에 추가
  sys.path.insert(0, os.path.dirname(__file__))
  ```
- 의존성: 없음
- 예상 소요: 3분

---

### Backend — P1 (MVP 포함)

#### TASK-03: core/ui.py 신규 파일 생성 (진행률 + 피드백)
- 파일: `lian_company/core/ui.py` (신규)
- 목적: 진행률 표시, 파일 저장 피드백, 에러 메시지 함수 통합
- 구현 내용:
  ```python
  def print_progress(step: int, total: int, agent_name: str, role: str):
      """에이전트 실행 헤더 출력 (진행률 포함)"""
      print(f"\n{'='*60}")
      print(f"[{step}/{total}] {agent_name} | {role}")
      print(f"{'='*60}")

  def print_save_feedback(filepath: str, agent_name: str):
      """파일 저장 완료 메시지"""
      print(f"✅ {agent_name} 결과 저장: {filepath}")

  def print_error(message: str, detail: str = ""):
      """에러 메시지 출력"""
      print(f"\n❌ 오류: {message}")
      if detail:
          print(f"   상세: {detail}")
  ```
- 의존성: 없음
- 예상 소요: 10분

#### TASK-04: core/pipeline.py 진행률 헤더 통합
- 파일: `lian_company/core/pipeline.py`
- 현재 문제: 각 에이전트마다 개별 print, 진행률 없음
- 수정 내용:
  - `from core.ui import print_progress, print_save_feedback` 추가
  - 각 에이전트 호출 전 `print_progress(n, 8, "에이전트명", "역할")` 추가
    - 태호: `print_progress(1, 8, "태호", "트렌드 분석")`
    - 서윤: `print_progress(2, 8, "서윤", "시장 조사")`
    - 민수: `print_progress(3, 8, "민수", "전략 수립")`
    - 하은: `print_progress(4, 8, "하은", "검증")`
    - 준혁: `print_progress(5, 8, "준혁", "최종 판단")`
    - 지훈: `print_progress(6, 8, "지훈", "PRD 작성")`
    - 종범: `print_progress(7, 8, "종범", "구현 지시서")`
    - 수아: `print_progress(8, 8, "수아", "마케팅 전략")`
  - 각 `save_file()` 호출 후 `print_save_feedback()` 추가
- 의존성: TASK-03 완료 후
- 예상 소요: 15분

#### TASK-05: agents/seoyun.py, minsu.py, haeun.py 에이전트 헤더 제거
- 파일: `lian_company/agents/seoyun.py`, `minsu.py`, `haeun.py`
- 현재 문제: 각 에이전트 내부에 `print("="*60)` 중복 출력
- 수정 내용: 각 파일의 `run()` 함수 내 헤더 출력 부분 제거
  - seoyun.py 8-10행 제거
  - minsu.py 8-10행 제거
  - haeun.py (동일 패턴 확인 후 제거)
- 의존성: TASK-04와 병렬 진행 가능
- 예상 소요: 5분

#### TASK-06: agents/junhyeok.py JSON 파싱 re.DOTALL 강화
- 파일: `lian_company/agents/junhyeok.py` (88행)
- 현재 문제: JSON이 여러 줄일 때 파싱 실패 가능성
- 수정 내용:
  ```python
  # 현재
  json_match = re.search(r'\{[^}]*"verdict"[^}]*\}', full_response)

  # 수정 후
  json_match = re.search(r'\{[^}]*"verdict"[^}]*\}', full_response, re.DOTALL)
  ```
- 의존성: 없음
- 예상 소요: 3분

#### TASK-07: main.py + core/pipeline.py 핵심 에러 한국어 메시지
- 파일: `lian_company/main.py`, `lian_company/core/pipeline.py`
- 수정 내용:
  - main.py `get_client()` 호출 부분 (34-38행):
    ```python
    try:
        client = get_client()
    except ValueError as e:
        print_error("API 키 오류", str(e))
        sys.exit(1)
    except Exception as e:
        print_error("초기화 실패", str(e))
        sys.exit(1)
    ```
  - pipeline.py 각 에이전트 호출 부분 try-except 추가:
    ```python
    try:
        seoyun_result = seoyun.run(context, client)
        context["seoyun"] = seoyun_result
        save_file(output_dir, "01_시장조사_서윤.md", seoyun_result)
        print_save_feedback("01_시장조사_서윤.md", "서윤")
    except Exception as e:
        print_error(f"서윤 실행 실패", str(e))
        print("계속 진행할까? [y/n]: ", end="")
        if input().strip().lower() != 'y':
            raise
        context["seoyun"] = "(에러 발생)"
    ```
- 의존성: TASK-03 완료 후
- 예상 소요: 20분

---

### Backend — P2 (시간 있으면)

#### TASK-08: core/output.py README.md 자동 생성
- 파일: `lian_company/core/output.py`
- 수정 내용:
  ```python
  def create_output_dir(project_name: str) -> str:
      # ... 기존 코드 ...
      os.makedirs(dir_path, exist_ok=True)

      # README 자동 생성
      readme_path = os.path.join(dir_path, "README.md")
      readme_content = f"""# {project_name}

  생성 시각: {timestamp}

  ## 산출물 목록
  - 01_시장조사_서윤.md — Perplexity 실시간 웹 리서치
  - 02_전략_민수.md — GPT-4o 비즈니스 전략
  - 03_검증_하은.md — Gemini 팩트 체크
  - 04_최종판단_준혁.json — Claude Opus 최종 판단
  - 05_PRD_지훈.md — PRD (Product Requirements Document)
  - 06_구현지시서_종범.md — UltraProduct용 CLAUDE.md
  - 07_마케팅_수아.md — 마케팅 전략
  - 08_트렌드_태호.md — 트렌드 분석

  ## 다음 단계
  1. 06_구현지시서_종범.md 열기
  2. UltraProduct 폴더에서 Claude Code 실행
  3. /work 명령어로 자동 개발 시작
  """
      with open(readme_path, "w", encoding="utf-8") as f:
          f.write(readme_content)

      return dir_path
  ```
- 의존성: 없음
- 예상 소요: 10분

#### TASK-09: core/pipeline.py CONDITIONAL-GO 확인 단계 개선
- 파일: `lian_company/core/pipeline.py` (73-75행)
- 현재 문제: CONDITIONAL-GO 시 조건 확인 없이 바로 진행
- 수정 내용:
  ```python
  if junhyeok_result["verdict"] == "CONDITIONAL_GO":
      print(f"\n\n⚠️  준혁 판단: 조건부 GO (점수: {junhyeok_result['score']})")
      print(junhyeok_result["text"])
      print("\n조건을 확인했어. 계속 진행할까? [진행해 / 중단]: ", end="")
      confirm = input().strip()
      if confirm not in ("진행해", "진행", "y", "yes"):
          print(f"\n📁 결과 저장: {output_dir}")
          print("조건부 GO로 중단. 조건 검토 후 다시 실행해줘.")
          return
  ```
- 의존성: 없음
- 예상 소요: 10분

---

## 개발 순서 (의존성 고려)

### Phase 1: P0 수정 (즉시, 병렬 가능)
```
TASK-01 (seoyun.py 문법)  ━━━┓
                              ┣━━ 테스트
TASK-02 (main.py UTF-8)   ━━━┛
```

### Phase 2: P1 인프라 (순차)
```
TASK-03 (ui.py 생성)
    ↓
TASK-04 (pipeline.py 진행률 통합)
    ↓
TASK-05 (에이전트 헤더 제거)
```

### Phase 3: P1 개선 (병렬 가능)
```
TASK-06 (JSON 파싱 강화)  ━━━┓
                              ┣━━ 통합 테스트
TASK-07 (에러 메시지)      ━━━┛
```

### Phase 4: P2 선택 개선 (시간 있으면)
```
TASK-08 (README 자동생성)  ━━━┓
                              ┣━━ 완료
TASK-09 (CONDITIONAL-GO)   ━━━┛
```

---

## 완료 기준 (Definition of Done)

### 필수 (Must)
- [ ] `python main.py "소상공인 인스타 캡션 자동화"` 실행 시 에러 없이 완료
- [ ] 터미널에서 한글 출력이 깨지지 않음
- [ ] 모든 8개 에이전트 응답이 출력됨
- [ ] `outputs/{timestamp}_{프로젝트명}/` 폴더에 8개 파일 저장됨
- [ ] 각 에이전트 실행 시 `[n/8]` 진행률이 표시됨
- [ ] Perplexity API가 정상 작동 (TASK-01 수정 후)

### 권장 (Should)
- [ ] API 키 오류 시 한국어 에러 메시지 출력
- [ ] 각 파일 저장 후 피드백 메시지 표시
- [ ] 준혁 최종판단 JSON 파싱 실패 시에도 진행
- [ ] 네트워크 에러 발생 시 한국어 안내

### 선택 (Could)
- [ ] `outputs/{timestamp}_{프로젝트명}/README.md` 자동 생성
- [ ] CONDITIONAL-GO 시 사용자 확인 단계

---

## 테스트 시나리오

### Scenario 1: 정상 플로우
```bash
cd lian_company
./venv/Scripts/python.exe main.py "소상공인용 AI 상세페이지 생성기"
```
- 예상: 8개 에이전트 순차 실행 → outputs/ 저장 → 완료 메시지

### Scenario 2: API 키 누락
```bash
# .env에서 PERPLEXITY_API_KEY 제거
./venv/Scripts/python.exe main.py "테스트"
```
- 예상: 서윤 단계에서 한국어 에러 메시지 출력

### Scenario 3: NO-GO 판단
```bash
./venv/Scripts/python.exe main.py "시장성 없는 아이디어"
```
- 예상: 준혁 단계에서 NO-GO 판단 → 실행팀 생략 → 완료

### Scenario 4: CONDITIONAL-GO 판단 (P2)
```bash
./venv/Scripts/python.exe main.py "애매한 아이디어"
```
- 예상: 준혁 단계에서 조건 출력 → 사용자 확인 → 진행/중단

---

## 산출물 저장 위치
`C:/Users/lian1/Documents/Work/LAINCP/projects/lian_company/wave2_pm_계획.md`

---

## 참고 자료
- Wave 2 합의문 (CPO + CTO + CDO 토론 결과)
- `/lian_company/agents/` — 에이전트 코드
- `/lian_company/core/` — 파이프라인 로직
- `CLAUDE.md` — 프로젝트 전체 상황 정리

---

**작성**: PM
**날짜**: 2026-03-18
**버전**: 1.0
