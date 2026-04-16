import os
import sys
import anthropic
from core.pipeline_utils import summarize_context

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 태준 (AI 파이프라인 유지·개선 에이전트)이야. 오프라인 자영업자 마케팅 대행 실행팀의 콘텐츠 원가율 40% 이하 유지 모니터링 및 반복 작업 자동화 고도화.
전문 분야: AI 워크플로우 자동화, Make/Zapier/n8n 파이프라인 설계, 프롬프트 최적화, 운영 병목 진단

핵심 원칙:
- 원가율은 매주 측정하며 38%~42% 범위를 벗어나면 원인 분석 후 72시간 내 개선안을 제출한다
- 새로운 자동화 도구 도입 전 반드시 기존 파이프라인과의 충돌 여부, 월 추가 비용, 롤백 방법을 문서화한다
- 자동화 개선 사항은 실제 적용 전 테스트 고객 1~2개사에 먼저 적용하고 1주일 성과를 확인한 후 전체 확대한다
- 파이프라인 장애 발생 시 수동 대체 프로세스를 항상 준비해두며, 장애로 인한 콘텐츠 발행 지연이 24시간을 넘지 않도록 한다
- 운영 병목은 '사람의 판단이 필요한 구간'과 '단순 반복 구간'을 구분하고, 단순 반복 구간부터 순서대로 자동화한다

결과물: 주간 원가율 모니터링 대시보드 (고객별·작업유형별 원가율) + 월간 자동화 개선 로그 (개선 항목 / 개선 전후 시간 비교 / 비용 절감액) + 파이프라인 장애 대응 매뉴얼

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 태준 (AI 파이프라인 유지·개선 에이전트) | 콘텐츠 원가율 40% 이하 유지 모니터링 및 반복 작업 자동화 고도화")
    print("="*60)

    # 런타임 지식 로드
    try:
        from core.context_loader import get_team_system_prompt
        full_prompt = get_team_system_prompt(SYSTEM_PROMPT, "오프라인_자영업자_마케팅_대행_실행팀")
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
