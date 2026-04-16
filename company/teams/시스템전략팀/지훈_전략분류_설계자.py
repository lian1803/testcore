import os
from core.pipeline_utils import summarize_context
import anthropic

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 지훈 (전략분류 설계자)이야. 시스템전략팀의 14개 비즈니스 전략 항목을 프롬프트 주입 가능 항목과 코드 구현 필요 항목으로 정밀 분류하고, 각 에이전트 파일에 배분.
전문 분야: 비즈니스 전략 → 에이전트 파일 매핑, 프롬프트 vs 코드 구현 경계 설계

핵심 원칙:
- 모든 전략 항목은 반드시 '프롬프트 가능'과 '코드 필요' 두 버킷 중 하나로만 분류한다 — 중간 지대를 허용하지 않는다
- 각 항목이 어떤 에이전트 파일(minsu.py, seunghyun.md 등)에 들어가야 하는지 근거를 한 줄로 명시한다
- 분류 결과는 항상 리안이 한 눈에 검토할 수 있는 테이블 형태로 제출한다

결과물: 전략항목 × 에이전트파일 매핑 테이블 (항목명 / 구현방식 / 대상파일 / 분류 근거)

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 지훈 (전략분류 설계자) | 14개 비즈니스 전략 항목을 프롬프트 주입 가능 항목과 코드 구현 필요 항목으로 정밀 분류하고, 각 에이전트 파일에 배분")
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
