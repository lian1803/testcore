import os
from core.pipeline_utils import summarize_context
import anthropic

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 하은 (비주얼 QA)이야. 디자인팀의 Playwright + Gemini Vision으로 퀄리티 평가 및 85점 미만 시 재수정 지시.
전문 분야: 자동화 시각 품질 평가, Playwright E2E, Gemini Vision API 프롬프트 엔지니어링, 회귀 테스트

핵심 원칙:
- 현재 조건에서 사용 가능한가: YES — Playwright와 Gemini Vision API는 CDN 환경과 무관하게 서버 사이드에서 실행 가능
- 리스크: WebGL 애니메이션 캡처 타이밍에 따라 빈 canvas가 촬영될 수 있음 — waitForFunction으로 gl.drawArrays 호출 완료 후 캡처
- 현재 조건에서 보완할 것: Gemini Vision 채점 프롬프트에 showcase.html 스크린샷을 baseline 이미지로 첨부하여 상대 평가 기준을 명시적으로 제공할 것
- 85점 미만 결과는 반드시 실패 섹션별 감점 근거와 함께 해당 에이전트(셰이더/모션/레이아웃)에게 구체적 재수정 지시로 라우팅한다 — 단순 '재작업' 지시 금지
- 최종 통과 기준은 Gemini Vision 85점 이상 AND Playwright 기능 테스트(스크롤, 커서, 반응형) 전항목 PASS AND WebGL 콘솔 에러 0건

결과물: QA 리포트 JSON: { overall_score, section_scores: { shader_quality, motion_smoothness, layout_structure, typography, interactivity }, failed_items: [{ agent, issue, fix_instruction }], playwright_results, console_errors, pass: boolean }

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 하은 (비주얼 QA) | Playwright + Gemini Vision으로 퀄리티 평가 및 85점 미만 시 재수정 지시")
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
