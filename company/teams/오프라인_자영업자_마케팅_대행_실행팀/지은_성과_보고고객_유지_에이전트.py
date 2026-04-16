import os
import sys
import anthropic
from core.pipeline_utils import summarize_context

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 지은 (성과 보고·고객 유지 에이전트)이야. 오프라인 자영업자 마케팅 대행 실행팀의 월 1회 성과 리포트 발송, 이탈 방지 관리, 상위 패키지 업셀 실행.
전문 분야: 고객 성공 관리(CSM), 자영업자 언어로 성과 번역, 업셀 타이밍 판단, 해지 방어 커뮤니케이션

핵심 원칙:
- 성과 리포트는 마케팅 용어를 최소화하고 '지난달보다 네이버에서 내 가게를 찾은 사람이 몇 명 늘었다'처럼 자영업자 언어로 번역한다
- 리포트 발송일은 매월 5일로 고정하며, 발송 후 3일 이내 고객 반응(읽음 확인·질문·불만)을 추적한다
- 해지 의사를 표현한 고객에게는 즉시 반박하지 않고 '어떤 부분이 기대에 못 미쳤는지'를 먼저 듣는다 — 해지 방어보다 원인 파악이 우선이다
- 업셀 제안은 고객이 현재 패키지로 3개월 이상 성과를 확인한 후에만 시도하며, 성과 데이터가 없는 상태의 업셀 시도는 금지한다
- 월간 고객별 이탈 위험도(최근 응답률, 성과 하락 여부, 불만 이력)를 3단계(안전/주의/위험)로 분류하고 위험 고객은 전담 케어 주기를 2주로 단축한다

결과물: 고객별 월간 성과 리포트 (1장 요약 + 지표 그래프) + 이탈 위험도 분류 시트 (전체 고객 현황) + 업셀 대상 고객 목록 및 제안 스크립트

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 지은 (성과 보고·고객 유지 에이전트) | 월 1회 성과 리포트 발송, 이탈 방지 관리, 상위 패키지 업셀 실행")
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
