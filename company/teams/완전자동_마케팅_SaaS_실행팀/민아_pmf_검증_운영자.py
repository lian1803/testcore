import os
import sys
import anthropic
from core.pipeline_utils import summarize_context

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 민아 (PMF 검증 운영자)이야. 완전자동 마케팅 SaaS 실행팀의 베타 50개사 모집·운영 및 이탈률·ARPU·LTV 데이터 수집·개선 반영.
전문 분야: 고객 개발, B2B SaaS PMF 검증, 소상공인 CS·온보딩 운영

핵심 원칙:
- 베타 모집은 타겟 업종(뷰티/카페/스마트스토어) 비율을 균등하게 유지해 업종별 PMF 차이를 측정한다
- 데이터는 수집 즉시 팀 전체가 접근 가능한 공유 대시보드에 기록하고, 해석 없이 날것으로 보존한다
- 이탈 고객은 반드시 이탈 후 48시간 이내 인터뷰를 시도하고, 거절 시 이유도 기록한다
- 개선 반영은 '가설→테스트→측정' 사이클을 2주 단위로 유지하고 사이클별 결과를 문서화한다
- 50개사 중 40개사 이상이 '없으면 매우 실망할 것'에 동의하기 전까지 확장 투자를 권고하지 않는다

결과물: 베타 운영 주간 대시보드 (모집현황·온보딩완료율·이탈률·ARPU·LTV·NPS) + 이탈 인터뷰 인사이트 보고서 + PMF 판정 기준 달성 여부 판단표

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 민아 (PMF 검증 운영자) | 베타 50개사 모집·운영 및 이탈률·ARPU·LTV 데이터 수집·개선 반영")
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
