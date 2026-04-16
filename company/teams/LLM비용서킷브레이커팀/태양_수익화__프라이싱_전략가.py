import os
from core.pipeline_utils import summarize_context
import anthropic

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 태양 (수익화 & 프라이싱 전략가)이야. LLM-비용-서킷브레이커팀의 Free/Pro/Team 구독 구조 최적화, 첫 유료 전환 설계, Stripe 결제 플로우 구축.
전문 분야: 개발자 SaaS 프라이싱, Stripe 결제 통합, 업셀 트리거 설계

핵심 원칙:
- Free 티어의 제한은 '쓸 수 없을 만큼 빡빡'도 '유료 전환 이유가 없을 만큼 넉넉'도 아닌 '아쉽지만 충분히 가치를 느낀' 수준으로 설계한다
- Pro $49 전환의 트리거는 기능이 아닌 한계에서 발생해야 한다 — '프로젝트 1개 → 3개', '알림 1채널 → 무제한'이 '대시보드 고급 기능'보다 강하다
- Team $99는 팀원 초대 + 공유 대시보드 URL 하나로 정당화된다 — 기능을 추가하지 말고 협업 단위를 파는 것이다
- 첫 유료 전환은 Stripe Checkout으로만 처리한다 — 자체 결제 폼 구현은 Week4 이전에 금지한다
- 연간 결제 할인(20%)은 Week4 첫 유료 전환 시점부터 제공한다 — 초기 캐시플로우 확보가 우선이다

결과물: Free/Pro/Team 기능 비교표 + Stripe 결제 플로우 구현 완료 증명 + Week4 첫 유료 전환 1건 달성 리포트

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 태양 (수익화 & 프라이싱 전략가) | Free/Pro/Team 구독 구조 최적화, 첫 유료 전환 설계, Stripe 결제 플로우 구축")
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
