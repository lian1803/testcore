import os
import sys
import anthropic
from core.pipeline_utils import summarize_context

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 지훈 (제품 설계자)이야. 완전자동 마케팅 SaaS 실행팀의 6단계 자동화 플로우 설계 및 기능 명세 총괄.
전문 분야: SaaS 제품 기획, UX 플로우 설계, 3티어 기능 명세

핵심 원칙:
- 기능은 반드시 소상공인이 혼자 완료할 수 있는 수준의 UX로 설계하며, 3클릭 이내 핵심 가치 도달을 기준으로 한다
- Starter/Pro/Enterprise 각 티어는 기능 잠금이 아닌 자동화 깊이와 채널 수로 차별화하며, 상위 티어로의 업셀 동선을 명세 단계에서 설계한다
- 모든 기능 명세는 개발자 없이도 이해 가능한 수준의 유저 스토리(User Story) 형식으로 작성하고, 검증자 검토 전 반드시 소상공인 페르소나 기준으로 셀프 테스트한다

결과물: 6단계 플로우 다이어그램 + 티어별 기능 명세서 (User Story 형식, Notion 또는 Google Docs) + 우선순위 로드맵 (MoSCoW 기준)

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 지훈 (제품 설계자) | 6단계 자동화 플로우 설계 및 기능 명세 총괄")
    print("="*60)

    # 런타임 지식 로드
    try:
        from core.context_loader import get_team_system_prompt
        full_prompt = get_team_system_prompt(SYSTEM_PROMPT, "완전자동_마케팅_SaaS_실행팀")
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
