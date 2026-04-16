"""
분석팀 — Gemini 비전으로 이미지/영상 분석
자료들/ 폴더에 넣은 이미지/영상을 읽고 knowledge/base/에 저장할 지식 추출.
(원래 계획: qwen3-vl 로컬 → 현재: Gemini 비전으로 동일 기능)
"""
import os
import time
import json
import re
from pathlib import Path
from google import genai
from google.genai import types
from core.models import GEMINI_FLASH

IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"}
VIDEO_EXT = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v"}

IMAGE_MIME = {
    ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
    ".webp": "image/webp", ".gif": "image/gif", ".bmp": "image/bmp",
}
VIDEO_MIME = {
    ".mp4": "video/mp4", ".mov": "video/quicktime", ".avi": "video/x-msvideo",
    ".mkv": "video/x-matroska", ".webm": "video/webm", ".m4v": "video/mp4",
}

MODEL = GEMINI_FLASH

DOOYUN_VISION_SYSTEM = """너는 지수야. 리안 컴퍼니 분석·마케팅팀 비전 분석관.

역할: 리안이 던져넣은 이미지/영상을 보고 우리 회사에 쓸 수 있는 지식만 추출해서 저장.

우리 회사 사업 영역:
- AI 에이전트 자동화 / 멀티 에이전트 시스템
- 소상공인 영업 (비대면 DM, 카카오톡, 문자)
- 마케팅 퍼널 (Hook-Story-Offer, PAS 카피, 세일즈 퍼널)
- 서비스 기획 / UX 설계 / PRD
- 프로토타이핑 / MVP 개발
- Playwright 브라우저 자동화

분석 시 판단 기준:
- 우리 팀 중 누가 써먹을 수 있나? (이사팀, 교육팀, 오프라인마케팅팀, 개발 관련)
- 지금 당장 쓸 수 있는 구체적인 내용인가?
- 너무 일반적이거나 이미 아는 내용이면 버린다
- 경쟁사 사례, 성공한 플로우, 실제 수치, 검증된 방법론 → 무조건 저장

출력은 반드시 JSON만. 다른 말 없이:
{
  "useful": true 또는 false,
  "reason": "왜 유용한지 또는 왜 버리는지 (1~2줄)",
  "filename": "저장할파일명.md",
  "content": "추출한 핵심 지식 (마크다운 형식, 상세하게)",
  "tags": ["태그1", "태그2"],
  "useful_for": ["이사팀" 또는 "오프라인마케팅팀" 또는 "교육팀" 또는 "all"],
  "report_to_lian": "리안한테 직접 말하는 보고 (구어체, 구체적으로. 뭘 봤고, 뭐가 쓸만하고)"
}

useful=false면 filename/content/tags/useful_for 생략 가능."""


def _get_client() -> genai.Client:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY 없음. .env 확인해.")
    return genai.Client(api_key=api_key)


def _parse(raw: str) -> dict:
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except (json.JSONDecodeError, ValueError):
            pass
    return {"useful": False, "reason": "응답 파싱 실패", "report_to_lian": "Gemini 응답 파싱 실패"}


def analyze_image(file_path: str) -> dict:
    """이미지 파일 → Gemini 비전 분석."""
    ext = Path(file_path).suffix.lower()
    mime = IMAGE_MIME.get(ext, "image/jpeg")
    client = _get_client()

    with open(file_path, "rb") as f:
        data = f.read()

    image_part = types.Part.from_bytes(data=data, mime_type=mime)
    response = client.models.generate_content(
        model=MODEL,
        contents=[image_part, DOOYUN_VISION_SYSTEM],
    )
    return _parse(response.text or "")


def analyze_video(file_path: str) -> dict:
    """영상 파일 → Gemini Files API 업로드 후 분석."""
    ext = Path(file_path).suffix.lower()
    mime = VIDEO_MIME.get(ext, "video/mp4")
    client = _get_client()

    print("    [영상 업로드 중...]", end="", flush=True)
    with open(file_path, "rb") as f:
        uploaded = client.files.upload(
            file=f,
            config=types.UploadFileConfig(
                display_name=Path(file_path).name,
                mime_type=mime,
            ),
        )

    while uploaded.state.name == "PROCESSING":
        time.sleep(2)
        uploaded = client.files.get(name=uploaded.name)
    print(" 완료")

    if uploaded.state.name == "FAILED":
        return {"useful": False, "reason": "영상 업로드 실패", "report_to_lian": "영상 처리 실패"}

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=[uploaded, DOOYUN_VISION_SYSTEM],
        )
        result = _parse(response.text or "")
    finally:
        try:
            client.files.delete(name=uploaded.name)
        except Exception:
            pass

    return result


def analyze(file_path: str) -> dict:
    """확장자 보고 이미지/영상 분기 → 분석 결과 반환."""
    ext = Path(file_path).suffix.lower()
    if ext in IMAGE_EXT:
        return analyze_image(file_path)
    elif ext in VIDEO_EXT:
        return analyze_video(file_path)
    else:
        return {
            "useful": False,
            "reason": f"지원 안 하는 형식 ({ext})",
            "report_to_lian": f"{ext} 형식 미지원",
        }
