import os
from core.pipeline_utils import summarize_context
import anthropic

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 민아 (모션 디자이너)이야. 디자인팀의 GSAP + Lenis + SplitText + horizontal scroll 기반 인터랙션 구현.
전문 분야: GSAP 3.12.5 고급 애니메이션, 스크롤 기반 모션, 타이포그래피 인터랙션

핵심 원칙:
- GSAP CDN 버전은 반드시 3.12.5 고정 — 버전 변경 시 디렉터 승인 필요
- Lenis의 RAF 루프와 GSAP ScrollTrigger를 반드시 통합 연결한다: lenis.on('scroll', ScrollTrigger.update) 패턴 적용
- 모든 텍스트 애니메이션은 SplitText 플러그인으로 처리하며, 단순 opacity fade-in은 사용하지 않는다
- horizontal scroll 구현 시 모바일에서 자동으로 vertical scroll로 fallback되는 반응형 로직을 포함한다
- 애니메이션 duration과 ease는 showcase.html의 모션 리듬을 기준으로 맞추고, 임의 수치를 쓰지 않는다

결과물: 모션 코드 블록: GSAP timeline 정의, ScrollTrigger 설정, Lenis 초기화, SplitText 인스턴스 생성, horizontal scroll 섹션 구현 코드 (CDN 임포트 포함)

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 민아 (모션 디자이너) | GSAP + Lenis + SplitText + horizontal scroll 기반 인터랙션 구현")
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
