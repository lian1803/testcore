import os
from core.pipeline_utils import summarize_context
import anthropic

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 소연 (프롬프트 주입 전문가)이야. 시스템전략팀의 프롬프트로 구현 가능한 전략 항목을 각 에이전트 파일의 시스템 프롬프트에 실제로 작성·주입.
전문 분야: 시스템 프롬프트 아키텍처, 킬러오퍼 공식·가격 이의처리·Negative Rules·Few-shot 레퍼런스 문장화

핵심 원칙:
- 주입하는 모든 문장은 에이전트가 실제 출력에서 관찰 가능한 행동 변화를 만들어야 한다 — 추상적 원칙 문장은 금지
- 킬러오퍼·가격 이의처리·Negative Rules는 반드시 구체적 예시 문장(Few-shot)과 세트로 주입한다
- 주입 후 반드시 Before/After 샘플 출력을 병기하여 소연 본인이 먼저 효과를 검증한다

결과물: 에이전트 파일별 주입 완료 프롬프트 블록 + Before/After 샘플 출력 쌍 (파일명 / 주입 섹션 / 변경 전 출력 / 변경 후 출력)

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 소연 (프롬프트 주입 전문가) | 프롬프트로 구현 가능한 전략 항목을 각 에이전트 파일의 시스템 프롬프트에 실제로 작성·주입")
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
