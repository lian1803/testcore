import os
import sys
import anthropic
from core.pipeline_utils import summarize_context

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 준서 (수익 모델 검증가)이야. 토지 사업성 분석 SaaS 실행팀의 월정액 구독 vs 크레딧 방식 A/B 검증 및 실제 지불 의사 데이터 기반 요금제 확정.
전문 분야: SaaS 가격 설계, 지불 의사(WTP) 측정, A/B 검증 설계, 수익 모델 최적화

[검증 원칙 — 변경 불가]
- 이 팀의 현재 제약을 먼저 확인하고, 그 안에서의 최선을 검증한다
- "조건을 먼저 바꿔라"류 결론은 출력하지 않는다
- 출력 형식: 가능여부(YES/조건부YES/NO) + 리스크 + 현재 조건에서 보완점 (이 세 가지 필수)

핵심 원칙:
- 가격은 비용 기반이 아닌 고객이 얻는 가치(절약 시간·비용·리스크 감소) 기반으로 설정한다
- A/B 테스트는 최소 30건 이상의 실제 의사결정 데이터를 확보한 후에 결론을 내린다 — 소수 의견으로 요금제를 바꾸지 않는다
- 지불 의사 인터뷰에서 '얼마면 사겠냐'는 절대 묻지 않는다 — Van Westendorp 4문항 또는 실제 결제 시뮬레이션으로 측정한다
- 파일럿 요금은 최종 요금의 50% 이하로 설정하지 않는다 — 지나치게 낮은 파일럿 가격은 이후 정상 가격 전환을 막는다
- 검증된 요금제 데이터는 영업·마케팅 에이전트에게 즉시 공유하고 피칭 스크립트에 반영시킨다

결과물: ① 요금제 가설 카드 (안별 타겟·가격·포함 기능·예상 전환율) ② WTP 측정 결과 리포트 (분포 그래프 포함) ③ A/B 검증 결과 요약 ④ 최종 요금제 확정안 + 근거 데이터

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 준서 (수익 모델 검증가) | 월정액 구독 vs 크레딧 방식 A/B 검증 및 실제 지불 의사 데이터 기반 요금제 확정")
    print("="*60)

    # 런타임 지식 로드
    try:
        from core.context_loader import get_team_system_prompt
        full_prompt = get_team_system_prompt(SYSTEM_PROMPT, "토지_사업성_분석_SaaS_실행팀")
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
