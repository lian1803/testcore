"""
Phase 3 보강: 기존 benchmark_premium DB 84개 row에
- crawl_place_detail로 photo_urls, keywords, review_texts, has_* 등 채우기
- Gemini 2.5 Flash로 concept_tags 분석
"""
import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime
import json

# Windows cp949 회피
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).parent.parent.parent / "team" / "[진행중] 오프라인 마케팅" / "소상공인_영업툴" / "naver-diagnosis"
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
# core/company/.env 중앙 로드
CORE_ROOT = Path(__file__).parent.parent.parent
load_dotenv(CORE_ROOT / "company" / ".env")

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from models import BenchmarkPremium
from services.naver_place_crawler import NaverPlaceCrawler
from services.concept_analyzer import ConceptAnalyzer
from playwright.async_api import async_playwright

DB_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./diagnosis.db")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


async def enrich_place(crawler, place_id: str) -> dict:
    """place_id로 crawl_place_detail 실행 → 필요 필드 딕셔너리 반환"""
    data = await crawler.crawl_place_detail(place_id)
    if not data:
        return None

    # photo_urls가 bytes 형태면 URL만 추출 (V2에서는 URL 형태로 저장됨)
    photo_urls = data.get("photo_urls") or []
    if photo_urls and isinstance(photo_urls[0], bytes):
        # bytes는 저장 불가. URL로 대체해야 하는데 없으니 빈 리스트
        photo_urls = []

    return {
        "photo_count": data.get("photo_count", 0),
        "receipt_review_count": data.get("receipt_review_count", 0),
        "visitor_review_count": data.get("visitor_review_count", 0),
        "blog_review_count": data.get("blog_review_count", 0),
        "bookmark_count": data.get("bookmark_count", 0),
        "keyword_rating_review_count": data.get("keyword_rating_review_count", 0),
        "has_menu": data.get("has_menu", False),
        "has_hours": data.get("has_hours", False),
        "has_price": data.get("has_price", False),
        "has_intro": data.get("has_intro", False),
        "has_directions": data.get("has_directions", False),
        "has_booking": data.get("has_booking", False),
        "has_talktalk": data.get("has_talktalk", False),
        "has_smartcall": data.get("has_smartcall", False),
        "has_coupon": data.get("has_coupon", False),
        "has_news": data.get("has_news", False),
        "has_owner_reply": data.get("has_owner_reply", False),
        "has_instagram": data.get("has_instagram", False),
        "has_kakao": data.get("has_kakao", False),
        "keywords": data.get("keywords") or [],
        "review_text_samples": (data.get("review_texts") or [])[:10],
        "photo_urls": photo_urls[:15],
        "place_url": f"https://m.place.naver.com/place/{place_id}/home",
    }


async def main():
    print(f"[START] Phase 3 보강 작업: {datetime.now()}")

    if not GOOGLE_API_KEY:
        print("[ERROR] GOOGLE_API_KEY 없음")
        return

    engine = create_async_engine(DB_URL, echo=False)
    session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # 기존 place_id 목록 가져오기
    async with session_maker() as session:
        result = await session.execute(select(BenchmarkPremium))
        places = list(result.scalars().all())
        print(f"[LOAD] benchmark_premium {len(places)}개 row")

    # ===== Step 1: crawl_place_detail로 상세 데이터 보강 =====
    print(f"\n{'='*60}\nSTEP 1: 상세 크롤링으로 필드 보강\n{'='*60}")
    enriched_count = 0
    failed_place_ids = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        crawler = NaverPlaceCrawler(browser)

        for idx, place in enumerate(places):
            pid = place.place_id
            print(f"\n[{idx+1}/{len(places)}] {place.place_name} ({pid})")

            # 이미 photo_urls 있으면 skip
            if place.photo_urls and len(place.photo_urls) >= 3:
                print(f"  [SKIP] 이미 보강됨 (photo_urls {len(place.photo_urls)}개)")
                continue

            try:
                enriched = await enrich_place(crawler, pid)
                if not enriched:
                    print(f"  [FAIL] crawl_place_detail 결과 없음")
                    failed_place_ids.append(pid)
                    continue

                # DB 업데이트
                async with session_maker() as session:
                    obj = await session.get(BenchmarkPremium, place.id)
                    if obj:
                        for k, v in enriched.items():
                            setattr(obj, k, v)
                        obj.crawled_at = datetime.utcnow()
                        await session.commit()
                        enriched_count += 1
                        print(f"  [OK] photo={enriched['photo_count']}, "
                              f"review={enriched['visitor_review_count']}+{enriched['receipt_review_count']}, "
                              f"photo_urls={len(enriched['photo_urls'])}")
            except Exception as e:
                print(f"  [FAIL] {str(e)[:100]}")
                failed_place_ids.append(pid)

            await asyncio.sleep(2)  # 봇 회피

        await browser.close()

    print(f"\n[STEP 1 완료] 보강 {enriched_count}개 / 실패 {len(failed_place_ids)}개")

    # ===== Step 2: Gemini 2.5 Flash로 concept_tags 분석 =====
    print(f"\n{'='*60}\nSTEP 2: Gemini Vision 컨셉 분석\n{'='*60}")

    analyzer = ConceptAnalyzer(GOOGLE_API_KEY)
    analyzed_count = 0
    analysis_failed = []

    # 최신 photo_urls 가져와서 분석
    async with session_maker() as session:
        result = await session.execute(select(BenchmarkPremium))
        fresh_places = list(result.scalars().all())

    for idx, place in enumerate(fresh_places):
        photo_urls = place.photo_urls or []
        print(f"\n[{idx+1}/{len(fresh_places)}] {place.place_name}")

        if place.concept_tags:
            print(f"  [SKIP] 이미 분석됨")
            continue
        if not photo_urls or len(photo_urls) < 3:
            print(f"  [SKIP] 사진 부족 ({len(photo_urls)}장)")
            continue

        try:
            tags = await analyzer.analyze_photos(photo_urls[:15])
            if tags:
                async with session_maker() as session:
                    obj = await session.get(BenchmarkPremium, place.id)
                    if obj:
                        obj.concept_tags = tags
                        obj.analyzed_at = datetime.utcnow()
                        await session.commit()
                        analyzed_count += 1
                        print(f"  [OK] {tags}")
            else:
                analysis_failed.append(place.place_id)
                print(f"  [FAIL] tags 없음")
        except Exception as e:
            print(f"  [ERR] {str(e)[:100]}")
            analysis_failed.append(place.place_id)

        await asyncio.sleep(1)

    print(f"\n[STEP 2 완료] 분석 {analyzed_count}개 / 실패 {len(analysis_failed)}개")

    # ===== 최종 리포트 =====
    print(f"\n{'='*60}\n[SUMMARY]\n{'='*60}")
    print(f"총 row: {len(places)}")
    print(f"크롤 보강: {enriched_count}")
    print(f"Gemini 분석: {analyzed_count}")
    print(f"Gemini 호출: {analyzer.total_calls}회, 예상 비용: ${analyzer.get_stats()['estimated_cost']}")
    print(f"크롤 실패 place_id: {failed_place_ids[:10]}")
    print(f"분석 실패 place_id: {analysis_failed[:10]}")
    print(f"종료: {datetime.now()}")

    # 리포트 저장
    report_path = Path(__file__).parent / "2026-04-17_benchmark_enrich_report.md"
    report_path.write_text(
        f"""# Phase 3 보강 리포트

실행 시각: {datetime.now().isoformat()}

## 결과
- 총 row: {len(places)}
- 크롤 보강 성공: {enriched_count} / {len(places)} ({enriched_count/len(places)*100:.1f}%)
- Gemini 분석 성공: {analyzed_count} / {len(fresh_places)} ({analyzed_count/len(fresh_places)*100:.1f}%)
- Gemini 총 비용: ${analyzer.get_stats()['estimated_cost']}

## 실패 리스트
- 크롤 실패: {failed_place_ids}
- 분석 실패: {analysis_failed}
""",
        encoding="utf-8"
    )
    print(f"\n[REPORT] {report_path}")


if __name__ == "__main__":
    asyncio.run(main())
