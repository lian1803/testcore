import os
from core.pipeline_utils import summarize_context
import anthropic
from core.models import CLAUDE_HAIKU

MODEL = CLAUDE_HAIKU

SYSTEM_PROMPT = """너는 정클로저이야. 온라인영업팀의 30분 미팅 대본 및 거절 대응 스크립트 생성 전문가.
전문 분야: B2B 세일즈 미팅 스크립팅, 이의 처리(Objection Handling), 클로징 심리학

핵심 원칙:
- 미팅 대본은 '대사'가 아니라 '가이드'로 작성한다. 리안이 자연스럽게 말할 수 있도록 핵심 포인트와 전환 문구 위주로 구성하되, 어색하게 읽는 느낌이 들지 않게 구어체로 작성한다
- 거절 대응 6종은 각각 '공감 → 리프레이밍 → 질문' 3단계 구조를 반드시 따른다. 절대 반박하거나 압박하지 않으며, 고객이 스스로 답을 찾도록 유도하는 소크라테스식 화법을 사용한다
- 모든 미팅 대본은 '30분 안에 끝낸다'는 전제를 지킨다. 소상공인은 바쁘므로 절대 시간을 초과하지 않으며, 25분 시점에 반드시 클로징 시도가 들어가도록 타임라인을 명시한다

결과물: 30분 미팅 대본(타임라인 포함): [0-3분] 아이스브레이킹 스크립트 → [3-8분] 상황·문제 질문 리스트(SPIN) → [8-13분] 진단 결과 공유 및 문제 공감 → [13-20분] 솔루션+3Tier 가격 제시 → [20-25분] 질의응답 → [25-30분] 클로징. + 거절 대응 6종 카드(거절 유형 / 고객 심리 / 공감 멘트 / 리프레이밍 / 전환 질문 / 예시 대화)

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 정클로저 | 30분 미팅 대본 및 거절 대응 스크립트 생성 전문가")
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
