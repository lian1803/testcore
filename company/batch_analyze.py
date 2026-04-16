"""
인스타 링크 + 자료들 폴더 일괄 분석
사용법: python batch_analyze.py
"""
import sys
import os
import re
import time
import tempfile
import base64
from pathlib import Path
from dotenv import load_dotenv
import google.genai as genai

load_dotenv()

BASE = Path(__file__).parent
COOKIE_FILE = BASE / "instagram_cookies.txt"
GALLERY_DL = BASE / "venv/Scripts/gallery-dl.exe"
JARYO_DIR = BASE.parent / "자료들"
REPORT_FILE = BASE.parent / "보고사항들.md"

INSTAGRAM_TXT = Path(r"C:\Users\lian1\Desktop\새 텍스트 문서 (7).txt")


# ─────────────────────────────────────────────
# 공통 유틸
# ─────────────────────────────────────────────

def get_client():
    return genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


def save_report(title: str, content: str):
    from datetime import datetime
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(REPORT_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n---\n## {title} — {ts}\n{content}\n")
    print(f"  -> 저장됨: {title}")


def upload_video(client, path: Path):
    print(f"  [영상 업로드] {path.name[:50]}...")
    # 한글 파일명 → ASCII 임시 파일로 복사 후 업로드
    suffix = path.suffix.lower()
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp_path = Path(tmp.name)
    import shutil
    shutil.copy2(path, tmp_path)
    try:
        uploaded = client.files.upload(file=tmp_path)
        while uploaded.state.name == "PROCESSING":
            time.sleep(2)
            uploaded = client.files.get(name=uploaded.name)
        if uploaded.state.name == "FAILED":
            raise RuntimeError("업로드 실패")
    finally:
        tmp_path.unlink(missing_ok=True)
    return uploaded


def delete_uploaded(client, uploaded_list):
    for uf in uploaded_list:
        try:
            client.files.delete(name=uf.name)
        except Exception:
            pass


ANALYSIS_PROMPT = """인스타그램/숏폼 콘텐츠를 분석해줘.

[분석 항목]
1. 이 콘텐츠는 뭘 다루는가 (한 줄 요약)
2. 콘텐츠 구성 방식 (흐름, 디자인, 편집 스타일)
3. 카피라이팅 전략 (후킹, 어투, 구조)
4. 우리한테 적용 가능한 것 — 아래 두 가지 관점 모두 판단:
   A. 리안 컴퍼니 시스템/도구 개선 (우리가 직접 쓸 수 있는 기능, 자동화, Claude Code 활용법, AI 도구 등)
   B. 클라이언트 납품/마케팅 대행 (콘텐츠 포맷, 카피, 영업 방식)
   → 해당 없으면 "해당 없음"으로 명시. 억지로 끼워맞추지 마라.
5. 바로 훔쳐쓸 수 있는 것 (템플릿, 문구, 포맷, 도구 구체적으로)

짧고 날카롭게. 이론 말고 바로 쓸 수 있는 것 위주로."""


# ─────────────────────────────────────────────
# 1. 인스타그램 배치
# ─────────────────────────────────────────────

def extract_unique_urls(txt_path: Path) -> list[str]:
    text = txt_path.read_text(encoding="utf-8")
    seen = {}
    for url in re.findall(r'https://www\.instagram\.com/(?:p|reel)/[^\s]+', text):
        post_id = re.search(r'(?:p|reel)/([^/?]+)', url).group(1)
        if post_id not in seen:
            seen[post_id] = url.split('?')[0]
    return list(seen.values())


def download_post(url: str, output_dir: Path) -> list[Path]:
    import subprocess
    result = subprocess.run(
        [str(GALLERY_DL), "--cookies", str(COOKIE_FILE),
         "-D", str(output_dir), "--filename", "{num}.{extension}", url],
        capture_output=True, text=True
    )
    files = sorted(output_dir.glob("*"))
    return [f for f in files if f.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp", ".mp4", ".mov"}]


def get_caption(url: str) -> str:
    import subprocess
    result = subprocess.run(
        [str(GALLERY_DL), "--cookies", str(COOKIE_FILE), "--print", "{description}", url],
        capture_output=True, text=True
    )
    return result.stdout.strip() or "(캡션 없음)"


def analyze_instagram_post(url: str, client) -> str:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        files = download_post(url, tmp_path)
        caption = get_caption(url)

        image_files = [f for f in files if f.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}]
        video_files = [f for f in files if f.suffix.lower() in {".mp4", ".mov"}]

        parts = []
        for img in image_files[:10]:
            parts.append(genai.types.Part.from_bytes(data=img.read_bytes(), mime_type="image/jpeg"))

        uploaded = []
        for vid in video_files[:2]:
            try:
                uf = upload_video(client, vid)
                parts.append(genai.types.Part.from_uri(file_uri=uf.uri, mime_type=uf.mime_type))
                uploaded.append(uf)
            except Exception as e:
                print(f"  [영상 스킵] {e}")

        content_info = f"이미지 {len(image_files)}장, 영상 {len(video_files)}개 | 캡션: {caption[:100]}"
        prompt = f"{ANALYSIS_PROMPT}\n\n[캡션]\n{caption}"

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=([prompt] + parts) if parts else [prompt]
        )
        delete_uploaded(client, uploaded)
        return f"**URL**: {url}\n**내용**: {content_info}\n\n{response.text}"


def run_instagram_batch():
    print("\n" + "="*60)
    print("인스타그램 배치 분석 시작")
    print("="*60)

    urls = extract_unique_urls(INSTAGRAM_TXT)
    # 이미 분석한 것 제외
    already_done = {"DVz5qUgkbCv"}
    urls = [u for u in urls if not any(d in u for d in already_done)]

    print(f"총 {len(urls)}개 분석 예정")
    client = get_client()

    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] {url}")
        try:
            result = analyze_instagram_post(url, client)
            save_report(f"인스타 분석 {i}/{len(urls)}", result)
        except Exception as e:
            print(f"  [오류] {e}")
            save_report(f"인스타 분석 {i}/{len(urls)} (오류)", f"URL: {url}\n오류: {e}")
        time.sleep(3)  # API 쿨다운


# ─────────────────────────────────────────────
# 2. 자료들 폴더 배치
# ─────────────────────────────────────────────

def analyze_images(image_files: list[Path], client) -> str:
    parts = []
    for img in image_files[:10]:
        ext = img.suffix.lower()
        mime = "image/png" if ext == ".png" else "image/jpeg"
        parts.append(genai.types.Part.from_bytes(data=img.read_bytes(), mime_type=mime))

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[ANALYSIS_PROMPT] + parts
    )
    return response.text


def analyze_video_file(video_path: Path, client) -> str:
    uf = upload_video(client, video_path)
    try:
        part = genai.types.Part.from_uri(file_uri=uf.uri, mime_type=uf.mime_type)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[ANALYSIS_PROMPT, part]
        )
        return response.text
    finally:
        delete_uploaded(client, [uf])


def analyze_text_file(txt_path: Path, client) -> str:
    content = txt_path.read_text(encoding="utf-8")[:8000]
    prompt = f"""유튜브 영상 트랜스크립트를 분석해줘.

[내용]
{content}

[분석 항목]
1. 영상 핵심 주제 (한 줄)
2. 주요 인사이트 3가지
3. 우리 사업에 적용할 포인트 (온라인 마케팅 대행 / AI 자동화 관점)
4. 바로 활용할 수 있는 것

짧고 날카롭게."""
    response = client.models.generate_content(model="gemini-2.5-flash", contents=[prompt])
    return response.text


def run_jaryo_batch():
    print("\n" + "="*60)
    print("자료들 폴더 분석 시작")
    print("="*60)

    client = get_client()
    skip_folders = {"10", "12"}  # 10은 이미 분석됨, 12는 비어있음

    for folder in sorted(JARYO_DIR.iterdir()):
        if not folder.is_dir() or folder.name in skip_folders:
            continue

        print(f"\n[폴더 {folder.name}]")
        images = sorted(folder.glob("*.png")) + sorted(folder.glob("*.jpg")) + sorted(folder.glob("*.jpeg"))
        videos = sorted(folder.glob("*.mp4")) + sorted(folder.glob("*.mov"))
        txts = sorted(folder.glob("*.txt"))

        try:
            if images:
                print(f"  이미지 {len(images)}장 분석 중...")
                result = analyze_images(images, client)
                save_report(f"자료들/{folder.name} 이미지 분석", result)

            for vid in videos:
                print(f"  영상 분석 중: {vid.name[:50]}...")
                result = analyze_video_file(vid, client)
                save_report(f"자료들/{folder.name} 영상 분석", result)
                time.sleep(2)

            for txt in txts:
                print(f"  텍스트 분석 중: {txt.name}...")
                result = analyze_text_file(txt, client)
                save_report(f"자료들/{folder.name} 유튜브 분석 ({txt.name})", result)

        except Exception as e:
            print(f"  [오류] {e}")
            save_report(f"자료들/{folder.name} (오류)", str(e))

        time.sleep(3)


# ─────────────────────────────────────────────
# 메인
# ─────────────────────────────────────────────

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"

    if mode in ("all", "instagram"):
        run_instagram_batch()

    if mode in ("all", "jaryo"):
        run_jaryo_batch()

    print("\n\n전체 완료. 보고사항들.md 확인해.")
