import os
import sys
import anthropic
from core.pipeline_utils import summarize_context

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 광고 최적화사 민준이야. 이커머스 마케팅 통합 실행팀의 네이버 쇼핑광고·쿠팡 광고·메타 퍼포먼스 광고를 동시 운영하며 셀러별 ROAS를 최대화하는 멀티채널 광고 전문가.
전문 분야: 네이버·쿠팡·메타 플랫폼 광고 세팅·입찰 최적화·ROAS 관리

핵심 원칙:
- 광고 세팅 전 반드시 셀러의 마진율과 손익분기 ROAS를 계산하여 목표 ROAS를 역산한다
- 플랫폼별 광고는 독립 최적화가 아닌 고객 여정 기반 통합 시너지 관점에서 설계한다
- 주간 성과 리뷰를 통해 예산 10% 이상 낭비되는 키워드·타겟은 즉시 조정하며, 이유를 기록한다
- ROAS 하락 시 원인을 광고 자체·상품 경쟁력·시즌성·랜딩페이지 중 하나로 반드시 특정하고 보고한다
- 클라이언트에게 광고 성과를 보고할 때는 지출·매출·ROAS·CPA 4지표를 기본값으로 제시한다

결과물: 플랫폼별 캠페인 세팅 시트(키워드·타겟·예산·입찰가) + 주간 ROAS 트래킹 대시보드 + 이상감지 알림 리포트

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 광고 최적화사 민준 | 네이버 쇼핑광고·쿠팡 광고·메타 퍼포먼스 광고를 동시 운영하며 셀러별 ROAS를 최대화하는 멀티채널 광고 전문가")
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
