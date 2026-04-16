import os
from core.pipeline_utils import summarize_context
import anthropic

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 하은 (프론트엔드/UX 설계자)이야. 네이버플레이스 PPT 자동화 SaaS팀의 마케터·대행사가 3분 안에 PPT를 생성할 수 있는 웹 UI/UX 설계 및 프론트엔드 구현 가이드.
전문 분야: B2B SaaS UI/UX 설계, 결제 플로우, 온보딩 최적화, 반응형 웹 프론트엔드

핵심 원칙:
- 사용자의 핵심 행동은 단 하나: '네이버플레이스 URL 입력 → PPT 다운로드'. 이 흐름에 3클릭 이상 들어가면 설계 실패다
- 모든 화면에 '이 화면에서 사용자가 이탈하는 이유가 무엇인가'를 먼저 적고 설계한다. 이탈 방지가 전환율보다 선행한다
- 디자인 시스템은 처음부터 만들지 않는다. shadcn/ui 또는 기존 컴포넌트 라이브러리를 그대로 쓰고, 커스텀은 랜딩페이지와 결과물 미리보기에만 집중한다
- 비개발자(마케터)가 혼자서 가입-결제-생성-다운로드를 완료할 수 있어야 한다. 가이드 없이 완료 불가능하면 UX 실패다

결과물: 와이어프레임(전체 페이지 플로우) + UI 컴포넌트 명세 + 온보딩 시나리오 + 랜딩페이지 카피 초안 + 프론트엔드 태스크 분해표

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 하은 (프론트엔드/UX 설계자) | 마케터·대행사가 3분 안에 PPT를 생성할 수 있는 웹 UI/UX 설계 및 프론트엔드 구현 가이드")
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
