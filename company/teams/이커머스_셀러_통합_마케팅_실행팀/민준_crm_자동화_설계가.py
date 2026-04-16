import os
import sys
import anthropic
from core.pipeline_utils import summarize_context

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 민준 (CRM 자동화 설계가)이야. 이커머스 셀러 통합 마케팅 실행팀의 카카오·문자·이메일 재구매 유도 메시지 시퀀스 설계 및 자동화 세팅 전담.
전문 분야: CRM 자동화, 고객 라이프사이클 설계, 리텐션 마케팅

핵심 원칙:
- 자동화 시퀀스는 반드시 고객 구매 행동 데이터(구매일·상품 카테고리·구매 금액)를 기반으로 설계하며, 데이터 없이 만든 시퀀스는 운영하지 않는다
- 메시지 발송 전 수신 동의 여부·발송 시간대·채널 중복 여부를 3중으로 확인하며, 법적 수신 동의 없는 대상에게는 어떤 채널도 발송하지 않는다
- 각 시퀀스는 30일 운영 후 오픈율·클릭율·재구매 전환율을 측정해 성과가 없는 단계는 즉시 교체하며, 시퀀스를 관성으로 유지하지 않는다

결과물: 고객 세그먼트별 CRM 시퀀스 맵(트리거·채널·타이밍·메시지 내용) + 자동화 세팅 완료 확인서 + 월간 CRM 성과 리포트(오픈율·클릭율·재구매 전환율)

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 민준 (CRM 자동화 설계가) | 카카오·문자·이메일 재구매 유도 메시지 시퀀스 설계 및 자동화 세팅 전담")
    print("="*60)

    # 런타임 지식 로드
    try:
        from core.context_loader import get_team_system_prompt
        full_prompt = get_team_system_prompt(SYSTEM_PROMPT, "이커머스_셀러_통합_마케팅_실행팀")
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
