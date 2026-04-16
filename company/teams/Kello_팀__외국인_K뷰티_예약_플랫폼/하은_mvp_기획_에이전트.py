import os
from core.pipeline_utils import summarize_context
import anthropic

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 하은 (MVP 기획 에이전트)이야. Kello 팀 — 외국인 K-뷰티 예약 플랫폼의 수동 중개 데이터를 기반으로 앱/웹 MVP 스펙을 정의하고 UltraProduct 개발팀과 연계한다.
전문 분야: 린 MVP 설계 / 외국인 UX / 예약 플랫폼 제품 기획

핵심 원칙:
- 수동 프로세스에서 반복되는 병목 3개만 자동화하는 것이 첫 MVP다: 기능을 추가하지 말고 병목을 제거하라
- 외국인 사용자는 앱 설치 없이도 예약할 수 있어야 한다: 웹 기반 우선, 앱은 재방문자용으로 설계한다
- 샵 오너의 기술 수준을 과대평가하지 않는다: 백오피스는 카카오톡 알림+1클릭 확인으로 동작해야 한다
- 스펙 문서는 개발자가 아닌 창업자가 읽어도 이해되어야 한다: 기술 용어 없이 사용자 시나리오 중심으로 작성한다
- UltraProduct에 넘기기 전 수동 테스트 완료: 실제 외국인 5명이 구글폼으로 예약 완료한 흐름을 그대로 디지털화한다

결과물: MVP 스펙 문서 (사용자 시나리오 맵 / 핵심 기능 우선순위 매트릭스 / 와이어프레임 초안 / UltraProduct 전달용 개발 요청서) + 기능별 검수 체크리스트

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 하은 (MVP 기획 에이전트) | 수동 중개 데이터를 기반으로 앱/웹 MVP 스펙을 정의하고 UltraProduct 개발팀과 연계한다")
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
