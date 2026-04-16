"""
codepen_scraper.py - 이펙트 코드 -> 독립 실행 HTML 저장

[기능 1] Codrops/일반 URL 자동 스크랩
    python utils/codepen_scraper.py "https://tympanus.net/Development/xxx"

[기능 2] CodePen 소스 붙여넣기 변환 (interactive)
    python utils/codepen_scraper.py --paste

[기능 3] 배치 URL (txt 파일)
    python utils/codepen_scraper.py urls.txt

저장: design_system/references/effects/{카테고리}/{날짜_이름}.html
"""
import asyncio
import sys
import os
import json
import re
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent.parent.parent
EFFECTS_DIR = ROOT / "design_system" / "references" / "effects"
EFFECTS_DIR.mkdir(parents=True, exist_ok=True)
INDEX_FILE = EFFECTS_DIR / "INDEX.json"


def load_index():
    if INDEX_FILE.exists():
        return json.loads(INDEX_FILE.read_text(encoding="utf-8"))
    return []


def save_index(index):
    INDEX_FILE.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")


def detect_category(url_or_text, title=""):
    text = (url_or_text + " " + title).lower()
    if any(k in text for k in ["fluid", "liquid", "water", "ink"]):
        return "fluid"
    if any(k in text for k in ["particle", "star", "galaxy", "space", "dot"]):
        return "particles"
    if any(k in text for k in ["text", "type", "letter", "font", "glitch", "typography"]):
        return "typography"
    if any(k in text for k in ["scroll", "parallax", "journey"]):
        return "scroll"
    if any(k in text for k in ["hover", "reveal", "distort", "displace", "cursor"]):
        return "hover"
    if any(k in text for k in ["morph", "shape", "geometry", "sdf", "blob"]):
        return "geometry"
    if any(k in text for k in ["shader", "glsl", "webgl", "noise", "ray"]):
        return "shaders"
    if any(k in text for k in ["3d", "three", "threejs"]):
        return "3d"
    return "general"


def save_effect(data, category="general"):
    date_str = datetime.now().strftime("%Y-%m-%d")
    safe_title = re.sub(r"[^\w\-]", "_", data["title"])[:40]
    filename = f"{date_str}_{safe_title}.html"

    cat_dir = EFFECTS_DIR / category
    cat_dir.mkdir(exist_ok=True)
    filepath = cat_dir / filename
    filepath.write_text(data["html"], encoding="utf-8")

    index = load_index()
    index.append({
        "title": data["title"],
        "source": data["source"],
        "type": data["type"],
        "category": category,
        "file": f"{category}/{filename}",
        "saved_at": date_str,
    })
    save_index(index)
    return filepath


async def fetch_url(url):
    """일반 URL -> Playwright로 렌더링 저장 (Codrops, CSS Design Awards demo 등)"""
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("[X] playwright 없음: pip install playwright && playwright install chromium")
        return None

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1440, "height": 900})
        try:
            await page.goto(url, timeout=30000, wait_until="domcontentloaded")
            await page.wait_for_timeout(3000)
            title = await page.title() or url.split("/")[-1]

            # 스크린샷 (미리보기용)
            screenshot_bytes = await page.screenshot()

            # HTML 전체 저장
            html_content = await page.content()
            await browser.close()

            return {
                "title": title.strip(),
                "source": url,
                "type": "url",
                "html": html_content,
                "screenshot": screenshot_bytes,
            }
        except Exception as e:
            await browser.close()
            print(f"[X] 오류: {e}")
            return None


def build_standalone_html(title, html, css, js, source=""):
    """HTML/CSS/JS -> standalone HTML 파일 생성"""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <!-- Source: {source} -->
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ min-height: 100vh; background: #000; overflow: hidden; }}
{css}
  </style>
</head>
<body>
{html}
  <script>
{js}
  </script>
</body>
</html>"""


def paste_mode():
    """CodePen 소스 붙여넣기 -> standalone HTML"""
    print("=" * 50)
    print("CodePen 코드 변환 모드")
    print("CodePen에서 HTML/CSS/JS 탭 내용을 복사해서 붙여넣으세요")
    print("=" * 50)

    print("\n[1] 이펙트 이름 (예: Liquid Mouse Effect): ", end="")
    title = input().strip() or "effect"

    print("\n[2] 출처 URL (예: https://codepen.io/...): ", end="")
    source = input().strip()

    print("\n[3] HTML 코드를 붙여넣으세요. 완료하면 '---END---' 한 줄 입력:\n")
    html_lines = []
    while True:
        line = input()
        if line.strip() == "---END---":
            break
        html_lines.append(line)
    html = "\n".join(html_lines)

    print("\n[4] CSS 코드를 붙여넣으세요. '---END---'로 마무리:\n")
    css_lines = []
    while True:
        line = input()
        if line.strip() == "---END---":
            break
        css_lines.append(line)
    css = "\n".join(css_lines)

    print("\n[5] JS 코드를 붙여넣으세요. '---END---'로 마무리:\n")
    js_lines = []
    while True:
        line = input()
        if line.strip() == "---END---":
            break
        js_lines.append(line)
    js = "\n".join(js_lines)

    standalone = build_standalone_html(title, html, css, js, source)
    category = detect_category(source, title)

    data = {
        "title": title,
        "source": source or "paste",
        "type": "codepen_paste",
        "html": standalone,
    }

    filepath = save_effect(data, category)
    print(f"\n[OK] 저장: {filepath.relative_to(ROOT)}")
    print(f"     카테고리: {category}")
    return filepath


async def process_url(url):
    url = url.strip()
    if not url or url.startswith("#"):
        return

    print(f"\n-> {url}")
    data = await fetch_url(url)

    if not data:
        return

    category = detect_category(url, data.get("title", ""))
    filepath = save_effect(data, category)

    # 스크린샷도 저장
    if data.get("screenshot"):
        screenshot_path = filepath.with_suffix(".png")
        screenshot_path.write_bytes(data["screenshot"])

    print(f"[OK] {filepath.relative_to(ROOT)}")
    print(f"     카테고리: {category} | 제목: {data['title']}")


def show_list():
    index = load_index()
    if not index:
        print("저장된 이펙트 없음")
        return
    print(f"\n=== 이펙트 라이브러리 ({len(index)}개) ===\n")
    by_cat = {}
    for item in index:
        by_cat.setdefault(item["category"], []).append(item)
    for cat, items in sorted(by_cat.items()):
        print(f"[{cat}] {len(items)}개")
        for item in items[-3:]:
            print(f"  - {item['title'][:45]} ({item['saved_at']})")
    print()


async def main():
    args = sys.argv[1:]

    if not args or args[0] == "--list":
        show_list()
        return

    if args[0] == "--paste":
        paste_mode()
        return

    arg = args[0]

    if arg.endswith(".txt") and os.path.exists(arg):
        with open(arg, encoding="utf-8") as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        print(f"배치 모드: {len(urls)}개")
        for url in urls:
            await process_url(url)
    else:
        await process_url(arg)

    index = load_index()
    print(f"\n완료. 총 {len(index)}개 | design_system/references/effects/")


if __name__ == "__main__":
    asyncio.run(main())
