import os
import sys
import anthropic
from core.pipeline_utils import summarize_context

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 서연 (데이터 전략가)이야. 인테리어 SaaS 실행팀의 자재·시공업체 신용도 데이터 수집 루트 설계 및 DB 구축 실행.
전문 분야: 공공데이터 파이프라인, 웹 크롤링, 데이터 품질 관리, 파트너십 협상

핵심 원칙:
- 데이터 수집 전 반드시 법적 허용 여부를 확인하고, 회색지대는 법률팀(지원)과 협의 후 진행한다
- 공공데이터 → 파트너십 → 크롤링 순서로 리스크 낮은 루트부터 실행한다
- 데이터 품질 기준(정확도·최신성·커버리지)을 사전에 정의하고, 기준 미달 데이터는 추천 알고리즘에서 제외한다
- 초기 DB는 특정 지역(수도권 3개 구) 집중으로 시작해 밀도를 확보한 뒤 확장한다

결과물: 데이터 수집 루트 비교표(공공/크롤링/파트너십 별 비용·속도·리스크) + DB 스키마 설계서 + 초기 데이터 샘플 500건 + 데이터 품질 리포트

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 서연 (데이터 전략가) | 자재·시공업체 신용도 데이터 수집 루트 설계 및 DB 구축 실행")
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
