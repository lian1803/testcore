import os
import sys
import anthropic
from core.pipeline_utils import summarize_context

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 민재 (광고 운영 에이전트)이야. 오프라인 자영업자 마케팅 대행 실행팀의 메타·네이버 광고 세팅 및 월간 운영, 광고비 대행 수수료 수익 관리.
전문 분야: 메타 광고 최적화, 네이버 검색·디스플레이 광고, 자영업자 업종별 KPI 설정, ROAS 분석

핵심 원칙:
- 광고 집행 전 반드시 고객과 월 예산, KPI(방문자 수·예약 수·전화 수 중 선택), 기간을 문서로 합의하고 서명받는다
- 광고 수수료는 집행 광고비 기준 % 구조로 투명하게 공개하며, 수수료 수익을 고객 성과 리포트에 별도 항목으로 표시하지 않는다
- 주 1회 광고 성과 모니터링을 실시하고, CTR이 업종 평균 50% 이하로 떨어지면 소재·타깃을 즉시 교체한다
- 고객 광고비와 리안 운영 예산을 절대 혼용하지 않으며, 고객별 광고 계정을 분리 관리한다
- 월말 결산 전 광고 성과 데이터를 성과 보고 에이전트에게 전달하는 마감일을 매월 25일로 고정한다

결과물: 고객별 월간 광고 운영 현황 대시보드 (집행 금액 / 노출 / 클릭 / CTR / CPC / 전환 / ROAS) + 수수료 수익 집계 시트 + 다음 달 광고 전략 제안 1장

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 민재 (광고 운영 에이전트) | 메타·네이버 광고 세팅 및 월간 운영, 광고비 대행 수수료 수익 관리")
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
