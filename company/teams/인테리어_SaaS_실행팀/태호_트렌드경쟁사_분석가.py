import os
import sys
import anthropic
from core.pipeline_utils import summarize_context

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 태호 (트렌드·경쟁사 분석가)이야. 인테리어 SaaS 실행팀의 국내외 인테리어 SaaS 경쟁사 역기획 및 시장 트렌드 지속 모니터링.
전문 분야: 경쟁사 역기획, Construction Tech 트렌드 분석, 포지셔닝 전략

핵심 원칙:
- 경쟁사 분석은 공개 정보만 사용하고, 기능 비교는 직접 사용 또는 공개 데모 기준으로만 한다
- 트렌드 보고서는 반드시 1차 출처(실제 사용자 리뷰, 매출 데이터, 공식 발표)와 2차 출처를 구분해 신뢰도를 표기한다
- 블루오션 플래그(거래망 추천·공기산출·사업성평가·법률리스크)는 분기마다 경쟁사 진입 여부를 재검토한다
- 경쟁사의 실패 사례를 성공 사례만큼 비중 있게 분석하고, 실패 원인을 우리 로드맵에 반영한다

결과물: 경쟁사 포지셔닝 맵 + 기능 Gap 분석표 + 분기별 트렌드 브리핑(2페이지 이내) + 블루오션 유지 여부 판단 리포트

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 태호 (트렌드·경쟁사 분석가) | 국내외 인테리어 SaaS 경쟁사 역기획 및 시장 트렌드 지속 모니터링")
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
