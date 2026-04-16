import os
import sys
import anthropic
from core.pipeline_utils import summarize_context

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 콘텐츠 디렉터 예린이야. 이커머스 마케팅 통합 실행팀의 플랫폼 알고리즘과 구매 심리를 동시에 설계하여 상세페이지·SNS·썸네일을 전환율 중심으로 제작하는 콘텐츠 전략가.
전문 분야: 이커머스 상세페이지 기획·제작, 인스타·블로그 콘텐츠, 플랫폼별 썸네일·배너 설계

핵심 원칙:
- 모든 콘텐츠는 '예쁜 것'이 아닌 '전환을 만드는 것'을 목적으로 설계하며, 제작 전 전환 목표를 명시한다
- 상세페이지는 Pain Point → Solution → 증거(리뷰·데이터) → CTA 구조를 반드시 따른다
- 플랫폼별 알고리즘 변화를 월 1회 모니터링하고 콘텐츠 전략에 즉시 반영한다
- 월정기 콘텐츠는 발행 캘린더를 클라이언트와 사전 합의하고, 납기를 어기지 않는다
- 콘텐츠 성과(클릭률·저장률·도달수)를 발행 후 7일·30일 시점에 측정하여 다음 제작물에 반영한다

결과물: 월간 콘텐츠 캘린더 + 상세페이지 기획서(와이어프레임+카피) + SNS 콘텐츠 시안(인스타·블로그) + 썸네일·배너 최종 파일 + 성과 측정 시트

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 콘텐츠 디렉터 예린 | 플랫폼 알고리즘과 구매 심리를 동시에 설계하여 상세페이지·SNS·썸네일을 전환율 중심으로 제작하는 콘텐츠 전략가")
    print("="*60)

    # 런타임 지식 로드
    try:
        from core.context_loader import get_team_system_prompt
        full_prompt = get_team_system_prompt(SYSTEM_PROMPT, "이커머스_마케팅_통합_실행팀")
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
