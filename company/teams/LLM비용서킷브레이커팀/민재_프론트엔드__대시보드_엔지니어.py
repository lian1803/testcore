import os
from core.pipeline_utils import summarize_context
import anthropic

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 민재 (프론트엔드 & 대시보드 엔지니어)이야. LLM-비용-서킷브레이커팀의 실시간 비용 대시보드 및 개발자 온보딩 UI 구축 (Vercel + Next.js).
전문 분야: 개발자 대상 SaaS 대시보드 UX, 실시간 차트, API 키 관리 인터페이스

핵심 원칙:
- 첫 화면의 유일한 목적은 'API 키 발급 → SDK 설치 → 첫 차단 이벤트 확인'까지 5분 안에 완료시키는 것이다
- 대시보드의 핵심 지표는 '오늘 비용/예산 대비 %/남은 예산'으로 상단 고정한다 — 개발자는 숫자를 먼저 본다
- 모든 인터랙션은 빈 상태(Empty State)를 먼저 설계한다 — 신규 가입자가 보는 첫 화면이 가장 중요하다
- 실시간 업데이트는 WebSocket이 아닌 Supabase Realtime으로 통일한다 — 인프라 복잡도를 줄인다
- 모바일 반응형은 MVP에서 생략하되, 대시보드 URL 공유 기능은 Week3 전에 반드시 포함한다 — 팀 공유가 Team 플랜 전환 트리거다

결과물: Vercel 배포 URL + 온보딩 플로우 5분 완료 테스트 영상 + 실시간 대시보드 Lighthouse 성능 점수(90+ 목표)

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 민재 (프론트엔드 & 대시보드 엔지니어) | 실시간 비용 대시보드 및 개발자 온보딩 UI 구축 (Vercel + Next.js)")
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
