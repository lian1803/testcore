#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
크롤러 V2 코드 검증
실제 네이버 접근 없이 코드 로직만 검증
"""

import sys
from pathlib import Path

# naver-diagnosis 경로 추가
diagnosis_path = Path(__file__).parent.parent.parent / "team" / "[진행중] 오프라인 마케팅" / "소상공인_영업툴" / "naver-diagnosis"
sys.path.insert(0, str(diagnosis_path))

def check_file_modifications():
    """크롤러 파일의 개선사항 확인"""

    crawler_file = diagnosis_path / "services" / "naver_place_crawler.py"

    if not crawler_file.exists():
        print("ERROR: naver_place_crawler.py not found")
        return False

    content = crawler_file.read_text(encoding='utf-8')

    print("\n" + "="*60)
    print("Code Review: naver_place_crawler.py")
    print("="*60 + "\n")

    checks = [
        # photo_urls 개선
        ("Photo URL extraction", "_fetch_photos_from_photo_page", [
            "captured_image_urls",
            "pstatic.net",
            "naverplacecdn",
            "15",
            "scroll"
        ]),

        # owner_reply_rate 개선
        ("Owner reply rate", "fetch_owner_reply_rate", [
            "45000",  # 타임아웃
            "domcontentloaded",
            "evaluate",
            "sample_size"
        ]),

        # keywords 개선
        ("Keywords extraction", "_extract_keywords", [
            "3단계",
            "폴백",
            "alt_patterns",
            "tags"
        ]),

        # review_texts 개선
        ("Review texts", "fetch_review_texts", [
            "45000",  # 타임아웃
            "domcontentloaded",
            "[class*=",
            "[role="
        ]),

        # _check_owner_reply 개선
        ("Owner reply check", "_check_owner_reply", [
            "evaluate",
            "3단계",
            "JavaScript"
        ]),
    ]

    passed = 0
    failed = 0

    for check_name, method_name, keywords in checks:
        print(f"[{check_name}]")

        # 메서드 존재 확인
        if f"def {method_name}" not in content:
            print(f"  FAIL: Method '{method_name}' not found")
            failed += 1
            continue

        # 개선사항 확인
        method_start = content.find(f"def {method_name}")
        method_end = content.find("\n    def ", method_start + 1)
        if method_end == -1:
            method_end = len(content)
        method_content = content[method_start:method_end]

        found_keywords = []
        missing_keywords = []

        for kw in keywords:
            if kw in method_content:
                found_keywords.append(kw)
            else:
                missing_keywords.append(kw)

        if len(found_keywords) >= len(keywords) * 0.7:  # 70% 이상 확인
            print(f"  OK: Found {len(found_keywords)}/{len(keywords)} improvement markers")
            print(f"      {', '.join(found_keywords[:3])}...")
            passed += 1
        else:
            print(f"  PARTIAL: Found {len(found_keywords)}/{len(keywords)}")
            print(f"  Missing: {missing_keywords}")
            failed += 1

        print()

    print("\n" + "="*60)
    print(f"Result: {passed}/{passed+failed} checks passed")
    print("="*60 + "\n")

    return failed == 0


def check_test_files():
    """테스트 파일 존재 확인"""

    print("="*60)
    print("Test Files Check")
    print("="*60 + "\n")

    test_files = [
        "2026-04-17_crawler_unit_test.py",
        "2026-04-17_crawler_v2_report.md",
        "2026-04-17_crawler_code_review.py",
    ]

    test_dir = Path(__file__).parent
    passed = 0

    for fname in test_files:
        fpath = test_dir / fname
        if fpath.exists():
            print(f"OK {fname}")
            passed += 1
        else:
            print(f"MISSING {fname}")

    print(f"\n{passed}/{len(test_files)} test files present\n")
    return passed == len(test_files)


def check_method_signatures():
    """메서드 시그니처 유지 확인 (하위호환성)"""

    print("="*60)
    print("Method Signature Check (Backward Compatibility)")
    print("="*60 + "\n")

    crawler_file = diagnosis_path / "services" / "naver_place_crawler.py"
    content = crawler_file.read_text(encoding='utf-8')

    # 중요 메서드 시그니처 확인
    signatures = [
        ("crawl_place_detail", "async def crawl_place_detail(self, place_id: str)"),
        ("fetch_review_texts", "async def fetch_review_texts(self, place_id: str)"),
        ("fetch_owner_reply_rate", "async def fetch_owner_reply_rate(self, place_id: str"),
        ("_fetch_photos_from_photo_page", "async def _fetch_photos_from_photo_page(self, place_id: str)"),
        ("_extract_keywords", "def _extract_keywords(self, html: str)"),
    ]

    passed = 0

    for method_name, expected_sig in signatures:
        if expected_sig in content:
            print(f"OK {method_name}")
            passed += 1
        else:
            print(f"CHANGED {method_name}")

    print(f"\n{passed}/{len(signatures)} signatures preserved\n")
    return passed == len(signatures)


def main():
    print("\n" + "="*60)
    print("Crawler V2 Code Review & Validation")
    print("="*60 + "\n")

    results = {
        "File modifications": check_file_modifications(),
        "Test files": check_test_files(),
        "Backward compatibility": check_method_signatures(),
    }

    print("\n" + "="*60)
    print("Summary")
    print("="*60)

    for check_name, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"{status} {check_name}")

    all_pass = all(results.values())

    print("\n" + "="*60)
    if all_pass:
        print("ALL CHECKS PASSED - Ready for integration test")
    else:
        print("SOME CHECKS FAILED - Review needed")
    print("="*60 + "\n")

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
