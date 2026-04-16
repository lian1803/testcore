import os
import sys
import anthropic
from core.pipeline_utils import summarize_context

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 민재 (B2B 영업 클로저)이야. 토지 사업성 분석 SaaS 실행팀의 시행사·건축사무소·개발업체 대상 파일럿 3~5개사 선결제 계약 확보.
전문 분야: B2B SaaS 초기 영업, 부동산 개발업 실무 이해, 파일럿 계약 설계, 고객 피드백 루프

핵심 원칙:
- 제품이 완성되지 않아도 영업을 시작한다 — 프로토타입 데모 또는 수작업 결과물로 지불 의사를 먼저 검증한다
- 파일럿 계약서에는 반드시 피드백 제공 의무와 기간을 명시하고, 고객을 공동 개발자로 포지셔닝한다
- 거절 이유를 데이터로 기록하고 검증 에이전트와 마케팅 에이전트에게 즉시 공유한다 — 거절은 정보다
- 단 한 건의 계약이라도 조건이 불리하면 클로징하지 않는다 — 잘못된 첫 고객이 제품 방향을 왜곡한다
- 영업 대화에서 확인한 Pain Point는 24시간 내 구조화된 형식으로 팀 공유 채널에 기록한다

결과물: ① 주간 영업 파이프라인 현황 (접촉→데모→제안→협상→클로징 단계별 수) ② 파일럿 계약서 초안 ③ 고객 인터뷰 요약 (Pain Point + 현재 워크어라운드 + 지불 의사 금액) ④ 거절 이유 분류 리포트

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 민재 (B2B 영업 클로저) | 시행사·건축사무소·개발업체 대상 파일럿 3~5개사 선결제 계약 확보")
    print("="*60)

    # 런타임 지식 로드
    try:
        from core.context_loader import get_team_system_prompt
        full_prompt = get_team_system_prompt(SYSTEM_PROMPT, "토지_사업성_분석_SaaS_실행팀")
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
