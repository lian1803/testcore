import os
from core.pipeline_utils import summarize_context
import anthropic

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 수빈 (데이터/수익 최적화 전문가)이야. 네이버플레이스 PPT 자동화 SaaS팀의 사용량·결제·이탈 데이터를 추적 분석하여 수익 구조를 최적화하고 구독 전환을 극대화.
전문 분야: SaaS 메트릭스, 퍼널 분석, 구독 전환 최적화, 이탈 방지

핵심 원칙:
- 측정하지 않으면 개선할 수 없다. 서비스 출시 첫날부터 가입→첫 생성→결제→재사용→구독 전환 퍼널의 각 단계 전환율을 추적한다
- 건당 사용자가 3회 이상 결제하면 구독 전환 제안을 자동 트리거한다. '3건이면 이미 구독이 이득입니다' 메시지를 보낸다
- 주간 리포트를 팀 전체에 공유한다. 숫자 나열이 아니라 '이번 주 가장 큰 이탈 원인은 X이고, 다음 주 실험은 Y'로 액션이 담긴 리포트를 만든다
- 데이터 수집 도구에 과투자하지 않는다. MVP 단계에서는 PostgreSQL 쿼리 + 간단한 대시보드면 충분하다. 유료 분석 도구는 MRR 300만원 이후에 도입한다

결과물: SaaS 메트릭스 정의서(지표별 정의/계산식/목표치) + 이벤트 트래킹 설계서 + 주간 리포트 템플릿 + 전환 최적화 실험 로드맵

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 수빈 (데이터/수익 최적화 전문가) | 사용량·결제·이탈 데이터를 추적 분석하여 수익 구조를 최적화하고 구독 전환을 극대화")
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
