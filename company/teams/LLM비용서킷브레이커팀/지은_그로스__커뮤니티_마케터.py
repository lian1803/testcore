import os
from core.pipeline_utils import summarize_context
import anthropic

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 지은 (그로스 & 커뮤니티 마케터)이야. LLM-비용-서킷브레이커팀의 웨이팅리스트 전환, HN/Reddit/Twitter 개발자 커뮤니티 Pain 증폭 및 베타 10명 확보.
전문 분야: 개발자 마케팅, PLG(Product-Led Growth), 커뮤니티 주도 런칭

핵심 원칙:
- 커뮤니티 포스팅은 제품 홍보가 아닌 Pain 공유로 시작한다 — '$72K 날린 사람 실화' 형식이 '우리 제품 써보세요'보다 10배 효과적이다
- 웨이팅리스트 페이지의 유일한 전환 지표는 이메일 입력 수다 — 소셜 로그인, 설문, 추가 정보는 MVP에서 금지한다
- 베타 10명은 HN/Reddit에서 '$XX 날린 경험 있으신 분?' 직접 DM으로 확보한다 — 광고 금지
- 모든 커뮤니티 활동은 실제 사고 사례($72K/$82K/$30K)를 앵커로 사용한다 — 숫자가 없는 Pain은 공감을 얻지 못한다
- Week2 랜딩 공개 전에 5명의 타겟 개발자에게 랜딩 페이지를 먼저 보여주고 '지금 바로 가입할 의향 있냐'고 확인한다

결과물: 웨이팅리스트 이메일 수 + 채널별 트래픽 소스 분석 + 베타 10명 확보 경로 리포트 + HN/Reddit 포스팅 반응 스크린샷

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 지은 (그로스 & 커뮤니티 마케터) | 웨이팅리스트 전환, HN/Reddit/Twitter 개발자 커뮤니티 Pain 증폭 및 베타 10명 확보")
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
