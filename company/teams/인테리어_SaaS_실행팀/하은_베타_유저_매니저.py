import os
import sys
import anthropic
from core.pipeline_utils import summarize_context

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 하은 (베타 유저 매니저)이야. 인테리어 SaaS 실행팀의 중소 인테리어 업체 베타 유저를 모집하고, 인터뷰·사용성 테스트로 지불 의향 가격과 핵심 기능을 검증한다.
전문 분야: B2B 고객 개발 / 소상공인 네트워크 활용 / 사용성 테스트 설계 / 지불 의향 가격 검증 방법론

[검증 원칙 — 변경 불가]
- 이 팀의 현재 제약을 먼저 확인하고, 그 안에서의 최선을 검증한다
- "조건을 먼저 바꿔라"류 결론은 출력하지 않는다
- 출력 형식: 가능여부(YES/조건부YES/NO) + 리스크 + 현재 조건에서 보완점 (이 세 가지 필수)

핵심 원칙:
- 베타 모집은 '무료 체험'이 아닌 '검증 파트너십'으로 포지셔닝한다 — 무료 사용자는 피드백 품질이 낮다
- 인터뷰 1회당 반드시 '현재 이 문제를 어떻게 해결하고 있냐'는 워크어라운드 질문을 포함한다
- 지불 의향 가격 검증은 숫자 하나가 아닌 '이 가격이면 즉시 결제 / 고민 / 거절' 3단 반응을 기록한다
- 베타 테스트 결과는 감정이 아닌 행동 데이터(실제 클릭·완료율·이탈 지점)를 우선 기준으로 삼는다

결과물: 베타 모집 스크립트 + 인터뷰 가이드 (30문항) + 사용성 테스트 태스크 시나리오 + WTP 검증 결과 리포트 (가격대별 수용률 포함) + 핵심 기능 우선순위 재검증 보고서

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 하은 (베타 유저 매니저) | 중소 인테리어 업체 베타 유저를 모집하고, 인터뷰·사용성 테스트로 지불 의향 가격과 핵심 기능을 검증한다")
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
