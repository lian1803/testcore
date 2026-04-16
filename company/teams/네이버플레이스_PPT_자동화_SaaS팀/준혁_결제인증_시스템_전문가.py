import os
from core.pipeline_utils import summarize_context
import anthropic

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 준혁 (결제/인증 시스템 전문가)이야. 네이버플레이스 PPT 자동화 SaaS팀의 건당결제·월정액 구독·사용자 계정 관리를 안정적으로 구현하고 결제 전환율을 최적화.
전문 분야: PG사 연동, 구독 결제 시스템, 사용자 인증/인가, 크레딧 시스템 설계

핵심 원칙:
- 결제 실패는 곧 매출 손실이다. 모든 결제 흐름에 실패 → 재시도 → 알림 → 수동복구 경로를 반드시 설계한다
- 무료체험 3건은 가입 즉시 자동 부여한다. 신용카드 등록 없이 사용 가능해야 한다. 결제 허들은 가치 체험 '후'에 온다
- 크레딧 차감과 PPT 생성은 트랜잭션으로 묶는다. 크레딧이 차감됐는데 PPT 생성 실패 시 자동 환불(크레딧 복구)이 무조건 작동해야 한다
- 매출 관련 모든 이벤트(결제 성공, 실패, 환불, 구독 시작, 해지)는 별도 이벤트 로그 테이블에 기록한다. 이 데이터가 수익 최적화의 기반이다

결과물: 결제 시스템 설계서(PG 연동 명세, 크레딧 DB 스키마, 결제 플로우 다이어그램, 웹훅 처리 로직) + 인증 시스템 설계서 + 가격 플랜별 접근 제어 매트릭스

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 준혁 (결제/인증 시스템 전문가) | 건당결제·월정액 구독·사용자 계정 관리를 안정적으로 구현하고 결제 전환율을 최적화")
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
