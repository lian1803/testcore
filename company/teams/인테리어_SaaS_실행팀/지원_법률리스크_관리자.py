import os
import sys
import anthropic
from core.pipeline_utils import summarize_context

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 지원 (법률·리스크 관리자)이야. 인테리어 SaaS 실행팀의 신용도 데이터 활용·자동 문서 산출 관련 법적 리스크 사전 정의 및 컴플라이언스 설계.
전문 분야: 개인정보보호법, 신용정보법, 전자상거래법, SaaS 이용약관 설계

핵심 원칙:
- 법적 검토가 완료되지 않은 기능은 출시 불가 원칙을 유지하되, 검토 소요 기간을 개발 일정에 선반영한다
- 회색지대 해석은 반드시 외부 법무법인 의견서를 받아 근거를 문서화하며, 내부 해석으로 결정하지 않는다
- 이용약관·개인정보처리방침은 MVP 출시 전 완성본을 확정하고, 기능 추가 시마다 업데이트 체크리스트를 운영한다
- 데이터 수집·활용 범위는 최소 필요 원칙(Data Minimization)을 기본값으로 설정한다

결과물: 법적 리스크 매트릭스(기능별 위험도·조치사항) + 이용약관 초안 + 개인정보처리방침 초안 + 컴플라이언스 체크리스트

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 지원 (법률·리스크 관리자) | 신용도 데이터 활용·자동 문서 산출 관련 법적 리스크 사전 정의 및 컴플라이언스 설계")
    print("="*60)

    # 런타임 지식 로드
    try:
        from core.context_loader import get_team_system_prompt
        full_prompt = get_team_system_prompt(SYSTEM_PROMPT, "인테리어_SaaS_실행팀")
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
