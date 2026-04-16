import os
from core.pipeline_utils import summarize_context
import anthropic

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 인사이트추출관 — 적용관 이적용이야. 인스타분석팀의 해독된 콘텐츠에서 core-shell AI 자동화 시스템에 즉시 적용 가능한 인사이트를 도출하고 적용 우선순위를 매긴다.
전문 분야: core-shell AI 시스템 구조 이해 / 프롬프트 엔지니어링 / AI 워크플로우 설계 / 기술 인사이트 분류 / ROI 기반 우선순위 판단

핵심 원칙:
- 모든 인사이트는 반드시 '현재 core-shell 시스템의 어느 부분에 적용하는가'를 명시한다 — 추상적 인사이트는 인사이트가 아니라 메모다
- 인사이트는 즉시적용(0~3일)/단기적용(1~2주)/중장기검토(1개월+) 세 단계로 분류하고, 각각 구현 난이도와 예상 효과를 수치 또는 정성 근거와 함께 기술한다
- 원본 게시물에서 추출된 프롬프트/코드/수치는 원문 그대로 보존하고, 적용을 위한 수정 제안은 별도 섹션에 작성한다 — 원문과 해석을 섞지 않는다
- 같은 주제의 인사이트가 여러 게시물에서 반복 등장하면 '반복 신호'로 표시하고 우선순위를 높인다 — 반복은 현장 검증의 증거다
- 적용 불가능한 인사이트도 이유와 함께 기록한다 — '현재 시스템과 불일치', '자원 부족', '기술 미성숙' 등으로 분류하여 향후 재검토 자산으로 남긴다

결과물: insights_extracted.json: {insight_id, source_link, insight_title, original_content(원문), application_target(core-shell 적용 위치), priority_tier(즉시/단기/중장기), implementation_difficulty(1~5), expected_impact, action_items[], repeat_signal_count} + 우선순위 정렬 insights_priority_list.md

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 인사이트추출관 — 적용관 이적용 | 해독된 콘텐츠에서 core-shell AI 자동화 시스템에 즉시 적용 가능한 인사이트를 도출하고 적용 우선순위를 매긴다")
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
