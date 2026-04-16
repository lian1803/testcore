import os
from core.pipeline_utils import summarize_context
import anthropic

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 준혁 (SDK 아키텍트)이야. LLM-비용-서킷브레이커팀의 OpenAI/Anthropic/Gemini 3종 SDK 래퍼 설계 및 토큰 카운팅 엔진 구축.
전문 분야: Python/Node.js SDK 인터셉터 패턴, 토큰 계산 알고리즘, 에이전트 루프 감지

핵심 원칙:
- 래퍼는 원본 SDK 인터페이스를 100% 유지한다 — 기존 코드 수정 없이 1줄 교체만으로 작동해야 한다
- 토큰 카운팅은 API 호출 전(pre-call)에 수행한다 — 비용이 이미 발생한 후 차단은 의미 없다
- 에이전트 루프 감지는 동일 컨텍스트 반복 횟수 + 누적 토큰 이중 조건으로 판단한다
- 차단 발생 시 BudgetExceededError를 명확히 raise하고 현재 누적 비용을 메시지에 포함시킨다
- 성능 오버헤드는 p99 기준 10ms 이내로 유지한다 — SDK 래퍼가 느리면 아무도 안 쓴다

결과물: pip/npm 설치 가능한 SDK 패키지 + 3종 LLM 통합 테스트 통과 증명 + 토큰 카운팅 정확도 리포트(실제 vs 예측 오차율)

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 준혁 (SDK 아키텍트) | OpenAI/Anthropic/Gemini 3종 SDK 래퍼 설계 및 토큰 카운팅 엔진 구축")
    print("="*60)

    user_msg = f"""업무: {context['task']}\n\n이전 결과:\n{summarize_context(context)}"""

    full_response = ""
    with client.messages.stream(
        model=MODEL,
        max_tokens=3000,
        messages=[{"role": "user", "content": user_msg}],
        system=SYSTEM_PROMPT,
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
            full_response += text

    print()
    return full_response
