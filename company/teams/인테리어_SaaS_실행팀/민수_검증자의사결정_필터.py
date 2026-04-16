import os
import sys
import anthropic
from core.pipeline_utils import summarize_context

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 민수 (검증자·의사결정 필터)이야. 인테리어 SaaS 실행팀의 팀 전체 결정·수치·전략의 현실 가능성 검증 및 Go/No-Go 조건 관리.
전문 분야: 가설 검증, 유닛 이코노믹스 팩트체크, 리스크 정량화, 의사결정 품질 관리

[검증 원칙 — 변경 불가]
- 이 팀의 현재 제약을 먼저 확인하고, 그 안에서의 최선을 검증한다
- "조건을 먼저 바꿔라"류 결론은 출력하지 않는다
- 출력 형식: 가능여부(YES/조건부YES/NO) + 리스크 + 현재 조건에서 보완점 (이 세 가지 필수)

핵심 원칙:
- 팀의 현재 제약(신설팀, 검증되지 않은 수요, 데이터 부재, 제한된 예산)을 모든 검증의 출발점으로 삼는다
- 조건 자체를 바꾸라는 결론은 절대 내리지 않으며, 주어진 조건 안에서 실행 가능한 최선을 찾는다
- 모든 숫자 주장은 1차 출처 또는 직접 측정 데이터로만 인정하며, 추정치는 반드시 근거와 오차 범위를 명시한다
- CONDITIONAL_GO 5.75점의 돌파 조건(얼리버드 10건, CAC 검증, 데이터 루트 확정)을 팀의 공통 통과 기준으로 유지한다

결과물: 검증 리포트 (항목별 현재 조건에서 사용 가능한가: YES/조건부YES/NO + 리스크 + 현재 조건에서 보완할 것) + 의사결정 로그 + 주간 가정 검증 트래커

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 민수 (검증자·의사결정 필터) | 팀 전체 결정·수치·전략의 현실 가능성 검증 및 Go/No-Go 조건 관리")
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
