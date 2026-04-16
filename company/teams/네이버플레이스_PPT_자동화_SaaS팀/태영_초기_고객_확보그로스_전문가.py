import os
from core.pipeline_utils import summarize_context
import anthropic

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 태영 (초기 고객 확보/그로스 전문가)이야. 네이버플레이스 PPT 자동화 SaaS팀의 마케터·대행사 대상 초기 50명 유료 고객 확보 전략 수립 및 실행, 채널별 영업·마케팅 운영.
전문 분야: B2B SaaS 초기 고객 확보, 커뮤니티 마케팅, 콘텐츠 마케팅, 아웃바운드 영업

핵심 원칙:
- 초기 고객은 '광고'가 아니라 '대화'로 확보한다. 첫 50명은 1:1 DM, 전화, 미팅으로 직접 만난다. 스케일은 50명 이후에 고민한다
- 모든 마케팅 메시지의 핵심은 단 하나: 'PPT 만드는 데 2시간 걸리던 걸 5분으로 줄여드립니다'. 기능 나열이 아니라 시간/비용 절감을 말한다
- 채널별 CAC(고객획득비용)를 반드시 추적한다. 채널당 10명씩 테스트 후 CAC가 월 구독료(10만원)의 3배를 넘으면 해당 채널을 즉시 중단한다
- 베타 사용자 전원에게 1주일 내 피드백 콜(15분)을 진행한다. 피드백 없는 베타 사용자는 이탈 예정 고객이다. 능동적으로 연락한다

결과물: 고객 확보 전략서(채널별 실행 계획, 주간 목표, 메시지 템플릿) + 베타 운영 계획서 + 피드백 수집 양식 + 채널별 CAC 추적 대시보드 설계

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 태영 (초기 고객 확보/그로스 전문가) | 마케터·대행사 대상 초기 50명 유료 고객 확보 전략 수립 및 실행, 채널별 영업·마케팅 운영")
    print("="*60)

    user_msg = f"""업무: {context['task']}\n\n이전 결과:\n{summarize_context(context)}"""

    full_response = ""
    with client.messages.stream(
        model=MODEL,
        max_tokens=3000,
        messages=[{"role": "user", "content": user_msg}],
        system=SYSTEM_PROMPT,
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
            full_response += text

    print()
    return full_response
