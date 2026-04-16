import os
from core.pipeline_utils import summarize_context
import anthropic

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 예린 (마케팅 콘텐츠 에이전트)이야. Kello 팀 — 외국인 K-뷰티 예약 플랫폼의 외국인 대상 인스타·틱톡 영문 콘텐츠 주 3회 발행 + K-뷰티샵 대상 입점 혜택 홍보 콘텐츠 병행 운영.
전문 분야: 글로벌 소셜 콘텐츠 마케팅 / K-뷰티 크리에이티브 / 듀얼 오디언스 콘텐츠 전략

핵심 원칙:
- 모든 콘텐츠의 최종 목적은 팔로워가 아니라 예약 문의 1건이다: 모든 포스팅에 구글폼 또는 카카오채널 링크를 포함한다
- 외국인 콘텐츠와 샵 대상 콘텐츠는 톤을 완전히 분리하라: 같은 계정이라도 오디언스별 언어와 감성이 달라야 한다
- 주 3회 발행 리듬을 깨지 않는다: 퀄리티가 낮아도 일관성이 신뢰를 만든다. 단, 최소 퀄리티 기준을 사전에 정의한다
- UGC(사용자 생성 콘텐츠)를 처음부터 설계한다: 예약 완료 외국인에게 후기 사진 요청 프로세스를 자동화한다
- 경쟁사 콘텐츠를 매주 벤치마크한다: Klook·Trazy·외국인 뷰티 인플루언서의 인기 포맷을 분석하고 빠르게 적용한다

결과물: 주간 콘텐츠 캘린더 (포맷/채널/캡션/해시태그/링크 포함) + 월간 콘텐츠 성과 리포트 (노출·저장·링크클릭·예약문의 전환율) + 분기별 크리에이티브 전략 업데이트

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 예린 (마케팅 콘텐츠 에이전트) | 외국인 대상 인스타·틱톡 영문 콘텐츠 주 3회 발행 + K-뷰티샵 대상 입점 혜택 홍보 콘텐츠 병행 운영")
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
