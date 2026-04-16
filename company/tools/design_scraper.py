# -*- coding: utf-8 -*-
"""
design_scraper.py - Awwwards SOTD 디자인 트렌드 자동 수집

실행:
    cd C:/Users/lian1/Documents/Work/core/company
    ./venv/Scripts/python.exe tools/design_scraper.py
"""

import os
import sys
import time
import asyncio
from pathlib import Path
from datetime import datetime

# Windows stdout 인코딩 강제 UTF-8
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

SCRIPT_DIR = Path(__file__).parent
LIAN_DIR = SCRIPT_DIR.parent
KNOWLEDGE_DIR = LIAN_DIR / "knowledge" / "base" / "design" / "trends"
TEMP_DIR = LIAN_DIR / "temp"

KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)
TEMP_DIR.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(LIAN_DIR))
from dotenv import load_dotenv
load_dotenv(LIAN_DIR / ".env")

# Playwright
try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_OK = True
except ImportError:
    PLAYWRIGHT_OK = False
    print("[WARNING] playwright 미설치: pip install playwright && playwright install chromium")

# Gemini (new SDK)
try:
    from google import genai
    from google.genai import types as gtypes
    GEMINI_OK = True
except ImportError:
    GEMINI_OK = False
    print("[WARNING] google-genai 미설치: pip install google-genai")


def get_gemini_client():
    if not GEMINI_OK:
        return None
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("[WARNING] GOOGLE_API_KEY 없음")
        return None
    return genai.Client(api_key=api_key)


async def scrape_awwwards():
    """Awwwards SOTD 상위 5개 사이트 URL 수집."""
    if not PLAYWRIGHT_OK:
        return []

    sites = []
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            print("[1/4] Awwwards SOTD 접속 중...")
            await page.goto("https://www.awwwards.com/websites/sites_of_the_day/", timeout=30000)
            await page.wait_for_load_state("networkidle")

            # 사이트 카드 선택 (다양한 선택자 시도)
            selectors = [
                "article.collectionItem a[href*='/sites/']",
                "a[href*='/sites/']",
                ".item-award a",
                "figure a"
            ]
            elements = []
            for sel in selectors:
                elements = await page.query_selector_all(sel)
                if elements:
                    break

            seen = set()
            for elem in elements:
                if len(sites) >= 5:
                    break
                try:
                    href = await elem.get_attribute("href")
                    if not href or href in seen:
                        continue
                    if "/sites/" not in href:
                        continue
                    seen.add(href)
                    # 전체 URL로 변환
                    if href.startswith("/"):
                        href = "https://www.awwwards.com" + href
                    # 제목: URL slug에서 추출 (/sites/my-site-name → My Site Name)
                    slug = href.rstrip("/").split("/sites/")[-1].split("?")[0]
                    title = slug.replace("-", " ").title() if slug else f"Site {len(sites)+1}"
                    sites.append({"title": title, "url": href})
                    print(f"  {len(sites)}. {title}")
                except Exception:
                    continue

            await browser.close()

    except Exception as e:
        print(f"[ERROR] Awwwards 스크랩 실패: {e}")

    return sites


async def get_site_screenshot(url: str, filename: str):
    """사이트 스크린샷 캡처."""
    if not PLAYWRIGHT_OK:
        return None
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(viewport={"width": 1280, "height": 800})
            print(f"  -> 스크린샷: {url[:60]}...")
            await page.goto(url, timeout=30000)
            await page.wait_for_load_state("networkidle")
            path = TEMP_DIR / filename
            await page.screenshot(path=str(path), full_page=False)
            await browser.close()
            return path
    except Exception as e:
        print(f"  [WARNING] 스크린샷 실패: {e}")
        return None


def analyze_with_gemini(client, image_path: Path) -> str:
    """Gemini Vision으로 디자인 패턴 분석."""
    if not client or not image_path or not image_path.exists():
        return ""
    try:
        image_bytes = image_path.read_bytes()
        prompt = """이 웹사이트 스크린샷을 보고 분석해줘:

1. **레이아웃** - 그리드 구조, 여백, 정렬 방식
2. **색상** - 주요 3색, 배경/텍스트 대비
3. **타이포** - 폰트 스타일, 크기 계층
4. **모션/인터랙션** - 스크롤/호버 효과 추측
5. **차별화** - 이 사이트만의 독특한 결정
6. **배울 것** - 우리가 적용 가능한 기법 1-2가지

한국어로, 각 항목 2문장으로."""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                gtypes.Part.from_bytes(data=image_bytes, mime_type="image/png"),
                gtypes.Part.from_text(text=prompt)
            ]
        )
        return response.text
    except Exception as e:
        print(f"  [WARNING] Gemini 분석 실패: {e}")
        return ""


def save_results(sites: list):
    """분석 결과 Markdown 저장."""
    if not sites:
        print("[ERROR] 저장할 데이터 없음")
        return None

    today = datetime.now().strftime("%Y-%m-%d")
    filepath = KNOWLEDGE_DIR / f"{today}.md"

    lines = [
        f"# 디자인 트렌드 — {today}",
        "",
        "> Awwwards SOTD 자동 수집 (Gemini Vision 분석)",
        ""
    ]

    for i, s in enumerate(sites, 1):
        lines += [
            f"## 사이트 {i}: {s['title']}",
            "",
            f"**URL:** {s['url']}",
            "",
            s.get("analysis", "(분석 없음)"),
            "",
            "---",
            ""
        ]

    filepath.write_text("\n".join(lines), encoding="utf-8")
    print(f"[OK] 저장: {filepath}")
    return filepath


def cleanup_temp():
    for f in TEMP_DIR.glob("*.png"):
        try:
            f.unlink()
        except Exception:
            pass


async def main():
    print("=" * 50)
    print("Awwwards 디자인 트렌드 수집 시작")
    print("=" * 50)

    # Step 1: 사이트 목록 수집
    sites = await scrape_awwwards()
    if not sites:
        print("[ERROR] 사이트 수집 실패. Awwwards 구조가 변경됐을 수 있음")
        return

    print(f"\n{len(sites)}개 사이트 발견")

    # Step 2: 스크린샷 + 분석
    print("\n[2/4] 스크린샷 + Gemini 분석...")
    client = get_gemini_client()
    results = []

    for i, site in enumerate(sites, 1):
        print(f"\n  [{i}/{len(sites)}] {site['title']}")
        shot = await get_site_screenshot(site["url"], f"site_{i:02d}.png")
        analysis = ""
        if shot:
            analysis = analyze_with_gemini(client, shot)
            if analysis:
                print("  [OK] 분석 완료")
            else:
                print("  [SKIP] 분석 실패")
        results.append({**site, "analysis": analysis})
        time.sleep(2)

    # Step 3: 저장
    print("\n[3/4] 결과 저장...")
    out = save_results(results)

    # Step 4: 임시 파일 정리
    print("\n[4/4] 임시 파일 정리...")
    cleanup_temp()

    print("\n" + "=" * 50)
    print(f"완료! 분석 사이트: {len([r for r in results if r['analysis']])}개")
    if out:
        print(f"저장 위치: {out}")
    print("=" * 50)


if __name__ == "__main__":
    # Windows: ProactorEventLoop 필수 (subprocess 지원)
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(main())
