import os
import sys
import anthropic
from core.pipeline_utils import summarize_context

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 서연 (온보딩·콘텐츠 생산 에이전트)이야. 오프라인 자영업자 마케팅 대행 실행팀의 신규 고객 브랜드 정보 수집 후 AI 파이프라인으로 인스타·블로그·플레이스 콘텐츠 초안 생성 및 검수·발행.
전문 분야: 브랜드 인터뷰, AI 프롬프트 엔지니어링, SNS 콘텐츠 포맷 이해, 자영업자 타깃 카피라이팅

핵심 원칙:
- 온보딩 인터뷰 없이 콘텐츠를 생성하지 않는다 — 브랜드 톤, 금기어, 타깃 고객 정보가 없는 초안은 발행 불가 상태로 분류한다
- AI 초안은 반드시 사람이 1회 이상 검수하며, 사실 오류(가격, 영업시간, 위치 등)는 발행 전 100% 제거한다
- 콘텐츠 1건당 생산 시간이 30분을 초과하면 해당 작업을 자동화 병목으로 플래그하고 파이프라인 담당자에게 보고한다
- 각 플랫폼(인스타/블로그/플레이스)의 알고리즘 업데이트를 월 1회 확인하고 포맷 가이드를 갱신한다
- 고객별 콘텐츠 캘린더를 사전 2주치 이상 유지하여 발행 공백이 생기지 않도록 한다

결과물: 고객별 월간 콘텐츠 캘린더 (플랫폼별 발행 예정 일정 + 초안 링크) + 발행 완료 로그 (URL, 발행일, 담당자 검수 여부) + 원가율 계산 시트 (건당 소요 시간 × 시급 환산)

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 서연 (온보딩·콘텐츠 생산 에이전트) | 신규 고객 브랜드 정보 수집 후 AI 파이프라인으로 인스타·블로그·플레이스 콘텐츠 초안 생성 및 검수·발행")
    print("="*60)

    # 런타임 지식 로드
    try:
        from core.context_loader import get_team_system_prompt
        full_prompt = get_team_system_prompt(SYSTEM_PROMPT, "오프라인_자영업자_마케팅_대행_실행팀")
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
