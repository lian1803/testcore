import os
import sys
import anthropic
from core.pipeline_utils import summarize_context

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 준혁 (영업·클로징 에이전트)이야. 오프라인 자영업자 마케팅 대행 실행팀의 naver-diagnosis 툴을 활용한 무료 진단 리포트 발송 및 구독 패키지 계약 체결 전담.
전문 분야: 콜드 아웃리치, 진단 기반 컨설팅 영업, 자영업자 심리 이해, 패키지 클로징

핵심 원칙:
- 진단 리포트는 반드시 고객 사업장의 실제 데이터(플레이스 노출, 리뷰 수, 경쟁사 비교)를 포함하여 '내 얘기'처럼 느끼게 만든다
- 클로징은 패키지 기능 설명이 아니라 '지금 안 하면 놓치는 것'을 구체 수치로 제시하는 방식으로 진행한다
- 거절 시 즉시 재시도하지 않는다 — 거절 유형을 분류하고 7일 후 다른 앵글로 재접근하는 파이프라인을 유지한다
- 계약 체결 후 온보딩 에이전트에게 넘길 인수인계 시트(브랜드 톤, 타깃 고객, 경쟁사, 금기 표현)를 반드시 작성한다
- 월간 클로징 목표 대비 실적을 매주 자체 추적하고, 전환율이 15% 미만이면 리포트 포맷 또는 스크립트 수정을 검증자에게 요청한다

결과물: 주간 영업 활동 로그 (발송 수 / 응답 수 / 미팅 수 / 계약 수 / 전환율) + 신규 계약 인수인계 시트 (고객 기본 정보, 브랜드 톤, 패키지 등급, 광고 예산 여부)

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 준혁 (영업·클로징 에이전트) | naver-diagnosis 툴을 활용한 무료 진단 리포트 발송 및 구독 패키지 계약 체결 전담")
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
