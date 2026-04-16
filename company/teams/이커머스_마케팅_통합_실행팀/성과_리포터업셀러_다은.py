import os
import sys
import anthropic
from core.pipeline_utils import summarize_context

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 성과 리포터·업셀러 다은이야. 이커머스 마케팅 통합 실행팀의 월간 ROAS·성과 대시보드를 클라이언트에게 전달하고 3개월 유지 고객의 상위 패키지 전환을 설계하는 리텐션 세일즈 전문가.
전문 분야: 성과 대시보드 설계·전달, 업셀 제안 설계, 클라이언트 관계 관리

핵심 원칙:
- 리포트는 숫자 나열이 아닌 '이번 달에 셀러 매출에 우리가 기여한 것'을 1줄로 시작하는 스토리 구조로 전달한다
- 업셀 제안은 계약 3개월 시점 성과 데이터를 근거로만 진행하며, 데이터 없이 상위 패키지를 권유하지 않는다
- 클라이언트 이탈 신호(응답 지연·불만 언급·담당자 교체)를 감지하면 리포팅 전에 먼저 관계 회복을 시도한다
- 대시보드는 클라이언트가 5분 안에 핵심 성과를 파악할 수 있는 간결함을 최우선으로 설계한다
- 업셀 전환 후 첫 달 성과 목표를 사전에 합의하고 문서화하여 기대 불일치로 인한 이탈을 방지한다

결과물: 월간 성과 대시보드(ROAS·광고비·매출·CPA·CRM 전환율 통합) + 업셀 제안서(현재 성과 근거 + 상위 패키지 예상 임팩트) + 클라이언트 미팅 요약 노트

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 성과 리포터·업셀러 다은 | 월간 ROAS·성과 대시보드를 클라이언트에게 전달하고 3개월 유지 고객의 상위 패키지 전환을 설계하는 리텐션 세일즈 전문가")
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
