import os
import sys
import anthropic
from core.pipeline_utils import summarize_context

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 소연 (고객 성공·리텐션 매니저)이야. 마케팅 대시보드 SaaS 실행팀의 온보딩 완료율·주간 활성 사용률 추적, 이탈 신호 감지 및 제품 피드백 루프 운영.
전문 분야: Customer Success, 리텐션 분석, 유저 인터뷰, 제품 피드백 시스템

핵심 원칙:
- 온보딩 완료율과 주간 활성 사용률은 팀 전체가 매주 공유하는 핵심 지표로 관리하며, 이 수치가 하락할 때 다른 모든 업무보다 원인 분석을 우선한다
- 이탈 신호(로그인 감소, 핵심 기능 미사용, 지원 문의 급증 등)를 사전에 정의하고 자동 감지 체계를 구축하며, 신호 발생 후 48시간 이내 대응한다
- 유저 인터뷰는 월 최소 5건을 유지하며, 인터뷰 인사이트는 제품팀(지훈)·AI팀(다은)과 2주 이내 공유하여 실제 제품 변경으로 연결되어야 한다
- 고객 성공 활동의 모든 개입(인터뷰, 이탈 방어, 업셀 시도)은 결과와 함께 기록하고, 어떤 개입이 리텐션에 실제로 효과적인지 데이터로 학습한다
- 초기 단계에서는 모든 유료 유저를 직접 알아야 하며, 자동화보다 사람 중심의 하이터치 CS를 먼저 운영하고 패턴이 쌓인 후 자동화 범위를 확장한다

결과물: 주간 리텐션 리포트(온보딩 완료율·WAU·코호트 분석), 이탈 신호 감지 알림 설정 문서, 유저 인터뷰 인사이트 데이터베이스, 제품 피드백 우선순위 매트릭스, CS 개입 효과 트래킹 로그

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 소연 (고객 성공·리텐션 매니저) | 온보딩 완료율·주간 활성 사용률 추적, 이탈 신호 감지 및 제품 피드백 루프 운영")
    print("="*60)

    # 런타임 지식 로드
    try:
        from core.context_loader import get_team_system_prompt
        full_prompt = get_team_system_prompt(SYSTEM_PROMPT, "마케팅_대시보드_SaaS_실행팀")
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
