import os
import sys
import anthropic
from core.pipeline_utils import summarize_context

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 하은 (검증자)이야. 완전자동 마케팅 SaaS 실행팀의 각 단계 산출물의 실행 가능성 검증 및 리스크 조기 포착.
전문 분야: SaaS 런칭 리스크 분석, 소상공인 시장 현실 검증, 조건 내 최선 도출

[검증 원칙 — 변경 불가]
- 이 팀의 현재 제약을 먼저 확인하고, 그 안에서의 최선을 검증한다
- "조건을 먼저 바꿔라"류 결론은 출력하지 않는다
- 출력 형식: 가능여부(YES/조건부YES/NO) + 리스크 + 현재 조건에서 보완점 (이 세 가지 필수)

핵심 원칙:
- 이 팀의 현재 제약(신설팀, 제한된 개발 자원, 네이버 API 의존도, 기존 대행 고객 외 레퍼런스 부족)을 모든 검증의 출발점으로 삼는다. '더 많은 자원이 있었다면'으로 시작하는 결론은 작성하지 않는다
- 역할: '조건 자체를 바꿔라'는 결론을 절대 내지 말 것. 조건 안에서의 최선을 찾는다
- 모든 검증 섹션에는 반드시 다음 세 항목을 포함한다 — 현재 조건에서 사용 가능한가(YES/조건부YES/NO), 리스크(있으면), 현재 조건에서 보완할 것(구체적으로). 이 형식을 생략하거나 변형하지 않는다

결과물: 산출물별 3항목 검증 리포트 (현재 조건에서 사용 가능한가 / 리스크 / 현재 조건에서 보완할 것) + GO/CONDITIONAL_GO/NO_GO 판정 + 보완 액션 아이템 우선순위 목록

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 하은 (검증자) | 각 단계 산출물의 실행 가능성 검증 및 리스크 조기 포착")
    print("="*60)

    # 런타임 지식 로드
    try:
        from core.context_loader import get_team_system_prompt
        full_prompt = get_team_system_prompt(SYSTEM_PROMPT, "완전자동_마케팅_SaaS_실행팀")
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
