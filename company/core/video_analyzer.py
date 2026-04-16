"""
인스타 콘텐츠 분석기 — Gemini로 영상/이미지 분석 + 리안 컴퍼니 업그레이드 관련성 판단
- 폴더 하나 = 인스타 포스트 하나 (이미지 여러 장 or 영상)
- 사용법: python core/video_analyzer.py [루트폴더]
- 기본: LAINCP/업그레이드 해야할거 (하위 폴더 전체 스캔)
"""
import os
import sys
import time
import io
import base64

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

from google import genai
from google.genai import types

MODEL = "gemini-2.5-flash"

VIDEO_EXT = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v"}
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
VIDEO_MIME = {".mp4": "video/mp4", ".mov": "video/quicktime", ".avi": "video/x-msvideo",
              ".mkv": "video/x-matroska", ".webm": "video/webm", ".m4v": "video/mp4"}
IMAGE_MIME = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
              ".webp": "image/webp", ".gif": "image/gif"}

ANALYZE_PROMPT = """이 인스타그램 포스트를 보고 아래 형식으로 분석해줘.
리안 컴퍼니는 "아이디어 하나 던지면 AI들이 기획→설계→개발→마케팅까지 자동 완성"하는 멀티AI 시스템이야.

## 핵심 내용
[이 포스트가 다루는 내용 2-3줄. 핵심만]

## 주요 개념/기법
[구체적으로 어떤 기술/방법론/툴인지. 없으면 "없음"]

## 판정
[쓸만함 / 참고용 / 필요없음] — 이유 한 줄

## 적용 포인트
[쓸만함이면: 어디에 어떻게 바로 쓸 수 있는지]
[참고용이면: 나중에 참고할 만한 아이디어]
[필요없음이면: 스킵]
"""


def get_media_files(folder: str) -> list:
    files = []
    for f in sorted(os.listdir(folder)):
        if f.startswith("_"):
            continue
        ext = os.path.splitext(f)[1].lower()
        if ext in VIDEO_EXT or ext in IMAGE_EXT:
            files.append(os.path.join(folder, f))
    return files


def get_subfolders(root: str) -> list:
    subs = []
    for name in sorted(os.listdir(root)):
        path = os.path.join(root, name)
        if os.path.isdir(path):
            subs.append((name, path))
    return subs


def build_image_part(image_path: str) -> types.Part:
    ext = os.path.splitext(image_path)[1].lower()
    mime = IMAGE_MIME.get(ext, "image/jpeg")
    with open(image_path, "rb") as f:
        data = f.read()
    return types.Part.from_bytes(data=data, mime_type=mime)


def upload_video(client, video_path: str):
    ext = os.path.splitext(video_path)[1].lower()
    mime = VIDEO_MIME.get(ext, "video/mp4")
    print("    [영상 업로드 중...]", end="", flush=True)
    with open(video_path, "rb") as f:
        uploaded = client.files.upload(
            file=f,
            config=types.UploadFileConfig(display_name="video", mime_type=mime)
        )
    while uploaded.state.name == "PROCESSING":
        time.sleep(2)
        uploaded = client.files.get(name=uploaded.name)
    print(" 완료")
    if uploaded.state.name == "FAILED":
        raise RuntimeError("영상 업로드 실패")
    return uploaded


def analyze_folder(client, folder_name: str, folder_path: str) -> dict:
    print(f"\n{'='*60}")
    print(f"  [{folder_name}] 분석 중...")
    print(f"{'='*60}")

    media_files = get_media_files(folder_path)
    if not media_files:
        return {"folder": folder_name, "files": [], "result": "미디어 파일 없음", "verdict": "스킵"}

    for f in media_files:
        print(f"    파일: {os.path.basename(f)}")

    # 콘텐츠 파트 구성
    contents = []
    uploaded_refs = []

    for path in media_files:
        ext = os.path.splitext(path)[1].lower()
        if ext in IMAGE_EXT:
            contents.append(build_image_part(path))
        elif ext in VIDEO_EXT:
            uploaded = upload_video(client, path)
            contents.append(uploaded)
            uploaded_refs.append(uploaded)

    contents.append(ANALYZE_PROMPT)

    print("    [분석 중...]")
    response = client.models.generate_content(
        model=MODEL,
        contents=contents,
    )
    result_text = response.text or ""
    print(result_text)

    # 판정 추출
    verdict = "알수없음"
    for line in result_text.splitlines():
        if "## 판정" in line:
            continue
        if "쓸만함" in line:
            verdict = "쓸만함"
            break
        elif "참고용" in line:
            verdict = "참고용"
            break
        elif "필요없음" in line:
            verdict = "필요없음"
            break

    # 업로드 파일 정리
    for ref in uploaded_refs:
        try:
            client.files.delete(name=ref.name)
        except Exception:
            pass

    return {
        "folder": folder_name,
        "files": [os.path.basename(f) for f in media_files],
        "result": result_text,
        "verdict": verdict
    }


def save_summary(root: str, results: list):
    output_path = os.path.join(root, "_전체분석결과.md")

    useful = [r for r in results if r["verdict"] == "쓸만함"]
    ref = [r for r in results if r["verdict"] == "참고용"]
    skip = [r for r in results if r["verdict"] == "필요없음"]
    err = [r for r in results if r["verdict"] not in ("쓸만함", "참고용", "필요없음")]

    lines = ["# 업그레이드 자료 분석 결과\n\n"]
    lines.append(f"총 {len(results)}개 | **쓸만함: {len(useful)}개** | 참고용: {len(ref)}개 | 스킵: {len(skip)}개\n\n")

    if useful:
        lines.append("## 바로 쓸 수 있는 것들\n")
        for r in useful:
            lines.append(f"- **[{r['folder']}]** {', '.join(r['files'])}\n")
        lines.append("\n")

    if ref:
        lines.append("## 나중에 참고할 것들\n")
        for r in ref:
            lines.append(f"- **[{r['folder']}]** {', '.join(r['files'])}\n")
        lines.append("\n")

    lines.append("---\n\n## 상세 분석\n\n")
    for r in results:
        lines.append(f"### [{r['folder']}] {', '.join(r['files'])}\n\n")
        lines.append(r["result"])
        lines.append("\n\n---\n\n")

    with open(output_path, "w", encoding="utf-8") as f:
        f.writelines(lines)

    print(f"\n[저장] {output_path}")
    return output_path


def main():
    default_root = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "업그레이드 해야할거"
    )
    root = sys.argv[1] if len(sys.argv) > 1 else default_root

    if not os.path.isdir(root):
        print(f"폴더 없음: {root}")
        sys.exit(1)

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("GOOGLE_API_KEY 없음. .env 확인해.")
        sys.exit(1)

    client = genai.Client(api_key=api_key)
    subfolders = get_subfolders(root)

    if not subfolders:
        # 하위 폴더 없으면 루트 자체를 단일 포스트로
        results = []
        try:
            r = analyze_folder(client, os.path.basename(root), root)
            results.append(r)
        except Exception as e:
            results.append({"folder": os.path.basename(root), "files": [], "result": f"오류: {e}", "verdict": "오류"})
    else:
        print(f"\n총 {len(subfolders)}개 폴더 발견")
        results = []
        for i, (name, path) in enumerate(subfolders, 1):
            print(f"\n[{i}/{len(subfolders)}]", end="")
            try:
                r = analyze_folder(client, name, path)
            except Exception as e:
                r = {"folder": name, "files": [], "result": f"오류: {e}", "verdict": "오류"}
                print(f"\n  오류: {e}")
            results.append(r)

    # 최종 요약
    print(f"\n\n{'='*60}")
    print("  전체 분석 완료")
    print(f"{'='*60}")
    useful = [r for r in results if r["verdict"] == "쓸만함"]
    ref = [r for r in results if r["verdict"] == "참고용"]
    skip = [r for r in results if r["verdict"] == "필요없음"]
    print(f"  쓸만함:  {len(useful)}개  {[r['folder'] for r in useful]}")
    print(f"  참고용:  {len(ref)}개  {[r['folder'] for r in ref]}")
    print(f"  필요없음: {len(skip)}개  {[r['folder'] for r in skip]}")

    save_summary(root, results)


if __name__ == "__main__":
    main()
