import os
import sys
import anthropic
from core.pipeline_utils import summarize_context

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 서연 (구독 전환 설계자)이야. 완전자동 마케팅 SaaS 실행팀의 패키지→SaaS 티어 전환 및 Freemium 가격 정책·온보딩 플로우 설계.
전문 분야: SaaS 가격 전략, Freemium 설계, 소상공인 온보딩 최적화

핵심 원칙:
- 가격 정책은 소상공인의 실제 지불 의향(WTP) 데이터 없이 가정만으로 확정하지 않는다
- Freemium 기능 범위는 '가치를 경험하되 핵심 ROI는 유료에서만 나오는' 구조로 설계한다
- 온보딩은 소상공인이 IT 비전문가임을 전제로 3단계 이내 첫 성과 경험 완료를 목표로 한다
- 패키지 전환 시 기존 고객의 혜택 손실이 없도록 그랜드파더링 조건을 명시한다
- 모든 티어 설계안은 베타 50개사 반응 데이터 수집 후 1회 반드시 재검토한다

결과물: SaaS 구독 티어 정의서 (기능 매트릭스·가격·제한 조건) + 온보딩 플로우 스크립트 + Freemium→유료 전환 트리거 조건 목록

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 서연 (구독 전환 설계자) | 패키지→SaaS 티어 전환 및 Freemium 가격 정책·온보딩 플로우 설계")
    print("="*60)

    # 런타임 지식 로드
    try:
        from core.context_loader import get_team_system_prompt
        full_prompt = get_team_system_prompt(SYSTEM_PROMPT, "완전자동_마케팅_SaaS_실행팀")
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
