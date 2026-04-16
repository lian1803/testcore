#!/usr/bin/env python3
"""
Video Cloner — 인스타/유튜브 URL → 디자인 스펙 추출 → HTML 재현

사용법:
  python utils/video_cloner.py "https://www.instagram.com/reel/..."
  python utils/video_cloner.py "https://www.youtube.com/watch?v=..."
"""

import sys
import os
import json
import re
from pathlib import Path
from urllib.parse import urlparse
import time

import yt_dlp
from google import genai
from google.genai import types
from anthropic import Anthropic

from dotenv import load_dotenv

load_dotenv()

VENV_PATH = Path(__file__).parent.parent / "venv"
TMP_DIR = Path(__file__).parent / "video_cloner_tmp"
OUTPUT_DIR = Path(__file__).parent / "video_cloner_output"
INSTAGRAM_COOKIES = Path(__file__).parent.parent / "instagram_cookies.txt"

TMP_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

gemini_client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def check_dependencies():
    """필수 패키지 확인"""
    missing = []
    try:
        import yt_dlp
    except ImportError:
        missing.append("yt-dlp")

    try:
        from google import genai as _genai
    except ImportError:
        missing.append("google-genai")

    try:
        import anthropic
    except ImportError:
        missing.append("anthropic")

    if missing:
        venv_python = str(VENV_PATH / ("Scripts" if sys.platform == "win32" else "bin") / "python")
        print(f"❌ 필수 패키지 설치 필요: {', '.join(missing)}")
        print(f"\n설치 명령어:")
        for pkg in missing:
            print(f"  {venv_python} -m pip install {pkg}")
        sys.exit(1)


def extract_url_id(url):
    """URL에서 고유 ID 추출"""
    if "instagram.com" in url:
        match = re.search(r'/reel/([A-Za-z0-9_-]+)/', url)
        if match:
            return f"insta_{match.group(1)}"
        match = re.search(r'/p/([A-Za-z0-9_-]+)/', url)
        if match:
            return f"insta_{match.group(1)}"
    elif "youtube.com" in url or "youtu.be" in url:
        match = re.search(r'(?:youtube\.com/watch\?v=|youtu\.be/)([A-Za-z0-9_-]+)', url)
        if match:
            return f"yt_{match.group(1)}"

    return f"video_{int(time.time())}"


def download_video(url):
    """[Step 1/4] yt-dlp로 영상 다운로드"""
    print("\n[Step 1/4] 영상 다운로드 중...")

    url_id = extract_url_id(url)
    output_path = TMP_DIR / f"{url_id}.mp4"

    if output_path.exists():
        print(f"  ✓ 이미 다운로드됨: {output_path}")
        return str(output_path), url_id

    ydl_opts = {
        "format": "best[ext=mp4][height<=1080]/best[ext=mp4]",
        "quiet": True,
        "no_warnings": True,
        "outtmpl": str(TMP_DIR / f"{url_id}.%(ext)s"),
    }

    if "instagram.com" in url and INSTAGRAM_COOKIES.exists():
        ydl_opts["cookiefile"] = str(INSTAGRAM_COOKIES)

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            duration_sec = info.get("duration", 0)

            if duration_sec > 600:
                print(f"  ⚠️  영상 길이: {duration_sec//60}분 (10분 이상 — Gemini 처리 시간 오래 걸릴 수 있음)")
            else:
                print(f"  ✓ 영상 다운로드 완료 ({duration_sec}초)")

        return str(output_path), url_id

    except Exception as e:
        print(f"  ❌ 다운로드 실패: {e}")
        sys.exit(1)


def extract_design_spec(video_path, url_id):
    """[Step 2/4] Gemini 2.5 Flash로 디자인 스펙 추출"""
    print("\n[Step 2/4] Gemini로 디자인 스펙 분석 중...")

    spec_path = OUTPUT_DIR / f"{url_id}_spec.json"

    try:
        ext = Path(video_path).suffix.lower()
        mime_map = {".mp4": "video/mp4", ".mov": "video/quicktime", ".avi": "video/x-msvideo",
                    ".mkv": "video/x-matroska", ".webm": "video/webm", ".m4v": "video/mp4"}
        mime_type = mime_map.get(ext, "video/mp4")

        print("  → Gemini File API에 업로드 중...")
        with open(video_path, "rb") as f:
            video_file = gemini_client.files.upload(
                file=f,
                config=types.UploadFileConfig(display_name=Path(video_path).name, mime_type=mime_type),
            )

        while video_file.state.name == "PROCESSING":
            time.sleep(2)
            video_file = gemini_client.files.get(name=video_file.name)

        if video_file.state.name == "FAILED":
            print("  ❌ Gemini 파일 처리 실패")
            sys.exit(1)

        print("  → 디자인 스펙 추출 중...")

        prompt = """너는 최고의 UI/UX 분석 전문가야. 이 영상을 보고 웹사이트를 완벽하게 재현하기 위한 모든 디자인 스펙을 추출해줘.

다음을 JSON 형식으로 정확히 추출해:
{
  "overview": "사이트 전체 느낌/컨셉 1~2줄 요약",
  "colors": {
    "background": ["#HEX"],
    "primary": ["#HEX"],
    "text": ["#HEX"],
    "accent": ["#HEX"]
  },
  "typography": {
    "heading": {"family": "폰트명 (Google Fonts)", "weight": "700", "size_range": "clamp(2rem, 5vw, 4rem)"},
    "body": {"family": "폰트명", "weight": "400", "size_range": "1rem~1.2rem"},
    "accent_text": {"style": "italic 또는 특수 스타일", "family": "폰트명"}
  },
  "layout": {
    "structure": "sections 설명 (Hero → Feature → CTA 형식)",
    "max_width": "px 또는 vw",
    "grid": "grid-template-columns 값",
    "spacing": "주요 padding/margin 패턴"
  },
  "animations": [
    {"element": "어떤 요소", "type": "fade-in/slide/parallax/etc", "timing": "0.3s ease-out 등", "trigger": "scroll/hover/load"}
  ],
  "interactions": [
    {"element": "어떤 요소", "event": "hover/click/scroll", "effect": "구체적 효과"}
  ],
  "background_effects": "배경 효과 상세 (gradient, shader, video, 패턴 등)",
  "special_elements": ["특이한 UI 요소들 목록"],
  "css_variables": {
    "--bg-primary": "#값",
    "--text-primary": "#값"
  },
  "recreation_notes": "이 디자인을 재현할 때 주의할 점들"
}

색상은 반드시 실제 HEX 코드로, 폰트는 Google Fonts 이름으로, 애니메이션 타이밍은 CSS transition 값으로 적어줘.
JSON만 반환해. 설명은 빼고."""

        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[types.Part.from_uri(file_uri=video_file.uri, mime_type=mime_type), prompt],
        )

        gemini_client.files.delete(name=video_file.name)

        spec_text = response.text
        json_match = re.search(r'\{.*\}', spec_text, re.DOTALL)

        if json_match:
            spec_json = json.loads(json_match.group())
            with open(spec_path, "w", encoding="utf-8") as f:
                json.dump(spec_json, f, ensure_ascii=False, indent=2)
            print(f"  ✓ 디자인 스펙 추출 완료: {spec_path}")
            return spec_json
        else:
            print("  ❌ JSON 파싱 실패")
            sys.exit(1)

    except Exception as e:
        print(f"  ❌ Gemini 처리 실패: {e}")
        print(f"  재시도 중...")
        time.sleep(3)
        return extract_design_spec(video_path, url_id)


def generate_clone_code(spec_json):
    """[Step 3/4] Claude로 HTML 코드 생성"""
    print("\n[Step 3/4] Claude로 HTML 코드 생성 중...")

    spec_str = json.dumps(spec_json, ensure_ascii=False, indent=2)

    prompt = f"""너는 최고의 프론트엔드 개발자야. 아래 디자인 스펙을 보고 완전히 동일한 HTML/CSS/JS 단일 파일을 만들어줘.

[디자인 스펙]
{spec_str}

요구사항:
- 단일 HTML 파일 (외부 CSS/JS 없이, 모두 인라인)
- 애니메이션/인터랙션 완전 구현
- Lenis smooth scroll 적용 (CDN)
- 커스텀 커서 (dot + ring)
- 배경 효과 정확히 재현 (shader면 WebGL, gradient면 CSS)
- 반응형 (clamp() 타이포그래피)
- 더미 콘텐츠로 실제 레이아웃 채우기
- 완성된 HTML 코드만 출력 (설명 없이)
- <!DOCTYPE html> 부터 시작해서 </html> 까지"""

    try:
        response = anthropic_client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=8000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        html_code = response.content[0].text

        if "<!DOCTYPE" not in html_code.upper():
            print("  ❌ HTML 생성 실패 (유효한 HTML 아님)")
            sys.exit(1)

        print(f"  ✓ HTML 코드 생성 완료")
        return html_code

    except Exception as e:
        print(f"  ❌ Claude 처리 실패: {e}")
        sys.exit(1)


def save_results(url_id, spec_json, html_code):
    """[Step 4/4] 결과 저장"""
    print("\n[Step 4/4] 결과 저장 중...")

    html_path = OUTPUT_DIR / f"{url_id}_clone.html"

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_code)

    print(f"  ✓ HTML 저장: {html_path}")

    print(f"\n{'='*60}")
    print(f"✅ 완료!")
    print(f"{'='*60}")
    print(f"\n📋 디자인 스펙: {OUTPUT_DIR / f'{url_id}_spec.json'}")
    print(f"🎨 HTML 클론: {html_path}")
    print(f"\n🔗 브라우저에서 열기: file:///{html_path}")
    print(f"\nℹ️  spec.json을 수정하고 다시 생성하려면:")
    print(f"  python utils/video_cloner.py --regenerate-html {url_id}")


def regenerate_html(url_id):
    """기존 spec에서 HTML만 다시 생성"""
    spec_path = OUTPUT_DIR / f"{url_id}_spec.json"

    if not spec_path.exists():
        print(f"❌ 스펙 파일을 찾을 수 없음: {spec_path}")
        sys.exit(1)

    with open(spec_path, "r", encoding="utf-8") as f:
        spec_json = json.load(f)

    html_code = generate_clone_code(spec_json)
    save_results(url_id, spec_json, html_code)


def main():
    check_dependencies()

    if len(sys.argv) < 2:
        print("사용법:")
        print("  python utils/video_cloner.py '<URL>'")
        print("  python utils/video_cloner.py --regenerate-html '<URL_ID>'")
        print("\n예시:")
        print("  python utils/video_cloner.py 'https://www.instagram.com/reel/...'")
        print("  python utils/video_cloner.py --regenerate-html 'insta_abc123'")
        sys.exit(1)

    if sys.argv[1] == "--regenerate-html":
        if len(sys.argv) < 3:
            print("❌ URL ID를 입력하세요")
            sys.exit(1)
        regenerate_html(sys.argv[2])
        return

    url = sys.argv[1]

    if not url.startswith(("http://", "https://")):
        print("❌ 유효한 URL을 입력하세요 (http:// 또는 https://로 시작)")
        sys.exit(1)

    print(f"\n🎬 Video Cloner 시작")
    print(f"URL: {url}")

    video_path, url_id = download_video(url)
    spec_json = extract_design_spec(video_path, url_id)
    html_code = generate_clone_code(spec_json)
    save_results(url_id, spec_json, html_code)


if __name__ == "__main__":
    main()
