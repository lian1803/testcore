#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
벤치마크 통계를 SQL로 직접 계산 (한글 인코딩 우회)
"""
import sqlite3
import json
from collections import defaultdict
from statistics import quantiles, mean

DB_PATH = "C:/Users/lian1/Documents/Work/core/team/[진행중] 오프라인 마케팅/소상공인_영업툴/naver-diagnosis/diagnosis.db"

conn = sqlite3.connect(DB_PATH)
conn.text_factory = lambda b: b.decode('utf-8', errors='replace')
cur = conn.cursor()

# 카테고리별 데이터 수집
cur.execute("SELECT DISTINCT category FROM benchmark_premium ORDER BY category")
categories = [row[0] for row in cur.fetchall()]

print(f"\n========== Benchmark Premium Statistics ==========\n")

# 각 카테고리별 통계
stats_by_category = {}

for category in categories:
    # 해당 카테고리의 모든 레코드 조회
    cur.execute("""
    SELECT
        photo_count,
        visitor_review_count + receipt_review_count AS total_review,
        blog_review_count,
        has_booking,
        has_instagram,
        has_owner_reply,
        has_coupon,
        has_talktalk,
        has_news
    FROM benchmark_premium
    WHERE category = ?
    """, (category,))

    records = cur.fetchall()
    count = len(records)

    if count == 0:
        continue

    # 데이터 추출
    photos = [r[0] for r in records]
    total_reviews = [r[1] for r in records]
    blogs = [r[2] for r in records]

    # Boolean 필드
    has_booking = sum(1 for r in records if r[3]) / count
    has_instagram = sum(1 for r in records if r[4]) / count
    has_owner_reply = sum(1 for r in records if r[5]) / count
    has_coupon = sum(1 for r in records if r[6]) / count
    has_talktalk = sum(1 for r in records if r[7]) / count
    has_news = sum(1 for r in records if r[8]) / count

    def calc_percentiles(data):
        if not data:
            return {"p10": 0, "p25": 0, "p50": 0, "p75": 0, "p90": 0, "mean": 0}
        if len(data) == 1:
            return {
                "p10": data[0],
                "p25": data[0],
                "p50": data[0],
                "p75": data[0],
                "p90": data[0],
                "mean": data[0],
            }

        q10 = quantiles(data, n=10)
        q4 = quantiles(data, n=4)

        return {
            "p10": int(q10[0]),
            "p25": int(q4[0]),
            "p50": int(q4[1]),
            "p75": int(q4[2]),
            "p90": int(q10[8]),
            "mean": int(mean(data)),
        }

    photo_stats = calc_percentiles(photos)
    review_stats = calc_percentiles(total_reviews)
    blog_stats = calc_percentiles(blogs)

    stats_by_category[category] = {
        "sample_size": count,
        "photo": photo_stats,
        "total_review": review_stats,
        "blog": blog_stats,
        "adoption_rates": {
            "has_booking": round(has_booking, 3),
            "has_instagram": round(has_instagram, 3),
            "has_owner_reply": round(has_owner_reply, 3),
            "has_coupon": round(has_coupon, 3),
            "has_talktalk": round(has_talktalk, 3),
            "has_news": round(has_news, 3),
        }
    }

    # 출력 (카테고리명은 한글 깨짐, 인덱스로 표시)
    cat_display = f"Category_{categories.index(category)}" if len(categories) > 1 else category
    print(f"\n--- {cat_display} (raw: {repr(category)}) (n={count}) ---")
    print(f"Photo count:")
    print(f"  p10: {photo_stats['p10']}, p25: {photo_stats['p25']}, p50: {photo_stats['p50']}, p75: {photo_stats['p75']}, p90: {photo_stats['p90']}, mean: {photo_stats['mean']}")
    print(f"Total review (visitor + receipt):")
    print(f"  p10: {review_stats['p10']}, p25: {review_stats['p25']}, p50: {review_stats['p50']}, p75: {review_stats['p75']}, p90: {review_stats['p90']}, mean: {review_stats['mean']}")
    print(f"Blog review:")
    print(f"  p10: {blog_stats['p10']}, p25: {blog_stats['p25']}, p50: {blog_stats['p50']}, p75: {blog_stats['p75']}, p90: {blog_stats['p90']}, mean: {blog_stats['mean']}")
    print(f"Adoption rates:")
    for k, v in stats_by_category[category]["adoption_rates"].items():
        print(f"  {k}: {v}")

# 권장 COMPETITOR_FALLBACK 값
print(f"\n========== Recommended COMPETITOR_FALLBACK ==========")
print(f"(Use p25 for avg values, p75 for top_review)\n")

for idx, category in enumerate(categories):
    if category not in stats_by_category:
        continue
    stats = stats_by_category[category]
    rec = {
        "avg_review": stats["total_review"]["p25"],
        "avg_photo": stats["photo"]["p25"],
        "avg_blog": stats["blog"]["p25"],
        "top_review": stats["total_review"]["p75"],
    }
    print(f'    # Category_{idx}: {repr(category)} (n={stats["sample_size"]})')
    print(f'    "category_{idx}": {{')
    print(f'        "avg_review": {rec["avg_review"]},')
    print(f'        "avg_photo": {rec["avg_photo"]},')
    print(f'        "avg_blog": {rec["avg_blog"]},')
    print(f'        "top_review": {rec["top_review"]},')
    print(f'    }},')

print()
conn.close()
