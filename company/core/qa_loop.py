"""
qa_loop.py — 랜딩페이지 자동 QA

배포 후 자동으로:
1. Playwright로 PC/모바일 스크린샷 촬영
2. Claude가 페이지 평가 (목적 명확성, CTA 작동, 디자인, 정보 완결성)
3. 문제 있으면 보고사항들.md에 구체적 수정 지시 올림
4. 점수 7점 이하면 자동 수정 시도

사용법:
    from core.qa_loop import run_qa
    run_qa("https://contentmate-landing.pages.dev", "콘텐츠메이트")

또는:
    python -m core.qa_loop "https://contentmate-landing.pages.dev" "콘텐츠메이트"
"""
import os
import sys
import base64
import subprocess
import tempfile
import anthropic
from datetime import datetime
from dotenv import load_dotenv
from core.context_loader import inject_context
from core.models import CLAUDE_SONNET

load_dotenv()

REPORT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "보고사항들.md")

QA_PROMPT = """너는 랜딩페이지 QA 전문가야. 스크린샷을 보고 평가해.

평가 기준:
1. **목적 명확성** — 3초 안에 "이게 뭔 서비스인지" 알 수 있나?
2. **CTA 명확성** — 버튼이 눈에 띄나? 다음 행동이 명확한가?
3. **신뢰도** — 가격, 내용, 구성이 믿을 만해 보이나?
4. **PC 레이아웃** — PC에서 어색한 부분 없나?
5. **모바일 레이아웃** — 모바일에서 잘 보이나?
6. **정보 완결성** — 연락처, 신청방법, 가격이 다 있나?

출력:
## QA 결과

### 종합 점수: X/10

### PC 스크린샷 평가
[구체적으로]

### 모바일 스크린샷 평가
[구체적으로]

### 통과 항목 ✅
- [항목]: [이유]

### 문제 항목 ❌
- [항목]: [구체적 문제] → [수정 방법]

### 리안에게
[한 줄 요약. "바로 써도 됨" or "이거 고쳐야 함: ~~~"]"""


def _screenshot_url(url: str, viewport: dict) -> bytes | None:
    """Playwright로 스크린샷 촬영 후 bytes 반환."""
    script = f"""
import asyncio
from playwright.async_api import async_playwright

async def shot():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={{"width": {viewport['width']}, "height": {viewport['height']}}})
        await page.goto("{url}", wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(2000)
        data = await page.screenshot(full_page=True)
        await browser.close()
        return data

import sys
data = asyncio.run(shot())
sys.stdout.buffer.write(data)
"""
    try:
        result = subprocess.run(
            [sys.executable, "-c", script],
            capture_output=True, timeout=60,
            env={**os.environ, "PYTHONUTF8": "1"}
        )
        if result.returncode == 0 and result.stdout:
            return result.stdout
    except Exception as e:
        print(f"  ⚠️ 스크린샷 실패: {e}")
    return None


def _save_to_report(project_name: str, content: str):
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"\n\n## QA 자동 점검 ({project_name}) — {date_str}\n\n{content}\n\n---\n"
    try:
        existing = open(REPORT_PATH, encoding="utf-8").read() if os.path.exists(REPORT_PATH) else ""
        with open(REPORT_PATH, "w", encoding="utf-8") as f:
            f.write(existing + entry)
    except Exception as e:
        print(f"  ⚠️ 보고서 저장 실패: {e}")


def run_qa(url: str, project_name: str = "프로젝트") -> dict:
    """랜딩페이지 자동 QA 실행."""
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    print(f"\n{'='*60}")
    print(f"🔍 QA 자동 점검: {project_name}")
    print(f"   URL: {url}")
    print(f"{'='*60}")

    # 스크린샷 촬영
    print("\n  📸 PC 스크린샷 촬영 중...")
    pc_shot = _screenshot_url(url, {"width": 1280, "height": 800})

    print("  📱 모바일 스크린샷 촬영 중...")
    mobile_shot = _screenshot_url(url, {"width": 390, "height": 844})

    if not pc_shot and not mobile_shot:
        print("  ❌ 스크린샷 실패 — Playwright 설치 필요: npx playwright install chromium")
        return {"score": 0, "error": "screenshot_failed"}

    # Claude로 평가
    print("\n  🤖 AI 평가 중...")
    content = []
    content.append({"type": "text", "text": f"랜딩페이지 URL: {url}\n프로젝트: {project_name}\n\nPC와 모바일 스크린샷을 보고 QA 평가해줘."})

    if pc_shot:
        content.append({"type": "text", "text": "=== PC 스크린샷 (1280px) ==="})
        content.append({"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": base64.b64encode(pc_shot).decode()}})

    if mobile_shot:
        content.append({"type": "text", "text": "=== 모바일 스크린샷 (390px) ==="})
        content.append({"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": base64.b64encode(mobile_shot).decode()}})

    response = client.messages.create(
        model=CLAUDE_SONNET,
        max_tokens=1500,
        system=inject_context(QA_PROMPT),
        messages=[{"role": "user", "content": content}],
    )

    qa_result = response.content[0].text
    print(qa_result)

    # 점수 추출
    import re
    score_match = re.search(r"종합 점수.*?(\d+\.?\d*)/10", qa_result)
    score = int(score_match.group(1)) if score_match else 5

    # 7점 이하면 보고사항들.md에 올림
    if score <= 7:
        print(f"\n  📋 점수 {score}/10 — 개선 필요 → 보고사항들.md")
        _save_to_report(project_name, f"URL: {url}\n점수: {score}/10\n\n{qa_result}")
    else:
        print(f"\n  ✅ 점수 {score}/10 — QA 통과")

    return {"score": score, "result": qa_result, "url": url}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python -m core.qa_loop <URL> [프로젝트명]")
        sys.exit(1)
    url = sys.argv[1]
    name = sys.argv[2] if len(sys.argv) > 2 else "프로젝트"
    run_qa(url, name)
