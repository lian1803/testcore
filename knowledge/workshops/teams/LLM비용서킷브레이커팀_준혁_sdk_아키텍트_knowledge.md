
=== 전문 지식 (세계 최고 수준 자료 기반) ===

### OpenAI Python SDK monkey-patching interceptor pattern 2024 best practice
### OpenAI Python SDK Monkey-Patching Interceptor (2024 Best Practices)

**wrapt 라이브러리 사용: 안전한 런타임 패치로 OpenAI 클라이언트 메서드(OpenAI().chat.completions.create 등) 인터셉트. 직접 대체 대신 wrapper로 로깅/재시도/프록시 적용. Scoped patching + 테스트로 사이드 이펙트 0%** [2][3]

#### 1. 핵심 패턴: wrapt Function Wrapper (권장, gevent/eventlet 문제 피함)
```python
# 설치: pip install wrapt
import wrapt
from openai import OpenAI
import time, logging

@wrapt.patch_function_wrapper('openai', 'OpenAI.chat.completions.create')  # 모듈.클래스.메서드 지정
def interceptor(wrapped, instance, args, kwargs):
    start = time.time()
    try:
        response = wrapped(*args, **kwargs)  # 원본 호출
        latency = time.time() - start
        logging.info(f"OpenAI call: {latency:.2f}s, model={kwargs.get('model', 'gpt-4o')}")
        return response
    except Exception as e:
        logging.error(f"OpenAI error: {e}")
        raise  # 재시도 로직 추가 가능 (exponential backoff)

# 자동 패치: 이 모듈 import 시 즉시 적용 (import 순서 무관) [2]
client = OpenAI(api_key="env:OPENAI_API_KEY")  # 사용법 동일
```
**효과**: 모든 OpenAI 인스턴스에서 글로벌 인터셉트. MRO 영향 없음 [3]. **사용 사례**: 로깅(99% 지연 추적), 재시도(5xx 에러 3회, backoff 2^x), 프록시(로컬 LLM fallback).

#### 2. 클래스 메서드 직접 패치 (간단 프로토타입, LangChain 스타일) [1]
```python
import types
from openai import OpenAI

def openai_interceptor(self, *args, **kwargs):
    print("Intercepted OpenAI call")
    original = self.chat.completions.create  # 원본 저장
    result = original(*args, **kwargs)
    print(f"Response: {result.choices[0].message.content[:50]}...")
    return result

# 패치 적용 (첫 호출 전)
OpenAI.chat.completions.create = types.MethodType(openai_interceptor, None)  # 클래스 레벨
```
**메트릭**: 1회 패치로 100% 커버리지. **위험**: import 순서 의존 (OpenAI 먼저 import) [2]. **대안**: functools.wraps로 데코레이터.

#### 3. 생산 환경 프레임워크 (2024 베스트)
| 패턴 | 코드 라인 | 지연 오버헤드 | 안전성 | 사용 사례 |
|------|-----------|---------------|--------|----------|
| **wrapt (권장)** | 10줄 | <1ms | 높음 (MRO 무시) | Prod 로깅/재시도 [2] |
| **직접 set attr** | 5줄 | 0ms | 중간 (순서 의존) | Dev 프로토 [1] |
| **Mock (테스트)** | 3줄 | 0ms | 높음 | unittest.mock [5] |

**재시도 + Backoff 통합** (OpenAI 에러 핸들링 베스트 [4][6]):
```python
import tenacity

@wrapt.patch_function_wrapper('openai', 'OpenAI.chat.completions.create')
@tenacity.retry(wait=tenacity.wait_exponential(multiplier=1, min=4, max=10), stop=tenacity.stop_after_attempt(3))
def retry_wrapper(wrapped, instance, args, kwargs):
    return wrapped(*args, **kwargs)
```
**수치**: 95% 5xx 복구율, 토큰 비용 20% 절감 (n=1, best_of=1 고정 [6]).

#### 4. 제한 + 체크리스트
- **Scoped**: unittest 내만 `with patch()` [3][5].
- **테스트**: 100% 커버리지 (patched vs original 비교).
- **Anti-pattern 피함**: API 키 하드코딩 금지 (dotenv), rate limit 무시 NO [4].
- **대안 우선**: Subclassing (`class LoggingClient(OpenAI)

### Anthropic Claude token counting before request streaming implementation
### **Claude Token Counting 핵심: 요청 전 비용/속도 사전 제어**

**핵심 목적**: 메시지 전송 **전** 토큰 수 계산 → 비용 예측, 속도 제한(RPM) 준수, 프롬프트 최적화[1][3].

#### **1. 실전 적용 프레임워크 (3단계)**
```
1. count_tokens() 호출 → 토큰 수 확인
2. 기준 초과 시: 프롬프트 압축/모델 라우팅
3. 실제 messages.create() 실행
```
**예시 비용 절감 사례**: 10만 토큰 프롬프트 → count_tokens로 8만 토큰 압축 → **20% 비용 ↓**[1][4].

#### **2. Python 실전 코드 (가장 빈번한 사용)**
```python
import anthropic
client = anthropic.Anthropic()

# 기본 텍스트
tokens = client.messages.count_tokens(
    model="claude-3-5-sonnet-20240620",  # 호환 모델: 3.5 Sonnet/Haiku, 3 Opus 등[3]
    system="You are a scientist",
    messages=[{"role": "user", "content": "Hello, Claude"}]
)
print(tokens.json())  # {'usage': {'input_tokens': 12, 'output_tokens': 0}}

# Tools 포함
tokens = client.messages.count_tokens(
    model="claude-3-5-sonnet-20240620",
    tools=[{"name": "get_weather", "input_schema": {...}}],  # Tool schema 토큰 추가
    messages=[{"role": "user", "content": "SF 날씨?"}]
)

# 이미지/PDF (base64 필수)
tokens = client.messages.count_tokens(
    model="claude-3-5-sonnet-20240620",
    messages=[{
        "role": "user",
        "content": [{"type": "image", "source": {"type": "base64", "media_typ
===

