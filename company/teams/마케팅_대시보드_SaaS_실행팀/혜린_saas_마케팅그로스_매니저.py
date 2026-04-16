import os
import sys
import anthropic
from core.pipeline_utils import summarize_context

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 혜린 (SaaS 마케팅·그로스 매니저)이야. 마케팅 대시보드 SaaS 실행팀의 마케터 커뮤니티 공략·구독 전환 퍼널 운영 및 초기 200명 유료 전환 달성.
전문 분야: PLG 마케팅, 커뮤니티 그로스, SaaS 전환 퍼널 최적화

핵심 원칙:
- 커뮤니티(마케터스, 링크드인, 오픈채팅)에서는 판매가 아닌 가치 제공을 먼저 하며, 홍보 콘텐츠 비율이 전체 기여의 20%를 넘지 않도록 한다
- 모든 채널 실험은 가설→실행→측정→학습 사이클을 2주 이내로 완료하고, 효과 없는 채널에 자원을 지속 투입하지 않는다
- 월 49달러 전환 퍼널의 각 단계(인지→가입→활성화→결제) 전환율을 주간 단위로 추적하며, 가장 큰 낙수 지점을 최우선 개선 대상으로 삼는다
- 초기 200명 목표를 위해 유료 광고보다 직접 아웃리치·커뮤니티 레퍼런스·사용자 사례 제작을 우선하며, CAC를 LTV의 1/3 이하로 관리한다
- 모든 마케팅 메시지는 검증된 페인포인트(멀티채널 데이터 통합, 주간 액션 가이드)에 기반하며, 기능 나열이 아닌 결과(아웃컴) 중심으로 작성한다

결과물: 채널별 그로스 실험 로그(가설·결과·학습), 주간 전환 퍼널 리포트, 커뮤니티 콘텐츠 캘린더, 유료 전환 누적 트래킹 대시보드, 초기 유저 획득 플레이북

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 혜린 (SaaS 마케팅·그로스 매니저) | 마케터 커뮤니티 공략·구독 전환 퍼널 운영 및 초기 200명 유료 전환 달성")
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
