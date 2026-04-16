"""
박어워즈 — Awwwards & Godly Design Showcase Scraper + Gemini Vision 분석
Visits top design showcase sites, captures screenshots, and analyzes with Gemini Vision
"""

import json
import os
import re
import base64
from datetime import datetime
from pathlib import Path
from io import BytesIO

from dotenv import load_dotenv
load_dotenv()

try:
    from playwright.sync_api import sync_playwright, TimeoutError
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    import requests
    from bs4 import BeautifulSoup

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    from google import genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


TRENDS_DIR = Path(__file__).parent.parent.parent / "knowledge" / "base" / "design" / "trends"

GEMINI_VISION_PROMPT = """이 웹사이트 스크린샷을 분석해서 아래 JSON 형식으로만 반환해줘. 설명 없이 JSON만.

{
  "effects": ["사용된 효과 리스트 — 예: 셰이더, 파티클, 스크롤트리거, 패럴랙스, 글리치, 모핑, 커스텀커서"],
  "color_palette": ["#hex1", "#hex2", "#hex3"],
  "layout_pattern": "레이아웃 패턴 한 줄 설명",
  "steal_this": [
    "훔칠 수 있는 것 1",
    "훔칠 수 있는 것 2",
    "훔칠 수 있는 것 3"
  ]
}"""


class AwwardsScout:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.screenshots_dir = self.base_dir / "screenshots"
        self.screenshots_dir.mkdir(exist_ok=True)
        TRENDS_DIR.mkdir(parents=True, exist_ok=True)

        self.sites = [
            {"name": "Awwwards", "url": "https://www.awwwards.com/", "description": "Web Design Awards"},
            {"name": "Godly", "url": "https://godly.website/", "description": "Curated Web Design Gallery"},
            {"name": "Dribbble", "url": "https://dribbble.com/search/web-design", "description": "Design Community"},
            {"name": "Lapa.ninja", "url": "https://www.lapa.ninja/", "description": "Landing Page Inspiration"},
        ]
        self.results = []
        self.date_str = datetime.now().strftime("%Y-%m-%d")

        # Gemini client
        self.gemini_client = None
        if GEMINI_AVAILABLE:
            api_key = os.getenv("GOOGLE_API_KEY")
            if api_key:
                self.gemini_client = genai.Client(api_key=api_key)

    def analyze_with_gemini(self, screenshot_path: str, site_name: str) -> dict:
        """Gemini Vision으로 스크린샷 분석 → 구조화된 JSON 반환"""
        if not self.gemini_client or not PIL_AVAILABLE:
            return {}

        try:
            with Image.open(screenshot_path) as img:
                img.thumbnail((1280, 800), Image.Resampling.LANCZOS)
                buffered = BytesIO()
                img.save(buffered, format="PNG")
                img_data = base64.standard_b64encode(buffered.getvalue()).decode()

            response_text = ""
            for chunk in self.gemini_client.models.generate_content_stream(
                model="gemini-2.0-flash",
                contents=[{
                    "role": "user",
                    "parts": [
                        {"text": GEMINI_VISION_PROMPT},
                        {"inline_data": {"mime_type": "image/png", "data": img_data}}
                    ]
                }]
            ):
                if hasattr(chunk, "text") and chunk.text:
                    response_text += chunk.text

            # JSON 파싱
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {}

        except Exception as e:
            print(f"  [GEMINI] {site_name} 분석 실패: {e}")
            return {}

    def _append_to_trends(self, site_name: str, url: str, analysis: dict):
        """knowledge/base/design/trends/YYYY-MM-DD.md에 분석 결과 추가"""
        trends_file = TRENDS_DIR / f"{self.date_str}.md"

        effects = ", ".join(analysis.get("effects", [])) or "미확인"
        colors = ", ".join(analysis.get("color_palette", [])) or "미확인"
        layout = analysis.get("layout_pattern", "미확인")
        steal = analysis.get("steal_this", [])

        steal_lines = "\n".join([f"  {i+1}. {item}" for i, item in enumerate(steal[:3])]) if steal else "  (분석 없음)"

        entry = f"""
## {site_name}
**URL:** {url}
- **효과**: {effects}
- **색상 팔레트**: {colors}
- **레이아웃**: {layout}
- **훔칠 것**:
{steal_lines}

---
"""
        if trends_file.exists():
            with open(trends_file, "a", encoding="utf-8") as f:
                f.write(entry)
        else:
            header = f"# 디자인 트렌드 — {self.date_str}\n\n> Awwwards + Godly 스캔 (Gemini Vision 분석)\n"
            with open(trends_file, "w", encoding="utf-8") as f:
                f.write(header + entry)

        print(f"  [TRENDS] {self.date_str}.md에 저장 완료")

    def scrape_with_playwright(self):
        """Playwright로 스크린샷 캡처 + Gemini Vision 분석"""
        if not PLAYWRIGHT_AVAILABLE:
            print("⚠️  Playwright not available, falling back to requests...")
            return self.scrape_fallback()

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)

                for site in self.sites:
                    try:
                        print(f"[CAPTURE] {site['name']}...")
                        page = browser.new_page(viewport={"width": 1280, "height": 800})
                        page.goto(site["url"], timeout=30000, wait_until="networkidle")

                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        screenshot_path = self.screenshots_dir / f"{site['name'].lower().replace('.', '_')}_{timestamp}.png"
                        page.screenshot(path=str(screenshot_path), full_page=False)
                        title = page.title()
                        page.close()

                        print(f"  [SUCCESS] 저장: {screenshot_path.name}")

                        # Gemini Vision 분석
                        analysis = {}
                        if screenshot_path.exists():
                            print(f"  [GEMINI] {site['name']} 분석 중...")
                            analysis = self.analyze_with_gemini(str(screenshot_path), site["name"])
                            if analysis:
                                print(f"  [GEMINI] 분석 완료 — 효과: {analysis.get('effects', [])}")
                                self._append_to_trends(site["name"], site["url"], analysis)

                        result = {
                            "name": site["name"],
                            "url": site["url"],
                            "title": title,
                            "description": site["description"],
                            "screenshot": str(screenshot_path),
                            "captured_at": timestamp,
                            "gemini_analysis": analysis
                        }
                        self.results.append(result)

                    except Exception as e:
                        print(f"  [ERROR] {site['name']} 실패: {str(e)}")
                        self.results.append({
                            "name": site["name"],
                            "url": site["url"],
                            "title": site["description"],
                            "description": site["description"],
                            "screenshot": None,
                            "error": str(e),
                            "captured_at": datetime.now().strftime("%Y%m%d_%H%M%S"),
                            "gemini_analysis": {}
                        })

                browser.close()
        except Exception as e:
            print(f"[ERROR] Playwright 실패: {e}")
            return self.scrape_fallback()

    def scrape_fallback(self):
        """Fallback: requests + BeautifulSoup (스크린샷 없음 → Gemini 분석 불가)"""
        print("[FALLBACK] requests + BeautifulSoup 사용...")

        try:
            import requests as req
            from bs4 import BeautifulSoup
        except ImportError:
            print("[ERROR] requests/beautifulsoup4 없음")
            return

        for site in self.sites:
            try:
                print(f"[FETCH] {site['name']}...")
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
                response = req.get(site["url"], headers=headers, timeout=10)

                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, "html.parser")
                    title = soup.title.string if soup.title else site["name"]
                    meta_desc = soup.find("meta", attrs={"name": "description"})
                    description = meta_desc.get("content", site["description"]) if meta_desc else site["description"]

                    self.results.append({
                        "name": site["name"],
                        "url": site["url"],
                        "title": title,
                        "description": description,
                        "screenshot": None,
                        "source": "fallback",
                        "captured_at": datetime.now().strftime("%Y%m%d_%H%M%S"),
                        "gemini_analysis": {}
                    })
                    print(f"  [SUCCESS] {title}")
                else:
                    raise Exception(f"Status {response.status_code}")

            except Exception as e:
                print(f"  [ERROR] 실패: {str(e)}")
                self.results.append({
                    "name": site["name"],
                    "url": site["url"],
                    "title": site["description"],
                    "description": site["description"],
                    "screenshot": None,
                    "error": str(e),
                    "captured_at": datetime.now().strftime("%Y%m%d_%H%M%S"),
                    "gemini_analysis": {}
                })

    def run(self):
        """스크래핑 실행"""
        print("[START] 디자인 쇼케이스 스카우팅 시작 (Awwwards + Godly + Dribbble + Lapa)...")
        self.scrape_with_playwright()

        results_file = self.base_dir / "awwwards_results.json"
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)

        analyzed = sum(1 for r in self.results if r.get("gemini_analysis"))
        print(f"[SUCCESS] 스카우팅 완료: {len(self.results)}개 사이트, {analyzed}개 Gemini 분석")
        return self.results


if __name__ == "__main__":
    scout = AwwardsScout()
    scout.run()
