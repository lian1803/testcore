#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
크롤러 개선사항 단위 테스트
각 메서드의 논리 검증 (실제 네이버 접근 X)
"""

import re
import sys
import os
from pathlib import Path

# UTF-8 인코딩 강제
os.environ['PYTHONIOENCODING'] = 'utf-8'
if sys.stdout.encoding and 'utf' not in sys.stdout.encoding.lower():
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# naver-diagnosis 경로 추가
diagnosis_path = Path(__file__).parent.parent.parent / "team" / "[진행중] 오프라인 마케팅" / "소상공인_영업툴" / "naver-diagnosis"
sys.path.insert(0, str(diagnosis_path))

# Mock NaverPlaceCrawler로 메서드만 테스트
class MockCrawler:
    """메서드 로직 테스트용 Mock"""

    def _extract_keywords(self, html: str):
        """
        HTML에서 keywordList 추출 (개선버전 로직)
        """
        try:
            # 1단계: keywordList 패턴 찾기
            pattern = r'"keywordList"\s*:\s*\[([^\]]+)\]'
            match = re.search(pattern, html)
            if match:
                keyword_json = '[' + match.group(1) + ']'
                import json
                keywords = json.loads(keyword_json)
                if isinstance(keywords, list):
                    result = [kw for kw in keywords if isinstance(kw, str)][:10]
                    if result:
                        return result
        except Exception as e:
            pass

        # 2단계: 정규식 폴백
        try:
            pattern = r'"keywordList"\s*:\s*\[(.*?)\]'
            match = re.search(pattern, html)
            if match:
                keywords = re.findall(r'"((?:[^"\\]|\\.)*)"', match.group(1))
                import codecs
                decoded_keywords = []
                for kw in keywords[:10]:
                    try:
                        decoded = codecs.decode(kw, 'unicode_escape')
                        decoded_keywords.append(decoded)
                    except:
                        decoded_keywords.append(kw)
                if decoded_keywords:
                    return decoded_keywords
        except:
            pass

        # 3단계: 대체 필드
        try:
            alt_patterns = [
                r'"tags"\s*:\s*\[(.*?)\]',
                r'"categories"\s*:\s*\[(.*?)\]',
            ]
            for pattern in alt_patterns:
                match = re.search(pattern, html)
                if match:
                    keywords = re.findall(r'"((?:[^"\\]|\\.)*)"', match.group(1))
                    if keywords:
                        return keywords[:10]
        except:
            pass

        return []

    def _extract_photo_urls_from_html(self, html: str):
        """
        HTML에서 이미지 URL 추출 (개선버전)
        """
        # 더 정확한 정규식: src="url" 또는 src='url' 모두 지원
        img_urls = re.findall(
            r'src=["\']([^"\']*(?:pstatic\.net|naverplacecdn)[^"\']*)["\']',
            html
        )
        if not img_urls:
            # 폴백: unquoted URL
            img_urls = re.findall(
                r'src=([^\s>]*(?:pstatic\.net|naverplacecdn)[^\s>]*)',
                html
            )
        # 중복 제거하고 최대 15개
        unique_urls = []
        for url in img_urls:
            url = url.strip()
            if url and url.startswith('http') and url not in unique_urls and len(unique_urls) < 15:
                unique_urls.append(url)
        return unique_urls


def test_keywords_extraction():
    """키워드 추출 3단계 폴백 테스트"""
    print("\n[TEST 1] Keywords - 3-level fallback")
    print("=" * 60)

    crawler = MockCrawler()

    # Test Case 1: 정상 JSON 형식
    html1 = '''"keywordList":["카페","커피","스페셜티"]'''
    result1 = crawler._extract_keywords(html1)
    print(f"OK Case 1 (normal JSON): {result1}")
    assert len(result1) == 3, f"Expected 3, got {len(result1)}"

    # Test Case 2: unicode escape
    html2 = r'''"keywordList":["cafe","specialty"]'''
    result2 = crawler._extract_keywords(html2)
    print(f"OK Case 2 (unicode): {len(result2)} items")
    assert len(result2) > 0, "Should extract at least 1 keyword"

    # Test Case 3: fallback field (tags)
    html3 = '''"tags":["cafe","good"]'''
    result3 = crawler._extract_keywords(html3)
    print(f"OK Case 3 (tags fallback): {result3}")
    assert len(result3) > 0, "Should fallback to tags"

    # Test Case 4: empty result
    html4 = '''<html></html>'''
    result4 = crawler._extract_keywords(html4)
    print(f"OK Case 4 (none): {result4}")
    assert result4 == [], "Should return empty list"

    print("PASS Keywords extraction\n")


def test_photo_url_extraction():
    """이미지 URL 추출 테스트"""
    print("\n[TEST 2] Photo URL extraction")
    print("=" * 60)

    crawler = MockCrawler()

    # Test Case 1: normal pstatic.net URL
    html1 = '''<img src="https://pstatic.net/image/123/abc.jpg" />'''
    result1 = crawler._extract_photo_urls_from_html(html1)
    print(f"OK Case 1 (pstatic.net): {len(result1)} items")
    assert len(result1) == 1, "Should extract 1 URL"
    assert "pstatic.net" in result1[0], "URL should contain pstatic.net"

    # Test Case 2: naverplacecdn URL
    html2 = '''<img src="https://naverplacecdn.com/image/456.jpg" />'''
    result2 = crawler._extract_photo_urls_from_html(html2)
    print(f"OK Case 2 (naverplacecdn): {len(result2)} items")
    assert len(result2) == 1, "Should extract 1 URL"

    # Test Case 3: multiple images
    html3 = '''
    <img src="https://pstatic.net/img1.jpg" />
    <img src="https://pstatic.net/img2.jpg" />
    <img src="https://pstatic.net/img3.jpg" />
    '''
    result3 = crawler._extract_photo_urls_from_html(html3)
    print(f"OK Case 3 (3 images): {len(result3)} items")
    assert len(result3) == 3, "Should extract 3 URLs"

    # Test Case 4: deduplication
    html4 = '''
    <img src="https://pstatic.net/img.jpg" />
    <img src="https://pstatic.net/img.jpg" />
    '''
    result4 = crawler._extract_photo_urls_from_html(html4)
    print(f"OK Case 4 (dedup): {len(result4)} items (duplicates removed)")
    assert len(result4) == 1, "Should deduplicate"

    # Test Case 5: max 15 limit
    html5 = "\n".join([f'<img src="https://pstatic.net/img{i}.jpg" />' for i in range(20)])
    result5 = crawler._extract_photo_urls_from_html(html5)
    print(f"OK Case 5 (20->15 limit): {len(result5)} items")
    assert len(result5) == 15, "Should limit to 15 URLs"

    print("PASS Photo URL extraction\n")


def test_regex_patterns():
    """정규식 패턴 검증"""
    print("\n[TEST 3] Regex pattern validation")
    print("=" * 60)

    # Image URL regex (실제 크롤러에서 사용하는 것과 동일)
    pattern = r'src=["\']([^"\']*(?:pstatic\.net|naverplacecdn)[^"\']*)["\']'

    test_cases = [
        ('src="https://pstatic.net/a.jpg"', True, "quoted double"),
        ("src='https://pstatic.net/b.jpg'", True, "quoted single"),
        ('src="https://naverplacecdn.com/d.jpg"', True, "naverplacecdn"),
        ('href="https://example.com"', False, "wrong domain"),
    ]

    for html, should_match, desc in test_cases:
        match = re.search(pattern, html)
        status = "OK" if (match is not None) == should_match else "FAIL"
        print(f"{status} {desc}: {html[:50]}")
        assert (match is not None) == should_match, f"Failed: {desc}"

    print("PASS Regex patterns\n")


def main():
    print("\n" + "=" * 60)
    print("Crawler V2 Improvements - Unit Tests")
    print("=" * 60)

    try:
        test_keywords_extraction()
        test_photo_url_extraction()
        test_regex_patterns()

        print("\n" + "=" * 60)
        print("ALL TESTS PASSED!")
        print("=" * 60 + "\n")

    except AssertionError as e:
        print(f"\nTEST FAILED: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\nUNEXPECTED ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
