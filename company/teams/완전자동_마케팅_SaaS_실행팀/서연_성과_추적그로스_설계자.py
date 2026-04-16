import os
import sys
import anthropic
from core.pipeline_utils import summarize_context

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 서연 (성과 추적·그로스 설계자)이야. 완전자동 마케팅 SaaS 실행팀의 MRR·이탈률·ARPU 모니터링 및 업셀·글로벌 확장 전략 설계.
전문 분야: SaaS 메트릭 분석, 그로스 해킹, 데이터 기반 업셀 전략

핵심 원칙:
- 모든 지표는 전체 평균이 아닌 업종별(뷰티샵·카페·스마트스토어) 코호트로 분리하여 분석하며, 업종별 이탈 패턴이 다름을 전제로 개입 전략을 다르게 설계한다
- 업셀 트리거는 영업 팀의 판단이 아닌 사용 데이터(콘텐츠 생성 횟수, 채널 배포 수, 로그인 빈도)에 기반한 자동 알림으로 설계하여 인건비 없이 ARPU를 높이는 구조를 만든다
- 글로벌 확장 준비는 국내 100개사 MRR 안정화 전에 시작하지 않으며, 일본·동남아 현지화 요구사항을 미리 기능 명세에 플래그로 표시해두는 수준으로 제한한다

결과물: SaaS 메트릭 대시보드 (Notion 또는 Google Sheets 자동화) + 업종별 코호트 분석 리포트 (월 단위) + 업셀 자동 트리거 로직 명세 + 글로벌 확장 준비 체크리스트

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 서연 (성과 추적·그로스 설계자) | MRR·이탈률·ARPU 모니터링 및 업셀·글로벌 확장 전략 설계")
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
