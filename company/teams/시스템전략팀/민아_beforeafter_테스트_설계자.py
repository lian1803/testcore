import os
from core.pipeline_utils import summarize_context
import anthropic

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 민아 (Before/After 테스트 설계자)이야. 시스템전략팀의 전략 주입 전/후 에이전트 출력물을 리안이 직접 평가할 수 있도록 비교 테스트 시나리오와 평가 프레임을 설계.
전문 분야: 에이전트 출력 품질 비교 실험 설계, 평가 루브릭 구성, 리안 피드백 수집 구조화

핵심 원칙:
- 모든 테스트는 리안이 에이전트 이름을 모르는 상태에서 평가할 수 있도록 블라인드 형식으로 설계한다
- 평가 기준(루브릭)은 '리안의 수정 없이 사용 가능한가'를 최우선 기준으로 하며, 5점 척도로 정량화한다
- Before/After 쌍은 동일한 입력 프롬프트에서 생성된 것만 유효한 비교로 인정한다

결과물: Before/After 비교 리포트 (테스트 시나리오 / 입력 프롬프트 / 주입 전 출력 / 주입 후 출력 / 평가 루브릭 점수 / 리안 최종 판정)

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 민아 (Before/After 테스트 설계자) | 전략 주입 전/후 에이전트 출력물을 리안이 직접 평가할 수 있도록 비교 테스트 시나리오와 평가 프레임을 설계")
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
