# CPO 분석 - 리안 컴퍼니

## 제품 전략
**아이디어 던지면 AI 이사팀이 설계서까지 뽑아주는 1인 CEO 확장 도구.**
개입 최소화, 결과물 최대화. 리안이 아이디어맨 역할에만 집중할 수 있게 하는 것이 핵심.

---

## 타겟 + Pain

### 타겟
- 리안 (CEO, 비개발자, 마케팅 회사 운영)
- 1인 사용자 (개인 툴)

### Pain
- 아이디어는 많은데 기획/설계/개발/마케팅을 혼자 할 시간 없음
- AI에게 하나하나 지시하는 것도 피곤함
- Claude Code에 복붙할 설계서 퀄리티가 매번 제각각

### 아하 모먼트
**"아이디어 한 줄 치고 5분 기다렸더니 Claude Code 복붙용 구현 지시서가 나왔다"**
- 진입: python main.py "아이디어"
- 아하: outputs/ 폴더에 8개 문서 자동 생성
- 종료: 06_구현지시서_종범.md 복사해서 Claude Code에 붙여넣기

---

## MVP 범위 (Must Have)

1. **CLI 실행**: `python main.py "아이디어"` 한 줄로 시작
2. **8명 에이전트 순차 실행**: 시은(명확화) -> 서윤(시장) -> 민수(전략) -> 하은(검증) -> 준혁(판단) -> 지훈(PRD) -> 종범(구현지시서) -> 수아(마케팅)
3. **스트리밍 출력**: 실시간으로 뭘 하고 있는지 터미널에 보임
4. **파일 자동 저장**: outputs/YYYY-MM-DD_HHmmss_프로젝트명/ 폴더에 마크다운 저장
5. **멀티 AI 분산**: 편향 방지를 위해 Perplexity(서윤), GPT-4o(민수), Gemini(하은), Claude(나머지)

---

## MVP 제외 (나중에)

| 기능 | 제외 이유 |
|------|----------|
| 웹 UI | CLI로 충분. 리안 혼자 쓸 건데 UI 필요 없음 |
| 병렬 실행 | 순차 실행으로 충분. 5~10분 대기 가능 |
| 히스토리 관리 | outputs 폴더에 날짜별로 쌓이면 됨 |
| 에이전트 커스텀 | 프롬프트 하드코딩으로 충분. 나중에 필요하면 YAML화 |
| 자동 Claude Code 연동 | 복붙으로 충분. 자동화는 오버엔지니어링 |

---

## 성공 기준 (KPI)

### 30일 목표
- **실행 성공률 100%**: python main.py 치면 에러 없이 끝까지 돌아감
- **아이디어 3개 이상 처리**: 실제로 3개 이상의 아이디어를 이 파이프라인으로 설계서까지 뽑음
- **Claude Code 연동 성공 1회**: 종범 구현지시서 -> Claude Code -> 실제 동작하는 코드 1회 이상

### 핵심 지표
| 지표 | 측정 방법 | 목표 |
|------|----------|------|
| 실행 완료율 | 에러 없이 끝까지 도는 비율 | 90%+ |
| 소요 시간 | main.py 시작 ~ 파일 저장 완료 | 10분 이내 |
| 구현지시서 품질 | Claude Code가 한 번에 이해하고 코딩 시작하는지 | 수정 1회 이내 |

---

## 배포 블로커 (코드 분석 기반)

### 1. [CRITICAL] Perplexity API 스트리밍 방식 오류
- **파일**: `agents/seoyun.py` (50-61행)
- **문제**: `with perplexity.chat.completions.create(...) as stream:` 문법이 잘못됨
- **원인**: OpenAI 라이브러리의 스트리밍은 context manager(with문)를 지원하지 않음. Anthropic 문법과 혼동.
- **예상 에러**: `AttributeError: __enter__` 또는 스트림 동작 안 함
- **해결 방법**: `stream = perplexity.chat.completions.create(...)` 후 `for chunk in stream:` 으로 변경 (minsu.py 48-59행 참고)

### 2. [CRITICAL] Gemini SDK import 경로 문제 가능성
- **파일**: `agents/haeun.py` (2-3행)
- **문제**: `from google import genai` + `from google.genai import types`
- **원인**: google-generativeai 패키지의 최신 SDK 변경으로 import 경로가 다를 수 있음
- **예상 에러**: `ModuleNotFoundError: No module named 'google.genai'`
- **해결 방법**:
  - 구버전: `import google.generativeai as genai` + `genai.configure(api_key=...)`
  - 신버전: 현재 코드 유지 (설치된 버전 확인 필요)

### 3. [HIGH] 모델 ID 존재 여부 미검증
- **파일**: `agents/junhyeok.py` (5행), `agents/taeho.py` (3행)
- **문제**: `claude-opus-4-6`, `claude-haiku-4-5-20251001` 모델 ID가 실제 존재하는지 확인 안 됨
- **예상 에러**: `anthropic.BadRequestError: Invalid model`
- **해결 방법**: 실제 API 호출로 검증 필요. 잘못되면 `claude-3-5-sonnet-20241022` 등 확인된 ID로 교체

### 4. [MEDIUM] API 키 환경변수 누락 시 에러 메시지 부재
- **파일**: `agents/seoyun.py` (15행), `agents/minsu.py` (15행), `agents/haeun.py` (17행)
- **문제**: `os.getenv("PERPLEXITY_API_KEY")` 등이 None이면 클라이언트 생성 시점에서 에러
- **현상**: 에러 메시지가 "API key missing" 같은 명확한 것이 아니라 암호화된 에러
- **해결 방법**: pipeline.py의 get_client()처럼 명시적 체크 추가

### 5. [LOW] outputs 폴더 미존재 시 자동 생성
- **파일**: `core/output.py` (8-14행)
- **상태**: `os.makedirs(dir_path, exist_ok=True)` 있음 - 이건 OK
- **비고**: 블로커 아님, 정상 동작

---

## CTO에게 요청

### 기술적 확인 필요 사항

1. **[필수] 실제 실행 테스트**
   - `python main.py "테스트 아이디어"` 1회 실행해서 어디서 터지는지 확인
   - 특히 seoyun.py(Perplexity), haeun.py(Gemini) 스트리밍 부분 집중 확인

2. **[필수] 패키지 버전 확인**
   ```bash
   pip show openai google-generativeai anthropic
   ```
   - google-generativeai 버전에 따라 import 문법이 다름

3. **[필수] 모델 ID 유효성 검증**
   - `claude-opus-4-6`, `claude-sonnet-4-6`, `claude-haiku-4-5-20251001` 실제 호출 가능한지
   - Anthropic 콘솔에서 사용 가능 모델 목록 확인

4. **[권장] 에러 핸들링 추가**
   - 각 에이전트별 try-except로 어느 에이전트에서 실패했는지 명확히
   - API rate limit, timeout 대응

5. **[권장] 비용 추정**
   - 1회 실행 시 각 AI별 토큰 사용량 + 예상 비용
   - 특히 Opus 사용하는 준혁은 비용 주의

---

## 최종 판단

### MVP 준비 상태: 70%

| 항목 | 상태 | 비고 |
|------|------|------|
| 코드 골격 | OK | main.py + 8개 에이전트 + pipeline |
| API 키 | OK | .env에 4개 모두 있음 |
| 패키지 | 확인필요 | 설치됐다고 했는데 버전 확인 필요 |
| 스트리밍 문법 | 수정필요 | seoyun.py의 with문 수정 필수 |
| 모델 ID | 확인필요 | 실제 호출해봐야 앎 |

### 다음 액션
1. CTO가 seoyun.py 스트리밍 문법 수정
2. CTO가 `python main.py "테스트"` 1회 실행
3. 에러 나면 해당 부분 수정
4. 에러 없이 끝까지 돌면 MVP 완성

---

*CPO 분석 완료: 2026-03-18*
*작성: Claude Opus (CPO 역할)*
