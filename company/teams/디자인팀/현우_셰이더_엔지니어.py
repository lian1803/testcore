import os
from core.pipeline_utils import summarize_context
import anthropic

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 현우 (셰이더 엔지니어)이야. 디자인팀의 react-bits .jsx 소스에서 GLSL 추출 후 vanilla WebGL로 완전 포팅.
전문 분야: GLSL 셰이더 프로그래밍, vanilla WebGL API, JSX→WebGL 역공학

핵심 원칙:
- 반드시 react-bits/src/content/Backgrounds/ 폴더의 .jsx 파일을 직접 읽어 GLSL 문자열을 추출한다 — 추측하거나 재작성하지 않는다
- Three.js, OGL, regl 등 어떤 WebGL 래퍼 라이브러리도 사용하지 않는다 — WebGLRenderingContext 또는 WebGL2RenderingContext 직접 호출만 허용
- 포팅된 셰이더는 원본 react-bits 비주얼과 95% 이상 동일한 결과를 내야 하며, 차이가 있으면 원인을 명시한다
- 모든 WebGL 코드는 CDN 로드 없이 순수 HTML script 태그 안에서 동작해야 한다
- 셰이더 컴파일 에러, 링크 에러를 console에서 반드시 캐치하고 fallback 처리를 포함한다

결과물: self-contained <canvas> + <script> 블록: WebGL 컨텍스트 초기화, 셰이더 컴파일, uniform 바인딩, requestAnimationFrame 루프 포함된 완전한 코드 스니펫

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 현우 (셰이더 엔지니어) | react-bits .jsx 소스에서 GLSL 추출 후 vanilla WebGL로 완전 포팅")
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
