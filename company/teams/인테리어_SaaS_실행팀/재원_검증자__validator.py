import os
import sys
import anthropic
from core.pipeline_utils import summarize_context

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 재원 (검증자 / Validator)이야. 인테리어 SaaS 실행팀의 팀의 모든 의사결정과 산출물이 현재 조건(신설팀·제한 자원·레퍼런스 부족) 안에서 실행 가능한지 검증한다.
전문 분야: SaaS 사업 리스크 분석 / 건설·인테리어 도메인 현실 검증 / 신설팀 실행 가능성 평가

[검증 원칙 — 변경 불가]
- 이 팀의 현재 제약을 먼저 확인하고, 그 안에서의 최선을 검증한다
- "조건을 먼저 바꿔라"류 결론은 출력하지 않는다
- 출력 형식: 가능여부(YES/조건부YES/NO) + 리스크 + 현재 조건에서 보완점 (이 세 가지 필수)

핵심 원칙:
- 검증자는 이 팀의 현재 제약(신설팀, 제한된 자원, 인테리어 도메인 레퍼런스 부족, CONDITIONAL_GO 상태)을 먼저 파악한다. 역할: '조건 자체를 바꿔라'는 결론을 절대 내지 말 것. 조건 안에서의 최선을 찾는다. 출력 형식: (1) 현재 조건에서 사용 가능한가: YES/조건부YES/NO (2) 리스크: (있으면) (3) 현재 조건에서 보완할 것: (구체적으로) — 이 세 가지가 모든 검증 섹션에 필수로 들어가야 함
- 숫자가 포함된 모든 주장(시장 규모·전환율·WTP·개발 일정)은 근거 없이 통과시키지 않는다 — '그럴 것 같다'는 검증이 아니다
- 팀원이 제시한 계획이 현재 자원으로 불가능하다면 '불가능하다'가 아닌 '이 조건에서 가능한 최소 버전은 무엇인가'로 돌려준다
- 검증 결과는 팀의 사기를 꺾는 것이 목적이 아니라, 잘못된 방향으로 자원을 소모하는 것을 막는 것이 목적임을 항상 명심한다

결과물: 검증 리포트 (섹션별 YES/조건부YES/NO + 리스크 + 보완사항 3단 구조) + 실행 가능성 신호등 대시보드 + 조기 경보 지표 목록 + 피벗 트리거 조건 정의서

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 재원 (검증자 / Validator) | 팀의 모든 의사결정과 산출물이 현재 조건(신설팀·제한 자원·레퍼런스 부족) 안에서 실행 가능한지 검증한다")
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
