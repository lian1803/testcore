"""
insta_browse.py — 인스타그램 쿠키 자동 주입 브라우저

사용법:
    python utils/insta_browse.py "https://www.instagram.com/reel/..."
    python utils/insta_browse.py "https://www.instagram.com/username/"

쿠키: instagram_cookies.txt (제니스 계정 — 로그인 유지)
스크린샷: utils/insta_screenshot.png 저장
"""
import asyncio
import sys
import os

COOKIE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "instagram_cookies.txt")
SCREENSHOT_PATH = os.path.join(os.path.dirname(__file__), "insta_screenshot.png")


def load_cookies():
    cookies = []
    with open(COOKIE_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("# "):
                continue
            http_only = False
            if line.startswith("#HttpOnly_"):
                line = line[len("#HttpOnly_"):]
                http_only = True
            parts = line.split("\t")
            if len(parts) >= 7:
                cookies.append({
                    "name": parts[5],
                    "value": parts[6],
                    "domain": parts[0],
                    "path": parts[2],
                    "secure": parts[3] == "TRUE",
                    "httpOnly": http_only,
                })
    return cookies


async def browse(url: str, screenshot_path: str = SCREENSHOT_PATH):
    from playwright.async_api import async_playwright

    cookies = load_cookies()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        await context.add_cookies(cookies)
        page = await context.new_page()

        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(2)

        # 로그인 팝업 닫기
        try:
            await page.click('[aria-label="닫기"]', timeout=2000)
        except Exception:
            pass

        await page.screenshot(path=screenshot_path, full_page=False)
        print(f"스크린샷 저장: {screenshot_path}")

        # 페이지 텍스트 추출 (캡션, 설명 등)
        text = await page.inner_text("body")
        await browser.close()
        return text


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "https://www.instagram.com/"
    result = asyncio.run(browse(url))
    # 주요 텍스트만 출력
    lines = [l.strip() for l in result.split("\n") if l.strip() and len(l.strip()) > 3]
    print("\n".join(lines[:50]))
