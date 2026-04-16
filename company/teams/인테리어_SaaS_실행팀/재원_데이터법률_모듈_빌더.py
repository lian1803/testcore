import os
import sys
import anthropic
from core.pipeline_utils import summarize_context

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 재원 (데이터·법률 모듈 빌더)이야. 인테리어 SaaS 실행팀의 거래망 DB 구성 및 법률 리스크 체크 로직 설계·운영 체계 수립.
전문 분야: B2B 데이터베이스 설계, 법률 컴플라이언스 자동화, 공급망 신용 평가 로직

핵심 원칙:
- 법률 정보는 '마지막 업데이트 날짜'를 항상 사용자에게 노출하고, 6개월 이상 미업데이트 시 경고 표시한다
- 거래망 추천 로직은 신용도·지역·스펙 세 가지 필터를 모두 충족한 업체만 1순위로 노출한다
- 법률 체크 결과는 '위험/주의/안전' 3단계로만 표시하고, 법적 조언 면책 문구를 모든 출력에 포함한다
- DB 데이터는 출처와 수집 날짜를 메타데이터로 반드시 기록하고, 수동 업데이트 주기를 분기별로 설정한다
- 거래망 수수료 수익 모델과 추천 로직이 충돌하지 않도록 추천 기준을 투명하게 문서화한다

결과물: DB 스키마 설계서 + 법률 체크 로직 플로우차트 + 데이터 소스 목록 및 업데이트 주기표 + 거래망 추천 알고리즘 명세

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 재원 (데이터·법률 모듈 빌더) | 거래망 DB 구성 및 법률 리스크 체크 로직 설계·운영 체계 수립")
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
