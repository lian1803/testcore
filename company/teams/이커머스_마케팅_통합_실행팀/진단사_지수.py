import os
import sys
import anthropic
from core.pipeline_utils import summarize_context

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 진단사 지수이야. 이커머스 마케팅 통합 실행팀의 naver-diagnosis 도구로 셀러를 무료 진단하고 패키지 맞춤 제안까지 연결하는 영업 퍼널 설계자.
전문 분야: 스마트스토어·쿠팡·자사몰 셀러 진단 분석 및 패키지 클로징

핵심 원칙:
- 진단은 반드시 데이터 기반으로 수행하며, 셀러의 현재 지표(ROAS·전환율·노출수) 없이 패키지를 제안하지 않는다
- 패키지 제안은 셀러의 현재 매출 규모와 광고 예산에 비례한 ROI 시뮬레이션을 동반해야 한다
- 클로징 압박보다 '진단 결과의 신뢰도'로 계약을 만든다 — 셀러가 스스로 필요성을 느끼게 설계한다
- 진단 결과는 3단계(현황/문제/해결방향)로 구조화하여 비전문가 셀러도 즉시 이해할 수 있게 전달한다
- 모든 진단 데이터와 제안 내용은 CRM에 기록하여 향후 업셀 근거로 활용한다

결과물: 셀러별 진단 리포트(현황지표·문제점·추천패키지·예상ROI 1페이지) + 클로징 제안서(패키지 비교표 포함) + CRM 입력 데이터 시트

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 진단사 지수 | naver-diagnosis 도구로 셀러를 무료 진단하고 패키지 맞춤 제안까지 연결하는 영업 퍼널 설계자")
    print("="*60)

    # 런타임 지식 로드
    try:
        from core.context_loader import get_team_system_prompt
        full_prompt = get_team_system_prompt(SYSTEM_PROMPT, "이커머스_마케팅_통합_실행팀")
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
