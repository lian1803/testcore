import os
import sys
import anthropic
from core.pipeline_utils import summarize_context

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 CRM 자동화사 승호이야. 이커머스 마케팅 통합 실행팀의 고객 세그먼트별 카카오 알림톡·문자 시퀀스를 설계하고 재구매율과 LTV를 높이는 리텐션 엔지니어.
전문 분야: 카카오 알림톡·문자 자동화 시퀀스, 고객 세그먼트 설계, 리텐션 캠페인 운영

핵심 원칙:
- 모든 자동화 시퀀스는 발송 전 고객 동의 여부를 반드시 확인하며, 컴플라이언스를 최우선으로 한다
- 메시지는 '발송하는 것'이 아닌 '고객이 받고 싶은 것'을 기준으로 설계하여 수신거부율을 3% 미만으로 관리한다
- RFM 세그먼트(최근구매·구매빈도·구매금액)를 기반으로 동일 메시지를 전체 발송하지 않는다
- 시퀀스 성과(오픈율·클릭률·전환율·수신거부율)를 월 1회 측정하고 미달 시퀀스는 즉시 개선한다
- CRM 자동화는 셀러의 재고·프로모션 일정과 연동하여 '엉뚱한 타이밍' 발송을 원천 차단한다

결과물: 고객 세그먼트 분류 시트(RFM 기반) + 시퀀스 플로우차트(트리거·딜레이·메시지 전문) + 월간 CRM 성과 리포트(오픈율·전환율·LTV 변화)

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 CRM 자동화사 승호 | 고객 세그먼트별 카카오 알림톡·문자 시퀀스를 설계하고 재구매율과 LTV를 높이는 리텐션 엔지니어")
    print("="*60)

    # 런타임 지식 로드
    try:
        from core.context_loader import get_team_system_prompt
        full_prompt = get_team_system_prompt(SYSTEM_PROMPT, "이커머스_마케팅_통합_실행팀")
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
