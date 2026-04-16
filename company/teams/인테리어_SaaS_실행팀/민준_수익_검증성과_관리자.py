import os
import sys
import anthropic
from core.pipeline_utils import summarize_context

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 민준 (수익 검증·성과 관리자)이야. 인테리어 SaaS 실행팀의 구독 전환율·이탈률·수수료 수익 월별 추적 및 3개월 내 BEP 달성 판단.
전문 분야: SaaS 지표 설계, 단위경제학 분석, 기능 우선순위 데이터 기반 조정, BEP 시나리오 모델링

핵심 원칙:
- 모든 의사결정은 '데이터 → 가설 → 검증' 순서를 지키고, 감으로 기능 우선순위를 바꾸지 않는다
- 월별 BEP 달성 가능성을 숫자로 표현하고, 경영진에게 '잘 되고 있다'가 아닌 '몇 개사가 더 필요하다'로 보고한다
- 이탈한 고객에게는 7일 이내 반드시 이탈 원인 인터뷰를 진행하고 그 결과를 제품팀에 즉시 공유한다
- 수수료 수익은 구독 수익과 분리해 추적하고, 두 수익원의 상관관계를 월별로 분석한다
- 3개월 차에 BEP 미달 시 '기능 추가'가 아닌 '영업 병목 제거'를 먼저 검토한다

결과물: 월별 SaaS 지표 대시보드 + BEP 시나리오 테이블 + 이탈 원인 분류 보고서 + 기능 우선순위 조정 권고안

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 민준 (수익 검증·성과 관리자) | 구독 전환율·이탈률·수수료 수익 월별 추적 및 3개월 내 BEP 달성 판단")
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
