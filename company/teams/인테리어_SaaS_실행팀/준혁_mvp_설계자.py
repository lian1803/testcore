import os
import sys
import anthropic
from core.pipeline_utils import summarize_context

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 준혁 (MVP 설계자)이야. 인테리어 SaaS 실행팀의 거래망 추천 기능 중심 MVP 아키텍처 설계 및 개발 우선순위 결정.
전문 분야: 린 SaaS 제품 설계, 추천 알고리즘, 빠른 프로토타이핑

핵심 원칙:
- 3개월 첫 결제 목표를 최우선으로 두고, 완성도보다 결제 가능한 최소 기능에 집중한다
- 기능 추가 요청에는 반드시 '이것이 첫 결제를 앞당기는가'를 기준으로 YES/NO 판단한다
- 기술 부채는 허용하되 반드시 문서화하고, 2라운드 개발 전 상환 계획을 명시한다
- 외부 API·공공데이터 의존도가 높은 기능은 fallback 로직을 MVP 단계부터 설계한다

결과물: 기능 명세서(Feature Spec) + 개발 스프린트 계획표 + 기술 스택 결정 문서 + 데모 가능한 프로토타입 링크

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 준혁 (MVP 설계자) | 거래망 추천 기능 중심 MVP 아키텍처 설계 및 개발 우선순위 결정")
    print("="*60)

    # 런타임 지식 로드
    try:
        from core.context_loader import get_team_system_prompt
        full_prompt = get_team_system_prompt(SYSTEM_PROMPT, "인테리어_SaaS_실행팀")
    except Exception:
        full_prompt = SYSTEM_PROMPT

    user_msg = f"""업무: {context['task']}\n\n이전 결과:\n{summarize_context(context)}"""

    full_response = ""
    with client.messages.stream(
        model=MODEL,
        max_tokens=3000,
        messages=[{"role": "user", "content": user_msg}],
        system=full_prompt,
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
            full_response += text

    print()
    return full_response
