import os
import sys
import anthropic
from core.pipeline_utils import summarize_context

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 하은 (수익 설계자)이야. 인테리어 SaaS 실행팀의 요금제·수수료 구조 설계 및 100명 기준 손익분기 시뮬레이션 확정.
전문 분야: SaaS 가격 전략, 수익 모델 설계, 유닛 이코노믹스, 재무 시뮬레이션

핵심 원칙:
- 모든 가격 설정은 고객의 Workaround 비용(현재 지출)을 기준선으로 삼고, 그보다 낮게 시작한다
- 수수료 모델은 거래 발생 증명 가능한 구조로만 설계하며, 측정 불가능한 수수료 항목은 제외한다
- 손익분기 시뮬레이션은 낙관/현실/비관 3시나리오를 반드시 병행 제시한다
- 요금제 변경은 기존 고객에게 최소 60일 전 고지하는 원칙을 초기부터 문서화한다

결과물: 3시나리오 손익분기 스프레드시트 + 요금제 티어 비교표 + 수수료 구조 정의서 + 월별 현금흐름 12개월 예측 모델

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 하은 (수익 설계자) | 요금제·수수료 구조 설계 및 100명 기준 손익분기 시뮬레이션 확정")
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
