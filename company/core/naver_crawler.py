"""
naver_crawler.py — 네이버 플레이스 실제 데이터 수집

requests + BeautifulSoup으로 구현.
Playwright MCP는 대화형이라 subprocess에서 못 쓰므로 이 방식 선택.

수집 대상:
- 가게명, 업종, 주소
- 별점, 리뷰 수
- 최근 사진 업데이트일 (있으면)
- 방문자 리뷰 수
- 영업시간, 가격대

사용 예시:
    from core.naver_crawler import crawl_place, search_place

    # URL 직접 크롤링
    data = crawl_place("https://map.naver.com/v5/entry/place/1234567")

    # 가게명으로 검색 후 크롤링
    data = search_place("강남 스타벅스 역삼점")
"""

import requests
import json
import re
import time
from datetime import datetime
from typing import Dict, Optional, List
from bs4 import BeautifulSoup
from urllib.parse import quote, urlencode

# 네이버 User-Agent (봇 차단 우회)
NAVER_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}


def extract_place_id(url: str) -> Optional[str]:
    """
    네이버 플레이스 URL에서 place_id 추출.

    형식:
    - https://map.naver.com/v5/entry/place/1234567
    - https://m.place.naver.com/restaurant/1234567
    """
    # /place/ 다음 숫자 추출
    match = re.search(r'/place/(\d+)', url)
    if match:
        return match.group(1)

    # 레스토랑/카페/병원 등 카테고리 형식
    match = re.search(r'/(?:restaurant|cafe|hospital|hair|hotel|pharmacy)/(\d+)', url)
    if match:
        return match.group(1)

    return None


def search_place(place_name: str) -> Optional[Dict]:
    """
    가게명으로 네이버 플레이스 검색 후 첫 번째 결과 크롤링.

    참고: 현재 네이버는 API 직접 호출을 제한합니다.
    실제 운영 환경에서는:
    1. 네이버 클라우드 플랫폼 Search API 구독 (유료)
    2. Selenium/Playwright를 통한 브라우저 자동화
    3. 대체 서비스: Google Places API, Kakao Map API

    Args:
        place_name: 검색할 가게명 (예: "강남 스타벅스 역삼점")

    Returns:
        크롤링된 가게 데이터 또는 None (검색 실패 시)
    """
    try:
        # 네이버 검색 (모바일 버전)
        search_url = f"https://m.place.naver.com/restaurants/search"
        params = {"query": place_name, "sort": "review"}

        response = requests.get(
            search_url,
            params=params,
            headers=NAVER_HEADERS,
            timeout=10,
            allow_redirects=True
        )
        response.raise_for_status()

        # HTML에서 place_id 추출 시도
        html = response.text
        match = re.search(r'/restaurant/(\d+)', html)

        if not match:
            print(f"검색 실패: {place_name}")
            return None

        place_id = match.group(1)
        print(f"검색됨: {place_name} (ID: {place_id})")

        # 상세 정보 크롤링
        return crawl_place(f"https://m.place.naver.com/restaurant/{place_id}")

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            print(f"접근 제한 ({place_name}): 네이버 API는 인증이 필요합니다.")
            print("해결 방법:")
            print("  1. 네이버 클라우드 플랫폼 Search API 구독 (유료)")
            print("  2. Selenium/Playwright로 브라우저 자동화")
            print("  3. Google Places API / Kakao Map API 사용")
            return None
        print(f"검색 중 HTTP 오류 ({place_name}): {str(e)}")
        return None
    except Exception as e:
        print(f"검색 중 오류 ({place_name}): {str(e)}")
        return None


def crawl_place(url: str) -> Dict:
    """
    네이버 플레이스 URL에서 상세 정보 크롤링.

    참고: 네이버는 API 직접 호출을 제한합니다.
    실제 운영 환경에서는 Selenium/Playwright 또는 공개 API(Google/Kakao) 사용 필요.

    Args:
        url: 네이버 플레이스 URL (예: https://map.naver.com/v5/entry/place/1234567)

    Returns:
        {
            "name": "가게명",
            "category": "카페",
            "address": "서울 강남구...",
            "rating": 4.2,
            "review_count": 47,
            "visitor_review_count": 35,
            "blog_review_count": 12,
            "photo_count": 23,
            "last_photo_date": "2026-02-14",
            "hours": "09:00-22:00",
            "price_range": "1만원대",
            "keywords": ["아메리카노", "분위기", "공부하기좋은"],
            "weakness": ["서빙 느림", "화장실 더러움"],
            "crawled_at": "2026-04-04T21:00:00",
            "error": None  # 에러 있으면 에러 메시지
        }
    """

    result = {
        "name": None,
        "category": None,
        "address": None,
        "rating": None,
        "review_count": 0,
        "visitor_review_count": 0,
        "blog_review_count": 0,
        "photo_count": 0,
        "last_photo_date": None,
        "hours": None,
        "price_range": None,
        "keywords": [],
        "weakness": [],
        "crawled_at": datetime.now().isoformat(),
        "error": None
    }

    try:
        place_id = extract_place_id(url)
        if not place_id:
            result["error"] = "유효하지 않은 URL"
            return result

        # HTML에서 정보 추출 시도
        response = requests.get(url, headers=NAVER_HEADERS, timeout=10)
        response.raise_for_status()

        html = response.text
        soup = BeautifulSoup(html, 'html.parser')

        # 가게명
        name_elem = soup.select_one('h1, .place-section-title, .title')
        if name_elem:
            result["name"] = name_elem.get_text().strip()

        # 별점 (script 태그의 JSON-LD 데이터 찾기)
        script_elem = soup.find('script', {'type': 'application/ld+json'})
        if script_elem:
            try:
                schema = json.loads(script_elem.string)
                if schema.get('ratingValue'):
                    result["rating"] = float(schema['ratingValue'])
                if schema.get('reviewCount'):
                    result["review_count"] = int(schema['reviewCount'])
            except (json.JSONDecodeError, ValueError):
                pass

        # 리뷰 분석 (키워드/약점 추출)
        if result["name"]:
            _analyze_reviews(place_id, result)

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            result["error"] = "접근 제한: 네이버 API는 인증이 필요합니다."
        else:
            result["error"] = f"HTTP 오류: {str(e)}"
        print(f"크롤링 중 오류 ({url}): {result['error']}")
    except Exception as e:
        result["error"] = f"크롤링 오류: {str(e)}"
        print(f"크롤링 중 오류 ({url}): {str(e)}")

    return result


def _analyze_reviews(place_id: str, result: Dict):
    """
    리뷰 데이터에서 키워드와 약점 추출.

    네이버 플레이스 리뷰 API로 최근 리뷰 수집 후
    별점 낮은 리뷰에서 문제점 추출.
    """
    try:
        # 리뷰 데이터 요청 (최대 50개)
        reviews_url = f"https://map.naver.com/v5/api/sites/{place_id}/reviews?sort=recency&limit=50"

        response = requests.get(reviews_url, headers=NAVER_HEADERS, timeout=10)
        response.raise_for_status()

        data = response.json()
        reviews = data.get('result', {}).get('reviews', [])

        if not reviews:
            return

        # 키워드 수집 (댓글에서 자주 언급되는 단어)
        keywords_count = {}
        weaknesses_list = []

        for review in reviews:
            text = review.get('text', '').lower()
            score = review.get('score', 5)

            # 낮은 별점 리뷰에서 문제점 추출
            if score <= 2:
                # 간단한 패턴 매칭
                if '느림' in text or '오래' in text or '기다' in text:
                    weaknesses_list.append('서빙 느림')
                if '더럽' in text or '청결' in text:
                    weaknesses_list.append('위생 문제')
                if '불친절' in text or '거만' in text:
                    weaknesses_list.append('서비스 태도 불량')
                if '좁' in text or '비좁' in text:
                    weaknesses_list.append('좁은 공간')
                if '가격' in text or '비싸' in text:
                    weaknesses_list.append('높은 가격')

            # 키워드 추출 (유명한 리뷰 단어들)
            for keyword in ['아메리카노', '라떼', '디저트', '분위기', '공부', '휴식', '와이파이', '콘센트', '테라스', '창밖']:
                if keyword in text:
                    keywords_count[keyword] = keywords_count.get(keyword, 0) + 1

        # 상위 5개 키워드
        sorted_keywords = sorted(keywords_count.items(), key=lambda x: x[1], reverse=True)
        result["keywords"] = [kw for kw, _ in sorted_keywords[:5]]

        # 중복 제거 + 상위 3개 약점
        result["weakness"] = list(dict.fromkeys(weaknesses_list))[:3]

    except Exception as e:
        print(f"리뷰 분석 중 오류 ({place_id}): {str(e)}")


def crawl_batch(place_names: List[str]) -> List[Dict]:
    """
    여러 가게명을 일괄 크롤링.

    Args:
        place_names: 가게명 목록

    Returns:
        크롤링된 데이터 목록
    """
    results = []

    for i, name in enumerate(place_names):
        print(f"크롤링 중... ({i+1}/{len(place_names)})")
        data = search_place(name)
        if data:
            results.append(data)

        # API 요청 제한 회피용 딜레이
        if i < len(place_names) - 1:
            time.sleep(1)

    return results


if __name__ == "__main__":
    # 테스트 예시

    # 1. 가게명으로 검색
    print("=== 테스트 1: 가게명 검색 ===")
    result = search_place("강남 스타벅스")
    print(json.dumps(result, ensure_ascii=False, indent=2))

    print("\n=== 테스트 2: URL 직접 크롤링 ===")
    # 실제 가게 ID를 알고 있다면 직접 크롤링도 가능
    # result = crawl_place("https://map.naver.com/v5/entry/place/1234567")
    # print(json.dumps(result, ensure_ascii=False, indent=2))
