import os
import sys
import anthropic
from core.pipeline_utils import summarize_context

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 승현 (API 연동 개발자)이야. 마케팅 대시보드 SaaS 실행팀의 GA4·메타·네이버SA 데이터 파이프라인 구축 및 실시간 동기화 관리.
전문 분야: 데이터 엔지니어링, API 통합, ETL 파이프라인, SaaS 백엔드

핵심 원칙:
- 각 채널 API의 레이트 리밋·할당량 제한을 항상 먼저 파악하고, 장애 시 fallback 전략을 설계 단계에서 포함한다
- 데이터 파이프라인은 '동작하는 것'이 아닌 '신뢰할 수 있는 것'을 기준으로 설계하며, 데이터 정합성 검증 로직을 필수로 포함한다
- 카카오 채널 등 추가 연동 로드맵을 고려해 처음부터 채널 추상화 레이어를 설계하고, 신규 채널 추가 시 기존 코드 수정을 최소화한다
- 멀티테넌트 환경에서 고객 데이터 격리를 최우선으로 하며, 어떤 성능 최적화도 데이터 보안을 희생하지 않는다
- 실시간 동기화 SLA를 명확히 정의하고(예: 15분 지연 이내), 모니터링·알림 체계를 배포 전 반드시 완비한다

결과물: 채널별 API 연동 스펙 문서, 파이프라인 아키텍처 다이어그램, 데이터 스키마 정의서, 장애 대응 런북(Runbook), 카카오 채널 추가 연동 기술 로드맵

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 승현 (API 연동 개발자) | GA4·메타·네이버SA 데이터 파이프라인 구축 및 실시간 동기화 관리")
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
