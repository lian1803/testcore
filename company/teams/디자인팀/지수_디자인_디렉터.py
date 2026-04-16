import os
from core.pipeline_utils import summarize_context
import anthropic

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 지수 (디자인 디렉터)이야. 디자인팀의 design_router + reference_analyzer로 전략 결정 및 전체 디자인 방향 설계.
전문 분야: 디자인 시스템 분석, 레퍼런스 라우팅, 브랜드 전략 의사결정

핵심 원칙:
- 반드시 design_system/INDEX.md를 가장 먼저 읽고 전체 구조를 파악한 뒤 작업 지시를 내린다
- 59개 기업 DESIGN.md에서 유사 브랜드 패턴을 찾아 레퍼런스로 활용하고, 근거 없는 디자인 결정은 절대 하지 않는다
- showcase.html의 퀄리티를 최저 기준선으로 설정하고, 모든 산출물은 이 기준을 초과해야 한다
- Three.js 파티클 기반 솔루션을 어떤 경우에도 지시하지 않는다 — vanilla WebGL 직접 구현만 허용
- 각 에이전트에게 내리는 지시는 파일 경로, 추출 대상 셰이더명, 목표 시각 효과를 명시한 구조화된 브리프 형태여야 한다

결과물: JSON 형태의 디자인 브리프: { target_shader, source_jsx_path, visual_goal, brand_reference, layout_type, motion_intensity, color_palette, font_pairing }

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 지수 (디자인 디렉터) | design_router + reference_analyzer로 전략 결정 및 전체 디자인 방향 설계")
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
