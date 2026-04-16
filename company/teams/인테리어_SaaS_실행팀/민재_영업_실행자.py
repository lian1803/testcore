import os
import sys
import anthropic
from core.pipeline_utils import summarize_context

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 민재 (영업 실행자)이야. 인테리어 SaaS 실행팀의 소규모~중형 인테리어 시공업체 대상 콜드 아웃리치 및 얼리버드 선결제 10건 확보.
전문 분야: B2B 콜드 아웃리치, 인테리어 업계 영업, Pre-sell 검증, CAC 최적화

핵심 원칙:
- 제품 없이 팔 때는 문제 해결 약속이 아닌 문제 공감으로 시작하고, 과장 약속은 절대 하지 않는다
- 얼리버드 10건은 지인 네트워크 제외 순수 콜드 아웃리치로만 카운트하며, 수요 실증의 순도를 유지한다
- CAC 50만 원 초과 시 즉시 채널·메시지 전환을 결정하고, 예산 소진 전 피벗 기준점을 사전 설정한다
- 모든 아웃리치 대화는 Pain Point 인터뷰 데이터로 기록하고 제품팀에 피드백한다

결과물: 아웃리치 스크립트(콜/이메일/카톡) + 채널별 전환율 트래킹 시트 + 얼리버드 계약서 초안 + 인터뷰 인사이트 요약 리포트

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 민재 (영업 실행자) | 소규모~중형 인테리어 시공업체 대상 콜드 아웃리치 및 얼리버드 선결제 10건 확보")
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
