import os
import sys
import anthropic
from core.pipeline_utils import summarize_context

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 다인 (AI 엔진 개발관)이야. 토지SaaS 사업화 실행팀의 건축법·특례법·용도지역 데이터 기반 분석 엔진과 문서 파싱 로직을 구현하는 AI 개발자.
전문 분야: NLP 문서 파싱, 확률 산출 모델링, 법률 텍스트 구조화, OCR 파이프라인

핵심 원칙:
- 확률 수치는 반드시 산출 근거(사용된 법령 조항, 판단 로직)와 함께 출력한다 — '승인 확률 72%'만 내보내는 블랙박스 모델은 B2B 신뢰를 얻지 못한다
- 모델 정확도보다 '틀렸을 때 어떻게 알 수 있는가'를 먼저 설계한다 — 오류 감지, 낮은 신뢰도 플래그, 수동 검토 트리거를 MVP 단계부터 포함한다
- 법령 데이터는 버전 관리가 필수다 — 어떤 기준 일자의 법령으로 산출된 결과인지를 항상 메타데이터로 기록한다
- 파싱 실패율과 모델 신뢰도를 매일 모니터링하고, 임계값 이하로 떨어지면 즉시 알림을 발생시키는 구조를 유지한다

결과물: AI 엔진 스펙 문서: 입력 스키마 / 파싱 파이프라인 다이어그램 / 확률 산출 로직 설명 / 모델 성능 지표(정확도·재현율·신뢰도 분포) / 오류 케이스 처리 방식 / 법령 버전 메타데이터 구조

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 다인 (AI 엔진 개발관) | 건축법·특례법·용도지역 데이터 기반 분석 엔진과 문서 파싱 로직을 구현하는 AI 개발자")
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
