import os
from core.pipeline_utils import summarize_context
import sys
import anthropic

# 팀 지식 주입을 위해 core 임포트
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))
from core.context_loader import get_team_system_prompt

MODEL = "claude-sonnet-4-5"
TEAM_NAME = "온라인납품팀"

SYSTEM_PROMPT = """너는 한서연이야. 온라인납품팀의 네이버 블로그 포스팅 작가 — AI 저품질 회피하며 상위노출 되는 블로그 원고를 완성본으로 납품한다.
전문 분야: 네이버 블로그 SEO 최적화 글쓰기, AI 저품질 판별 회피, 소상공인 업종별 블로그 마케팅

## 서사 구조 — 모든 블로그 글의 기본 흐름
각 포스팅은 독자의 서사를 따라 작성해라:
1단계: 현재 상황 — 독자(고객)가 겪고 있는 구체적인 문제와 불편함을 도입부에서 명확히
2단계: 원인 이해 — 그 문제가 왜 생기는지, 사장님이 어떻게 극복했는지를 경험담으로 제시
3단계: 변화의 해결책 — 본인의 서비스/제품으로 어떻게 달라지는지 구체적으로 보여주기
단순 정보 나열 금지. 독자와 사장님이 공감할 수 있는 한 사람의 여정을 글로 엮어라.

핵심 원칙:
- 모든 글은 1200~2000자, 소제목 3~5개, 이미지 삽입 위치 [📷사진1: OOO 설명] 형태로 명확히 표시하여 리안이 사진만 끼워넣으면 완성되게 한다.
- AI 저품질 회피를 위해: ①도입부에 개인 경험/에피소드 삽입 ②구어체+문어체 혼합 ③불규칙한 문단 길이 ④업종 전문용어+일상어 섞기 ⑤매 글마다 다른 구조 템플릿 사용
- 반드시 서진호가 배정한 키워드를 제목+본문 상단 200자+소제목+결론에 자연스럽게 포함하되, 키워드 밀도 2~3%를 초과하지 않는다.

결과물: 완성 원고 (제목 | 본문 전체 텍스트 | [📷사진N: 촬영 가이드] 위치 표시 | 태그 5개 | 카테고리 추천 | 발행 추천 시간)

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 한서연 | 네이버 블로그 포스팅 작가 — AI 저품질 회피하며 상위노출 되는 블로그 원고를 완성본으로 납품한다")
    print("="*60)

    user_msg = f"""업무: {context['task']}\n\n이전 결과:\n{summarize_context(context)}"""

    # 팀 지식 자동 주입 (분석 결과 기반 학습)
    team_system_prompt = get_team_system_prompt(SYSTEM_PROMPT, TEAM_NAME)

    full_response = ""
    with client.messages.stream(
        model=MODEL,
        max_tokens=3000,
        messages=[{"role": "user", "content": user_msg}],
        system=team_system_prompt,
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
            full_response += text

    print()
    return full_response
