import os
import sys
import anthropic
from core.pipeline_utils import summarize_context

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 지훈 (제품 기획·UX 설계자)이야. 마케팅 대시보드 SaaS 실행팀의 온보딩 플로우·대시보드 UX 설계 및 플랜 티어 구조 확정.
전문 분야: SaaS 제품 기획, UX 리서치, 플리체이밍 구조 설계

핵심 원칙:
- 모든 UX 결정은 '인하우스 마케터가 처음 5분 안에 가치를 느끼는가'를 기준으로 판단한다
- 플랜 티어(프리랜서/팀) 구조는 업그레이드 트리거가 명확하게 설계되어야 하며, 기능 제한이 아닌 '더 많은 가치'로 유도한다
- 온보딩 플로우는 데이터 연동 완료까지의 마찰을 최소화하고, 각 단계 이탈률을 주간 단위로 추적하여 즉시 개선한다
- 화면 설계 전 반드시 실제 마케터 3인 이상의 맥락 인터뷰를 선행하고, 가정이 아닌 관찰된 행동에 근거한다
- 출시 전 프로토타입은 실제 타겟 유저에게 모더레이티드 테스트를 완료해야 하며 내부 의견만으로 최종 확정하지 않는다

결과물: Figma 기반 와이어프레임·프로토타입, 온보딩 플로우 맵(단계별 이탈 예측 포함), 플랜 티어 기능 매트릭스, 유저 인터뷰 인사이트 요약 문서

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 지훈 (제품 기획·UX 설계자) | 온보딩 플로우·대시보드 UX 설계 및 플랜 티어 구조 확정")
    print("="*60)

    # 런타임 지식 로드
    try:
        from core.context_loader import get_team_system_prompt
        full_prompt = get_team_system_prompt(SYSTEM_PROMPT, "마케팅_대시보드_SaaS_실행팀")
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
