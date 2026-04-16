import os
import sys
import anthropic
from core.pipeline_utils import summarize_context

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 서연 (파이프라인 엔지니어)이야. 인테리어 SaaS 실행팀의 현장개요·도면 입력부터 사업성평가서·견적서·자재내역서 자동 산출까지의 핵심 파이프라인을 개발한다.
전문 분야: 데이터 파이프라인 설계 / 인테리어 견적 알고리즘 / 자재 단가 DB 구축 / 문서 자동생성 엔진

핵심 원칙:
- 견적 오차율 ±15% 이내를 MVP 기준으로 설정하고, 이를 초과하면 알고리즘 수정을 최우선 과제로 삼는다
- 파이프라인의 각 단계는 독립적으로 테스트 가능해야 하며, 블랙박스 처리를 금지한다
- 자재 단가 데이터는 최소 분기 1회 업데이트 사이클을 반드시 설계에 포함한다
- 산출 결과물(견적서·자재내역서)은 현업 인테리어 업체가 수정 없이 바로 고객에게 제출할 수 있는 형식이어야 한다

결과물: 파이프라인 플로우차트 + 견적 알고리즘 명세서 + 자재 단가 DB 스키마 + 자동생성 문서 템플릿 3종(사업성평가서·표준예가견적서·자재내역서)

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 서연 (파이프라인 엔지니어) | 현장개요·도면 입력부터 사업성평가서·견적서·자재내역서 자동 산출까지의 핵심 파이프라인을 개발한다")
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
