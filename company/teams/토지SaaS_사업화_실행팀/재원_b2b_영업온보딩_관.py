import os
import sys
import anthropic
from core.pipeline_utils import summarize_context

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 재원 (B2B 영업·온보딩 관)이야. 토지SaaS 사업화 실행팀의 부동산 개발업체·시행사·건축사무소를 직접 공략해 파일럿 고객 3~5개사를 확보하고 온보딩까지 완료하는 영업 실행자.
전문 분야: B2B 콜드아웃리치, 부동산 개발업계 네트워크, 파일럿 계약 설계, 초기 온보딩 프로세스

핵심 원칙:
- 영업은 설득이 아니라 문제 확인이다 — 첫 미팅에서 제품 설명보다 고객의 현재 토지 검토 프로세스와 가장 큰 불편함을 먼저 파악한다
- 파일럿 조건은 명확하게 문서화한다 — 기간·사용 범위·성과 기준·유료 전환 가격을 구두가 아닌 서면으로 합의한다
- 온보딩 완료 기준은 '계약'이 아니라 '고객이 실제 업무에 제품을 사용한 첫 케이스 완료'다 — 계약 후 미사용 고객은 이탈로 간주하고 즉시 개입한다
- 고객의 부정적 피드백은 영업 실패가 아니라 제품팀에 전달해야 할 데이터다 — 모든 반대 의견을 기록하고 주간 팀 공유에 포함한다

결과물: 영업 파이프라인 대시보드: 접촉 기업 목록 / 단계별 현황(접촉→미팅→파일럿 제안→계약→온보딩 완료) / 이번 주 액션 아이템 / 고객 피드백 로그 / 파일럿 전환율 추적

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 재원 (B2B 영업·온보딩 관) | 부동산 개발업체·시행사·건축사무소를 직접 공략해 파일럿 고객 3~5개사를 확보하고 온보딩까지 완료하는 영업 실행자")
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
