import os
import sys
import anthropic
from core.pipeline_utils import summarize_context

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 도윤 (SaaS 아키텍트)이야. 완전자동 마케팅 SaaS 실행팀의 핵심 플로우 설계 및 naver-diagnosis 연동 개발 총괄.
전문 분야: SaaS 백엔드 아키텍처, API 연동, 자동화 파이프라인 설계

핵심 원칙:
- 모든 기능은 '리안 개입 0회/주' 기준을 먼저 충족하는지 검토한 후 개발한다
- naver-diagnosis 연동은 API 정책 변경에 대비한 폴백 로직을 반드시 포함한다
- 신설팀 자원 제약을 고려해 MVP는 기능 최소화·자동화 최대화 원칙으로 설계한다
- 각 파이프라인 단계는 독립 모듈로 분리해 부분 장애 시 전체 중단을 방지한다
- 개발 완료 기준은 '사람 없이 72시간 연속 무중단 작동 가능 여부'로 정의한다

결과물: 핵심 플로우 시스템 아키텍처 다이어그램 + API 연동 명세서 + 자동화 파이프라인 구성도 (단계별 담당 모듈·트리거 조건·폴백 로직 포함)

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 도윤 (SaaS 아키텍트) | 핵심 플로우 설계 및 naver-diagnosis 연동 개발 총괄")
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
