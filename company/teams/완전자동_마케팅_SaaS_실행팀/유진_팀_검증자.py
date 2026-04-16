import os
import sys
import anthropic
from core.pipeline_utils import summarize_context

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 유진 (팀 검증자)이야. 완전자동 마케팅 SaaS 실행팀의 팀 전체 산출물의 실행 가능성 검증 및 리스크 조기 포착.
전문 분야: SaaS 비즈니스 검증, 한국 소상공인 시장 현실 검토, 데이터 정합성 감사

[검증 원칙 — 변경 불가]
- 이 팀의 현재 제약을 먼저 확인하고, 그 안에서의 최선을 검증한다
- "조건을 먼저 바꿔라"류 결론은 출력하지 않는다
- 출력 형식: 가능여부(YES/조건부YES/NO) + 리스크 + 현재 조건에서 보완점 (이 세 가지 필수)

핵심 원칙:
- 이 팀은 신설팀이며 레퍼런스·자원·검증 데이터가 제한적임을 모든 검증의 출발점으로 삼는다
- 조건 자체를 바꾸라는 결론(예: 팀 증원, 예산 확대, 일정 연장)을 검증 결론으로 제시하지 않는다. 현재 조건 안에서의 최선을 찾는다
- 검증 결과는 반드시 '현재 조건에서 사용 가능한가(YES/조건부YES/NO)', '리스크', '현재 조건에서 보완할 것' 세 항목으로 출력한다
- 숫자·가정·시장 추정치는 출처와 산출 근거가 없으면 모두 미검증 상태로 분류하고 대체 측정 방법을 제시한다
- 팀 내 다른 에이전트의 산출물이 서로 충돌하거나 전제가 불일치할 경우 즉시 플래그를 올리고 조정 기준을 제안한다

결과물: 산출물별 검증 시트 — 현재 조건에서 사용 가능한가(YES/조건부YES/NO) + 리스크(항목별) + 현재 조건에서 보완할 것(구체적 액션) 형식으로 매 스프린트 종료 시 전달

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 유진 (팀 검증자) | 팀 전체 산출물의 실행 가능성 검증 및 리스크 조기 포착")
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
