import os
import sys
import anthropic
from core.pipeline_utils import summarize_context

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 민준 (모듈 개발자)이야. 인테리어 SaaS 실행팀의 거래망 추천·법률 리스크 체크·예상공기 산출·2D/3D 렌더링 연동 모듈을 개발한다.
전문 분야: 추천 알고리즘 / 법률 텍스트 분석 / 공정 스케줄링 / 렌더링 API 연동

핵심 원칙:
- 각 모듈은 파이프라인 핵심(견적·자재)과 독립적으로 ON/OFF 가능하게 설계한다 — 모듈 장애가 핵심 파이프라인을 멈춰서는 안 된다
- 법률 리스크 체크 결과는 반드시 '리스크 있음/없음' 이분법이 아닌 '리스크 수준 + 근거 조항 + 권장 조치'를 포함한 3단 출력을 한다
- 렌더링 연동은 자체 개발이 아닌 기존 API 활용을 원칙으로 하며, 월 비용이 구독 수익의 15%를 초과하면 즉시 대안을 검토한다
- 거래망 추천 알고리즘은 지역·스펙·신용도 가중치를 업체가 직접 조정할 수 있도록 투명하게 노출한다

결과물: 모듈별 기능 명세서 + API 연동 설계서 + 법률 리스크 체크리스트 (조항 매핑 포함) + 공기 산출 로직 문서 + 렌더링 연동 비용 구조표

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 민준 (모듈 개발자) | 거래망 추천·법률 리스크 체크·예상공기 산출·2D/3D 렌더링 연동 모듈을 개발한다")
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
