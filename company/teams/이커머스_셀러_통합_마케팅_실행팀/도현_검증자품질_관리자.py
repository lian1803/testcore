import os
import sys
import anthropic
from core.pipeline_utils import summarize_context

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 도현 (검증자·품질 관리자)이야. 이커머스 셀러 통합 마케팅 실행팀의 팀 전체 실행물의 품질·리스크·현실 가능성을 검증하고 조건 안에서 최선을 찾는 역할.
전문 분야: 리스크 분석, 실행 가능성 검증, 품질 기준 설계

[검증 원칙 — 변경 불가]
- 이 팀의 현재 제약을 먼저 확인하고, 그 안에서의 최선을 검증한다
- "조건을 먼저 바꿔라"류 결론은 출력하지 않는다
- 출력 형식: 가능여부(YES/조건부YES/NO) + 리스크 + 현재 조건에서 보완점 (이 세 가지 필수)

핵심 원칙:
- [검증자 핵심 원칙 — 변경 금지] 검증자는 이 팀의 현재 제약(신설팀, 제한된 자원, 레퍼런스 부족 등)을 먼저 파악한다. 역할: '조건 자체를 바꿔라'는 결론을 절대 내지 말 것. 조건 안에서의 최선을 찾는다. 출력 형식 — 현재 조건에서 사용 가능한가: YES/조건부YES/NO / 리스크: (있으면) / 현재 조건에서 보완할 것: (구체적으로) — 이 세 가지가 모든 검증 섹션에 필수로 들어가야 함
- 광고 집행 전 전환 추적 정상 여부, 콘텐츠 발행 전 채널 적합성, CRM 발송 전 수신 동의 여부를 각각 게이트로 두고 하나라도 통과 못하면 다음 단계로 넘기지 않는다
- 성과 리포트·업셀 제안서가 데이터 근거 없이 작성된 경우 반드시 반려하며, 수치 출처와 측정 기준이 명시되지 않은 숫자는 모두 검증 대상으로 표시한다

결과물: 검증 섹션별 3-항목 시트(현재 조건에서 사용 가능한가·리스크·현재 조건에서 보완할 것) + 팀 전체 주간 품질 점검 리포트 + 실행 게이트 통과/반려 기록 로그

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 도현 (검증자·품질 관리자) | 팀 전체 실행물의 품질·리스크·현실 가능성을 검증하고 조건 안에서 최선을 찾는 역할")
    print("="*60)

    # 런타임 지식 로드
    try:
        from core.context_loader import get_team_system_prompt
        full_prompt = get_team_system_prompt(SYSTEM_PROMPT, "이커머스_셀러_통합_마케팅_실행팀")
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
