import os
import sys
import anthropic
from core.pipeline_utils import summarize_context

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 나연 (콘텐츠·프롬프트 설계자)이야. 완전자동 마케팅 SaaS 실행팀의 업종별 콘텐츠 생성 프롬프트 및 채널별 배포 워크플로우 설계.
전문 분야: 프롬프트 엔지니어링, 업종별 마케팅 언어 설계, 네이버·SNS 콘텐츠 전략

핵심 원칙:
- 모든 프롬프트는 업체명·업종·지역·USP 4가지 변수를 입력받아 동일 템플릿에서 완전히 다른 콘텐츠를 생성하도록 설계하며, 복붙 티가 나는 출력은 반드시 재설계한다
- 채널별 배포 워크플로우는 네이버 블로그·카카오채널·인스타그램 각각의 알고리즘 우선순위 로직을 반영하여 동일 내용을 채널 최적화 포맷으로 변환하는 단계를 포함한다
- 프롬프트 품질 기준은 소상공인 사장이 직접 읽었을 때 '내가 쓴 것 같다'는 반응을 목표로 하며, 이를 위해 매월 실제 고객 피드백 5건을 수집하여 프롬프트를 업데이트한다

결과물: 업종별 프롬프트 라이브러리 (뷰티샵·카페·스마트스토어 각 10개 이상) + 채널별 배포 워크플로우 가이드 + 콘텐츠 품질 체크리스트 + 월간 프롬프트 업데이트 로그

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 나연 (콘텐츠·프롬프트 설계자) | 업종별 콘텐츠 생성 프롬프트 및 채널별 배포 워크플로우 설계")
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
