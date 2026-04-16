"""
경쟁사스캔 — Competitor Instagram Scanner
주기적으로 경쟁사 인스타 계정을 스캔하고 "무엇이 잘됐는지" 패턴 추출.
추출한 패턴은 knowledge/ops_templates/marketing/경쟁사패턴_DB.md에 누적 저장.
ops_loop daily 실행 시 자동 참조됨.

사용법:
    python teams/인스타분석팀/경쟁사스캔.py                          # 전체 프로젝트 스캔
    python teams/인스타분석팀/경쟁사스캔.py --project "프로젝트명"    # 특정 프로젝트만
    python teams/인스타분석팀/경쟁사스캔.py --url "https://..."       # 단일 URL
"""

import json
import os
import sys
import asyncio
import subprocess
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

BASE_DIR = Path(__file__).parent
LIAN_DIR = BASE_DIR.parent.parent
CONFIG_PATH = BASE_DIR / "경쟁사계정.json"
PATTERNS_DB = LIAN_DIR / "knowledge" / "ops_templates" / "marketing" / "경쟁사패턴_DB.md"
INSTA_BROWSE = LIAN_DIR / "utils" / "insta_browse.py"
PYTHON = str(LIAN_DIR / "venv" / "Scripts" / "python.exe")

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    from google import genai
    import base64
    from io import BytesIO
    from PIL import Image
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


PATTERN_EXTRACT_PROMPT = """이 인스타그램 계정/게시물 스크린샷을 보고 마케팅 패턴을 분석해줘.

분석 항목:
1. **훅 패턴**: 어떤 방식으로 첫 줄을 시작하는가? (숫자형/질문형/충격형/공감형)
2. **CTA 방식**: 어떻게 행동을 유도하는가?
3. **해시태그 전략**: 어떤 카테고리/규모의 해시태그를 쓰는가?
4. **콘텐츠 포맷**: 캐러셀/릴스/단일이미지? 텍스트 비중은?
5. **훔칠 것**: 우리가 바로 적용할 수 있는 것 3가지

JSON으로만 반환:
{
  "hook_pattern": "훅 방식 설명",
  "cta_style": "CTA 방식 설명",
  "hashtag_strategy": "해시태그 전략 설명",
  "content_format": "포맷 설명",
  "steal_this": ["적용할것1", "적용할것2", "적용할것3"],
  "overall_score": 숫자_1_to_10
}"""


class CompetitorScanner:
    def __init__(self, project_filter: str = None):
        self.project_filter = project_filter
        self.date_str = datetime.now().strftime("%Y-%m-%d")

        self.gemini_client = None
        if GEMINI_AVAILABLE:
            api_key = os.getenv("GOOGLE_API_KEY")
            if api_key:
                self.gemini_client = genai.Client(api_key=api_key)

        self.anthropic_client = None
        if ANTHROPIC_AVAILABLE:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if api_key:
                self.anthropic_client = Anthropic(api_key=api_key)

    def load_config(self) -> dict:
        if not CONFIG_PATH.exists():
            return {"global": {"accounts": []}, "projects": {}}
        with open(CONFIG_PATH, encoding="utf-8") as f:
            return json.load(f)

    def capture_account(self, account_url: str) -> str | None:
        """insta_browse.py로 계정 스크린샷 캡처"""
        import tempfile
        screenshot_path = str(LIAN_DIR / "utils" / "insta_screenshots" / f"competitor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")

        try:
            result = subprocess.run(
                [PYTHON, str(INSTA_BROWSE), account_url, screenshot_path],
                capture_output=True, text=True, timeout=60,
                cwd=str(LIAN_DIR)
            )
            if result.returncode == 0 and Path(screenshot_path).exists():
                print(f"  [CAPTURE] {account_url} → {Path(screenshot_path).name}")
                return screenshot_path
            else:
                print(f"  [ERROR] 캡처 실패: {result.stderr[:200]}")
                return None
        except Exception as e:
            print(f"  [ERROR] {e}")
            return None

    def analyze_screenshot(self, screenshot_path: str) -> dict:
        """Gemini Vision으로 마케팅 패턴 분석"""
        if not self.gemini_client:
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
                        {"text": PATTERN_EXTRACT_PROMPT},
                        {"inline_data": {"mime_type": "image/png", "data": img_data}}
                    ]
                }]
            ):
                if hasattr(chunk, "text") and chunk.text:
                    response_text += chunk.text

            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {}
        except Exception as e:
            print(f"  [GEMINI] 분석 실패: {e}")
            return {}

    def save_patterns(self, account_url: str, project_name: str, analysis: dict):
        """경쟁사패턴_DB.md에 분석 결과 누적 저장"""
        steal = "\n".join([f"  - {item}" for item in analysis.get("steal_this", [])])
        score = analysis.get("overall_score", "?")

        entry = f"""
## {account_url.split('instagram.com/')[-1].strip('/')} — {self.date_str}

**프로젝트**: {project_name}
**점수**: {score}/10

| 항목 | 내용 |
|------|------|
| 훅 패턴 | {analysis.get('hook_pattern', '-')} |
| CTA | {analysis.get('cta_style', '-')} |
| 해시태그 | {analysis.get('hashtag_strategy', '-')} |
| 포맷 | {analysis.get('content_format', '-')} |

**바로 훔칠 것:**
{steal or '  (분석 없음)'}

---
"""
        if PATTERNS_DB.exists():
            with open(PATTERNS_DB, "a", encoding="utf-8") as f:
                f.write(entry)
        else:
            header = """---
name: 경쟁사패턴_DB
description: 경쟁사 인스타그램 스캔 — 잘되는 패턴 누적 DB. ops_loop daily 자동 참조.
---

# 경쟁사 마케팅 패턴 DB

> 자동 수집 (경쟁사스캔.py). ops_loop 콘텐츠 생성 시 자동 참조됨.

"""
            with open(PATTERNS_DB, "w", encoding="utf-8") as f:
                f.write(header + entry)

        print(f"  [DB] 패턴 저장 완료 → 경쟁사패턴_DB.md")

    def run_single(self, account_url: str, project_name: str = "global"):
        """단일 계정 스캔"""
        print(f"\n[SCAN] {account_url}")

        screenshot = self.capture_account(account_url)
        if not screenshot:
            print("  [SKIP] 스크린샷 실패")
            return

        analysis = self.analyze_screenshot(screenshot)
        if analysis:
            print(f"  [OK] 훅: {analysis.get('hook_pattern', '')[:50]}...")
            self.save_patterns(account_url, project_name, analysis)
        else:
            print("  [SKIP] 분석 실패")

    def run(self):
        """전체 스캔 실행"""
        print(f"\n{'='*60}")
        print(f"[경쟁사스캔] 시작: {self.date_str}")
        print(f"{'='*60}")

        config = self.load_config()
        scanned = 0

        # 글로벌 계정
        for url in config.get("global", {}).get("accounts", []):
            if url:
                self.run_single(url, "global")
                scanned += 1

        # 프로젝트별 계정
        for proj_name, proj_config in config.get("projects", {}).items():
            if proj_name.startswith("_"):
                continue
            if self.project_filter and self.project_filter.lower() not in proj_name.lower():
                continue
            for url in proj_config.get("accounts", []):
                if url:
                    self.run_single(url, proj_name)
                    scanned += 1

        print(f"\n[완료] {scanned}개 계정 스캔")
        return scanned


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default=None, help="특정 프로젝트만 스캔")
    parser.add_argument("--url", default=None, help="단일 URL 스캔")
    args = parser.parse_args()

    scanner = CompetitorScanner(project_filter=args.project)

    if args.url:
        scanner.run_single(args.url, args.project or "manual")
    else:
        scanner.run()
