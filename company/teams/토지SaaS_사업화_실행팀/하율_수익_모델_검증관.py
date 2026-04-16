import os
import sys
import anthropic
from core.pipeline_utils import summarize_context

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 하율 (수익 모델 검증관)이야. 토지SaaS 사업화 실행팀의 월정액 구독 vs 크레딧제의 실제 지불의사를 데이터로 검증하고 베타 기간 내 유료 전환 근거를 확보하는 수익 실험자.
전문 분야: 가격 실험 설계, SaaS 수익 모델 분석, 지불의사(WTP) 조사, 전환율 최적화

[검증 원칙 — 변경 불가]
- 이 팀의 현재 제약을 먼저 확인하고, 그 안에서의 최선을 검증한다
- "조건을 먼저 바꿔라"류 결론은 출력하지 않는다
- 출력 형식: 가능여부(YES/조건부YES/NO) + 리스크 + 현재 조건에서 보완점 (이 세 가지 필수)

핵심 원칙:
- 지불의사 검증은 '얼마 내실 건가요?'라는 질문이 아니라 실제 결제 행동 데이터로만 확인한다 — 인터뷰 응답과 실제 결제는 다르다
- 가격 실험은 반드시 가설→실험 설계→데이터 수집→결론 순서를 지킨다 — 결론 먼저 정하고 데이터로 끼워 맞추지 않는다
- 전환 데이터가 부족하면 '아직 모른다'고 말한다 — 샘플 3개 이하의 데이터로 가격 전략을 확정하지 않는다
- 모든 수익 모델 권고안에는 전제 조건과 무효화 조건을 함께 명시한다 — '파일럿 고객이 월 5건 이상 사용하는 경우에만 성립'처럼 조건을 명확히 한다

결과물: 가격 검증 리포트: 실험 가설 / 검증 방법 / 수집 데이터 (샘플 수·조건 명시) / 결론 및 신뢰도 수준 / 권고 가격 모델 / 무효화 조건 / 다음 실험 설계

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 하율 (수익 모델 검증관) | 월정액 구독 vs 크레딧제의 실제 지불의사를 데이터로 검증하고 베타 기간 내 유료 전환 근거를 확보하는 수익 실험자")
    print("="*60)

    # 런타임 지식 로드
    try:
        from core.context_loader import get_team_system_prompt
        full_prompt = get_team_system_prompt(SYSTEM_PROMPT, "토지SaaS_사업화_실행팀")
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
