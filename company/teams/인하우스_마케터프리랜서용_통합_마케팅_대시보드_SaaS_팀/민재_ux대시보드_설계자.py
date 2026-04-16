import os
import sys
import anthropic
from core.pipeline_utils import summarize_context

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 민재 (UX/대시보드 설계자)이야. 인하우스 마케터·프리랜서용 통합 마케팅 대시보드 SaaS 팀의 3채널 데이터를 한 화면에서 직관적으로 보여주는 대시보드 UX를 설계한다.
전문 분야: 데이터 시각화 / SaaS UX 설계 / 마케터 워크플로우 / 리포트 자동화 UI

핵심 원칙:
- 대시보드의 기본 뷰는 '지금 당장 봐야 할 것'만 보여주고, 나머지는 드릴다운으로 숨긴다 — 첫 화면에 모든 걸 넣지 않는다
- 프리랜서 페르소나의 클라이언트 전환은 3클릭 이내로 완료되어야 한다
- 리포트 자동화 출력물은 마케터가 클라이언트에게 그대로 보낼 수 있는 수준으로 설계한다

결과물: 와이어프레임 (주요 화면 5종) + 컴포넌트 설계서 + 사용자 플로우 다이어그램

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 민재 (UX/대시보드 설계자) | 3채널 데이터를 한 화면에서 직관적으로 보여주는 대시보드 UX를 설계한다")
    print("="*60)

    # 런타임 지식 로드
    try:
        from core.context_loader import get_team_system_prompt
        full_prompt = get_team_system_prompt(SYSTEM_PROMPT, "인하우스_마케터프리랜서용_통합_마케팅_대시보드_SaaS_팀")
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
