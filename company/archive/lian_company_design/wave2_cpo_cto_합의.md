# CPO-CTO 합의문

## 토론 요약

### CPO 입장
- MVP 준비도 70%, 코드 골격 완성
- 배포 블로커: seoyun.py Perplexity 스트리밍 문법 오류
- UX 측면: 리안(비개발자)이 진행 상황 파악 필요 -> 진행률 표시 중요
- 에러 발생 시 리안이 직접 해결 불가 -> 한국어 에러 메시지 필요

### CTO 입장
- P0: seoyun.py `with` context manager 제거 필수
- 이모지 처리: UTF-8 강제가 이모지 전체 제거보다 효율적
- 진행률 표시: 구현 복잡도 낮음 (10분)
- JSON 파싱 강화: 복잡도 낮음 (5분)

### 합의 과정
1. **이모지 처리**: CPO는 UX 직관성 위해 유지 선호, CTO는 UTF-8 강제가 빠르다고 판단 -> UTF-8 강제로 합의
2. **진행률 표시**: CPO 강력 요청, CTO 구현 복잡도 낮음 확인 -> MVP 포함
3. **에러 메시지**: CPO 필요성 제기, CTO는 최소 범위(API 키, 네트워크)로 제한 제안 -> 핵심 에러만 MVP 포함
4. **README 자동생성**: CPO도 MVP에 과하다고 동의 -> 제외

---

## 즉시 수정 (P0 - Wave 3에서 필수)

### 1. seoyun.py Perplexity 스트리밍 수정
**문제**: `with` context manager가 Perplexity API에서 미지원
**해결**: minsu.py 방식으로 변경

```python
# AS-IS (오류)
with perplexity.chat.completions.create(..., stream=True) as stream:
    for chunk in stream:
        ...

# TO-BE (정상)
stream = perplexity.chat.completions.create(..., stream=True)
for chunk in stream:
    ...
```

### 2. Windows 콘솔 UTF-8 인코딩 강제
**문제**: Windows 콘솔에서 이모지 출력 시 인코딩 에러 가능
**해결**: main.py 상단에 추가

```python
import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
```

---

## MVP 포함 (P1 - Wave 3에서 구현)

### 1. 진행률 표시
**이유**: 리안이 "지금 어디쯤인지" 알아야 불안하지 않음
**구현**: pipeline.py에서 각 에이전트 실행 전 출력

```
[1/8] 태호 - 트렌드 분석 중...
[2/8] 서윤 - 시장 조사 중...
[3/8] 민수 - 전략 수립 중...
...
```

### 2. junhyeok.py JSON 파싱 강화
**문제**: 멀티라인 JSON 응답 시 파싱 실패 가능
**해결**: 정규식 개선 또는 마지막 JSON 블록 추출 로직

```python
# 개선된 정규식
json_match = re.search(r'\{[^{}]*"verdict"[^{}]*\}', full_response, re.DOTALL)
```

### 3. 핵심 에러 한국어 메시지
**범위**: API 키 없음, 네트워크 에러만
**구현**: pipeline.py의 get_client() 및 각 에이전트 run()에 try-except

```python
# 예시
except Exception as e:
    if "API" in str(e) or "key" in str(e).lower():
        print("[오류] API 키가 없거나 잘못됐어. .env 파일 확인해줘.")
    elif "connect" in str(e).lower() or "timeout" in str(e).lower():
        print("[오류] 네트워크 연결 실패. 인터넷 상태 확인해줘.")
    else:
        print(f"[오류] {e}")
    raise
```

---

## MVP 제외 (나중에)

| 항목 | 제외 이유 |
|------|----------|
| outputs/ README.md 자동생성 | MVP 핵심 가치와 무관, 나중에 추가 가능 |
| CONDITIONAL-GO 확인 단계 | 이미 pipeline.py line 73-75에 구현됨 (추가 구현 불필요) |
| 상세 에러 복구 가이드 | 모든 에러 케이스 커버는 과함, MVP 후 피드백 기반 추가 |

---

## Wave 3 BE 지시사항

BE 에이전트는 아래 항목을 순서대로 수정/구현할 것:

### P0 (필수 - 먼저 완료)
1. **seoyun.py** (line 50-61): `with` context manager 제거, minsu.py 방식으로 변경
2. **main.py** 상단: Windows UTF-8 인코딩 강제 코드 추가

### P1 (MVP 포함)
3. **pipeline.py**: 각 에이전트 실행 전 진행률 출력 추가
   - 형식: `[n/8] {에이전트명} - {작업내용} 중...`
   - 적용 위치: taeho, seoyun, minsu, haeun, junhyeok, jihun, jongbum, sua 각각 앞

4. **junhyeok.py** (line 88): JSON 파싱 정규식 개선
   - `re.DOTALL` 플래그 추가 또는 더 견고한 패턴 적용

5. **pipeline.py**: get_client() 및 run_pipeline() 에 try-except 추가
   - API 키 없음 -> 한국어 메시지
   - 네트워크 에러 -> 한국어 메시지

### 수정 파일 목록
- `lian_company/main.py`
- `lian_company/agents/seoyun.py`
- `lian_company/agents/junhyeok.py`
- `lian_company/core/pipeline.py`

### 테스트 명령어
```bash
cd C:/Users/lian1/Documents/Work/LAINCP/lian_company
./venv/Scripts/python.exe main.py "테스트 아이디어"
```

---

## 서명

- **CPO**: 합의 완료 (2026-03-18)
- **CTO**: 합의 완료 (2026-03-18)

---

## 다음 단계
1. PM이 이 합의문 기반으로 Wave 3 작업 계획 수립
2. BE가 P0 -> P1 순서로 수정 진행
3. QA가 수정 후 테스트 실행
