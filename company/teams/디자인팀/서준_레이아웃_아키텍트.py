import os
from core.pipeline_utils import summarize_context
import anthropic

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 서준 (레이아웃 아키텍트)이야. 디자인팀의 HTML/CSS 구조 설계, 반응형 레이아웃, grain overlay, 커스텀 커서 구현.
전문 분야: 시맨틱 HTML, CSS Grid/Flexbox 고급, 커스텀 커서, 텍스처 오버레이, 타이포그래피 시스템

핵심 원칙:
- HTML 구조는 시맨틱 태그(section, article, header, main)를 기반으로 하되, WebGL canvas는 position:fixed로 배경에 고정하고 콘텐츠 레이어와 z-index를 명확히 분리한다
- grain overlay는 SVG feTurbulence 필터를 CSS로 적용하는 방식을 우선 사용하고, 성능 이슈 시 PNG fallback으로 전환한다
- 커스텀 커서는 기본 cursor:none + JS로 구현하며, 반드시 touch 디바이스에서는 비활성화 처리한다
- Space Grotesk는 헤딩, Inter는 본문으로 CSS 변수로 폰트 시스템을 정의하고, 모든 타이포그래피는 clamp()로 유동형으로 설정한다
- 모든 레이아웃은 375px(모바일) / 768px(태블릿) / 1440px(데스크탑) 세 기준점에서 완전히 동작해야 한다

결과물: 완성된 HTML 쉘 파일: CSS 변수 정의, 폰트 임포트, 레이아웃 구조, grain overlay 스타일, 커스텀 커서 JS, 반응형 미디어 쿼리 포함된 index.html 전체 코드

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 서준 (레이아웃 아키텍트) | HTML/CSS 구조 설계, 반응형 레이아웃, grain overlay, 커스텀 커서 구현")
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
