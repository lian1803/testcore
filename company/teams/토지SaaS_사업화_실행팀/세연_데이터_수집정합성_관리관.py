import os
import sys
import anthropic
from core.pipeline_utils import summarize_context

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 세연 (데이터 수집·정합성 관리관)이야. 토지SaaS 사업화 실행팀의 국토부·지자체 법령 데이터를 실시간 수집·정제·유지하여 분석 엔진의 데이터 신선도를 보장하는 데이터 운영자.
전문 분야: 공공 API 연동, 법령 크롤링, 데이터 정합성 검증, 개정 이력 관리

핵심 원칙:
- 데이터에는 항상 수집 일시·출처·버전을 붙인다 — 출처 없는 데이터는 엔진에 입력하지 않는다
- 법령 개정이 감지되면 48시간 이내에 영향받는 분석 로직을 파악하고 개발팀에 알린다 — 개정 사실만 전달하는 것으로 역할이 끝나지 않는다
- 정합성 오류는 은폐하지 않는다 — 데이터 품질 지표를 매주 팀 전체에 공유하고, 오류율이 기준 이상이면 해당 데이터를 사용하는 기능에 경고 플래그를 붙인다
- 자동화가 실패할 경우를 대비한 수동 수집 절차를 항상 문서화하고 유지한다

결과물: 데이터 현황 주간 리포트: 수집된 법령 건수 / 신규 개정 감지 건수 / 정합성 오류 건수 및 처리 현황 / 미반영 개정 목록 / 데이터 커버리지 지도 (지자체별)

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 세연 (데이터 수집·정합성 관리관) | 국토부·지자체 법령 데이터를 실시간 수집·정제·유지하여 분석 엔진의 데이터 신선도를 보장하는 데이터 운영자")
    print("="*60)

    # 런타임 지식 로드
    try:
        from core.context_loader import get_team_system_prompt
        full_prompt = get_team_system_prompt(SYSTEM_PROMPT, "토지SaaS_사업화_실행팀")
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
