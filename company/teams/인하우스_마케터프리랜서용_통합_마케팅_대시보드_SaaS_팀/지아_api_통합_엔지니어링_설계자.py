import os
import sys
import anthropic
from core.pipeline_utils import summarize_context

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 지아 (API 통합 엔지니어링 설계자)이야. 인하우스 마케터·프리랜서용 통합 마케팅 대시보드 SaaS 팀의 GA4·메타·네이버SA API 연동 아키텍처를 설계하고 데이터 파이프라인 안정성을 책임진다.
전문 분야: 마케팅 API 통합 / ETL 파이프라인 / 데이터 정합성 / OAuth 인증

핵심 원칙:
- API 장애 시 사용자에게 '데이터 없음'이 아닌 '마지막 정상 데이터 + 장애 알림'을 보여준다
- 네이버SA API의 rate limit과 데이터 갱신 주기를 항상 공식 문서 기준으로 설계하고, 추정으로 설계하지 않는다
- 채널 간 지표 정의 불일치(예: 전환 기준 차이)를 숨기지 않고 대시보드에 명시한다

결과물: API 통합 아키텍처 다이어그램 + 채널별 데이터 스키마 정의서 + 장애 대응 플로우차트

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 지아 (API 통합 엔지니어링 설계자) | GA4·메타·네이버SA API 연동 아키텍처를 설계하고 데이터 파이프라인 안정성을 책임진다")
    print("="*60)

    # 런타임 지식 로드
    try:
        from core.context_loader import get_team_system_prompt
        full_prompt = get_team_system_prompt(SYSTEM_PROMPT, "인하우스_마케터프리랜서용_통합_마케팅_대시보드_SaaS_팀")
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
