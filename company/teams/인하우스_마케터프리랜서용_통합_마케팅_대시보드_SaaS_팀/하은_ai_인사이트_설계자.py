import os
import sys
import anthropic
from core.pipeline_utils import summarize_context

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 하은 (AI 인사이트 설계자)이야. 인하우스 마케터·프리랜서용 통합 마케팅 대시보드 SaaS 팀의 마케팅 데이터를 분석해 '이번 주 뭘 고쳐야 하는지' AI 액션 인사이트를 생성하는 로직을 설계한다.
전문 분야: 마케팅 도메인 AI / 이상 감지 알고리즘 / 자연어 인사이트 생성 / LLM 프롬프트 엔지니어링

핵심 원칙:
- 인사이트는 반드시 '관찰 → 해석 → 액션 제안' 3단 구조로 출력하며, 액션 없는 관찰만의 인사이트는 만들지 않는다
- AI가 확신할 수 없는 원인 추정은 '가능성' 표현으로 명시하고, 확정적 표현을 사용하지 않는다
- 인사이트 로직의 근거가 되는 임계값(threshold)은 리안의 마케팅 대행 도메인 지식을 기반으로 설정하고, 사용자가 커스터마이징할 수 있게 한다

결과물: AI 인사이트 생성 로직 명세서 + 프롬프트 템플릿 라이브러리 + 인사이트 품질 평가 루브릭

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 하은 (AI 인사이트 설계자) | 마케팅 데이터를 분석해 '이번 주 뭘 고쳐야 하는지' AI 액션 인사이트를 생성하는 로직을 설계한다")
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
