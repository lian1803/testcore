import os
from core.pipeline_utils import summarize_context
import sys
import io
import anthropic

# Windows UTF-8 환경 설정 (runner에서 이미 처리됐으면 스킵)
if not os.environ.get("_LIANCP_UTF8_DONE"):
    try:
        if sys.stdout and hasattr(sys.stdout, 'buffer') and not sys.stdout.buffer.closed:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except (ValueError, AttributeError):
        pass

# Meta Ads 분석 모듈 임포트
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../utils'))
try:
    from meta_ads import spy, find_gaps
except ImportError:
    spy = None
    find_gaps = None

# 웹 스크래퍼 임포트
try:
    from web_scraper import scrape_url, scrape_naver_place
except ImportError:
    scrape_url = None
    scrape_naver_place = None

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 박탐정이야. 온라인영업팀의 타겟 소상공인 잠재고객 분석 및 식별 기준 설계 전문가.
전문 분야: 소상공인 온라인 취약점 식별, 업종별 타겟팅 기준 수립, 수작업 가능한 잠재고객 발굴 프로세스 설계

핵심 원칙:
- 절대 크롤링 도구나 자동 수집 봇을 추천하지 않는다. 네이버 크롤링은 법적으로 금지되어 있으므로, 반드시 수작업 검색 또는 공개 API만 활용하는 방법을 안내한다
- 리안이 직접 실행 가능한 '검색어 + 체크리스트' 형태로만 산출물을 만든다. 코딩이나 개발 도구가 필요한 방법은 절대 제시하지 않는다
- 잠재고객 식별 기준은 반드시 수치화한다. '리뷰 30개 미만', '인스타 포스팅 월 2회 미만', '블로그 없음' 등 누구나 판단 가능한 객관적 기준만 사용한다

결과물: 업종별 타겟 소상공인 식별 체크리스트(점수표 포함), 네이버/인스타/블로그에서 취약 업체 찾는 단계별 검색 가이드, 주간 잠재고객 리스트 템플릿(업체명/업종/지역/네이버리뷰수/인스타팔로워/취약점요약/우선순위점수)

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 박탐정 | 타겟 소상공인 잠재고객 분석 및 식별 기준 설계 전문가")
    print("="*60)

    # Meta Ads 분석 자동 실행 (경쟁사 정보가 있으면)
    meta_analysis = ""
    if spy and find_gaps:
        task_lower = context.get('task', '').lower()

        # 경쟁사명 감지 (예: "카페", "음식점", "미용실" 등 업종명이 있으면)
        if any(keyword in task_lower for keyword in ['경쟁', '경쟁사', '분석', '비교']):
            print("\n🔍 Meta Ads 경쟁사 분석 중...")

            # 간단한 경쟁사 추출 (실제로는 더 정교한 파싱 가능)
            competitors = []
            if '경쟁사' in context.get('task', ''):
                # task에서 경쟁사명 추출 시도
                competitors = ['네이버', '구글', '카카오']  # 기본값

            if competitors:
                meta_analysis = f"\n\n=== Meta Ads 경쟁사 분석 결과 ===\n"
                meta_analysis += spy(competitors[0])
                meta_analysis += "\n\n=== 경쟁사 틈새 분석 ===\n"
                meta_analysis += find_gaps(competitors)

    # 웹 스크래핑 추가 (URL이 context에 있으면)
    web_content = ""
    if scrape_url:
        # context에서 URL 패턴 찾기
        import re
        context_str = str(context)
        url_pattern = r'https?://[^\s"\)>]+'
        urls = re.findall(url_pattern, context_str)

        if urls:
            print(f"\n🌐 웹페이지 스크래핑 중... ({len(urls)}개 URL)")
            for url in urls[:3]:  # 최대 3개까지만 처리
                try:
                    content = scrape_url(url)
                    if content:
                        web_content += f"\n\n{content}"
                except Exception as e:
                    # 실패해도 조용히 넘어감
                    pass

    user_msg = f"""업무: {context['task']}\n\n이전 결과:\n{summarize_context(context)}{meta_analysis}{web_content}"""

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
