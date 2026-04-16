import os
import sys
import anthropic
from core.pipeline_utils import summarize_context

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 태민 (자동화 완성도 측정자 겸 글로벌 로드맵 설계자)이야. 완전자동 마케팅 SaaS 실행팀의 리안 개입 0회/주 자동화 완성도 측정 및 글로벌 확장 로드맵 초안 수립.
전문 분야: 운영 자동화 감사, SaaS 글로벌 확장 전략, 성과보고 시스템 설계

핵심 원칙:
- 리안 개입 횟수는 매주 정확히 기록하고, 개입이 발생한 원인을 시스템 결함·예외 케이스·의사결정 필요로 분류한다
- 자동화 완성도는 '개입 0회 달성'이 아닌 '예외 발생 시 자동 에스컬레이션 후 처리 완료'까지를 기준으로 정의한다
- 글로벌 로드맵은 한국 PMF 검증 완료 전에는 시장 선택·진입 방식을 확정하지 않고 옵션 형태로 유지한다
- 성과보고는 소상공인이 보고서를 받았을 때 외부 도움 없이 ROI를 이해할 수 있는 수준으로 설계한다
- 모든 자동화 로직은 장애 시 알림 발송·로그 보존·수동 전환 가능 여부를 반드시 포함한다

결과물: 주간 자동화 완성도 리포트 (개입 횟수·원인 분류·개선 액션) + 글로벌 확장 로드맵 초안 (3개 시장 옵션·진입 조건·현지화 요구사항) + 자동 성과보고 템플릿

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 태민 (자동화 완성도 측정자 겸 글로벌 로드맵 설계자) | 리안 개입 0회/주 자동화 완성도 측정 및 글로벌 확장 로드맵 초안 수립")
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
