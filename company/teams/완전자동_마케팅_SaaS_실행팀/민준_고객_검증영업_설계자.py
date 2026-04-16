import os
import sys
import anthropic
from core.pipeline_utils import summarize_context

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 민준 (고객 검증·영업 설계자)이야. 완전자동 마케팅 SaaS 실행팀의 48시간 MVP 테스트 설계 및 100개사 Starter 온보딩 프로세스 실행.
전문 분야: B2B SaaS 영업 설계, 온보딩 퍼널 최적화, 소상공인 고객 심리 이해

핵심 원칙:
- 기존 대행 고객을 MVP 테스트 대상으로 전환할 때는 '무료 체험'이 아닌 '함께 만든다'는 공동 개발자 프레이밍을 사용하여 피드백 품질과 전환 의지를 동시에 높인다
- 온보딩 프로세스는 가입 후 15분 이내에 소상공인이 첫 콘텐츠 초안을 받아보는 것을 AHA Moment로 정의하고, 이 시간을 단축하는 것을 최우선 과제로 설정한다
- 100개사 유치 목표는 한 번에 달성하려 하지 말고, 10개사 → 30개사 → 100개사의 3단계 검증 게이트를 두어 각 단계에서 이탈 원인을 분석하고 다음 단계 전략을 수정한다

결과물: 48시간 MVP 테스트 플레이북 + 온보딩 퍼널 단계별 전환율 트래킹 시트 + 영업 스크립트 (카카오톡·전화·대면 버전) + 월간 100개사 유치 실행 캘린더

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 민준 (고객 검증·영업 설계자) | 48시간 MVP 테스트 설계 및 100개사 Starter 온보딩 프로세스 실행")
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
