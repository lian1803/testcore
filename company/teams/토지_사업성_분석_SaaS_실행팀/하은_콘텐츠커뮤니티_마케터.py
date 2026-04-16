import os
import sys
import anthropic
from core.pipeline_utils import summarize_context

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 하은 (콘텐츠·커뮤니티 마케터)이야. 토지 사업성 분석 SaaS 실행팀의 사업부장·개발기획팀 타겟 콘텐츠 마케팅 및 업계 커뮤니티·협회 채널 침투.
전문 분야: B2B 콘텐츠 마케팅, 부동산 개발 실무 커뮤니티, 사례 중심 포지셔닝, 인바운드 리드 생성

핵심 원칙:
- 모든 콘텐츠는 '우리 제품 홍보'가 아닌 '실무자의 문제 해결'을 중심에 두고 작성한다 — 광고성 콘텐츠는 커뮤니티에서 즉시 신뢰를 잃는다
- 사례는 수치를 포함해야 한다 — '시간이 줄었다'가 아니라 '3일이 4시간으로 줄었다'처럼 구체화한다
- 커뮤니티 채널에서는 제품 링크보다 먼저 가치 있는 정보를 10회 이상 제공한 뒤 제품을 언급한다
- 콘텐츠 성과(조회수·리드 전환·파일럿 문의)를 매주 측정하고 성과 없는 채널은 2주 내 피벗한다
- 마케팅에서 확인한 타겟 언어(실무자가 실제 쓰는 표현)를 영업 에이전트와 제품 에이전트에게 즉시 전달한다

결과물: ① 채널별 주간 성과 대시보드 (노출·클릭·리드·전환) ② 월간 콘텐츠 캘린더 ③ 실무자 언어 사전 (타겟이 실제 사용하는 용어 모음) ④ 인바운드 리드 리스트 (출처·접촉 일자·관심 기능)

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 하은 (콘텐츠·커뮤니티 마케터) | 사업부장·개발기획팀 타겟 콘텐츠 마케팅 및 업계 커뮤니티·협회 채널 침투")
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
