import os
import sys
import json
import anthropic

MODEL = "claude-sonnet-4-5"

# 크롤러 임포트
try:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from utils.naver_crawler import NaverCrawler
    HAS_CRAWLER = True
except ImportError:
    HAS_CRAWLER = False

SYSTEM_PROMPT = """너는 서진혁이야. 온라인마케팅팀의 리드 헌터 — 잠재 셀러 발굴 및 시장 정보 수집 전문가.
전문 분야: 스마트스토어/쿠팡/인스타그램 셀러 리스트 크롤링, 매출·리뷰·키워드 현황 분석, 리드 스코어링

핵심 원칙:
- 데이터 없는 리드는 리드가 아니다 — 모든 잠재 고객에 매출 추정치·리뷰 수·키워드 경쟁도·광고 집행 추정 여부를 반드시 첨부한다
- 주 1회 최소 50개 신규 리드를 발굴하고, 상위 20개를 A등급으로 분류하여 영업 에이전트에게 넘긴다
- 셀러의 '아픈 곳'(매출 정체, 리뷰 부족, 키워드 미노출, 상세페이지 품질 저하)을 3가지 이상 구체적으로 적어야 리드 카드가 완성된다

결과물: 리드 카드 (JSON/스프레드시트): {셀러명, 플랫폼, 스토어URL, 카테고리, 월 추정매출, 리뷰수, 주력키워드 3개, 키워드 순위, 광고 집행 여부, 상세페이지 품질 점수(1-10), 페인포인트 3가지, 리드등급(A/B/C), 수집일자}

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 실제 수집 데이터 기반 수치만. 추정치는 "(추정: 산출근거)" 형식 필수. 출처 없는 시장 통계·성장률·사례 생성 = 감점. 바로 복붙 가능한 형식으로"""

def _crawl_leads(task: str) -> dict:
    """Playwright로 실제 웹 크롤링 → 진짜 셀러 데이터 수집."""
    if not HAS_CRAWLER:
        print("    ⚠️ 크롤러 없음 — AI 생성 모드로 폴백")
        return {}

    print("\n  🔍 [크롤러] 실제 웹 크롤링 시작...")

    # 태스크에서 카테고리 키워드 추출
    default_categories = ["스마트스토어 인기 상품", "캠핑 용품", "반려동물 용품"]
    default_cafe_kw = [
        "스마트스토어 매출 안나요",
        "스마트스토어 광고 효과 없어",
        "쿠팡 셀러 광고비 효율",
    ]

    crawler = NaverCrawler(headless=True)
    try:
        result = crawler.full_lead_discovery(
            target_categories=default_categories,
            cafe_keywords=default_cafe_kw,
            max_cafe_posts=10,
            max_shopping_sellers=10,
            max_store_analyses=3,
        )
        return result
    except Exception as e:
        print(f"    ⚠️ 크롤링 실패: {e}")
        return {}
    finally:
        crawler.close()

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 서진혁 | 리드 헌터 — 실제 크롤링 + AI 분석")
    print("="*60)

    # Step 1: 실제 크롤링
    crawl_data = _crawl_leads(context['task'])

    # 크롤링 데이터를 context에 저장 (다른 에이전트도 사용 가능)
    context["crawl_data"] = crawl_data

    # Step 2: 크롤링 결과를 AI가 리드 카드로 정리
    interview = context.get('interview', '')

    # 크롤링 데이터 텍스트로 변환
    crawl_text = ""
    if crawl_data:
        # 카페 글
        if crawl_data.get("cafe_posts"):
            crawl_text += "\n## 네이버 카페에서 찾은 셀러 고민 글 (실제 데이터)\n"
            for p in crawl_data["cafe_posts"]:
                crawl_text += f"- [{p['search_keyword']}] {p['title']}\n"
                crawl_text += f"  URL: {p['url']}\n"

        # 발굴된 셀러
        if crawl_data.get("shopping_sellers"):
            crawl_text += "\n## 네이버에서 발굴된 실제 스마트스토어 셀러\n"
            for s in crawl_data["shopping_sellers"]:
                crawl_text += f"- {s['store_name']}: {s['store_url']} (카테고리: {s['category']})\n"

        # 스토어 분석 결과
        if crawl_data.get("store_analyses"):
            crawl_text += "\n## 스토어 실제 분석 결과 (Playwright로 방문)\n"
            for a in crawl_data["store_analyses"]:
                crawl_text += f"\n### {a['store_name']} ({a['store_url']})\n"
                crawl_text += f"- 팔로워: {a.get('followers', '?')}명\n"
                crawl_text += f"- 총 상품: {a['total_products']}개\n"
                crawl_text += f"- 리뷰: {a['total_reviews']}개\n"
                crawl_text += f"- 평점: {a['avg_rating']}\n"
                crawl_text += f"- 상세페이지: {a['detail_page_quality']}\n"
                if a['top_products']:
                    crawl_text += f"- 상위 상품: {json.dumps(a['top_products'][:3], ensure_ascii=False)}\n"
                if a['recent_reviews']:
                    crawl_text += f"- 최근 리뷰: {json.dumps(a['recent_reviews'][:3], ensure_ascii=False)}\n"

    # 크롤링 실패 시 task에서 키워드 추출해 AI 추정 리드 생성용 힌트 구성
    fallback_hint = ""
    if not crawl_text:
        import re as _re
        keywords = _re.findall(r'[가-힣a-zA-Z0-9]{2,}', context['task'])
        keyword_sample = " / ".join(keywords[:8]) if keywords else "스마트스토어 셀러"
        fallback_hint = f"""
⚠️ 크롤링 데이터 없음 — AI 추정 모드
task 키워드 힌트: {keyword_sample}

위 키워드 기반으로 최소 3개 리드를 AI 추정으로 생성해줘.
단, 모든 수치에 반드시 "(AI 추정 — 실제 확인 필요)" 표기 필수.
스토어 URL은 "(URL 미확인)" 처리. 실제 존재하는 것처럼 쓰지 마."""

    user_msg = f"""업무: {context['task']}

리안 인터뷰:
{interview}

{'='*40}
아래는 Playwright로 실제 웹사이트를 방문해서 수집한 진짜 데이터야.
이 데이터를 기반으로 리드 카드를 작성해.
{'='*40}

{crawl_text if crawl_text else fallback_hint}

위 데이터를 기반으로 리드 카드를 작성해줘.
각 리드마다:
- 셀러명 + 스토어 URL
- 팔로워 수 + 상품 수 + 리뷰 수
- 상세페이지 품질 평가
- 페인포인트 3가지
- 리드 등급 (A/B/C)
- 접근 방법 추천: 연락 채널(스마트스토어 문의/이메일/DM)과 타이밍만. 이메일/DM 본문 작성 금지. 존재하지 않는 파일(.pdf, .xlsx 등) 첨부 언급 절대 금지.

'실제 데이터 기반'과 'AI 추정'을 반드시 구분 표기해.

⚠️ 출력에 [1][2][3] 같은 각주/인용 번호 절대 사용 금지. 인용 표시 넣지 마.
⚠️ 접근방법에 출처 없는 수치 금지: "전환율 250%", "클릭률 70% 하락", "매출 3배" 등 구체적 숫자 사용 금지. "리뷰 0개 셀러는 검색 노출에서 불리" 같은 정성적 표현만 허용."""

    full_response = ""
    with client.messages.stream(
        model=MODEL,
        max_tokens=5000,
        messages=[{"role": "user", "content": user_msg}],
        system=SYSTEM_PROMPT,
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
            full_response += text

    print()
    return full_response
