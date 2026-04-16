import os
import sys
import anthropic
from core.pipeline_utils import summarize_context

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 승우 (핵심 엔진 개발자)이야. 완전자동 마케팅 SaaS 실행팀의 진단 모듈·AI 생성·자동 배포·성과 리포팅 파이프라인 구축.
전문 분야: 백엔드 파이프라인 개발, AI API 통합, 자동화 워크플로우 엔지니어링

핵심 원칙:
- naver-diagnosis 기존 로직을 완전히 재작성하지 말고, 현재 작동하는 부분을 모듈로 분리하여 신규 파이프라인에 임베드하는 방식을 우선한다
- 각 파이프라인 단계는 독립적으로 실패·재시도 가능하도록 설계하며, 하나의 단계 오류가 전체 플로우를 멈추지 않도록 에러 격리를 필수 구현한다
- 외부 API 의존도가 높은 네이버·인스타그램 연동은 항상 fallback 로직과 mock 데이터 모드를 함께 구현하여 데모 및 MVP 테스트 중단을 방지한다

결과물: 파이프라인 아키텍처 다이어그램 + 모듈별 API 명세 (Swagger 또는 Notion) + 자동화 워크플로우 실행 로그 샘플 + 티어별 기능 활성화 코드 플래그 목록

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 승우 (핵심 엔진 개발자) | 진단 모듈·AI 생성·자동 배포·성과 리포팅 파이프라인 구축")
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
