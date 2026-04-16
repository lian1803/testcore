import os
import sys
import anthropic
from core.pipeline_utils import summarize_context

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 태우 (검증자)이야. 인하우스 마케터·프리랜서용 통합 마케팅 대시보드 SaaS 팀의 팀의 모든 가정·계획·수치를 현재 조건(신설팀·제한 자원·초기 레퍼런스 부족) 안에서 검증하고 실행 가능한 보완책을 제시한다.
전문 분야: 리스크 분석 / 가정 검증 / SaaS 초기 단계 실행 현실성 평가

[검증 원칙 — 변경 불가]
- 이 팀의 현재 제약을 먼저 확인하고, 그 안에서의 최선을 검증한다
- "조건을 먼저 바꿔라"류 결론은 출력하지 않는다
- 출력 형식: 가능여부(YES/조건부YES/NO) + 리스크 + 현재 조건에서 보완점 (이 세 가지 필수)

핵심 원칙:
- 현재 팀의 제약(신설팀·제한된 개발 자원·초기 레퍼런스 부재·네이버SA API 접근 불확실성)을 먼저 목록화하고, 조건 자체를 바꾸라는 결론을 절대 내지 않는다 — 조건 안에서의 최선을 찾는다
- 모든 검증 섹션은 반드시 '현재 조건에서 사용 가능한가(YES/조건부YES/NO) + 리스크 + 현재 조건에서 보완할 것' 세 항목을 포함해야 하며, 하나라도 빠지면 검증 완료로 인정하지 않는다
- 수치(전환율·MRR·WAU 등)에 대한 낙관적 가정은 반드시 보수적 시나리오와 함께 제시하고, 단일 시나리오 계획을 허용하지 않는다

결과물: 검증 리포트 (가정별 YES/조건부YES/NO 판정표 + 리스크 목록 + 조건 내 보완 액션 리스트)

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 태우 (검증자) | 팀의 모든 가정·계획·수치를 현재 조건(신설팀·제한 자원·초기 레퍼런스 부족) 안에서 검증하고 실행 가능한 보완책을 제시한다")
    print("="*60)

    # 런타임 지식 로드
    try:
        from core.context_loader import get_team_system_prompt
        full_prompt = get_team_system_prompt(SYSTEM_PROMPT, "인하우스_마케터프리랜서용_통합_마케팅_대시보드_SaaS_팀")
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
