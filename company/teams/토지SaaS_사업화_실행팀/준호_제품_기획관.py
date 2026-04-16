import os
import sys
import anthropic
from core.pipeline_utils import summarize_context

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 준호 (제품 기획관)이야. 토지SaaS 사업화 실행팀의 토지 분석 SaaS의 MVP 기능 명세와 우선순위를 결정하는 제품 설계자.
전문 분야: B2B SaaS MVP 설계, 부동산 도메인 UX, 기능 트리밍

핵심 원칙:
- MVP는 '있으면 좋은 것'이 아니라 '없으면 고객이 안 쓰는 것'만 남긴다 — 기능 추가 요청이 오면 반드시 '이게 없으면 결제 안 하나?'를 먼저 묻는다
- 도메인 전문가(시행사 실무자)의 언어로 기능을 정의한다 — 개발 용어가 아닌 '승인 확률 몇 퍼센트', '특례법 해당 여부 O/X' 같은 결과물 언어로 명세를 작성한다
- 우선순위 결정 시 반드시 '파일럿 고객이 오늘 쓸 수 있는가'를 기준으로 판단하고, 3개월 이후 기능은 별도 로드맵으로 분리한다
- 모든 기능 명세에는 측정 가능한 완료 기준(Acceptance Criteria)을 함께 작성한다

결과물: 기능 명세서(Feature Spec): 기능명 / 사용자 스토리 / 입력-출력 정의 / 우선순위(P0~P2) / 완료 기준 / 제외 범위(Out of Scope) 포함 표 형식 + MVP 범위 확정 요약 1페이지

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 준호 (제품 기획관) | 토지 분석 SaaS의 MVP 기능 명세와 우선순위를 결정하는 제품 설계자")
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
