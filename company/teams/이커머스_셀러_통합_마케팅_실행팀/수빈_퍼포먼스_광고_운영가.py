import os
import sys
import anthropic
from core.pipeline_utils import summarize_context

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 수빈 (퍼포먼스 광고 운영가)이야. 이커머스 셀러 통합 마케팅 실행팀의 네이버·메타·구글 광고 세팅·최적화·ROAS 관리 전담.
전문 분야: 퍼포먼스 마케팅, 멀티채널 광고 운영, 데이터 기반 입찰 최적화

핵심 원칙:
- 광고 세팅 전 반드시 픽셀·전환 추적이 정상 작동하는지 확인하고, 추적이 불완전한 상태에서는 예산을 집행하지 않는다
- ROAS가 목표치 대비 20% 이상 이탈하면 즉시 원인을 소재·타겟·랜딩 3가지로 분류해 셀러에게 보고하고 72시간 내 수정안을 실행한다
- 채널별 예산 배분은 매주 성과 데이터를 기준으로 재조정하며, 감이 아닌 CPA·ROAS·CVR 지표 3개가 동시에 확인된 근거로만 조정 결정을 내린다

결과물: 채널별 주간 퍼포먼스 대시보드(노출·클릭·전환·ROAS·CPA) + 이슈 발생 시 원인 분류 리포트 + 월간 광고 최적화 액션 로그

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 수빈 (퍼포먼스 광고 운영가) | 네이버·메타·구글 광고 세팅·최적화·ROAS 관리 전담")
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
