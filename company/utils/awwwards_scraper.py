"""
awwwards_scraper.py - Awwwards 사이트 자동 수집 -> 디자인 레퍼런스 카드

사용법:
    python utils/awwwards_scraper.py           # 최근 10개 수집
    python utils/awwwards_scraper.py 20        # 20개 수집
    python utils/awwwards_scraper.py --list    # 저장된 목록 보기

저장: design_system/references/awwwards/
  INDEX.json - 전체 목록
  각 항목: 제목, URL, 색상 팔레트, 스크린샷(png), 카테고리
"""
import asyncio
import sys
import json
import re
import os
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent.parent.parent
AWWWARDS_DIR = ROOT / "design_system" / "references" / "awwwards"
AWWWARDS_DIR.mkdir(parents=True, exist_ok=True)
INDEX_FILE = AWWWARDS_DIR / "INDEX.json"


def load_index():
    if INDEX_FILE.exists():
        return json.loads(INDEX_FILE.read_text(encoding="utf-8"))
    return []


def save_index(index):
    INDEX_FILE.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")


def extract_colors(png_path, n=5):
    try:
        from PIL import Image
        from collections import Counter
        img = Image.open(png_path).convert("RGB").resize((120, 120))
        pixels = list(img.getdata())
        bucket = [(r // 40 * 40, g // 40 * 40, b // 40 * 40) for r, g, b in pixels]
        common = Counter(bucket).most_common(n * 3)
        colors = []
        for (r, g, b), _ in common:
            brightness = (r + g + b) / 3
            if 15 < brightness < 240:
                colors.append(f"#{r:02x}{g:02x}{b:02x}")
            if len(colors) >= n:
                break
        return colors
    except Exception:
        return []


async def scrape_awwwards(count=10):
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("playwright 없음: pip install playwright && playwright install chromium")
        return

    index = load_index()
    existing_slugs = {item.get("slug") for item in index}

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        print("Awwwards 수집 중...")
        await page.goto("https://www.awwwards.com/websites/", timeout=30000, wait_until="domcontentloaded")
        await page.wait_for_timeout(4000)

        # /sites/xxx 링크 수집 (중복 제거)
        links = await page.eval_on_selector_all(
            "a[href*='/sites/']",
            "els => [...new Set(els.map(e => e.getAttribute('href')))].filter(h => h && h.startsWith('/sites/'))"
        )
        links = links[:count]
        print(f"  발견: {len(links)}개 사이트")

        new_count = 0
        for href in links:
            slug = href.strip("/").split("/")[-1]
            if slug in existing_slugs:
                print(f"  [스킵] {slug} (이미 수집됨)")
                continue

            detail_url = f"https://www.awwwards.com{href}"
            print(f"\n  -> {slug}")

            detail_page = await context.new_page()
            try:
                await detail_page.goto(detail_url, timeout=20000, wait_until="domcontentloaded")
                await detail_page.wait_for_timeout(2000)

                # 제목
                title_el = await detail_page.query_selector("h1, .site-header__title, [class*='title']")
                title = (await title_el.inner_text()).strip() if title_el else slug

                # 실제 사이트 URL
                site_url = ""
                for sel in ["a.site-header__visit", "a[class*='visit']", "a[target='_blank'][class*='site']"]:
                    el = await detail_page.query_selector(sel)
                    if el:
                        site_url = await el.get_attribute("href") or ""
                        break

                # 카테고리 태그
                cat_els = await detail_page.query_selector_all("[class*='tag'], [class*='category'], [class*='type']")
                cats = []
                for el in cat_els[:5]:
                    t = (await el.inner_text()).strip()
                    if t and len(t) < 30:
                        cats.append(t)

                # 점수
                score = ""
                score_el = await detail_page.query_selector("[class*='score'], .score, [class*='rating']")
                if score_el:
                    score = (await score_el.inner_text()).strip()[:10]

                # 스크린샷 저장
                date_str = datetime.now().strftime("%Y-%m-%d")
                safe_slug = re.sub(r"[^\w\-]", "_", slug)
                folder = AWWWARDS_DIR / f"{date_str}_{safe_slug}"
                folder.mkdir(exist_ok=True)

                screenshot_path = folder / "screenshot.png"
                await detail_page.screenshot(path=str(screenshot_path), full_page=False)

                # 색상 추출
                colors = extract_colors(str(screenshot_path))

                # 메타 저장
                meta = {
                    "title": title,
                    "slug": slug,
                    "awwwards_url": detail_url,
                    "site_url": site_url,
                    "categories": cats,
                    "score": score,
                    "color_palette": colors,
                    "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                }
                (folder / "meta.json").write_text(
                    json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
                )

                index.append({
                    "title": title,
                    "slug": slug,
                    "awwwards_url": detail_url,
                    "site_url": site_url,
                    "categories": cats[:3],
                    "color_palette": colors[:3],
                    "folder": folder.name,
                    "collected_at": date_str,
                })
                existing_slugs.add(slug)
                new_count += 1

                print(f"     제목: {title[:40]}")
                print(f"     카테고리: {', '.join(cats[:3]) or 'n/a'}")
                print(f"     색상: {' '.join(colors[:4]) or '추출 실패'}")
                print(f"     저장: {folder.name}/")

            except Exception as e:
                print(f"     [X] 오류: {e}")
            finally:
                await detail_page.close()

        save_index(index)
        await browser.close()

        print(f"\n완료: {new_count}개 새로 수집 | 총 {len(index)}개")
        print(f"저장 위치: design_system/references/awwwards/")


def show_list():
    index = load_index()
    if not index:
        print("저장된 레퍼런스 없음")
        return
    print(f"\n=== Awwwards 레퍼런스 ({len(index)}개) ===\n")
    for i, item in enumerate(index, 1):
        print(f"{i:2}. {item['title'][:40]:<40} | {', '.join(item.get('categories', []))[:20]:<20} | {item['collected_at']}")
        print(f"     {' '.join(item.get('color_palette', []))}")


if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] == "--list":
        show_list()
    elif args and args[0].isdigit():
        asyncio.run(scrape_awwwards(count=int(args[0])))
    else:
        asyncio.run(scrape_awwwards(count=10))
