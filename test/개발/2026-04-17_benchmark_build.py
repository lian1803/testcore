#!/usr/bin/env python3
"""
Phase 3: 벤치마크 프리미엄 DB 구축 파이프라인
- Step 1: 쿼리 생성 및 크롤링
- Step 2: Gemini Vision 분석 (선택)
- Step 3: DB 저장 완료
"""
import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime
import json

# Windows cp949 인코딩 회피
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# 경로 설정
PROJECT_ROOT = Path(__file__).parent.parent.parent / "team" / "[진행중] 오프라인 마케팅" / "소상공인_영업툴" / "naver-diagnosis"
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
from services.benchmark_builder import BenchmarkBuilder
from services.concept_analyzer import ConceptAnalyzer
from database import init_db
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from models import BenchmarkPremium

load_dotenv(PROJECT_ROOT / ".env")

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
DB_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./naver_diagnosis.db")


async def get_places_needing_analysis(db_url: str) -> list:
    """분석이 필요한 업체 (concept_tags가 null인 것)"""
    engine = create_async_engine(db_url, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        result = await session.execute(
            select(BenchmarkPremium).where(BenchmarkPremium.concept_tags == None)
        )
        places = result.scalars().all()
        places_data = [{
            "place_id": p.place_id,
            "photo_urls": p.photo_urls,
            "db_id": p.id
        } for p in places]

    await engine.dispose()
    return places_data


async def save_concept_tags(db_url: str, place_id: str, concept_tags: dict):
    """분석 결과를 DB에 저장"""
    engine = create_async_engine(db_url, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        result = await session.execute(
            select(BenchmarkPremium).where(BenchmarkPremium.place_id == place_id)
        )
        place = result.scalars().first()
        if place:
            place.concept_tags = concept_tags
            place.analyzed_at = datetime.utcnow()
            await session.commit()

    await engine.dispose()


async def step1_crawl(test_mode: bool = False):
    """Step 1: 크롤링"""
    print("\n" + "="*70)
    print("STEP 1: 크롤링 (업종 × 지역 매트릭스)")
    print("="*70)

    builder = BenchmarkBuilder(DB_URL)

    try:
        queries = await builder.generate_queries()
        print(f"쿼리 생성: {len(queries)}개 (10개 업종 × 7개 지역)")

        result = await builder.crawl_and_save(queries, display=10, test_mode=test_mode)

        return result

    finally:
        await builder.close()


async def step2_analyze(skip_analysis: bool = False):
    """Step 2: Gemini Vision 분석 (선택)"""
    if skip_analysis or not GOOGLE_API_KEY:
        print("\n[SKIP] Step 2 분석 스킵 (API 키 없음 또는 --skip-analysis 옵션)")
        return {"skipped": True}

    print("\n" + "="*70)
    print("STEP 2: Gemini Vision 분석 (사진 10~20장)")
    print("="*70)

    analyzer = ConceptAnalyzer(GOOGLE_API_KEY)

    try:
        # 분석이 필요한 업체 조회
        places = await get_places_needing_analysis(DB_URL)
        print(f"분석 대상: {len(places)}개 업체")

        if not places:
            print("분석할 업체가 없습니다.")
            return {"analyzed": 0, "total": 0}

        # 일괄 분석
        results = await analyzer.batch_analyze(places)

        # 결과 저장
        analyzed_count = 0
        for result in results:
            if result["concept_tags"]:
                await save_concept_tags(DB_URL, result["place_id"], result["concept_tags"])
                analyzed_count += 1

        stats = analyzer.get_stats()
        print(f"\n분석 완료: {analyzed_count}/{len(places)}개")
        print(f"예상 비용: ${stats['estimated_cost']:.4f}")

        return {
            "analyzed": analyzed_count,
            "total": len(places),
            "cost": stats['estimated_cost']
        }

    except Exception as e:
        print(f"분석 오류: {str(e)}")
        return {"error": str(e)}


async def get_summary():
    """DB 요약 통계"""
    engine = create_async_engine(DB_URL, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # 전체 개수
        result = await session.execute(select(BenchmarkPremium))
        total = len(result.scalars().all())

        # 카테고리별 개수
        result = await session.execute(select(BenchmarkPremium.category).distinct())
        categories = [row[0] for row in result.fetchall()]

        # 지역별 개수
        result = await session.execute(select(BenchmarkPremium.region).distinct())
        regions = [row[0] for row in result.fetchall()]

        # 분석 완료 개수
        result = await session.execute(
            select(BenchmarkPremium).where(BenchmarkPremium.concept_tags != None)
        )
        analyzed = len(result.scalars().all())

    await engine.dispose()

    return {
        "total": total,
        "categories": len(categories),
        "regions": len(regions),
        "analyzed": analyzed
    }


async def main():
    """메인 실행"""
    import argparse

    parser = argparse.ArgumentParser(description="Phase 3: 벤치마크 DB 구축")
    parser.add_argument("--test", action="store_true", help="테스트 모드 (1개 쿼리)")
    parser.add_argument("--full", action="store_true", help="전체 실행 (크롤링 + 분석)")
    parser.add_argument("--crawl-only", action="store_true", help="크롤링만 (분석 스킵)")
    parser.add_argument("--analyze-only", action="store_true", help="분석만 (크롤링 스킵)")
    parser.add_argument("--skip-analysis", action="store_true", help="Gemini 분석 스킵")
    args = parser.parse_args()

    test_mode = args.test
    skip_analysis = args.skip_analysis or args.crawl_only

    if not (args.test or args.full or args.crawl_only or args.analyze_only):
        print("사용법:")
        print("  python 2026-04-17_benchmark_build.py --test          (테스트 모드)")
        print("  python 2026-04-17_benchmark_build.py --full          (전체 실행)")
        print("  python 2026-04-17_benchmark_build.py --crawl-only    (크롤링만)")
        print("  python 2026-04-17_benchmark_build.py --analyze-only  (분석만)")
        return

    print("[START] Phase 3: 벤치마크 프리미엄 DB 구축")
    print(f"시작: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # DB 테이블 초기화
    print("[DB] 테이블 초기화 중...")
    await init_db(drop_existing=False)

    start_time = datetime.now()

    try:
        # Step 1: 크롤링
        if not args.analyze_only:
            crawl_result = await step1_crawl(test_mode=test_mode)
            print(f"\n크롤링 결과:")
            print(f"  수집: {crawl_result['total_places']}개")
            print(f"  저장: {crawl_result['saved_places']}개")
            print(f"  실패: {len(crawl_result['failed_queries'])}개")
        else:
            print("[SKIP] Step 1 크롤링 스킵 (--analyze-only)")

        # Step 2: 분석
        if not args.crawl_only:
            analysis_result = await step2_analyze(skip_analysis=skip_analysis)
            if "skipped" not in analysis_result:
                print(f"\n분석 결과:")
                if "error" not in analysis_result:
                    print(f"  분석: {analysis_result['analyzed']}/{analysis_result['total']}개")
                    print(f"  비용: ${analysis_result.get('cost', 0):.4f}")

        # 요약
        summary = await get_summary()
        print("\n" + "="*70)
        print("SUMMARY: DB 현황")
        print("="*70)
        print(f"총 업체: {summary['total']}개")
        print(f"  카테고리: {summary['categories']}개")
        print(f"  지역: {summary['regions']}개")
        print(f"  분석 완료: {summary['analyzed']}개 ({100*summary['analyzed']//max(1, summary['total'])}%)")

        elapsed = (datetime.now() - start_time).total_seconds()
        print(f"\n소요 시간: {int(elapsed//60)}분 {int(elapsed%60)}초")
        print(f"종료: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    except KeyboardInterrupt:
        print("\n[INTERRUPT] 사용자 중단")
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Windows에서 asyncio 이벤트 루프 정책 설정
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(main())
