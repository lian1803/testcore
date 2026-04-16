#!/usr/bin/env python3
"""
인스타그램 링크 분석 — 이미지 캡처 + Gemini Vision 분석
core-shell 시스템에 "훔쳐서 바로 적용"할 수 있는 아이디어 추출

사용법:
  python utils/insta_analyze.py "C:/path/to/links.txt"

결과: 보고사항들.md에 자동 저장
"""
import asyncio
import sys
import os
import io
import json
import re
import time
from pathlib import Path
from datetime import datetime

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

from utils.insta_browse import browse
from core.models import GEMINI_FLASH

LIANCP_ROOT = os.path.dirname(os.path.dirname(__file__))
SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "insta_screenshots")
REPORT_FILE = os.path.join(LIANCP_ROOT, "보고사항들.md")

INSTA_ANALYSIS_SYSTEM = """너는 서연이야. 리안 컴퍼니 시스템 전략가.

임무: 이 인스타그램 게시물을 보고, core-shell AI 자동화 시스템에 "훔쳐서 바로 적용"할 수 있는 것을 찾아라.

core-shell이 뭔지:
- AI 에이전트 자동화 (이사팀, 영업팀, 마케팅팀, 납품팀)
- 소상공인 오프라인 영업 자동화 (PDF 진단서, DM 자동 생성, CRM)
- 인스타/블로그/카카오 콘텐츠 자동 생성
- 멀티 에이전트 파이프라인 (Perplexity+Claude+GPT+Gemini)

훔쳐올 것 판단 기준:
- 콘텐츠 포맷/구조 (카드뉴스 구성, 후킹 방식, CTA)
- 마케팅 전략/카피 패턴
- UI/UX 아이디어
- 워크플로우/자동화 아이디어
- 실제 숫자, 사례, 증거 (신뢰도 높은 것)

출력은 반드시 JSON만:
{
  "steal_worthy": true 또는 false,
  "what": "뭘 훔칠 수 있나 (1~2줄 핵심)",
  "how_to_apply": "core-shell에 어떻게 적용하나 (구체적으로)",
  "category": "콘텐츠전략" 또는 "마케팅카피" 또는 "UX아이디어" 또는 "자동화아이디어" 또는 "영업전략" 또는 "기타",
  "priority": "즉시" 또는 "나중에" 또는 "참고만",
  "report_to_lian": "리안한테 직접 보고 (구어체, 짧게, 뭘 봤고 뭘 훔칠 수 있는지)"
}
"""


def _parse_json(raw: str) -> dict:
    """응답에서 JSON 추출 및 파싱."""
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except (json.JSONDecodeError, ValueError):
            pass
    return {"steal_worthy": False, "what": "", "category": "기타", "priority": "참고만",
            "report_to_lian": "분석 실패"}


def _get_gemini_client():
    """Gemini 클라이언트 생성."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY 없음. .env 확인해.")

    from google import genai
    return genai.Client(api_key=api_key)


def analyze_screenshot(screenshot_path: str, insta_url: str) -> dict:
    """스크린샷을 Gemini Vision으로 분석."""
    from google.genai import types
    from pathlib import Path

    client = _get_gemini_client()
    ext = Path(screenshot_path).suffix.lower()
    mime = "image/png" if ext == ".png" else "image/jpeg"

    try:
        with open(screenshot_path, "rb") as f:
            data = f.read()
    except Exception as e:
        return {"steal_worthy": False, "what": "", "category": "기타", "priority": "참고만",
                "report_to_lian": f"스크린샷 읽기 실패: {e}"}

    try:
        image_part = types.Part.from_bytes(data=data, mime_type=mime)
        response = client.models.generate_content(
            model=GEMINI_FLASH,
            contents=[image_part, INSTA_ANALYSIS_SYSTEM],
        )
        return _parse_json(response.text or "")
    except Exception as e:
        return {"steal_worthy": False, "what": "", "category": "기타", "priority": "참고만",
                "report_to_lian": f"Gemini 분석 실패: {e}"}


def load_urls_from_txt(file_path: str) -> list:
    """txt 파일에서 URL 파싱 (빈 줄, 중복 제거)."""
    urls = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    if line.startswith("http"):
                        urls.append(line)
    except Exception as e:
        print(f"파일 읽기 실패: {e}")
        return []

    # 중복 제거 (순서 유지)
    seen = set()
    unique_urls = []
    for url in urls:
        if url not in seen:
            unique_urls.append(url)
            seen.add(url)

    return unique_urls


def write_report(results: list):
    """보고사항들.md 업데이트."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [f"## 서연 (인스타 분석) — {now}\n"]

    total = len(results)
    steal_worthy = [r for r in results if r.get("steal_worthy")]

    lines.append(f"링크 {total}개 분석 완료. 즉시 적용 {len(steal_worthy)}개 발견.\n")

    # 즉시 적용 (priority=즉시)
    immediate = [r for r in steal_worthy if r.get("priority") == "즉시"]
    if immediate:
        lines.append("### 즉시 적용\n")
        for i, r in enumerate(immediate, 1):
            lines.append(f"**링크 {i}** — `{r.get('category', '기타')}`")
            lines.append(f"- 훔칠 것: {r.get('what', '')}")
            lines.append(f"- 적용 방법: {r.get('how_to_apply', '')}")
            lines.append(f"- {r.get('report_to_lian', '')}")
            lines.append("")

    # 나중에 (priority=나중에/참고만)
    later = [r for r in steal_worthy if r.get("priority") in ["나중에", "참고만"]]
    if later:
        lines.append("### 참고 및 나중에\n")
        for r in later:
            lines.append(f"- **{r.get('category', '기타')}**: {r.get('what', '')}")

    # 버린 것
    not_worthy = [r for r in results if not r.get("steal_worthy")]
    if not_worthy:
        lines.append("\n### 분석 불가\n")
        lines.append(f"{len(not_worthy)}개 항목 분석 불가 또는 적용 불가.\n")

    lines.append("---\n")
    new_section = "\n".join(lines)

    if os.path.exists(REPORT_FILE):
        with open(REPORT_FILE, "r", encoding="utf-8") as f:
            existing = f.read()
        split = existing.split("---\n", 1)
        result = (split[0] + "---\n\n" + new_section + split[1]) if len(split) == 2 else (existing + "\n" + new_section)
    else:
        header = "# 보고사항들\n\n> 에이전트들이 리안한테 직접 보고하는 공간.\n\n---\n\n"
        result = header + new_section

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(result)


async def process_url(url: str, idx: int, total: int) -> dict:
    """URL을 스크린샷으로 캡처 + 분석."""
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    screenshot_path = os.path.join(SCREENSHOT_DIR, f"insta_{idx:02d}.png")

    print(f"[{idx}/{total}] 캡처 중: {url}", flush=True)

    try:
        await browse(url, screenshot_path)
        print(f"[{idx}/{total}] 분석 중...", flush=True)
        result = analyze_screenshot(screenshot_path, url)
        result["url"] = url
        return result
    except Exception as e:
        print(f"[{idx}/{total}] 오류: {e}", flush=True)
        return {
            "url": url,
            "steal_worthy": False,
            "what": "",
            "category": "기타",
            "priority": "참고만",
            "report_to_lian": f"처리 실패: {e}"
        }


async def main(txt_file: str):
    """메인 실행."""
    urls = load_urls_from_txt(txt_file)

    if not urls:
        print(f"URL 없음: {txt_file}")
        return

    print(f"\n{'='*60}")
    print(f"서연 (인스타 분석) | URL {len(urls)}개 발견")
    print(f"{'='*60}\n")

    results = []
    for i, url in enumerate(urls, 1):
        result = await process_url(url, i, len(urls))
        results.append(result)
        if i < len(urls):
            await asyncio.sleep(1)  # 인스타 차단 방지

    write_report(results)

    print(f"\n{'='*60}")
    print(f"완료. 보고사항들.md 업데이트됨.")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python utils/insta_analyze.py <링크_목록.txt>")
        sys.exit(1)

    txt_file = sys.argv[1]
    if not os.path.exists(txt_file):
        print(f"파일 없음: {txt_file}")
        sys.exit(1)

    asyncio.run(main(txt_file))
