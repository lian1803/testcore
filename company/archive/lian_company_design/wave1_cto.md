# CTO 분석 - 리안 컴퍼니 Python CLI

## 기술 스택 결정

| 항목 | 선택 | 이유 |
|------|------|------|
| 언어 | Python 3.11 | CLI 툴에 적합, SDK 호환성 |
| 패키지 관리 | venv | 가벼운 프로젝트에 적합 |
| Claude API | anthropic SDK | 공식 SDK, streaming 지원 |
| GPT API | openai SDK | 공식 SDK |
| Perplexity API | openai SDK (호환) | OpenAI 호환 API |
| Gemini API | google-genai | 신규 SDK (google-generativeai 아님) |
| 환경변수 | python-dotenv | 표준적 선택 |

---

## 아키텍처

```
                    main.py (Entry Point)
                         |
                         v
               +--------------------+
               |  sieun.py          |
               |  (오케스트레이터)   |
               |  Claude Sonnet     |
               +--------------------+
                         |
                         v
              "진행해" 확인 -> pipeline.py
                         |
    +--------------------+--------------------+
    |                    |                    |
    v                    v                    v
+--------+        +-----------+        +----------+
| 이사팀  |        |  실행팀    |        |  산출물   |
+--------+        +-----------+        +----------+
    |                    |                    |
    v                    v                    v
[순차 실행]          [순차 실행]         output.py
                                              |
taeho.py (Haiku)     jihun.py (Sonnet)       v
    |                    |              outputs/
    v                    v              [timestamp]/
seoyun.py (Perplexity)  jongbum.py (Sonnet)
    |                    |
    v                    v
minsu.py (GPT-4o)    sua.py (Sonnet)
    |
    v
haeun.py (Gemini)
    |
    v
junhyeok.py (Opus)
    |
    v
GO/NO_GO 판단
```

---

## Engineering Rules (에이전트 개발 규칙)

### 필수 준수
1. **API 키 환경변수**: 각 에이전트는 `os.getenv()`로 자신의 API 키만 사용
2. **Streaming 필수**: 모든 AI 호출은 streaming 방식으로 (UX를 위해)
3. **Context 전달**: `run(context: dict, client=None)` 시그니처 통일
4. **파일 저장**: UTF-8 인코딩 필수 (`encoding="utf-8"`)
5. **에러 핸들링**: API 키 누락시 명확한 에러 메시지

### 코드 규칙
6. **모델 ID 상수화**: 각 파일 상단에 `MODEL = "..."` 선언
7. **프롬프트 분리**: `SYSTEM_PROMPT` 상수로 분리
8. **반환값 명시**: 순수 텍스트 반환 (junhyeok만 dict)

---

## 기술 리스크 + 해결 방법

| 리스크 | 심각도 | 해결 방법 |
|--------|--------|---------|
| Perplexity streaming context manager 미지원 | **높음** | `with` 문 제거, 직접 iteration |
| Windows 이모지 출력 깨짐 | 중간 | `chcp 65001` 또는 이모지 제거 |
| Gemini SDK import 경로 | 낮음 | 현재 `google.genai` 사용 중 (정상) |
| junhyeok JSON 파싱 실패시 기본값 | 낮음 | 기본값 GO로 설정됨 (의도적) |
| API 타임아웃 처리 없음 | 중간 | timeout 파라미터 추가 권장 |

---

## 당장 수정이 필요한 코드 이슈 (우선순위 순)

### P0 (즉시 수정 - 실행 불가)

#### 1. seoyun.py - Perplexity streaming context manager 오류
**파일**: `agents/seoyun.py` (line 50-61)
**문제**: OpenAI SDK의 `chat.completions.create(stream=True)`는 context manager를 지원하지 않음
**현재 코드**:
```python
with perplexity.chat.completions.create(..., stream=True) as stream:
    for chunk in stream:
```
**수정 필요**:
```python
stream = perplexity.chat.completions.create(..., stream=True)
for chunk in stream:
```

---

### P1 (높은 우선순위 - 실행은 되지만 문제 발생 가능)

#### 2. main.py / pipeline.py - Windows 이모지 출력 문제
**파일**: `main.py`, `pipeline.py`, 모든 agents/*.py
**문제**: Windows CMD/PowerShell에서 이모지 출력시 `UnicodeEncodeError` 발생 가능
**영향받는 라인**:
- main.py: 37, 43, 45
- pipeline.py: 27, 67, 74, 80, 100, 101
- 모든 에이전트 print 문

**해결 방안**:
1. 방법 A: 이모지 제거하고 ASCII로 대체 (`[OK]`, `[!]`, `[x]`)
2. 방법 B: main.py 상단에 `sys.stdout.reconfigure(encoding='utf-8')` 추가
3. 방법 C: 환경변수 `PYTHONIOENCODING=utf-8` 설정

#### 3. junhyeok.py - JSON 파싱 정규식 개선 필요
**파일**: `agents/junhyeok.py` (line 88-95)
**문제**: JSON이 여러 줄에 걸쳐 있으면 파싱 실패
**현재 정규식**: `r'\{[^}]*"verdict"[^}]*\}'`
**권장 개선**:
```python
json_match = re.search(r'\{"verdict":\s*"[^"]+",\s*"score":\s*[\d.]+\}', full_response)
```
또는 마지막 `{...}` 블록을 찾는 방식

#### 4. pipeline.py - junhyeok 결과 접근시 KeyError 위험
**파일**: `core/pipeline.py` (line 54-56)
**문제**: `junhyeok.run()`이 예외 발생시 dict 반환 보장 안됨
**현재 코드**:
```python
context["junhyeok_text"] = junhyeok_result["text"]
context["verdict"] = junhyeok_result["verdict"]
context["score"] = junhyeok_result["score"]
```
**권장**: try-except 또는 `.get()` 사용

---

### P2 (중간 우선순위 - 개선 권장)

#### 5. 모든 에이전트 - API 타임아웃 미설정
**문제**: 네트워크 문제시 무한 대기
**권장**: 각 API 호출에 timeout 파라미터 추가

#### 6. haeun.py - Gemini streaming 응답 None 체크
**파일**: `agents/haeun.py` (line 54)
**현재**: `text = chunk.text or ""`
**상태**: 정상 (None 체크 있음)

#### 7. output.py - 프로젝트명 특수문자 처리 불완전
**파일**: `core/output.py` (line 7)
**현재**: `/`, `\`, ` ` 만 처리
**누락**: `:`, `?`, `*`, `"`, `<`, `>`, `|` (Windows 금지 문자)

---

### P3 (낮은 우선순위 - 향후 개선)

#### 8. sieun.py - 모델 ID 미래 호환성
**파일**: `agents/sieun.py`, `jihun.py`, `jongbum.py`, `sua.py` (line 3)
**현재**: `claude-sonnet-4-6`
**확인 필요**: 모델 ID가 최신인지 확인 (claude-sonnet-4-20250514 형식일 수 있음)

#### 9. taeho.py - Haiku 모델 ID
**파일**: `agents/taeho.py` (line 3)
**현재**: `claude-haiku-4-5-20251001`
**상태**: 버전 명시됨 (정상)

---

## CDO에게 요청

1. **CLI 출력 디자인**: 이모지 대신 ASCII 기반 아이콘 사용 검토 필요 (Windows 호환성)
   - 예: `[*]`, `[+]`, `[-]`, `[!]` 등
2. **진행 상태 표시**: 현재 "=" 구분선만 있음. 프로그레스 표시 고려

---

## CPO에게 피드백

1. **GO/NO-GO 기본값 재검토**: junhyeok JSON 파싱 실패시 기본값이 `GO`로 설정됨. 안전을 위해 `NO_GO`가 나을 수 있음
2. **에러 발생시 사용자 경험**: API 오류 발생시 어떻게 처리할지 정책 필요
3. **병렬 실행 가능성**: 현재 이사팀 순차 실행이나, seoyun/minsu/haeun 병렬 실행 가능 (단, 의존성 있음)

---

## 검증 완료 항목

| 항목 | 상태 | 비고 |
|------|------|------|
| haeun.py Gemini SDK | OK | `google.genai` 사용, streaming 정상 |
| junhyeok.py verdict/score 파싱 | OK | pipeline.py와 호환됨 |
| 파일 인코딩 | OK | UTF-8 명시됨 |
| 환경변수 로딩 | OK | dotenv 정상 사용 |

---

## 요약: 즉시 수정 필요 사항

```
1. seoyun.py line 50: "with" 문 제거 (P0 - 실행 불가)
2. Windows 이모지 처리 (P1 - 환경 의존)
3. junhyeok.py JSON 파싱 개선 (P1 - 엣지케이스)
```

---

*CTO 분석 완료: 2026-03-18*
*분석 대상: 리안 컴퍼니 Python CLI v1.0*
