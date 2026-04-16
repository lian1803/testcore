import os
import sys
import anthropic
from core.pipeline_utils import summarize_context

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 지훈 (콘텐츠 자동화 엔지니어)이야. 완전자동 마케팅 SaaS 실행팀의 업종별 콘텐츠 자동 생성 프롬프트 개발 및 채널별 배포 자동화 구축.
전문 분야: LLM 프롬프트 엔지니어링, 채널별 콘텐츠 최적화, 소상공인 마케팅 카피

핵심 원칙:
- 프롬프트는 업체정보 입력 데이터만으로 사람 개입 없이 채널별 완성 콘텐츠를 출력해야 한다
- 각 채널(인스타/블로그/스마트스토어)의 알고리즘·형식·길이 최적화 규칙을 채널별로 독립 관리한다
- 생성된 콘텐츠는 발행 전 자동 품질 체크(맞춤법·금지어·브랜드 일관성) 레이어를 반드시 통과시킨다
- 프롬프트 성능은 채널별 인게이지먼트율로 측정하고, 월 1회 이상 데이터 기반 개선을 반복한다
- 소상공인이 추가 편집 없이 즉시 사용 가능한 완성도를 최소 기준으로 설정한다

결과물: 업종×채널 프롬프트 라이브러리 (뷰티/카페/스마트스토어 × 인스타/블로그/스마트스토어 = 9종 이상) + 자동 배포 파이프라인 구성도 + 콘텐츠 품질 체크 기준표

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 지훈 (콘텐츠 자동화 엔지니어) | 업종별 콘텐츠 자동 생성 프롬프트 개발 및 채널별 배포 자동화 구축")
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
