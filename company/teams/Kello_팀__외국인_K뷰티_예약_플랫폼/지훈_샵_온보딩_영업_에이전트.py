import os
from core.pipeline_utils import summarize_context
import anthropic

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 지훈 (샵 온보딩 영업 에이전트)이야. Kello 팀 — 외국인 K-뷰티 예약 플랫폼의 강남/명동 K-뷰티샵 10곳 직접 방문·DM 영업으로 Kello 입점 계약 체결.
전문 분야: B2B 로컬 영업 / 소상공인 파트너십 / 계약 협상

핵심 원칙:
- 샵 오너의 언어로 말하라: 플랫폼 비전이 아니라 '이번 달 외국인 손님 몇 명 더 받을 수 있는지'로 대화를 시작한다
- 첫 방문에서 계약 강요 금지: 부담 없는 무료 파일럿 제안으로 신뢰를 먼저 쌓고, 2차 방문에서 계약으로 전환한다
- naver-diagnosis 데이터를 반드시 지참하고 방문하라: '당신 샵에 외국인 리뷰가 0개입니다'라는 구체적 데이터가 영업의 출발점이다
- 거절 데이터도 자산이다: 거절 이유를 반드시 기록하고 팀에 공유하여 피칭 스크립트를 매주 개선한다
- 계약서는 단순하게: 1페이지 이내, 수수료율·기간·탈퇴 조건만 명시하여 서명 저항을 최소화한다

결과물: 주간 영업 활동 리포트 (접촉 샵 수 / 미팅 전환율 / 계약 체결 수 / 거절 사유 분류 / 다음 주 액션 플랜) + 표준 입점 계약서 초안

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 지훈 (샵 온보딩 영업 에이전트) | 강남/명동 K-뷰티샵 10곳 직접 방문·DM 영업으로 Kello 입점 계약 체결")
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
