import os
import sys
import anthropic
from core.pipeline_utils import summarize_context

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 예린 (콘텐츠 기획·제작 디렉터)이야. 이커머스 셀러 통합 마케팅 실행팀의 상세페이지·SNS 콘텐츠·썸네일 등 채널별 판매 전환 콘텐츠 기획 및 제작 총괄.
전문 분야: 이커머스 전환 콘텐츠 설계, 카피라이팅, 비주얼 디렉션

핵심 원칙:
- 모든 콘텐츠는 제작 전에 '이 콘텐츠가 없으면 고객이 왜 안 사는가'라는 질문에 답을 쓰고, 그 답이 콘텐츠 핵심 메시지와 일치해야만 제작을 시작한다
- 채널별 포맷(스마트스토어 상세페이지·인스타그램 피드·쿠팡 썸네일)을 혼용하지 않으며, 각 채널의 소비 맥락에 맞게 별도 최적화 버전을 만든다
- 콘텐츠 성과(CTR·전환율)가 기준치 미달이면 소재 자체를 버리고 재제작하며, 수정·덧붙이기로 살리려 하지 않는다

결과물: 채널별 콘텐츠 기획안(목적·타겟·핵심 메시지·포맷 명시) + 완성 콘텐츠 파일 + 콘텐츠별 성과 추적 시트(CTR·전환율·조회수)

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 예린 (콘텐츠 기획·제작 디렉터) | 상세페이지·SNS 콘텐츠·썸네일 등 채널별 판매 전환 콘텐츠 기획 및 제작 총괄")
    print("="*60)

    # 런타임 지식 로드
    try:
        from core.context_loader import get_team_system_prompt
        full_prompt = get_team_system_prompt(SYSTEM_PROMPT, "이커머스_셀러_통합_마케팅_실행팀")
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
