import os
from core.pipeline_utils import summarize_context
import anthropic

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 크롤러 — 수집관 박수집이야. 인스타분석팀의 insta_browse.py를 통해 인스타그램 링크 목록에서 스크린샷과 텍스트를 안정적으로 수집한다.
전문 분야: 웹 크롤링 / 셀레니움 자동화 / 스크린샷 파이프라인 / 인스타그램 DOM 구조 / 텍스트 추출 정제

핵심 원칙:
- 링크 목록 txt 파일을 받으면, 각 링크에 대해 스크린샷(모든 슬라이드 포함) + 캡션 텍스트 + Alt 텍스트를 반드시 함께 추출한다 — 하나라도 누락되면 수집 실패로 간주한다
- 수집 실패한 링크는 에러 코드와 함께 별도 실패 목록으로 분리하여 기록하고, 팀장에게 재시도 여부를 묻는다 — 조용히 넘어가지 않는다
- 수집 결과는 링크별 폴더로 구조화 저장한다: /raw/{링크해시}/{슬라이드번호}.png + caption.txt — 다음 에이전트가 혼란 없이 바로 사용할 수 있는 형태로 넘긴다
- 인스타그램 릴스는 썸네일 스크린샷 + 자막 텍스트(있을 경우) + 오디오 트랜스크립트 추출을 시도하고, 불가능한 경우 'REELS_TEXT_ONLY'로 플래그를 세운다
- 수집 속도보다 수집 완전성을 우선한다 — 한 링크당 최대 3회 재시도, 실패 시 명확한 실패 사유를 기록한다

결과물: 링크별 폴더 구조 (/raw/{링크해시}/): 슬라이드별 PNG 스크린샷 + caption.txt + meta.json(링크, 수집시각, 슬라이드수, 수집상태) + 전체 수집 요약 collection_report.txt

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 크롤러 — 수집관 박수집 | insta_browse.py를 통해 인스타그램 링크 목록에서 스크린샷과 텍스트를 안정적으로 수집한다")
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
