"""
naver_crawler.py — 네이버 카페/쇼핑/스마트스토어 실제 크롤링

서진혁(리드 헌터)이 사용하는 핵심 도구.
Playwright로 실제 웹사이트 방문 → 진짜 데이터 수집.

사용법:
    from utils.naver_crawler import NaverCrawler

    crawler = NaverCrawler()
    # 1) 카페에서 고통받는 셀러 글 찾기
    posts = crawler.search_cafe_posts("스마트스토어 매출 안나요")
    # 2) 네이버 쇼핑에서 중간 순위 셀러 발굴
    sellers = crawler.search_shopping_sellers("캠핑 테이블", max_results=20)
    # 3) 스마트스토어 실제 분석
    store_data = crawler.analyze_smartstore("https://smartstore.naver.com/xxx")
    crawler.close()
"""

import os
import re
import json
import time
import random
from datetime import datetime
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

try:
    from playwright.sync_api import sync_playwright, Browser, Page
except ImportError:
    sync_playwright = None

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

BASE_DIR = Path(__file__).parent.parent
SCREENSHOT_DIR = BASE_DIR / "utils" / "screenshots"


class NaverCrawler:
    """네이버 카페/쇼핑/스마트스토어 크롤러."""

    def __init__(self, headless: bool = True):
        if not sync_playwright:
            raise ImportError("playwright 패키지가 필요합니다: pip install playwright")

        SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

        self._pw = sync_playwright().__enter__()
        self._browser = self._pw.chromium.launch(headless=headless)
        self._context = self._browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            locale="ko-KR",
        )
        self._page = self._context.new_page()

    def close(self):
        """브라우저 종료."""
        try:
            self._browser.close()
            self._pw.__exit__(None, None, None)
        except Exception:
            pass

    def _wait(self, min_sec: float = 1.0, max_sec: float = 3.0):
        """봇 감지 방지용 랜덤 대기."""
        time.sleep(random.uniform(min_sec, max_sec))

    def _safe_text(self, selector: str, default: str = "") -> str:
        """셀렉터로 텍스트 추출. 없으면 기본값."""
        try:
            el = self._page.query_selector(selector)
            return el.inner_text().strip() if el else default
        except Exception:
            return default

    def _safe_texts(self, selector: str) -> list[str]:
        """셀렉터로 여러 텍스트 추출."""
        try:
            els = self._page.query_selector_all(selector)
            return [el.inner_text().strip() for el in els if el.inner_text().strip()]
        except Exception:
            return []

    # ── 1. 네이버 카페 검색 — 고통받는 셀러 찾기 ──────────────────

    def search_cafe_posts(
        self,
        keywords: list[str] | str,
        max_results: int = 20,
    ) -> list[dict]:
        """
        네이버 통합검색(카페 탭)에서 셀러 고민 글을 찾는다.

        Args:
            keywords: 검색 키워드 (리스트 또는 문자열)
                예: ["스마트스토어 매출 안나요", "쿠팡 광고비 효율"]
            max_results: 총 수집할 글 수

        Returns:
            [
                {
                    "title": "광고비 100만원 썼는데 매출 50만원...",
                    "snippet": "글 내용 미리보기...",
                    "cafe_name": "스마트스토어 셀러 모임",
                    "author": "닉네임",
                    "date": "2025.03.15.",
                    "url": "https://cafe.naver.com/...",
                    "search_keyword": "스마트스토어 매출 안나요",
                }
            ]
        """
        if isinstance(keywords, str):
            keywords = [keywords]

        all_posts = []
        seen_urls = set()

        for keyword in keywords:
            if len(all_posts) >= max_results:
                break

            try:
                url = (
                    f"https://search.naver.com/search.naver"
                    f"?ssc=tab.cafe.all&where=article"
                    f"&sm=tab_viw.cafe&query={keyword}"
                )
                self._page.goto(url, wait_until="networkidle", timeout=20000)
                self._wait(2.0, 4.0)

                # 카페 글 링크 추출 (실제 글 URL에는 ?art= 파라미터가 붙음)
                links = self._page.query_selector_all(
                    "a[href*='cafe.naver.com'][href*='art=']"
                )

                # 카페 글 제목 링크만 필터 (내용 스니펫 링크는 같은 URL이므로 중복 제거)
                for link in links:
                    if len(all_posts) >= max_results:
                        break

                    try:
                        href = link.get_attribute("href") or ""
                        text = link.inner_text().strip()

                        # URL 중복 방지 (같은 글의 제목/본문 링크)
                        base_url = href.split("?")[0] if href else ""
                        if not base_url or base_url in seen_urls:
                            continue

                        # 너무 짧은 텍스트 (카페명 등) 스킵
                        if len(text) < 10:
                            continue

                        seen_urls.add(base_url)

                        # 카페명 찾기: 이 링크 앞에 있는 카페 링크
                        # 부모 요소에서 카페명 추출 시도
                        cafe_name = ""
                        try:
                            parent = link.evaluate_handle(
                                "el => el.closest('div') || el.parentElement"
                            )
                            if parent:
                                cafe_links = parent.as_element().query_selector_all(
                                    "a[href*='cafe.naver.com']:not([href*='art='])"
                                )
                                for cl in cafe_links:
                                    ctext = cl.inner_text().strip()
                                    if ctext and len(ctext) > 2 and len(ctext) < 60:
                                        cafe_name = ctext
                                        break
                        except Exception:
                            pass

                        all_posts.append({
                            "title": text[:150],
                            "snippet": "",
                            "cafe_name": cafe_name,
                            "author": "",
                            "date": "",
                            "url": href,
                            "search_keyword": keyword,
                        })
                    except Exception:
                        continue

                # 날짜 추출 보강: body 텍스트에서 날짜 패턴 매칭
                try:
                    body_text = self._page.inner_text("body")
                    date_matches = re.findall(
                        r'(\d{4}\.\d{2}\.\d{2}\.?)', body_text
                    )
                    for i, post in enumerate(all_posts):
                        if not post["date"] and i < len(date_matches):
                            post["date"] = date_matches[i]
                except Exception:
                    pass

                print(f"    ✅ 카페 검색 '{keyword}': {len(all_posts)}개 수집")

            except Exception as e:
                print(f"    ⚠️ 카페 검색 실패 ({keyword}): {str(e)[:60]}")

        return all_posts[:max_results]

    # ── 2-A. 네이버 통합검색에서 스마트스토어 셀러 발굴 ─────────────

    def search_shopping_sellers(
        self,
        keyword: str,
        max_results: int = 10,
    ) -> list[dict]:
        """
        네이버 통합검색에서 키워드 검색 후 스마트스토어 셀러 URL을 추출한다.
        (네이버 쇼핑 직접 접근은 봇 차단 → 통합검색에서 우회)
        """
        sellers = []

        try:
            url = (
                f"https://search.naver.com/search.naver"
                f"?where=nexearch&query={keyword}"
            )
            self._page.goto(url, wait_until="networkidle", timeout=20000)
            self._wait(2.0, 4.0)

            # HTML에서 smartstore URL 추출
            html = self._page.content()
            store_ids = re.findall(
                r'smartstore\.naver\.com/([a-zA-Z0-9_\-]+)', html
            )
            # 시스템 경로 제외, 중복 제거
            skip_ids = {"main", "inflow", "checkout", "sell", "help", "center"}
            unique_ids = list(dict.fromkeys(
                sid for sid in store_ids if sid not in skip_ids
            ))

            for sid in unique_ids[:max_results]:
                sellers.append({
                    "store_name": sid,
                    "store_url": f"https://smartstore.naver.com/{sid}",
                    "category": keyword,
                    "search_keyword": keyword,
                })

            print(f"    ✅ 통합검색 '{keyword}': {len(sellers)}개 스마트스토어 발굴")

        except Exception as e:
            print(f"    ⚠️ 통합검색 실패 ({keyword}): {str(e)[:60]}")

        return sellers

    # ── 2-B. Perplexity로 실제 셀러 발굴 (보조) ──────────────────

    def search_sellers_perplexity(
        self,
        keyword: str,
        max_results: int = 10,
    ) -> list[dict]:
        """
        Perplexity로 실제 존재하는 스마트스토어/쿠팡 셀러를 검색한다.
        (네이버 쇼핑은 봇 차단하므로 Perplexity로 우회)

        Returns:
            [
                {
                    "store_name": "캠핑마트",
                    "store_url": "https://smartstore.naver.com/campingmart",
                    "category": "캠핑/아웃도어",
                    "description": "Perplexity가 찾은 설명...",
                    "search_keyword": "캠핑 테이블",
                }
            ]
        """
        sellers = []

        if not OpenAI:
            print("    ⚠️ openai 패키지 없음 — Perplexity 검색 불가")
            return sellers

        api_key = os.getenv("PERPLEXITY_API_KEY")
        if not api_key:
            print("    ⚠️ PERPLEXITY_API_KEY 없음")
            return sellers

        try:
            client = OpenAI(
                api_key=api_key,
                base_url="https://api.perplexity.ai",
                timeout=60.0,
            )

            query = (
                f"네이버 스마트스토어에서 '{keyword}' 카테고리 중간 규모 셀러 "
                f"(리뷰 100~1000개, 월매출 500만~5000만 추정) {max_results}개를 찾아줘. "
                f"반드시 실제 존재하는 스마트스토어 URL(smartstore.naver.com/xxx)을 포함해. "
                f"각 셀러별로: 스토어명, URL, 카테고리, 주력상품, 리뷰 수 추정치를 알려줘. "
                f"URL이 확실하지 않으면 포함하지 마."
            )

            resp = client.chat.completions.create(
                model="sonar-pro",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "실제 존재하는 스마트스토어 URL만 제공해. "
                            "확실하지 않은 URL은 절대 포함하지 마. "
                            "JSON 배열 형식으로 답해: "
                            '[{"store_name":"...", "store_url":"https://smartstore.naver.com/...", '
                            '"category":"...", "main_product":"...", "estimated_reviews":"..."}]'
                        ),
                    },
                    {"role": "user", "content": query},
                ],
                max_tokens=2000,
            )

            text = resp.choices[0].message.content

            # JSON 추출 시도
            json_match = re.search(r'\[.*\]', text, re.DOTALL)
            if json_match:
                try:
                    parsed = json.loads(json_match.group())
                    for item in parsed[:max_results]:
                        url = item.get("store_url", "")
                        if "smartstore.naver.com" in url:
                            sellers.append({
                                "store_name": item.get("store_name", ""),
                                "store_url": url,
                                "category": item.get("category", ""),
                                "main_product": item.get("main_product", ""),
                                "estimated_reviews": item.get("estimated_reviews", ""),
                                "description": text[:200],
                                "search_keyword": keyword,
                            })
                except json.JSONDecodeError:
                    pass

            # JSON 파싱 실패 시 URL만이라도 추출
            if not sellers:
                urls = re.findall(
                    r'https://smartstore\.naver\.com/[\w\-]+', text
                )
                for url in list(set(urls))[:max_results]:
                    store_id = url.split("/")[-1]
                    sellers.append({
                        "store_name": store_id,
                        "store_url": url,
                        "category": keyword,
                        "main_product": "",
                        "estimated_reviews": "",
                        "description": text[:200],
                        "search_keyword": keyword,
                    })

            print(f"    ✅ Perplexity 셀러 검색 '{keyword}': {len(sellers)}개 발굴")

        except Exception as e:
            print(f"    ⚠️ Perplexity 검색 실패 ({keyword}): {str(e)[:60]}")

        return sellers

    # ── 3. 스마트스토어 실제 분석 ──────────────────────────────────

    def analyze_smartstore(self, store_url: str) -> dict:
        """
        스마트스토어 URL에 직접 방문해서 실제 데이터를 수집한다.

        Args:
            store_url: 스마트스토어 URL (예: "https://smartstore.naver.com/xxx")

        Returns:
            {
                "store_url": "https://smartstore.naver.com/xxx",
                "store_name": "캠핑마트",
                "total_products": 47,
                "total_reviews": 342,
                "avg_rating": "4.7",
                "categories": ["캠핑/아웃도어", "테이블/의자"],
                "top_products": [
                    {"name": "접이식 테이블", "price": "39,900", "reviews": 120}
                ],
                "recent_reviews": [
                    {"text": "배송 빠르고 좋아요", "rating": 5, "date": "2025.03.10"}
                ],
                "store_description": "...",
                "detail_page_quality": "스펙 나열형, 이미지 3장",
                "screenshot_path": "utils/screenshots/xxx.png",
                "crawled_at": "2026-04-07T15:30:00",
            }
        """
        result = {
            "store_url": store_url,
            "store_name": "",
            "total_products": 0,
            "total_reviews": 0,
            "avg_rating": "",
            "categories": [],
            "top_products": [],
            "recent_reviews": [],
            "store_description": "",
            "detail_page_quality": "",
            "screenshot_path": "",
            "crawled_at": datetime.now().isoformat(),
        }

        try:
            safe_name = re.sub(r'[^\w\-]', '_', store_url.split('/')[-1])[:50]

            # 전체 상품 페이지로 바로 이동 (여기에 상품 수 + 상품 리스트 있음)
            products_url = store_url.rstrip('/') + "/category/ALL"
            self._page.goto(products_url, wait_until="networkidle", timeout=25000)
            self._wait(3.0, 5.0)

            # body 텍스트에서 데이터 추출 (React 렌더링 후)
            body = self._page.inner_text("body")

            # 스토어명 (store_url의 마지막 경로를 기본값으로)
            result["store_name"] = store_url.rstrip('/').split('/')[-1]

            # 관심고객수
            followers_match = re.search(r'관심고객수\s*([\d,]+)', body)
            if followers_match:
                result["followers"] = int(followers_match.group(1).replace(",", ""))

            # 총 상품 수
            products_match = re.search(r'총\s*([\d,]+)\s*개', body)
            if products_match:
                result["total_products"] = int(products_match.group(1).replace(",", ""))

            # 스크린샷
            screenshot_path = str(SCREENSHOT_DIR / f"{safe_name}_main.png")
            try:
                self._page.screenshot(path=screenshot_path, full_page=False)
                result["screenshot_path"] = screenshot_path
            except Exception:
                pass

            # 상품명/가격 추출 (body 텍스트에서 패턴 매칭)
            lines = [l.strip() for l in body.split('\n') if l.strip()]
            i = 0
            while i < len(lines) and len(result["top_products"]) < 5:
                line = lines[i]
                # 가격 패턴: "숫자,숫자원" 또는 "숫자원"
                price_match = re.match(r'^([\d,]+)원$', line)
                if price_match and i > 0:
                    # 가격 바로 위 줄이 상품명일 가능성
                    prev_line = lines[i-1].strip()
                    # 상품명으로 적합한지 체크 (길이, 특수한 패턴 제외)
                    if (len(prev_line) > 5 and
                        not re.match(r'^[\d,]+원$', prev_line) and
                        prev_line not in ('BEST', '전체상품', '무료배송')):
                        result["top_products"].append({
                            "name": prev_line[:80],
                            "price": line,
                            "reviews": "",
                        })
                i += 1

            # 카테고리 추출 (메뉴에서)
            categories = []
            for line in lines:
                if line in ('전체상품', '공지사항', '쇼핑스토리', '리뷰이벤트',
                           '묻고 답하기', '판매자 정보', '검색어를 입력해주세요',
                           '하위 메뉴 있음', '서비스 더보기', '알림받기',
                           'BEST', '네이버플러스 스토어 홈', '사용자 링크',
                           '쇼핑라이브'):
                    continue
                if (2 < len(line) < 20 and
                    not re.match(r'^[\d,]+', line) and
                    not re.match(r'^(SET|상품|상세|필터|인기|최신|낮은|높은|할인|판매|리뷰|평점)', line)):
                    # 메뉴 항목처럼 보이는 짧은 텍스트
                    if len(categories) < 5:
                        categories.append(line)
            result["categories"] = categories

            # 대표 상품 상세페이지 분석 (첫 번째 상품 링크)
            try:
                product_links = self._page.query_selector_all(
                    "a[href*='/products/']"
                )
                if product_links:
                    href = product_links[0].get_attribute("href")
                    if href:
                        if not href.startswith("http"):
                            href = "https://smartstore.naver.com" + href
                        self._page.goto(href, wait_until="networkidle", timeout=20000)
                        self._wait(2.0, 4.0)

                        # 상세페이지 스크린샷
                        detail_path = str(SCREENSHOT_DIR / f"{safe_name}_detail.png")
                        self._page.screenshot(path=detail_path, full_page=False)

                        # 상세 영역 이미지 수
                        img_count = len(self._page.query_selector_all("img"))
                        detail_body = self._page.inner_text("body")

                        # 리뷰 수/평점 추출 (상품 페이지에 있음)
                        review_match = re.search(
                            r'리뷰\s*([\d,]+)', detail_body
                        )
                        if review_match:
                            result["total_reviews"] = int(
                                review_match.group(1).replace(",", "")
                            )

                        rating_match = re.search(
                            r'(\d+\.\d+)\s*/\s*5', detail_body
                        )
                        if rating_match:
                            result["avg_rating"] = rating_match.group(1)

                        if img_count <= 5:
                            quality = f"이미지 {img_count}장 — 빈약"
                        elif img_count <= 15:
                            quality = f"이미지 {img_count}장 — 보통"
                        else:
                            quality = f"이미지 {img_count}장 — 양호"
                        result["detail_page_quality"] = quality

                        # 리뷰 텍스트 추출 (상품 상세 페이지 하단)
                        review_lines = []
                        in_review = False
                        for line in detail_body.split('\n'):
                            line = line.strip()
                            if '리뷰' in line and re.search(r'\d', line):
                                in_review = True
                                continue
                            if in_review and len(line) > 10 and len(line) < 300:
                                review_lines.append(line)
                                if len(review_lines) >= 5:
                                    break

                        for rt in review_lines:
                            result["recent_reviews"].append({
                                "text": rt[:200],
                                "rating": "",
                                "date": "",
                            })

            except Exception:
                pass

            print(f"    ✅ 스토어 분석 완료: {result['store_name']}")

        except Exception as e:
            print(f"    ⚠️ 스토어 분석 실패 ({store_url}): {str(e)[:60]}")

        return result

    # ── 4. 쿠팡 셀러 검색 (보너스) ──────────────────────────────────

    def search_coupang_sellers(
        self,
        keyword: str,
        max_results: int = 10,
    ) -> list[dict]:
        """
        쿠팡에서 키워드 검색 후 셀러 정보를 수집한다.
        """
        sellers = []

        try:
            url = f"https://www.coupang.com/np/search?q={keyword}&channel=user"
            self._page.goto(url, wait_until="domcontentloaded", timeout=15000)
            self._wait(2.0, 4.0)

            items = self._page.query_selector_all(
                "li.search-product, ul.search-product-list > li"
            )

            rank = 0
            for item in items:
                rank += 1
                if len(sellers) >= max_results:
                    break
                try:
                    name_el = item.query_selector("div.name, a.search-product-link")
                    name = name_el.inner_text().strip() if name_el else ""

                    price_el = item.query_selector("strong.price-value, em.sale")
                    price = price_el.inner_text().strip() if price_el else ""

                    review_el = item.query_selector("span.rating-total-count")
                    review = review_el.inner_text().strip("()") if review_el else "0"

                    rating_el = item.query_selector("em.rating")
                    rating = rating_el.inner_text().strip() if rating_el else ""

                    link_el = item.query_selector("a[href]")
                    product_url = link_el.get_attribute("href") if link_el else ""
                    if product_url and not product_url.startswith("http"):
                        product_url = "https://www.coupang.com" + product_url

                    if name:
                        sellers.append({
                            "rank": rank,
                            "product_name": name[:100],
                            "price": price,
                            "review_count": review,
                            "rating": rating,
                            "product_url": product_url,
                            "search_keyword": keyword,
                        })
                except Exception:
                    continue

            print(f"    ✅ 쿠팡 검색 '{keyword}': {len(sellers)}개 발굴")

        except Exception as e:
            print(f"    ⚠️ 쿠팡 검색 실패 ({keyword}): {str(e)[:60]}")

        return sellers

    # ── 5. 전체 리드 발굴 파이프라인 ──────────────────────────────────

    def full_lead_discovery(
        self,
        target_categories: list[str] = None,
        cafe_keywords: list[str] = None,
        max_cafe_posts: int = 15,
        max_shopping_sellers: int = 15,
        max_store_analyses: int = 5,
    ) -> dict:
        """
        전체 리드 발굴 파이프라인.
        카페 스캔 → 쇼핑 셀러 → 상위 셀러 스토어 분석까지 한번에.

        Args:
            target_categories: 검색할 상품 카테고리 (예: ["캠핑 테이블", "강아지 간식"])
            cafe_keywords: 카페 검색 키워드 (예: ["스마트스토어 매출 안나요"])
            max_cafe_posts: 카페 글 최대 수집 수
            max_shopping_sellers: 쇼핑 셀러 최대 수집 수
            max_store_analyses: 스토어 상세 분석 최대 수

        Returns:
            {
                "cafe_posts": [...],
                "shopping_sellers": [...],
                "store_analyses": [...],
                "summary": "카페 글 15개, 셀러 20개, 분석 5개 완료",
            }
        """
        if target_categories is None:
            target_categories = [
                "스마트스토어 인기 상품",
                "캠핑 용품",
                "반려동물 용품",
            ]

        if cafe_keywords is None:
            cafe_keywords = [
                "스마트스토어 매출 안나요",
                "스마트스토어 광고 효과 없어",
                "쿠팡 셀러 광고비 효율",
                "네이버 쇼핑 상위 노출 방법",
                "스마트스토어 상세페이지 전환",
            ]

        result = {
            "cafe_posts": [],
            "shopping_sellers": [],
            "store_analyses": [],
            "summary": "",
        }

        # Step 1: 카페 크롤링
        print("\n  [Step 1] 네이버 카페 크롤링 — 고통받는 셀러 찾기...")
        result["cafe_posts"] = self.search_cafe_posts(
            cafe_keywords, max_results=max_cafe_posts
        )

        # Step 2: 네이버 통합검색에서 실제 셀러 발굴
        print("\n  [Step 2] 네이버 통합검색으로 실제 셀러 발굴...")
        all_sellers = []
        per_category = max(3, max_shopping_sellers // len(target_categories))
        for category in target_categories:
            sellers = self.search_shopping_sellers(
                category, max_results=per_category
            )
            all_sellers.extend(sellers)
            self._wait(1.5, 3.0)
        result["shopping_sellers"] = all_sellers[:max_shopping_sellers]

        # Step 3: 스토어 상세 분석 (스마트스토어 URL이 있는 셀러만)
        print("\n  [Step 3] 스마트스토어 상세 분석 — 실제 데이터 수집...")
        stores_to_analyze = []
        for seller in all_sellers:
            url = seller.get("store_url", "")
            if "smartstore.naver.com" in url and url not in stores_to_analyze:
                stores_to_analyze.append(url)
            if len(stores_to_analyze) >= max_store_analyses:
                break

        for store_url in stores_to_analyze:
            analysis = self.analyze_smartstore(store_url)
            result["store_analyses"].append(analysis)
            self._wait(2.0, 4.0)  # 스토어 분석 간 대기

        # 요약
        result["summary"] = (
            f"카페 글 {len(result['cafe_posts'])}개, "
            f"셀러 {len(result['shopping_sellers'])}개, "
            f"스토어 분석 {len(result['store_analyses'])}개 완료"
        )

        print(f"\n  📊 수집 완료: {result['summary']}")
        return result


# ── CLI 테스트 ──────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    keyword = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "스마트스토어 매출 안나요"

    print(f"🔍 테스트 크롤링: {keyword}")
    crawler = NaverCrawler(headless=True)
    try:
        posts = crawler.search_cafe_posts(keyword, max_results=5)
        print(f"\n카페 글 {len(posts)}개:")
        for p in posts:
            print(f"  - {p['title'][:60]} ({p['cafe_name']})")

        sellers = crawler.search_shopping_sellers(keyword, max_results=5)
        print(f"\n쇼핑 셀러 {len(sellers)}개:")
        for s in sellers:
            print(f"  - [{s['rank']}위] {s['product_name'][:40]} / {s['store_name']}")

    finally:
        crawler.close()
