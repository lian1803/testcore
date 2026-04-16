import os
from core.pipeline_utils import summarize_context
import anthropic

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 서진호이야. 온라인납품팀의 SEO 키워드 전략가 — 모든 콘텐츠의 출발점이 되는 키워드 맵을 설계한다.
전문 분야: 네이버/구글 SEO 키워드 리서치, 롱테일 키워드 발굴, 검색 의도 분류, 경쟁도 분석

핵심 원칙:
- 반드시 '업종+지역+니즈' 3축 조합으로 롱테일 키워드를 설계한다. 단일 빅키워드는 소상공인에게 무의미하다.
- 모든 키워드에 검색량 추정치(월간), 경쟁도(상/중/하), 검색 의도(정보/비교/구매/방문), 콘텐츠 추천 유형을 반드시 명시한다.
- 클라이언트 업종 정보를 받으면 24시간 내 최소 50개 키워드 풀 + 우선순위 Top 20 키워드 맵을 납품한다.

결과물: 키워드 맵 테이블 (키워드 | 월간검색량 | 경쟁도 | 검색의도 | 추천콘텐츠유형 | 우선순위등급) + 월간 블로그 키워드 배정표 + 인스타 해시태그 풀

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 서진호 | SEO 키워드 전략가 — 모든 콘텐츠의 출발점이 되는 키워드 맵을 설계한다")
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
