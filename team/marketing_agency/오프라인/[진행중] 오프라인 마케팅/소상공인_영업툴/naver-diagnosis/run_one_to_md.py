"""
엑셀 업체 1개 진단 → 바탕화면 .md 파일 출력

사용: python run_one_to_md.py [업체명]
업체명 없으면 엑셀 첫 번째 업체 자동 사용
"""
import sys, io, os, asyncio, json
from pathlib import Path
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

THIS_DIR = Path(__file__).parent
sys.path.insert(0, str(THIS_DIR))

DESKTOP = Path.home() / "Desktop"
EXCEL_PATH = Path(__file__).parent.parent.parent / "소상공인 010수집 최종본" / "db" / "양주_010번호_최종_20260326_144032.xlsx"


def read_first_business(xlsx_path: Path, skip_franchise=True) -> str:
    import openpyxl
    wb = openpyxl.load_workbook(str(xlsx_path), read_only=True, data_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    wb.close()
    franchise_kw = ["본점", "직영", "체인", "가맹", "프랜차이즈", "1호점", "2호점"]
    headers = [str(h).strip() if h else "" for h in rows[0]]
    name_idx = next((i for i, h in enumerate(headers) if "업체명" in h or "상호" in h), 2)
    for row in rows[1:]:
        if not row or name_idx >= len(row):
            continue
        name = str(row[name_idx]).strip() if row[name_idx] else ""
        if not name or name == "None":
            continue
        if skip_franchise and any(kw in name for kw in franchise_kw):
            continue
        return name
    return ""


def build_md(data: dict, messages: dict) -> str:
    biz = data.get("business_name", "업체")
    grade = data.get("grade", "?")
    score = round(data.get("total_score", 0), 1)
    rank = data.get("naver_place_rank", 0)
    lost = data.get("estimated_lost_customers", 0)
    category = data.get("category", "")
    address = data.get("address", "")
    today = datetime.now().strftime("%Y-%m-%d")

    keywords = data.get("keywords") or []
    kw_lines = "\n".join(
        f"  - {k.get('keyword','-')}: {k.get('search_volume',0):,}회/월"
        for k in keywords[:5]
    ) or "  - 수집 중"

    def yn(v): return "✅" if v else "❌"

    improvement = data.get("improvement_points") or []
    imp_lines = "\n".join(f"  - {p.get('message', str(p))}" for p in improvement[:5]) or "  - 없음"

    msg1 = ""
    msg2 = ""
    msg3 = ""
    if messages:
        try: msg1 = messages.get("first", {}).get("text", "") or messages.get("first", "")
        except: msg1 = str(messages.get("first", ""))
        try: msg2 = messages.get("second", "")
        except: msg2 = ""
        try: msg3 = messages.get("third", "")
        except: msg3 = ""

    competitor_name = data.get("competitor_name") or "지역 1위"
    comp_brand_vol = data.get("competitor_brand_search_volume", 0)
    own_brand_vol = data.get("own_brand_search_volume", 0)

    md = f"""# {biz} 네이버 플레이스 진단 리포트
> 진단일: {today}

---

## 기본 정보
| 항목 | 내용 |
|---|---|
| 업체명 | {biz} |
| 업종 | {category} |
| 주소 | {address} |
| 네이버 플레이스 순위 | {rank}위 |
| 종합 등급 | **{grade}등급** |
| 종합 점수 | {score}/100 |
| 월 예상 손실 고객 | **{lost:,}명** |

---

## 항목별 점수
| 항목 | 점수 |
|---|---|
| 사진 | {round(data.get('photo_score',0),1)} |
| 리뷰 | {round(data.get('review_score',0),1)} |
| 블로그 | {round(data.get('blog_score',0),1)} |
| 키워드 | {round(data.get('keyword_score',0),1)} |
| 정보 | {round(data.get('info_score',0),1)} |
| 편의기능 | {round(data.get('convenience_score',0),1)} |
| 참여도 | {round(data.get('engagement_score',0),1)} |

---

## 플레이스 현황
| 항목 | 현황 |
|---|---|
| 사진 | {data.get('photo_count',0)}장 |
| 방문자 리뷰 | {data.get('visitor_review_count',0)}개 |
| 영수증 리뷰 | {data.get('receipt_review_count',0)}개 |
| 블로그 리뷰 | {data.get('blog_review_count',0)}개 |
| 북마크 | {data.get('bookmark_count',0)}개 |
| 메뉴 | {yn(data.get('has_menu'))} ({data.get('menu_count',0)}개) |
| 소개글 | {yn(data.get('has_intro'))} |
| 오시는길 | {yn(data.get('has_directions'))} |
| 영업시간 | {yn(data.get('has_hours'))} |
| 가격 | {yn(data.get('has_price'))} |
| 네이버 예약 | {yn(data.get('has_booking'))} |
| 톡톡 | {yn(data.get('has_talktalk'))} |
| 스마트콜 | {yn(data.get('has_smartcall'))} |
| 쿠폰 | {yn(data.get('has_coupon'))} |
| 새소식 | {yn(data.get('has_news'))} |
| 인스타그램 | {yn(data.get('has_instagram'))} |
| 카카오 | {yn(data.get('has_kakao'))} |

---

## 경쟁사 비교
| 항목 | 우리 | 경쟁사 평균 |
|---|---|---|
| 리뷰 수 | {data.get('visitor_review_count',0)+data.get('receipt_review_count',0)}개 | {data.get('competitor_avg_review',0)}개 |
| 사진 수 | {data.get('photo_count',0)}장 | {data.get('competitor_avg_photo',0)}장 |
| 블로그 수 | {data.get('blog_review_count',0)}개 | {data.get('competitor_avg_blog',0)}개 |
| 브랜드 검색량 | {own_brand_vol:,}회 | {comp_brand_vol:,}회 ({competitor_name}) |

---

## 키워드 검색량
{kw_lines}

---

## 개선 포인트
{imp_lines}

---

## 영업 메시지

### 1차 (첫 접촉)
{msg1}

### 2차 (진단 결과)
{msg2}

### 3차 (패키지 제안)
{msg3}

---
*자동 생성 — naver-diagnosis 시스템*
"""
    return md


async def run_diagnosis(business_name: str) -> dict:
    from playwright.async_api import async_playwright
    from services.naver_place_crawler import NaverPlaceCrawler
    from services.scorer import DiagnosisScorer
    from config.industry_weights import get_competitor_fallback

    print(f"  Playwright 브라우저 시작...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        try:
            crawler = NaverPlaceCrawler(browser)

            print(f"  place_id 검색 중: {business_name}")
            place_id = await crawler.find_place_id(business_name)
            if place_id:
                print(f"  place_id 발견: {place_id} → 상세 크롤링")
                data = await crawler.crawl_place_detail(place_id)
                if not data or not data.get("place_id"):
                    print(f"  상세 크롤링 실패 → 검색 기반 폴백")
                    data = await crawler.crawl_from_search(business_name)
            else:
                print(f"  place_id 없음 → 검색 기반 크롤링")
                data = await crawler.crawl_from_search(business_name)

            if not data:
                print(f"  크롤링 실패")
                return {}

            # business_name 보정
            if not data.get("business_name"):
                data["business_name"] = business_name

            # owner_reply_rate가 0이고 place_id 있으면 별도 수집
            if data.get("place_id") and not data.get("owner_reply_rate"):
                try:
                    reply_rate = await crawler.fetch_owner_reply_rate(data["place_id"])
                    data["owner_reply_rate"] = reply_rate
                except Exception as e:
                    print(f"  답글률 재수집 실패 (계속 진행): {e}")

            # 키워드 검색량
            if data.get("keywords"):
                try:
                    from services.naver_search_ad import NaverSearchAdAPI
                    ad_api = NaverSearchAdAPI()
                    enriched = []
                    for kw in data["keywords"][:5]:
                        kw_name = kw if isinstance(kw, str) else kw.get("keyword", "")
                        if not kw_name:
                            continue
                        stats = await ad_api.get_keyword_stats(kw_name)
                        enriched.append({
                            "keyword": kw_name,
                            "search_volume": (stats.get("monthly_search_pc", 0) or 0) + (stats.get("monthly_search_mobile", 0) or 0),
                        })
                    if enriched:
                        data["keywords"] = enriched
                except Exception as e:
                    print(f"  키워드 검색량 실패 (계속 진행): {e}")

            # 리뷰 합계
            data["review_count"] = data.get("visitor_review_count", 0) + data.get("receipt_review_count", 0)

            # 점수 계산
            scores = DiagnosisScorer.calculate_all(data)
            data.update(scores)

            # 경쟁사 폴백
            fb = get_competitor_fallback(data.get("category", ""))
            data.setdefault("competitor_avg_review", fb["avg_review"])
            data.setdefault("competitor_avg_photo", fb["avg_photo"])
            data.setdefault("competitor_avg_blog", fb["avg_blog"])

            # 손실 고객
            data["estimated_lost_customers"] = DiagnosisScorer.calculate_estimated_lost_customers(
                rank=data.get("naver_place_rank", 0),
                keywords=data.get("keywords", []),
                competitor_avg_review=fb["avg_review"],
                review_count=data.get("review_count", 0),
            )

            return data

        finally:
            await browser.close()


async def main():
    # 업체명 결정
    if len(sys.argv) > 1:
        business_name = sys.argv[1]
    else:
        print(f"엑셀에서 첫 업체 읽는 중: {EXCEL_PATH.name}")
        business_name = read_first_business(EXCEL_PATH)
        if not business_name:
            print("❌ 업체명을 찾을 수 없음")
            sys.exit(1)

    print(f"\n{'='*50}")
    print(f"진단 시작: {business_name}")
    print(f"{'='*50}\n")

    # 크롤링 실행
    data = await run_diagnosis(business_name)

    if not data:
        print("❌ 진단 데이터 수집 실패")
        sys.exit(1)

    # 메시지 생성
    messages = {}
    try:
        from services.message_generator import generate_all_messages
        messages = generate_all_messages(data)
        print("  영업 메시지 생성 완료")
    except Exception as e:
        print(f"  메시지 생성 실패 (계속 진행): {e}")

    # 마크다운 생성
    md_content = build_md(data, messages)

    # 바탕화면에 저장
    date_str = datetime.now().strftime("%Y%m%d_%H%M")
    out_path = DESKTOP / f"{business_name}_진단_{date_str}.md"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"\n{'='*50}")
    print(f"✅ 완료!")
    print(f"   업체: {data.get('business_name')}")
    print(f"   등급: {data.get('grade')} / 점수: {round(data.get('total_score',0),1)}")
    print(f"   손실 추정: 월 {data.get('estimated_lost_customers',0):,}명")
    print(f"   저장: {out_path}")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(main())
