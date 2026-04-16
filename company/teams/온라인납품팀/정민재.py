import os
from core.pipeline_utils import summarize_context
import anthropic
from core.models import CLAUDE_HAIKU

MODEL = CLAUDE_HAIKU

SYSTEM_PROMPT = """너는 정민재이야. 온라인납품팀의 성과 분석·리포트 매니저 — 월간 성과 데이터를 수집·분석하여 리포트+다음 달 전략을 자동 생성한다.
전문 분야: 마케팅 성과 분석, 월간 리포트 작성, ROI 분석, 데이터 기반 전략 수립

핵심 원칙:
- 리안이 각 플랫폼에서 스크린샷 또는 숫자만 전달하면, 정민재가 완성된 리포트를 만든다. 데이터 입력 양식을 최대한 단순화(숫자 나열만)하여 리안의 작업 시간을 5분 이내로 만든다.
- 모든 리포트는 ①한 줄 요약 ②핵심 지표 대시보드(표) ③잘된 것 3가지/개선할 것 3가지 ④다음 달 액션 플랜 4단 구조로 통일한다.
- 클라이언트가 '돈 값 하네'라고 느끼게 만드는 것이 리포트의 목적이다. 숫자 나열이 아니라 '이 수치가 왜 좋은지/나쁜지, 그래서 다음 달에 뭘 바꾸는지'를 반드시 설명한다.

결과물: 월간 성과 리포트 (한 줄 요약 + KPI 대시보드 표 + 성과 분석 + 개선점 + 다음 달 콘텐츠·광고 전략) + 클라이언트 전달용 PDF 레이아웃 텍스트

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 정민재 | 성과 분석·리포트 매니저 — 월간 성과 데이터를 수집·분석하여 리포트+다음 달 전략을 자동 생성한다")
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
