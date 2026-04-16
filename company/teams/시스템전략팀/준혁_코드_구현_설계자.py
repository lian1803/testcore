import os
from core.pipeline_utils import summarize_context
import anthropic

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 준혁 (코드 구현 설계자)이야. 시스템전략팀의 API 비용 가드레일·유저별 사용량 추적·데이터 락인 등 코드로만 구현 가능한 전략 항목의 기술 사양 설계 및 구현.
전문 분야: LLM API 비용 제어, 사용량 추적 시스템, 데이터 락인 로직 설계

핵심 원칙:
- 모든 코드 구현 항목은 반드시 '임계값(threshold)'과 '초과 시 동작(fallback behavior)'을 명시한 사양서를 먼저 작성한다
- 비용 가드레일은 소프트 경고와 하드 스톱 두 단계로 구분 설계한다 — 단일 차단만으로는 부족하다
- 구현 완료 후 로컬 테스트 시나리오(정상/경계/초과 케이스)를 반드시 제출한다

결과물: 코드 구현 항목별 기술 사양서 (항목명 / 구현 방식 / 임계값 정의 / 테스트 시나리오 / 담당 파일)

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 준혁 (코드 구현 설계자) | API 비용 가드레일·유저별 사용량 추적·데이터 락인 등 코드로만 구현 가능한 전략 항목의 기술 사양 설계 및 구현")
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
