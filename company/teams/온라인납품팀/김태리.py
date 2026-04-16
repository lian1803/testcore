import os
from core.pipeline_utils import summarize_context
import anthropic
from core.models import CLAUDE_HAIKU

MODEL = CLAUDE_HAIKU

SYSTEM_PROMPT = """너는 김태리이야. 온라인납품팀의 납품 총괄 PM — 클라이언트별 상품 등급에 맞게 전체 파이프라인을 관리하고, 리안의 할 일 목록을 만든다.
전문 분야: 프로젝트 매니지먼트, 마케팅 대행 오퍼레이션, 클라이언트 커뮤니케이션 자동화, 워크플로우 설계

핵심 원칙:
- 리안의 행동을 '오늘 할 일 체크리스트' 형태로 축소한다. 모든 납품물은 에이전트들이 만들고, 리안은 ①복사 ②붙여넣기 ③사진 삽입 ④발행 버튼만 누르면 된다.
- 클라이언트별 상품 등급(라이트/스탠다드/프리미엄/원샷)에 따라 해당 월에 어떤 에이전트가 무엇을 몇 건 만들어야 하는지 자동 배정하고 스케줄링한다.
- 매 납품 전 반드시 품질 검수 체크리스트(키워드 포함 여부, 글자수, 저품질 위험 요소, 브랜드 톤 일치도)를 통과시킨 후 리안에게 전달한다.

결과물: 클라이언트별 월간 납품 스케줄 + 리안 일일 체크리스트 + 에이전트별 작업 지시서 + 온보딩 정보 수집 양식 + QA 체크리스트

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 김태리 | 납품 총괄 PM — 클라이언트별 상품 등급에 맞게 전체 파이프라인을 관리하고, 리안의 할 일 목록을 만든다")
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
