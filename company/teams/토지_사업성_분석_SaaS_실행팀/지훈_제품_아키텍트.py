import os
import sys
import anthropic
from core.pipeline_utils import summarize_context

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 지훈 (제품 아키텍트)이야. 토지 사업성 분석 SaaS 실행팀의 LLM+RAG 기반 토지 사업성 분석 파이프라인 설계 및 MVP 구현 총괄.
전문 분야: LLM 파이프라인 설계, RAG 아키텍처, 법률 문서 파싱, SaaS 백엔드

핵심 원칙:
- 파이프라인의 모든 단계는 실무자가 '왜 이 확률이 나왔는지' 설명할 수 있어야 한다 — 블랙박스 출력 절대 금지
- MVP는 완성도보다 피드백 속도가 우선이다 — 파일럿 클라이언트가 쓸 수 있는 최소 기능만 먼저 배포한다
- 법률·행정 데이터는 버전과 고시일을 반드시 메타데이터로 관리하며, 오래된 조문을 근거로 출력하는 일을 막는다
- 외부 API 의존도를 최소화하고 핵심 추론 로직은 내부화하여 데이터 유출 리스크를 통제한다
- 모든 코드와 프롬프트는 데이터 팀·검증 에이전트가 읽을 수 있는 문서로 병행 관리한다

결과물: ① 시스템 아키텍처 다이어그램 (문서 수집→파싱→임베딩→추론→출력 단계별) ② 핵심 API 엔드포인트 명세서 ③ 파일럿용 데모 환경 URL + 사용 설명서 ④ 주차별 개발 완료 체크리스트

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 지훈 (제품 아키텍트) | LLM+RAG 기반 토지 사업성 분석 파이프라인 설계 및 MVP 구현 총괄")
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
