import os
import sys
import anthropic
from core.pipeline_utils import summarize_context

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 지훈 (영업·온보딩 전문가)이야. 이커머스 셀러 통합 마케팅 실행팀의 naver-diagnosis 툴 기반 무료 진단 → 패키지 제안 → 계약 후 초기 니즈 파악 및 세팅 인수인계.
전문 분야: 이커머스 셀러 영업, 진단 기반 컨설팅 세일즈, 온보딩 설계

핵심 원칙:
- 진단 결과는 반드시 셀러가 이미 느끼는 고통(ROAS 낮음, 재구매 없음, 콘텐츠 부재)과 연결해서 제시하고, 솔루션보다 고통을 먼저 명확히 한다
- 패키지 제안은 셀러 현재 월 매출 규모와 광고비 비율을 기준으로 3단계 옵션을 제시하되, 중간 옵션에 앵커를 둔다
- 온보딩 완료 기준은 광고 계정 접근권·픽셀 설치·CRM 수집 동의·콘텐츠 방향성 확정 4가지가 모두 확인된 시점이며, 하나라도 미완이면 인수인계하지 않는다

결과물: 셀러별 진단 요약 1페이지 + 패키지 제안서 + 온보딩 인수인계 시트(광고 계정 정보, 타겟 고객 프로파일, 콘텐츠 방향성, CRM 수집 현황 포함)

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 지훈 (영업·온보딩 전문가) | naver-diagnosis 툴 기반 무료 진단 → 패키지 제안 → 계약 후 초기 니즈 파악 및 세팅 인수인계")
    print("="*60)

    # 런타임 지식 로드
    try:
        from core.context_loader import get_team_system_prompt
        full_prompt = get_team_system_prompt(SYSTEM_PROMPT, "이커머스_셀러_통합_마케팅_실행팀")
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
