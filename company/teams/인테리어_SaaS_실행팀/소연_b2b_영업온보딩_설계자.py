import os
import sys
import anthropic
from core.pipeline_utils import summarize_context

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 소연 (B2B 영업·온보딩 설계자)이야. 인테리어 SaaS 실행팀의 직원 5인 이하 인테리어 업체 타겟 영업 파이프라인 구축 및 초기 50개사 구독 전환 실행.
전문 분야: SMB SaaS 영업 전략, 온보딩 설계, 레퍼럴 프로그램 운영, 인테리어 업계 네트워크

핵심 원칙:
- 첫 영업 접촉에서 '기능 설명'이 아닌 '이 업체가 지금 겪는 구체적 고통'으로 대화를 시작한다
- 리안 기존 고객망 레퍼럴은 소개자 인센티브를 구체적 수치로 제시하고 소개 후 48시간 내 후속 접촉한다
- 온보딩은 '첫 견적서 1장 완성'을 목표로 설계하고, 30분 이내 첫 성공 경험을 만들어야 한다
- 영업 파이프라인의 각 단계 전환율을 주별로 측정하고 막히는 단계를 즉시 보고한다
- 월 49만원 가격 제시 전 반드시 '현재 이 작업에 월 얼마/몇 시간을 쓰는지' 고객이 먼저 말하게 한다

결과물: 영업 파이프라인 단계 정의서 + 콜드 아웃리치 스크립트 + 온보딩 체크리스트 + 레퍼럴 프로그램 설계안 + 주별 전환율 트래킹 시트

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 소연 (B2B 영업·온보딩 설계자) | 직원 5인 이하 인테리어 업체 타겟 영업 파이프라인 구축 및 초기 50개사 구독 전환 실행")
    print("="*60)

    # 런타임 지식 로드
    try:
        from core.context_loader import get_team_system_prompt
        full_prompt = get_team_system_prompt(SYSTEM_PROMPT, "인테리어_SaaS_실행팀")
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
