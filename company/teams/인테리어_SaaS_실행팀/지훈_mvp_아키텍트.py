import os
import sys
import anthropic
from core.pipeline_utils import summarize_context

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 지훈 (MVP 아키텍트)이야. 인테리어 SaaS 실행팀의 6개 기능의 개발 우선순위와 단계별 로드맵을 설계하고 기술 스택을 확정한다.
전문 분야: SaaS MVP 설계 / 기능 우선순위 프레임워크 / 건설·인테리어 도메인 기술 요구사항 분석

핵심 원칙:
- 기능 추가보다 핵심 파이프라인(현장입력→견적산출) 완성도를 먼저 잡는다 — 동작하지 않는 화려한 기능은 없는 것과 같다
- 각 기능은 '베타 유저가 오늘 실제로 쓸 수 있는가'를 기준으로 완료 여부를 판단한다
- 기술 선택은 팀 역량과 6개월 유지보수 가능성을 기준으로 한다 — 트렌디한 스택보다 완성 가능한 스택을 선택한다
- 로드맵은 2주 단위 스프린트로 쪼개고, 각 스프린트 종료 시 데모 가능한 산출물이 반드시 있어야 한다

결과물: 기능별 우선순위 매트릭스(RICE 스코어 포함) + 3단계 로드맵(M1~M6) + 기술 스택 확정서 + 스프린트 계획표

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 지훈 (MVP 아키텍트) | 6개 기능의 개발 우선순위와 단계별 로드맵을 설계하고 기술 스택을 확정한다")
    print("="*60)

    # 런타임 지식 로드
    try:
        from core.context_loader import get_team_system_prompt
        full_prompt = get_team_system_prompt(SYSTEM_PROMPT, "인테리어_SaaS_실행팀")
    except Exception:
        full_prompt = SYSTEM_PROMPT

    user_msg = f"""업무: {context['task']}\n\n이전 결과:\n{summarize_context(context)}"""

    full_response = ""
    with client.messages.stream(
        model=MODEL,
        max_tokens=3000,
        messages=[{"role": "user", "content": user_msg}],
        system=full_prompt,
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
            full_response += text

    print()
    return full_response
