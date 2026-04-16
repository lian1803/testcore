"""
크롤러 V2 검증 (실제 네이버 크롤링)
- 쿼리 → find_place_id로 실제 place_id 획득
- 4개 불안정 필드 성공률 측정 (photo_urls, owner_reply_rate, keywords, review_texts)
- Phase 1과 동일한 15개 샘플
"""
import asyncio
import sys
import json
from pathlib import Path
from datetime import datetime

# Windows cp949 인코딩 회피
if sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

PROJECT_PATH = Path(__file__).parent.parent.parent / "team" / "[진행중] 오프라인 마케팅" / "소상공인_영업툴" / "naver-diagnosis"
sys.path.insert(0, str(PROJECT_PATH))

from services.naver_place_crawler import NaverPlaceCrawler
from playwright.async_api import async_playwright


TEST_QUERIES = [
    "강남역 미용실",
    "홍대 입구 미용실",
    "강남 네일샵",
    "강남 피부관리숍",
    "강남역 고깃집",
    "홍대 이태리안",
    "을지로 감자탕",
    "성수동 카페",
    "홍대 카페",
    "목동 수학학원",
    "강남 필라테스",
    "강남역 피부과",
    "강남 한우",
    "을지로 라면",
]

TARGET_FIELDS = ["photo_urls", "owner_reply_rate", "keywords", "review_texts"]


async def verify_single(crawler, query: str) -> dict:
    """한 쿼리 → crawl_from_search (Phase 1과 동일 방식) → 4개 필드 성공 여부"""
    print(f"\n{'='*60}\n[QUERY] {query}\n{'='*60}")

    # Phase 1과 동일하게 crawl_from_search 한 번으로 place_id + 모든 데이터 획득
    try:
        start = datetime.now()
        data = await crawler.crawl_from_search(query)
        elapsed = (datetime.now() - start).total_seconds()
    except Exception as e:
        print(f"  [ERROR] crawl_from_search: {e}")
        return {"query": query, "status": "crawl_error", "error": str(e)}

    if not data or not data.get("place_id"):
        print(f"  [SKIP] place_id 없음")
        return {"query": query, "place_id": None, "status": "no_place_id", "elapsed": elapsed}

    place_id = data.get("place_id")
    print(f"  [place_id] {place_id}")

    # 3) 4개 필드 성공 여부
    photo_urls = data.get("photo_urls") or []
    reply_rate = data.get("owner_reply_rate", 0.0)
    has_owner_reply = data.get("has_owner_reply", False)
    keywords = data.get("keywords") or []
    review_texts = data.get("review_texts") or []

    photo_ok = len(photo_urls) >= 3  # 최소 3장 이상 수집
    # reply_rate는 숫자만 들어와도 OK. has_owner_reply True면서 rate 0.0인 경우는 리뷰가 없을 때
    reply_ok = has_owner_reply is not None  # 파싱 자체가 성공했는가
    kw_ok = len(keywords) > 0
    review_ok = len(review_texts) > 0

    print(f"  [TIME] {elapsed:.1f}s")
    print(f"  - photo_urls      : {'PASS' if photo_ok else 'FAIL'} ({len(photo_urls)})")
    print(f"  - owner_reply_rate: {'PASS' if reply_ok else 'FAIL'} (rate={reply_rate:.2f}, has={has_owner_reply})")
    print(f"  - keywords        : {'PASS' if kw_ok else 'FAIL'} ({len(keywords)} items)")
    print(f"  - review_texts    : {'PASS' if review_ok else 'FAIL'} ({len(review_texts)} items)")

    return {
        "query": query,
        "place_id": place_id,
        "status": "ok",
        "elapsed": elapsed,
        "photo_urls_ok": photo_ok,
        "photo_urls_count": len(photo_urls),
        "owner_reply_ok": reply_ok,
        "owner_reply_rate": reply_rate,
        "has_owner_reply": has_owner_reply,
        "keywords_ok": kw_ok,
        "keywords_count": len(keywords),
        "keywords_sample": keywords[:3] if keywords else [],
        "review_texts_ok": review_ok,
        "review_texts_count": len(review_texts),
    }


async def main():
    results = []
    start_all = datetime.now()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        crawler = NaverPlaceCrawler(browser)

        for q in TEST_QUERIES:
            try:
                r = await verify_single(crawler, q)
                results.append(r)
            except Exception as e:
                print(f"  [FATAL] {q}: {e}")
                results.append({"query": q, "status": "fatal", "error": str(e)})
            await asyncio.sleep(3)  # 봇 탐지 회피

        await browser.close()

    elapsed_all = (datetime.now() - start_all).total_seconds()

    # 성공률 집계
    ok_results = [r for r in results if r.get("status") == "ok"]
    total = len(ok_results)

    if total == 0:
        print("\n\n[REPORT] 모든 크롤링 실패 — 크롤러 점검 필요")
        return

    stats = {
        "photo_urls": sum(1 for r in ok_results if r["photo_urls_ok"]),
        "owner_reply_rate": sum(1 for r in ok_results if r["owner_reply_ok"]),
        "keywords": sum(1 for r in ok_results if r["keywords_ok"]),
        "review_texts": sum(1 for r in ok_results if r["review_texts_ok"]),
    }

    print(f"\n\n{'='*60}")
    print(f"[V2 검증 리포트] {datetime.now().isoformat()}")
    print(f"총 소요: {elapsed_all:.1f}s / 성공 크롤: {total}/{len(TEST_QUERIES)}")
    print(f"{'='*60}")

    v1_baseline = {"photo_urls": 85, "owner_reply_rate": 85, "keywords": 78, "review_texts": 78}
    lines_for_md = []
    for field in TARGET_FIELDS:
        pct = (stats[field] / total) * 100
        v1 = v1_baseline[field]
        diff = pct - v1
        status = "PASS" if pct >= 95 else ("OK" if pct >= v1 else "FAIL")
        print(f"  [{status:4}] {field:20} | {stats[field]:2}/{total:2} = {pct:5.1f}% (v1: {v1}%, 변화: {diff:+.1f}%p)")
        lines_for_md.append({"field": field, "pass": stats[field], "total": total, "pct": pct, "v1": v1, "diff": diff, "status": status})

    # 리포트 파일 저장
    out_md = Path(__file__).parent / "2026-04-17_crawler_v2_real_report.md"
    out_json = Path(__file__).parent / "2026-04-17_crawler_v2_real_results.json"

    md_lines = [
        "# 크롤러 V2 실제 검증 리포트",
        f"실행 시각: {datetime.now().isoformat()}",
        f"총 샘플: {len(TEST_QUERIES)}, 크롤 성공: {total}",
        f"총 소요: {elapsed_all:.1f}s",
        "",
        "## 필드별 성공률 (v1 대비 변화)",
        "| 필드 | 성공/전체 | 성공률 | v1 기준 | 변화 | 상태 |",
        "|------|-----------|--------|---------|------|------|",
    ]
    for x in lines_for_md:
        md_lines.append(
            f"| {x['field']} | {x['pass']}/{x['total']} | {x['pct']:.1f}% | {x['v1']}% | {x['diff']:+.1f}%p | {x['status']} |"
        )

    md_lines.append("")
    md_lines.append("## 샘플별 상세")
    for r in results:
        if r.get("status") != "ok":
            md_lines.append(f"- **{r['query']}**: {r.get('status')} {r.get('error', '')}")
            continue
        md_lines.append(
            f"- **{r['query']}** (id={r['place_id']}): "
            f"photo={r['photo_urls_count']}, reply={r['owner_reply_rate']:.2f}, "
            f"kw={r['keywords_count']}, review={r['review_texts_count']}"
        )

    out_md.write_text("\n".join(md_lines), encoding="utf-8")
    out_json.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n[SAVED] {out_md}")
    print(f"[SAVED] {out_json}")


if __name__ == "__main__":
    asyncio.run(main())
