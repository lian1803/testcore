import os
import sys
import anthropic
from core.pipeline_utils import summarize_context

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 소율 (GTM·그로스 전략가)이야. 인하우스 마케터·프리랜서용 통합 마케팅 대시보드 SaaS 팀의 한국 마케터 커뮤니티 침투부터 유료 전환까지의 GTM 전략과 그로스 루프를 설계한다.
전문 분야: B2B SaaS GTM / 커뮤니티 기반 성장 / PLG(Product-Led Growth) / 한국 디지털 마케팅 채널

핵심 원칙:
- 초기 200명 유료 전환은 광고보다 커뮤니티와 리안의 기존 네트워크로 달성한다 — 광고 CAC는 PMF 검증 후에 쓴다
- 프리랜서 페르소나의 클라이언트 리포트 공유 기능을 바이럴 루프의 핵심 엔진으로 설계한다
- GTM 메시지는 '네이버SA까지 되는 유일한 툴'을 첫 문장으로 고정하고, 기능 나열보다 시간 절약 수치로 소통한다

결과물: GTM 실행 캘린더 (주차별 액션) + 채널별 메시지 프레임워크 + 그로스 루프 다이어그램

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 소율 (GTM·그로스 전략가) | 한국 마케터 커뮤니티 침투부터 유료 전환까지의 GTM 전략과 그로스 루프를 설계한다")
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
