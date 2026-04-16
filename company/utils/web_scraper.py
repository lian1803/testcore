"""
웹 스크래핑 유틸리티 — 영업팀용 URL 분석

특징:
- requests 기반 경량 구현 (기존 의존성만 사용)
- HTML 정규식 처리로 마크다운 변환
- 타임아웃 30초, 실패 시 빈 문자열 반환 (파이프라인 무중단)
"""

import requests
import re
from urllib.parse import urlparse
from typing import Optional


def extract_text_from_html(html: str) -> str:
    """HTML → 마크다운 텍스트 변환 (정규식 기반)"""
    # 스크립트/스타일 제거
    text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)

    # 제목 추출
    title_match = re.search(r'<title[^>]*>([^<]+)</title>', text, re.IGNORECASE)
    content = []
    if title_match:
        content.append(f"# {title_match.group(1).strip()}")

    # 주요 태그 추출 (h1~h3, p, li)
    h1_matches = re.findall(r'<h1[^>]*>([^<]+)</h1>', text, re.IGNORECASE)
    h2_matches = re.findall(r'<h2[^>]*>([^<]+)</h2>', text, re.IGNORECASE)
    h3_matches = re.findall(r'<h3[^>]*>([^<]+)</h3>', text, re.IGNORECASE)
    p_matches = re.findall(r'<p[^>]*>([^<]+(?:<[^>]+>[^<]*)*[^<]*)</p>', text, re.IGNORECASE)
    li_matches = re.findall(r'<li[^>]*>([^<]+)</li>', text, re.IGNORECASE)

    for match in h1_matches[:3]:
        content.append(f"\n## {match.strip()}")
    for match in h2_matches[:3]:
        content.append(f"\n## {match.strip()}")
    for match in h3_matches[:2]:
        content.append(f"\n### {match.strip()}")
    for match in p_matches[:10]:
        clean = re.sub(r'<[^>]+>', '', match).strip()
        if clean and len(clean) > 10:
            content.append(clean)
    for match in li_matches[:8]:
        clean = re.sub(r'<[^>]+>', '', match).strip()
        if clean:
            content.append(f"- {clean}")

    # 공백 정리
    result = '\n'.join(content)
    result = re.sub(r'\s+', ' ', result)
    return result.strip()


def scrape_url(url: str) -> str:
    """
    URL을 마크다운 텍스트로 스크랩

    Args:
        url: 스크랩할 URL

    Returns:
        마크다운 형식 텍스트 (실패 시 빈 문자열)
    """
    if not url or not isinstance(url, str):
        return ""

    # URL 유효성 검증
    try:
        result = urlparse(url)
        if not result.scheme:
            url = f"https://{url}"
    except Exception:
        return ""

    try:
        response = requests.get(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            },
            timeout=30,
            allow_redirects=True
        )
        response.raise_for_status()

        # HTML → 마크다운
        text = extract_text_from_html(response.text)

        # 기본 포맷팅
        if text:
            return f"## 웹페이지 분석: {url}\n\n{text[:3000]}"  # 3000자 제한
        return ""

    except requests.Timeout:
        return ""
    except requests.HTTPError:
        return ""
    except Exception:
        return ""


def scrape_naver_place(place_url: str) -> Optional[dict]:
    """
    네이버플레이스 URL에서 기본 정보 추출

    Args:
        place_url: 네이버플레이스 URL (예: https://place.naver.com/...)

    Returns:
        {
            "name": "업체명",
            "rating": 4.5,
            "review_count": 42,
            "category": "카페",
            "url": "..."
        }
        또는 None (실패 시)
    """
    if not place_url or 'naver.com' not in place_url:
        return None

    try:
        response = requests.get(
            place_url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            },
            timeout=15,
            allow_redirects=True
        )
        response.raise_for_status()

        html = response.text

        # 기본 정보 추출 (정규식)
        name_match = re.search(r'"title":"([^"]+)"', html)
        rating_match = re.search(r'"ratingScore":(\d+\.?\d*)', html)
        review_match = re.search(r'"reviewCount":(\d+)', html)

        return {
            "name": name_match.group(1) if name_match else "Unknown",
            "rating": float(rating_match.group(1)) if rating_match else None,
            "review_count": int(review_match.group(1)) if review_match else 0,
            "url": place_url,
            "source": "naver_place"
        }

    except Exception:
        return None
