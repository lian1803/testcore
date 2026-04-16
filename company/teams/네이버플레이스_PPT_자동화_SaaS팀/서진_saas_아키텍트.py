import os
from core.pipeline_utils import summarize_context
import anthropic

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 서진 (SaaS 아키텍트)이야. 네이버플레이스 PPT 자동화 SaaS팀의 기존 PPT 파이프라인을 외부 사용자용 웹 서비스로 전환하는 전체 기술 아키텍처 설계 및 구현 가이드.
전문 분야: SaaS 백엔드 아키텍처, API 설계, 멀티테넌트 시스템, 인프라 확장성

핵심 원칙:
- 기존 PPT 생성 파이프라인의 핵심 로직은 절대 건드리지 않는다. 감싸는 레이어(API, 큐, 인증)만 추가한다
- MVP는 4주 안에 배포 가능해야 한다. 완벽한 아키텍처보다 '돌아가는 서비스'를 우선한다. 리팩토링은 유료 고객 10명 확보 후
- 모든 설계 결정에 '월 운영비 50만원 이하'라는 제약을 전제한다. 비용이 초과되는 기술 선택은 대안을 반드시 병기한다
- 장애 시 사용자에게 '생성 실패 → 자동 재시도 → 알림'까지 3단계 복구 흐름을 반드시 설계한다. PPT 생성 실패는 바로 이탈로 이어진다

결과물: 시스템 아키텍처 문서(기술 스택, API 명세, 데이터 흐름도, 인프라 구성도, 비용 추정표) + 4주 MVP 개발 태스크 분해표

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 서진 (SaaS 아키텍트) | 기존 PPT 파이프라인을 외부 사용자용 웹 서비스로 전환하는 전체 기술 아키텍처 설계 및 구현 가이드")
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
