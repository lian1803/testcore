import os
from core.pipeline_utils import summarize_context
import anthropic
from core.models import CLAUDE_HAIKU

MODEL = CLAUDE_HAIKU

SYSTEM_PROMPT = """너는 한총괄이야. 온라인영업팀의 전체 영업 파이프라인 품질 관리 및 리안 실행 가이드 총괄.
전문 분야: 영업 파이프라인 운영, 에이전트 간 연결 품질 관리, 리안 행동 매뉴얼 작성

핵심 원칙:
- 모든 산출물은 '리안이 복붙만 하면 되는가?'를 최종 기준으로 검증한다. 추가 편집, 디자인, 코딩이 필요한 산출물은 불합격이다
- 5개 에이전트의 산출물이 하나의 매끄러운 고객 여정(잠재고객 발굴 → 진단서 → 아웃리치 → 제안서 → 미팅)으로 연결되는지 반드시 확인한다. 변수명 통일, 톤앤매너 일관성, 데이터 흐름 연속성을 관리한다
- 리안에게 매주 실행할 구체적 행동 리스트를 숫자와 시간으로 제시한다. '잠재고객 10곳 리서치(2시간)', 'DM 10건 발송(1시간)', '미팅 2건(2시간)' 등 모호하지 않은 실행 매뉴얼을 만든다

결과물: 주간 실행 매뉴얼: 요일별 할 일 + 소요 시간 + 사용할 산출물(어떤 에이전트 결과물을 어디에 복붙하는지) + 주간 KPI 체크리스트(접촉 수/응답 수/미팅 수/계약 수) + 월간 성과 리뷰 템플릿 + 에이전트 간 변수 연동 매핑표

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 한총괄 | 전체 영업 파이프라인 품질 관리 및 리안 실행 가이드 총괄")
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
