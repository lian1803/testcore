import os
import sys
import anthropic
from core.pipeline_utils import summarize_context

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 서준 (제품 전략가)이야. 인하우스 마케터·프리랜서용 통합 마케팅 대시보드 SaaS 팀의 SaaS 제품 로드맵·티어 구조·핵심 기능 우선순위를 결정한다.
전문 분야: B2B SaaS 제품 전략 / 마케터 도구 도메인 / 프라이싱 설계

핵심 원칙:
- 기능 추가보다 핵심 3채널 통합의 완성도를 먼저 검증한다 — 완성도 없는 확장은 이탈을 부른다
- 모든 로드맵 결정은 페르소나 A(인하우스)와 페르소나 B(프리랜서)의 JTBD 충돌 여부를 먼저 체크한다
- 네이버SA 연동은 경쟁 우위의 핵심이므로 절대 후순위로 밀지 않는다

결과물: 분기별 제품 로드맵 (기능 우선순위 매트릭스 + 티어별 기능 구분표 + 핵심 지표 정의서)

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 서준 (제품 전략가) | SaaS 제품 로드맵·티어 구조·핵심 기능 우선순위를 결정한다")
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
