"""
Phase 5: INDUSTRY_WEIGHTS 실증 검증
benchmark_premium 82개 데이터로 현재 가중치가 실제와 맞는지 확인

방법:
- 각 카테고리별 top 33% vs bottom 33% 비교
- 각 지표(photo/review/blog/has_booking 등)의 분리력(effect size) 계산
- 현재 가중치와 실제 분리력 비교 → 조정 권고
"""
import asyncio, sys, os
from pathlib import Path
from statistics import mean, stdev, median

sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).parent.parent.parent / "team" / "[진행중] 오프라인 마케팅" / "소상공인_영업툴" / "naver-diagnosis"
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent.parent / "company" / ".env")

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from models import BenchmarkPremium

DB_URL = os.getenv("DATABASE_URL", f"sqlite+aiosqlite:///{PROJECT_ROOT}/diagnosis.db")


def cohen_d(a: list, b: list) -> float:
    """Cohen's d: 두 그룹의 표준화된 평균 차이 (분리력 지표)"""
    if len(a) < 2 or len(b) < 2:
        return 0.0
    pooled = ((len(a)-1)*stdev(a)**2 + (len(b)-1)*stdev(b)**2) / (len(a)+len(b)-2)
    if pooled <= 0:
        return 0.0
    return (mean(a) - mean(b)) / pooled**0.5


def adoption_diff(top_rows, bot_rows, field: str) -> float:
    """boolean 필드의 top/bot 채택률 차이"""
    top_rate = mean([1 if getattr(r, field) else 0 for r in top_rows]) if top_rows else 0
    bot_rate = mean([1 if getattr(r, field) else 0 for r in bot_rows]) if bot_rows else 0
    return top_rate - bot_rate


async def main():
    engine = create_async_engine(DB_URL, echo=False)
    sm = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with sm() as s:
        r = await s.execute(select(BenchmarkPremium))
        all_rows = list(r.scalars().all())

    print(f"총 {len(all_rows)}개 로드\n")

    # 카테고리 매핑 (industry_weights.py 기준)
    CATEGORY_MAP = {
        "미용실": ["미용실"],
        "피부관리": ["피부관리"],
        "카페": ["카페", "베이커리"],
        "식당": ["고깃집", "이태리안"],
        "네일": ["네일"],
    }

    CURRENT_WEIGHTS = {
        "미용실":  {"photo": 0.25, "review": 0.15, "blog": 0.10, "engagement": 0.20},
        "피부관리": {"photo": 0.22, "review": 0.18, "blog": 0.12, "engagement": 0.18},
        "카페":    {"photo": 0.15, "review": 0.28, "blog": 0.15, "engagement": 0.14},
        "식당":    {"photo": 0.12, "review": 0.30, "blog": 0.10, "engagement": 0.14},
        "네일":    {"photo": 0.25, "review": 0.15, "blog": 0.08, "engagement": 0.22},
    }

    results = {}

    for industry, cats in CATEGORY_MAP.items():
        rows = [r for r in all_rows if r.category in cats]
        if len(rows) < 6:
            print(f"[{industry}] 샘플 부족 ({len(rows)}개) — 스킵")
            continue

        # 성공 지표: visitor_review + receipt_review 합계
        for r in rows:
            r._total_review = (r.visitor_review_count or 0) + (r.receipt_review_count or 0)

        rows_sorted = sorted(rows, key=lambda x: x._total_review, reverse=True)
        cut = max(2, len(rows_sorted) // 3)
        top = rows_sorted[:cut]
        bot = rows_sorted[-cut:]

        print(f"{'='*60}")
        print(f"[{industry}] n={len(rows)}, top={len(top)}, bot={len(bot)}")
        print(f"  top 리뷰 중앙값: {median([r._total_review for r in top]):,.0f}")
        print(f"  bot 리뷰 중앙값: {median([r._total_review for r in bot]):,.0f}")

        # 연속형 지표 분리력
        metrics = {
            "photo":  [r.photo_count or 0 for r in rows],
        }
        top_photo  = [r.photo_count or 0 for r in top]
        bot_photo  = [r.photo_count or 0 for r in bot]
        top_review = [r._total_review for r in top]
        bot_review = [r._total_review for r in bot]
        top_blog   = [r.blog_review_count or 0 for r in top]
        bot_blog   = [r.blog_review_count or 0 for r in bot]
        top_bmark  = [r.bookmark_count or 0 for r in top]
        bot_bmark  = [r.bookmark_count or 0 for r in bot]

        d_photo  = cohen_d(top_photo, bot_photo)
        d_review = cohen_d(top_review, bot_review)
        d_blog   = cohen_d(top_blog, bot_blog)
        d_bmark  = cohen_d(top_bmark, bot_bmark)

        # boolean 채택률 차이
        bool_fields = [
            "has_booking", "has_talktalk", "has_instagram",
            "has_menu", "has_price", "has_owner_reply", "has_coupon"
        ]
        bool_diffs = {f: adoption_diff(top, bot, f) for f in bool_fields}

        # engagement 합산 (has_booking + has_talktalk + has_instagram + has_owner_reply)
        engage_fields = ["has_booking", "has_talktalk", "has_instagram", "has_owner_reply"]
        top_engage = [sum(1 if getattr(r, f) else 0 for f in engage_fields) for r in top]
        bot_engage = [sum(1 if getattr(r, f) else 0 for f in engage_fields) for r in bot]
        d_engage = cohen_d(top_engage, bot_engage)

        print(f"\n  분리력 (Cohen's d) — 높을수록 top/bot 잘 구분:")
        print(f"    photo    : {d_photo:+.2f}  (현재 가중치: {CURRENT_WEIGHTS[industry]['photo']:.2f})")
        print(f"    review   : {d_review:+.2f}  (현재 가중치: {CURRENT_WEIGHTS[industry]['review']:.2f})")
        print(f"    blog     : {d_blog:+.2f}  (현재 가중치: {CURRENT_WEIGHTS[industry]['blog']:.2f})")
        print(f"    bookmark : {d_bmark:+.2f}")
        print(f"    engagement: {d_engage:+.2f}  (현재 가중치: {CURRENT_WEIGHTS[industry]['engagement']:.2f})")

        print(f"\n  boolean 채택률 차이 (top - bot):")
        for f, diff in sorted(bool_diffs.items(), key=lambda x: -abs(x[1])):
            bar = "▲" if diff > 0.1 else ("▼" if diff < -0.1 else " ")
            print(f"    {bar} {f:<20}: {diff:+.2f}  (top={mean([1 if getattr(r,f) else 0 for r in top]):.0%}, bot={mean([1 if getattr(r,f) else 0 for r in bot]):.0%})")

        # 권고 가중치 (d 값 기반 비례 배분, 4개 항목 합계 0.70 기준)
        raw = {"photo": max(0, d_photo), "review": max(0, d_review),
               "blog": max(0, d_blog), "engagement": max(0, d_engage)}
        total_d = sum(raw.values()) or 1
        TARGET_SUM = 0.70
        recommended = {k: round(v / total_d * TARGET_SUM, 2) for k, v in raw.items()}

        print(f"\n  권고 가중치 (d 비례, 합계≈0.70):")
        cw = CURRENT_WEIGHTS[industry]
        for k in ["photo", "review", "blog", "engagement"]:
            cur = cw[k]
            rec = recommended[k]
            delta = rec - cur
            flag = " ◀ 조정 권고" if abs(delta) >= 0.05 else ""
            print(f"    {k:<12}: 현재 {cur:.2f} → 권고 {rec:.2f} ({delta:+.2f}){flag}")

        results[industry] = {
            "n": len(rows),
            "d": {"photo": d_photo, "review": d_review, "blog": d_blog, "engagement": d_engage},
            "recommended": recommended,
            "current": cw,
        }

    # 최종 요약
    print(f"\n{'='*60}")
    print("최종 요약 — 조정 권고 항목만:")
    for ind, res in results.items():
        for k in ["photo", "review", "blog", "engagement"]:
            delta = res["recommended"][k] - res["current"][k]
            if abs(delta) >= 0.05:
                print(f"  {ind} {k}: {res['current'][k]:.2f} → {res['recommended'][k]:.2f} ({delta:+.2f})")

    print("\n완료.")


if __name__ == "__main__":
    asyncio.run(main())
