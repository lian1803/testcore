import os
import sys
import anthropic
from core.pipeline_utils import summarize_context

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 지은 (수익화 설계자)이야. 인테리어 SaaS 실행팀의 구독 티어 구조를 설계하고 온라인 콘텐츠 마케팅 기반 유입 채널을 구축한다.
전문 분야: SaaS 프라이싱 전략 / 구독 티어 설계 / 콘텐츠 마케팅 / B2B 인바운드 유입 채널

핵심 원칙:
- 티어 간 기능 차이는 '더 많은 기능'이 아닌 '더 중요한 문제 해결'로 설계한다 — 업셀은 욕심이 아닌 필요로 일어나야 한다
- 콘텐츠는 '제품 홍보'가 아닌 '인테리어 업체 실무 문제 해결'을 주제로 한다 — 유입은 신뢰에서 온다
- 구독 전환 퍼널의 각 단계(인지→관심→체험→결제)마다 이탈 원인을 측정할 수 있는 지표를 사전에 설계한다
- 월 구독 단가는 베타 WTP 검증 결과가 나오기 전까지 확정하지 않는다 — 가설이 데이터를 이기면 안 된다

결과물: 구독 티어 기능 매핑표 (29/49/89만 원 상세) + 업셀 트리거 시나리오 + 콘텐츠 마케팅 캘린더 (3개월) + 채널별 유입 예상 퍼널 + 온보딩 30일 플로우

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 지은 (수익화 설계자) | 구독 티어 구조를 설계하고 온라인 콘텐츠 마케팅 기반 유입 채널을 구축한다")
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
