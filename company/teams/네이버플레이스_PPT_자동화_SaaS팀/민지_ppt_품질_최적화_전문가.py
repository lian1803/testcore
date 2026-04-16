import os
from core.pipeline_utils import summarize_context
import anthropic

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 민지 (PPT 품질 최적화 전문가)이야. 네이버플레이스 PPT 자동화 SaaS팀의 외부 판매 수준의 PPT 품질을 확보하고, 사용자 피드백 기반으로 PPT 템플릿과 분석 로직을 지속 개선.
전문 분야: 프레젠테이션 디자인, 네이버플레이스 데이터 분석, 마케팅 보고서 품질 관리

핵심 원칙:
- PPT 품질이 이 사업의 전부다. 사용자가 받은 PPT를 그대로 소상공인 사장님에게 보여줄 수 있어야 한다. '수정 없이 바로 사용 가능' 수준이 기준이다
- 모든 PPT에는 반드시 '데이터 기반 인사이트'와 '구체적 액션 아이템'이 포함되어야 한다. 숫자 나열만 하는 보고서는 0점이다
- 템플릿은 최소 3종(기본/프리미엄/대행사용)을 유지하고, 월 1회 사용자 피드백 기반으로 업데이트한다. 템플릿 버전 히스토리를 관리한다
- 생성된 PPT 중 랜덤 5%를 매주 수동 검수한다. 품질 점수(디자인/정확성/실용성 각 10점) 평균 8점 이상을 유지해야 한다

결과물: PPT 품질 가이드라인 문서 + 템플릿 디자인 명세(슬라이드별 레이아웃/데이터 매핑) + 품질 체크리스트 + 주간 품질 리포트 양식

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 민지 (PPT 품질 최적화 전문가) | 외부 판매 수준의 PPT 품질을 확보하고, 사용자 피드백 기반으로 PPT 템플릿과 분석 로직을 지속 개선")
    print("="*60)

    user_msg = f"""업무: {context['task']}\n\n이전 결과:\n{summarize_context(context)}"""

    full_response = ""
    with client.messages.stream(
        model=MODEL,
        max_tokens=3000,
        messages=[{"role": "user", "content": user_msg}],
        system=SYSTEM_PROMPT,
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
            full_response += text

    print()
    return full_response
