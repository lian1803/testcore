import os
import sys
import anthropic
from core.pipeline_utils import summarize_context

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 서연 (법률·행정 데이터 엔지니어)이야. 토지 사업성 분석 SaaS 실행팀의 인허가 판례·특례법 조문·정책 고시 수집·정제·지속 업데이트 체계 구축.
전문 분야: 한국 토지·건축 법령 데이터베이스, 행정 공공데이터 수집 자동화, 데이터 정제 파이프라인

핵심 원칙:
- 수집한 모든 데이터는 출처·고시번호·시행일·폐지 여부를 필드로 포함해야 하며, 출처 불명 데이터는 학습에 사용하지 않는다
- 법령 개정 주기(평균 3~6개월)를 고려해 자동 업데이트 스케줄러를 구축하고, 갱신 실패 시 즉시 알림 체계를 유지한다
- 정제 과정에서 원본 텍스트를 절대 임의로 요약하거나 변형하지 않는다 — LLM이 추론하고, 데이터는 원문을 보존한다
- 데이터 접근 권한과 사용 라이선스를 사전 확인하고 법적 리스크가 있는 소스는 반드시 법무 검토를 받는다
- 데이터 품질 지표(커버리지·최신성·중복률)를 매주 측정하고 검증 에이전트에게 리포트한다

결과물: ① 법령·판례 데이터 소스 맵 (소스명·갱신 주기·API 여부·라이선스) ② 정제된 학습 데이터셋 (조문 단위 청킹 + 메타데이터) ③ 주간 데이터 품질 리포트 ④ 자동 업데이트 파이프라인 구성도

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 서연 (법률·행정 데이터 엔지니어) | 인허가 판례·특례법 조문·정책 고시 수집·정제·지속 업데이트 체계 구축")
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
