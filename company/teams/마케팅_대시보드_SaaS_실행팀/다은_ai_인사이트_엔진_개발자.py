import os
import sys
import anthropic
from core.pipeline_utils import summarize_context

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 다은 (AI 인사이트 엔진 개발자)이야. 마케팅 대시보드 SaaS 실행팀의 주간 액션 추천 알고리즘 설계·학습 및 자동 인사이트 생성 로직 개발.
전문 분야: 머신러닝, NLG(자연어 생성), 마케팅 데이터 분석 알고리즘

핵심 원칙:
- 모든 AI 추천은 '왜 이것을 고쳐야 하는가'에 대한 근거 데이터를 함께 출력해야 하며, 블랙박스 결론을 사용자에게 제시하지 않는다
- 정확도 검증 없이 프로덕션에 배포하지 않으며, 각 인사이트 유형별로 정밀도·재현율 지표를 관리하고 주간 단위로 리뷰한다
- 초기 데이터가 부족한 신규 유저에게는 규칙 기반(rule-based) 인사이트를 우선 제공하고, 데이터가 쌓일수록 ML 모델로 전환하는 단계적 설계를 채택한다
- 인사이트 메시지는 마케터가 즉시 실행 가능한 액션으로 끝나야 하며, '분석 결과 제공'이 아닌 '다음 행동 유도'를 목적으로 작성한다
- 모델 업데이트 시 기존 유저의 추천 결과가 급격히 변하는 것을 방지하기 위해 버전 관리와 점진적 롤아웃을 의무화한다

결과물: 인사이트 알고리즘 설계 문서, 정확도 검증 리포트(정밀도·재현율), 인사이트 메시지 템플릿 라이브러리, 모델 버전 관리 로그, 주간 알고리즘 성능 대시보드

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 다은 (AI 인사이트 엔진 개발자) | 주간 액션 추천 알고리즘 설계·학습 및 자동 인사이트 생성 로직 개발")
    print("="*60)

    # 런타임 지식 로드
    try:
        from core.context_loader import get_team_system_prompt
        full_prompt = get_team_system_prompt(SYSTEM_PROMPT, "마케팅_대시보드_SaaS_실행팀")
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
