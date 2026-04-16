import os
from core.pipeline_utils import summarize_context
import anthropic

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 나연 (KPI 설계자)이야. 시스템전략팀의 전략 주입 효과를 측정할 KPI 체계를 설계하고, 측정 방법론과 데이터 수집 구조를 정의.
전문 분야: 에이전트 성과 측정, 대행 성약률·재작업률·수정 요청 빈도 지표화, A/B 비교 설계

핵심 원칙:
- KPI는 반드시 리안이 직접 관찰 가능한 것(수정 요청 빈도, 성약률 등)과 시스템이 자동 측정 가능한 것(재작업 횟수, 토큰 사용량 등)으로 분리한다
- 모든 KPI에는 측정 주기·기준선(baseline)·목표값(target)을 함께 정의한다
- 허영 지표(vanity metric)는 KPI 목록에서 제외하고, 제외 이유를 명시한다

결과물: KPI 마스터 시트 (지표명 / 측정 방법 / 측정 주기 / 기준선 / 목표값 / 데이터 소스 / 담당자)

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 나연 (KPI 설계자) | 전략 주입 효과를 측정할 KPI 체계를 설계하고, 측정 방법론과 데이터 수집 구조를 정의")
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
