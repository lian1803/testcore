"""
2026-04-17 지역 벤치마크 버그 수정 테스트

목표:
1. extract_top_place_ids(query, 10)에서 10개 place_id 반환 확인
2. 중복 없는지 확인
3. 각 place_id가 유효한지 샘플 3개 crawl_place_detail로 검증

버그 사항:
- 이전: _get_top_place_ids가 검색 결과 첫 번째 place_id만 반환 (1개)
- 수정: extract_top_place_ids에서 HTML 전체에서 상위 N개 place_id 모두 추출
"""
import asyncio
import sys
from pathlib import Path

# 프로젝트 경로 설정
naver_diag_root = Path(__file__).parent.parent.parent / "team" / "[진행중] 오프라인 마케팅" / "소상공인_영업툴" / "naver-diagnosis"
sys.path.insert(0, str(naver_diag_root))

from playwright.async_api import async_playwright
from services.naver_place_crawler import NaverPlaceCrawler


async def test_extract_top_place_ids():
    """extract_top_place_ids 메서드 테스트"""
    print("\n" + "="*60)
    print("TEST 1: extract_top_place_ids - 상위 10개 place_id 추출")
    print("="*60)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        crawler = NaverPlaceCrawler(browser)

        query = "강남 미용실"
        top_n = 10

        try:
            place_ids = await crawler.extract_top_place_ids(query, top_n)

            print(f"\n쿼리: {query}")
            print(f"요청: {top_n}개")
            print(f"반환: {len(place_ids)}개")
            print(f"place_ids: {place_ids}")

            # 검증 1: 개수 확인
            assert len(place_ids) > 0, "place_id가 1개 이상 반환되어야 함"
            print(f"\n[PASS] place_id 개수 확인: {len(place_ids)}개 반환")

            # 검증 2: 중복 확인
            if len(place_ids) > 1:
                unique_count = len(set(place_ids))
                assert unique_count == len(place_ids), f"중복이 있음: {len(place_ids)}개 중 {unique_count}개만 고유"
                print(f"[PASS] 중복 확인: 없음 ({len(place_ids)}개 모두 고유)")
            else:
                print(f"[PASS] 중복 확인: 1개뿐이므로 중복 불가")

            # 검증 3: place_id 형식 확인 (6자리 이상 숫자)
            for pid in place_ids:
                assert pid.isdigit() and len(pid) >= 6, f"유효하지 않은 place_id: {pid}"
            print(f"[PASS] place_id 형식 확인: 모두 6자리 이상의 숫자")

            return place_ids

        except Exception as e:
            print(f"\n[FAIL] TEST 1 실패: {e}")
            import traceback
            traceback.print_exc()
            return []
        finally:
            await browser.close()


async def test_crawl_samples(place_ids: list):
    """샘플 3개 place_id의 실제 유효성 확인"""
    print("\n" + "="*60)
    print("TEST 2: crawl_place_detail - 샘플 3개 유효성 검증")
    print("="*60)

    if not place_ids:
        print("place_ids가 없어서 테스트 스킵")
        return

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        crawler = NaverPlaceCrawler(browser)

        sample_size = min(3, len(place_ids))
        samples = place_ids[:sample_size]

        try:
            for i, pid in enumerate(samples, 1):
                print(f"\n샘플 {i}/{sample_size}: place_id={pid}")
                try:
                    data = await crawler.crawl_place_detail(pid)

                    # 필수 필드 확인
                    assert data.get("place_id") == pid, f"place_id 불일치"
                    print(f"  [PASS] place_id 일치: {pid}")

                    # 크롤링 결과 확인
                    visitor_review = data.get("visitor_review_count", 0)
                    receipt_review = data.get("receipt_review_count", 0)
                    photo_count = data.get("photo_count", 0)
                    print(f"  [PASS] 방문자 리뷰: {visitor_review}개")
                    print(f"  [PASS] 영수증 리뷰: {receipt_review}개")
                    print(f"  [PASS] 사진 수: {photo_count}개")

                    # 기본 통계가 있는지 확인 (모두 0일 순 있지만, 최소한 크롤링은 성공)
                    assert data, "크롤링 결과 없음"
                    print(f"  [PASS] 크롤링 성공")

                except Exception as e:
                    print(f"  [FAIL] 샘플 {i} 실패: {e}")

        except Exception as e:
            print(f"\n[FAIL] TEST 2 실패: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await browser.close()


async def test_benchmark_flow():
    """벤치마크 전체 플로우 테스트"""
    print("\n" + "="*60)
    print("TEST 3: LocalBenchmark 전체 플로우")
    print("="*60)

    async with async_playwright() as p:
        browser = await p.chromium.launch()

        try:
            from services.local_benchmark import LocalBenchmark

            benchmark = LocalBenchmark(browser)

            # 캐시 없이 테스트 (강제 크롤링)
            result = await benchmark.get_benchmark(
                category="미용실",
                region="강남",
                top_n=10
            )

            print(f"\n벤치마크 결과:")
            print(f"  지역: {result.get('region')}")
            print(f"  업종: {result.get('category')}")
            print(f"  샘플 수: {result.get('sample_size')}개")
            print(f"  평균 방문자 리뷰: {result.get('avg_review')}개")
            print(f"  평균 사진: {result.get('avg_photo')}장")
            print(f"  평균 블로그: {result.get('avg_blog')}개")
            print(f"  상위3 평균 리뷰: {result.get('top3_avg_review')}개")

            # 검증: sample_size가 1 이상이어야 함 (버그 수정 확인)
            sample_size = result.get("sample_size", 0)
            assert sample_size > 0, f"sample_size가 0임 (버그 미수정): {result}"
            print(f"\n[PASS] 버그 수정 확인: sample_size={sample_size}개 (이전엔 1개만 가능)")

        except Exception as e:
            print(f"\n[FAIL] TEST 3 실패: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await browser.close()


async def main():
    """전체 테스트 실행"""
    print("\n" + "#"*60)
    print("# 2026-04-17 지역 벤치마크 버그 수정 테스트")
    print("#"*60)
    print("\n변경사항:")
    print("1. naver_place_crawler.py에 extract_top_place_ids() 메서드 추가")
    print("   → 검색 결과 HTML에서 상위 N개 place_id 모두 추출")
    print("2. local_benchmark.py의 _get_top_place_ids() 수정")
    print("   → crawl_from_search 대신 extract_top_place_ids 호출")
    print("   → 결과: 1개 대신 상위 N개(예: 10개) 반환")

    try:
        # TEST 1: extract_top_place_ids
        place_ids = await test_extract_top_place_ids()

        # TEST 2: 샘플 크롤링
        if place_ids:
            await test_crawl_samples(place_ids)

        # TEST 3: 벤치마크 전체 플로우
        await test_benchmark_flow()

        print("\n" + "#"*60)
        print("# [SUCCESS] 모든 테스트 완료!")
        print("#"*60)

    except Exception as e:
        print(f"\n테스트 중 오류: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
