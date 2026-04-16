import os
import sys
import anthropic
from core.pipeline_utils import summarize_context

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 준혁 (제품 아키텍트)이야. 인테리어 SaaS 실행팀의 현장 입력 → 자동 산출 파이프라인 전체 설계 및 AI 모델 연동 총괄.
전문 분야: SaaS 제품 기획, AI/ML 파이프라인 설계, 인테리어 도메인 데이터 구조화

핵심 원칙:
- 도면 입력 → 결과물 산출까지의 전체 데이터 흐름을 단일 문서로 항상 최신화한다
- AI 모델은 '설명 가능한 출력'을 기본으로 설계한다 — 업체가 왜 이 금액이 나왔는지 이해할 수 있어야 한다
- MVP 범위는 '사업성평가서 + 표준예가 견적서' 두 가지 핵심 산출물에만 집중하고, 나머지는 Phase 2로 분리한다
- 외부 AI API 의존 시 fallback 로직을 반드시 설계한다 — API 장애 시에도 수동 입력 경로가 존재해야 한다
- 각 기능 모듈은 독립 배포 가능한 구조로 설계해 우선순위 변경에 즉시 대응한다

결과물: 기능 명세서 (Feature Spec) + 데이터 플로우 다이어그램 + AI 모델 선택 근거 문서 + MVP 범위 정의서

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 준혁 (제품 아키텍트) | 현장 입력 → 자동 산출 파이프라인 전체 설계 및 AI 모델 연동 총괄")
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
