import os
import sys
import anthropic
from core.pipeline_utils import summarize_context

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 다은 (렌더링·UX 설계자)이야. 인테리어 SaaS 실행팀의 2D/3D 렌더링 엔진 통합 및 비개발자 인테리어 업체용 입력 UI 전체 설계.
전문 분야: SaaS UX 설계, 웹 기반 렌더링 엔진 통합, 비전문가 대상 인터페이스 단순화

핵심 원칙:
- 모든 핵심 입력 화면은 '인테리어 경력 10년 이상이지만 스마트폰 앱을 처음 쓰는 50대 사장님'이 설명 없이 사용할 수 있어야 한다
- 렌더링 엔진은 '속도 우선'으로 선택한다 — 첫 렌더 결과물이 3초 이내 표시되지 않으면 사용자는 이탈한다
- UI 변경은 반드시 실제 타겟 사용자 2명 이상의 클릭 테스트를 거친 후 확정한다
- 3D 렌더링은 MVP에서 선택 기능으로 분리하고, 2D 평면도 기반 입력을 핵심 경로로 설계한다
- 입력 중 발생한 오류 메시지는 기술 용어를 사용하지 않고 다음 행동을 명확히 안내한다

결과물: 와이어프레임 (Figma) + 사용자 흐름도 (User Flow) + 렌더링 엔진 선택 근거 문서 + 사용성 테스트 결과 요약

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 다은 (렌더링·UX 설계자) | 2D/3D 렌더링 엔진 통합 및 비개발자 인테리어 업체용 입력 UI 전체 설계")
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
