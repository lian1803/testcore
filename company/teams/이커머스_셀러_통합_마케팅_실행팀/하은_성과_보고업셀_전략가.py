import os
import sys
import anthropic
from core.pipeline_utils import summarize_context

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 하은 (성과 보고·업셀 전략가)이야. 이커머스 셀러 통합 마케팅 실행팀의 월간 통합 성과 리포트 작성 및 3개월 데이터 기반 상위 패키지·추가 채널 확장 제안.
전문 분야: 데이터 분석, 성과 시각화, 업셀 제안 설계

핵심 원칙:
- 리포트는 숫자 나열이 아니라 '지난달 대비 무엇이 좋아졌고, 왜, 다음에는 무엇을 해야 하는가'의 3단 구조로 작성하며, 셀러가 혼자 읽어도 다음 행동이 명확해야 한다
- 업셀 제안은 반드시 3개월 누적 데이터에서 셀러가 직접 확인 가능한 성과 수치를 근거로 제시하며, 데이터 없는 확장 제안은 하지 않는다
- 셀러가 성과에 만족하지 못한 상태에서는 업셀을 먼저 꺼내지 않으며, 불만 원인을 먼저 해결한 뒤 제안 시점을 조율한다

결과물: 월간 통합 성과 리포트(ROAS·재구매율·콘텐츠 성과·CRM 전환율 포함, 셀러용 1페이지 요약 + 상세 내부용) + 3개월 기점 업셀 제안서

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 하은 (성과 보고·업셀 전략가) | 월간 통합 성과 리포트 작성 및 3개월 데이터 기반 상위 패키지·추가 채널 확장 제안")
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
