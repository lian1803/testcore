#!/usr/bin/env python3
"""
인스타분석팀 파이프라인

목적:
1. 인스타/유튜브 링크 목록 txt → 영상 다운로드 (yt-dlp)
2. Gemini File API로 영상 직접 분석 (실제 내용 전사)
3. Claude로 core-shell 적용 인사이트 추출
4. 보고사항들.md 저장

사용법:
  python teams/인스타분석팀/pipeline.py "C:/path/to/links.txt"
  python run_인스타분석팀.py "C:/path/to/links.txt"
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
from typing import Optional

# 경로 설정
LIANCP_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, LIANCP_ROOT)

from dotenv import load_dotenv
load_dotenv(os.path.join(LIANCP_ROOT, ".env"))

from utils.video_cloner import download_video, extract_design_spec, generate_clone_code, OUTPUT_DIR as CLONE_OUTPUT_DIR
from core.models import GEMINI_FLASH, CLAUDE_SONNET
import anthropic
from google import genai
from google.genai import types

VIDEO_TMP_DIR = Path(LIANCP_ROOT) / "utils" / "video_cloner_tmp"
REPORT_FILE = os.path.join(LIANCP_ROOT, "보고사항들.md")
INSTAGRAM_COOKIES = Path(LIANCP_ROOT) / "instagram_cookies.txt"

VIDEO_TMP_DIR.mkdir(exist_ok=True)


# ──────────────────────────────────────────────────────────────
# STEP 1: URL 수집
# ──────────────────────────────────────────────────────────────

def load_urls_from_txt(file_path: str) -> list[str]:
    """txt 파일에서 URL 파싱."""
    urls = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and line.startswith("http"):
                    urls.append(line)
    except Exception as e:
        print(f"⚠️ 파일 읽기 실패: {e}")
        return []

    seen = set()
    unique = []
    for url in urls:
        if url not in seen:
            unique.append(url)
            seen.add(url)
    return unique


def is_youtube_url(url: str) -> bool:
    return "youtube.com/watch" in url or "youtu.be/" in url or "youtube.com/shorts/" in url


# ──────────────────────────────────────────────────────────────
# STEP 2: 영상 다운로드 (인스타/유튜브 공통)
# ──────────────────────────────────────────────────────────────

def download_video_for_analysis(url: str, idx: int) -> Optional[str]:
    """
    yt-dlp로 영상 다운로드.
    이미 있으면 재사용. 반환값: 로컬 mp4 경로 or None
    """
    import yt_dlp, re as _re

    # URL ID 추출
    if "instagram.com" in url:
        m = _re.search(r'/reel/([A-Za-z0-9_-]+)', url) or _re.search(r'/p/([A-Za-z0-9_-]+)', url)
        url_id = f"insta_{m.group(1)}" if m else f"insta_{idx:02d}"
    else:
        m = _re.search(r'(?:youtube\.com/watch\?v=|youtu\.be/)([A-Za-z0-9_-]+)', url)
        url_id = f"yt_{m.group(1)}" if m else f"video_{idx:02d}"

    output_path = VIDEO_TMP_DIR / f"{url_id}.mp4"

    if output_path.exists():
        print(f"  ✓ 기존 영상 재사용: {output_path.name}")
        return str(output_path)

    ydl_opts = {
        "format": "best[ext=mp4][height<=1080]/best[ext=mp4]/best",
        "quiet": True,
        "no_warnings": True,
        "outtmpl": str(VIDEO_TMP_DIR / f"{url_id}.%(ext)s"),
    }
    if "instagram.com" in url and INSTAGRAM_COOKIES.exists():
        ydl_opts["cookiefile"] = str(INSTAGRAM_COOKIES)

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            duration = info.get("duration", 0)
            print(f"  ✓ 다운로드 완료 ({duration}초)")

        # 확장자가 mp4가 아닐 수 있음 — 첫 번째 mp4 파일 찾기
        if not output_path.exists():
            candidates = list(VIDEO_TMP_DIR.glob(f"{url_id}.*"))
            if candidates:
                return str(candidates[0])
        return str(output_path)
    except Exception as e:
        print(f"  ✗ 다운로드 실패: {e}")
        return None


# ──────────────────────────────────────────────────────────────
# STEP 3: Gemini로 영상 분석 (인스타/유튜브 공통)
# ──────────────────────────────────────────────────────────────

ANALYSIS_PROMPT = """이 영상의 실제 내용을 해독해라.

관심 있는 것:
- 영상/자막/화면에 보이는 텍스트 전부 읽어라
- AI/프롬프트/워크플로우/도구 사용법이 나오면 원문 그대로 추출
- 구체적인 방법론, 단계, 수치, 명령어, 프롬프트 예시 전부 포함
- 어떤 도구/기술/플랫폼을 쓰는지

관심 없는 것:
- "좋아요", "구독", "팔로우" 같은 CTA
- 계정명, 해시태그, 광고

출력은 반드시 이 JSON 형식으로만:
{
  "content_type": "릴스/유튜브영상/쇼츠/카드뉴스 등",
  "main_topic": "핵심 주제 1줄",
  "full_text": "영상 내용 전사 (최대한 완전하게)",
  "key_items": ["핵심 정보 1", "핵심 정보 2"],
  "tools_mentioned": ["언급된 도구/플랫폼/기술"],
  "has_actionable_content": true 또는 false
}"""


def decode_video_with_gemini(video_path: str) -> dict:
    """
    로컬 영상 파일 → Gemini File API 업로드 → 영상 직접 분석.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return {"content_type": "오류", "main_topic": "GOOGLE_API_KEY 없음",
                "full_text": "", "key_items": [], "tools_mentioned": [],
                "has_actionable_content": False, "error": "GOOGLE_API_KEY 없음"}
    try:
        client = genai.Client(api_key=api_key)
        ext = Path(video_path).suffix.lower()
        mime_map = {".mp4": "video/mp4", ".mov": "video/quicktime",
                    ".webm": "video/webm", ".m4v": "video/mp4", ".mkv": "video/x-matroska"}
        mime_type = mime_map.get(ext, "video/mp4")

        print(f"  → Gemini File API 업로드 중...")
        with open(video_path, "rb") as f:
            video_file = client.files.upload(
                file=f,
                config=types.UploadFileConfig(display_name=Path(video_path).name, mime_type=mime_type)
            )

        while video_file.state.name == "PROCESSING":
            time.sleep(2)
            video_file = client.files.get(name=video_file.name)

        if video_file.state.name == "FAILED":
            return {"content_type": "오류", "main_topic": "Gemini 파일 처리 실패",
                    "full_text": "", "key_items": [], "tools_mentioned": [],
                    "has_actionable_content": False, "error": "FAILED"}

        print(f"  → 영상 분석 중...")
        response = client.models.generate_content(
            model=GEMINI_FLASH,
            contents=[types.Part.from_uri(file_uri=video_file.uri, mime_type=mime_type), ANALYSIS_PROMPT]
        )

        client.files.delete(name=video_file.name)

        text = response.text or ""
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass

        return {"content_type": "파싱 불가", "main_topic": "응답 형식 오류",
                "full_text": text[:500], "key_items": [], "tools_mentioned": [],
                "has_actionable_content": False, "error": "JSON 파싱 실패"}

    except Exception as e:
        print(f"  ✗ Gemini 영상 분석 실패: {e}")
        return {"content_type": "오류", "main_topic": str(e), "full_text": "",
                "key_items": [], "tools_mentioned": [], "has_actionable_content": False,
                "error": str(e)}


# ──────────────────────────────────────────────────────────────
# STEP 3: Claude로 인사이트 추출 (core-shell 적용점)
# ──────────────────────────────────────────────────────────────

def extract_insights_with_claude(decoded_contents: list[dict]) -> list[dict]:
    """
    Claude Sonnet으로 core-shell 적용 가능 인사이트 추출.
    각 게시물마다 "이거 우리 시스템에 어떻게 적용할까?" 판단.

    개선사항:
    1. 시스템 프롬프트: 기술/방법론/AI 프롬프트 중심으로 변경
    2. JSON 파싱: 더 강력한 파싱 로직
    3. 폴백: 파싱 실패 시 raw text 로그
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("⚠️ ANTHROPIC_API_KEY 없음")
        return []

    client = anthropic.Anthropic(api_key=api_key)

    # 모든 게시물 콘텐츠를 Claude에게 전달
    formatted_contents = []
    for i, content in enumerate(decoded_contents, 1):
        if content.get("error"):
            continue
        text = f"""[게시물 {i}]
주제: {content.get('main_topic', '')}
종류: {content.get('content_type', '')}
내용: {content.get('full_text', '')}
핵심 아이템: {', '.join(content.get('key_items', []))}
사용 도구: {', '.join(content.get('tools_mentioned', []))}
"""
        formatted_contents.append(text)

    if not formatted_contents:
        print("⚠️ 분석 가능한 콘텐츠 없음")
        return []

    combined_text = "\n\n".join(formatted_contents)

    system_prompt = """너는 core-shell AI 시스템의 업그레이드 전략가다.

core-shell이란:
- 멀티 에이전트 파이프라인 (이사팀/영업팀/마케팅팀/납품팀)
- 소상공인 오프라인 영업 자동화 (PDF 진단서, DM 자동생성, CRM)
- 인스타/블로그/카카오 콘텐츠 자동생성
- Claude/GPT/Gemini/Perplexity 멀티AI 조합

분석 관점: 마케팅 기법(댓글유도, CTA 등)이 아니라 게시물 안에 담긴 실제 기술/방법론/AI 프롬프트/워크플로우/도구활용법을 훔쳐와라.

예시:
- "토큰 95% 절감 방법" 게시물 → 그 방법이 뭔지, 어떻게 core-shell 에이전트에 적용하나
- "Claude 프롬프트 예시" → 그 프롬프트 패턴을 우리 에이전트 프롬프트에 적용
- "n8n 워크플로우" → 우리 파이프라인 구조에 벤치마킹

반드시 JSON 배열만 출력. 텍스트 설명 없이 이 형식으로 (각 게시물마다 1개 항목):
[
  {
    "post_id": 1,
    "topic": "게시물 주제",
    "steal_worthy": true,
    "what": "실제로 뭘 훔치나 (기술/방법론/프롬프트 등 구체적으로)",
    "how_to_apply": "core-shell 어느 에이전트/모듈에 어떻게 적용하나",
    "category": "프롬프트기법/워크플로우/도구활용/AI기술/콘텐츠구조/기타",
    "priority": "즉시/나중에/참고만"
  }
]

steal_worthy=false인 것도 포함해서 전체 게시물 수만큼 배열 항목을 반환해.
JSON 형식만 반환하고 다른 텍스트는 절대 넣지 마."""

    try:
        response = client.messages.create(
            model=CLAUDE_SONNET,
            max_tokens=8192,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": f"아래 인스타그램 게시물들을 분석해줘:\n\n{combined_text}"
                }
            ]
        )

        text = response.content[0].text if response.content else ""
        print(f"  📝 Claude 응답 길이: {len(text)} 글자")

        # 방법 1: JSON 직접 파싱
        try:
            results = json.loads(text.strip())
            if isinstance(results, list):
                print(f"  ✓ JSON 파싱 성공: {len(results)}개 항목")
                return results
        except json.JSONDecodeError as e:
            print(f"    (방법1 실패: {e})")

        # 방법 2: ```json ... ``` 코드 블록 제거 후 파싱
        try:
            # 코드블록 제거: 백틱 처리 (더 간단하고 안전함)
            cleaned = text
            # 시작 백틱 제거
            if '```json' in cleaned:
                cleaned = cleaned.split('```json', 1)[1]
            elif '```' in cleaned:
                cleaned = cleaned.split('```', 1)[1]
            # 끝 백틱 제거
            if '```' in cleaned:
                cleaned = cleaned.split('```')[0]

            cleaned = cleaned.strip()

            results = json.loads(cleaned)
            if isinstance(results, list):
                print(f"  ✓ 코드블록 제거 후 JSON 파싱 성공: {len(results)}개 항목")
                return results
        except json.JSONDecodeError as e:
            print(f"    (방법2 실패: {e})")

        # 방법 3: JSON 배열 regex로 추출 (가장 안전함)
        match = re.search(r'(\[.*\])', text, re.DOTALL)
        if match:
            try:
                json_str = match.group(1)
                results = json.loads(json_str)
                if isinstance(results, list):
                    print(f"  ✓ Regex 배열 추출 후 JSON 파싱 성공: {len(results)}개 항목")
                    return results
            except json.JSONDecodeError as e:
                print(f"    (방법3 실패: {e})")

        # 방법 4: 파싱 실패 — 로그만 기록하고 빈 배열 반환
        print(f"  ⚠️ JSON 파싱 실패 (모든 방법 시도됨)")
        # 디버그 출력
        print(f"  텍스트 시작: {repr(text[:100])}")
        return []

    except Exception as e:
        print(f"⚠️ Claude 인사이트 추출 실패: {e}")
        return []


# ──────────────────────────────────────────────────────────────
# STEP 4: 터미널 출력 + MD 저장
# ──────────────────────────────────────────────────────────────

def print_results(insights: list[dict], decoded_contents: list[dict]) -> tuple[list, list]:
    """
    터미널에 결과 출력.
    각 포스팅 간략 설명 + 필요/불필요 구분.
    Returns (needed_indices, not_needed_indices)
    """
    total = len(decoded_contents)
    sep = "=" * 60
    insight_map = {i.get("post_id"): i for i in insights}

    needed = []
    not_needed = []

    print(f"\n{sep}")
    print(f"인스타분석팀 결과 | 총 {total}개 포스팅")
    print(sep)

    for idx, content in enumerate(decoded_contents, 1):
        insight = insight_map.get(idx, {})
        steal = insight.get("steal_worthy", False)
        topic = content.get("main_topic", "주제 불명")
        ctype = content.get("content_type", "")
        tools = ", ".join(content.get("tools_mentioned", [])) or "없음"

        print(f"\n[{idx}/{total}] {topic} ({ctype})")
        print(f"  도구/기술: {tools}")

        if content.get("error"):
            print(f"  ⚠️ 수집 실패: {content.get('error')}")
            not_needed.append(idx)
            continue

        if steal:
            priority = insight.get("priority", "")
            category = insight.get("category", "")
            what = insight.get("what", "")
            how = insight.get("how_to_apply", "")
            print(f"  ✅ 필요 [{priority}] [{category}]")
            print(f"     뭘 훔치나: {what}")
            print(f"     어떻게 적용: {how}")
            needed.append(idx)
        else:
            print(f"  ❌ 불필요")
            not_needed.append(idx)

    # 최종 요약
    print(f"\n{sep}")
    print(f"필요 {len(needed)}개 / 불필요 {len(not_needed)}개 / 총 {total}개")
    print(sep)

    immediate = [i for i in insights if i.get("steal_worthy") and i.get("priority") == "즉시"]
    later = [i for i in insights if i.get("steal_worthy") and i.get("priority") != "즉시"]

    if immediate:
        print(f"\n즉시 적용 ({len(immediate)}개):")
        for i in immediate:
            print(f"  [{i.get('post_id')}] {i.get('topic', '')} — {i.get('what', '')[:80]}")
    if later:
        print(f"\n나중에/참고 ({len(later)}개):")
        for i in later:
            print(f"  [{i.get('post_id')}] {i.get('topic', '')} — {i.get('what', '')[:80]}")

    return needed, not_needed


def save_to_md(insights: list[dict], decoded_contents: list[dict],
               needed: list, not_needed: list) -> str:
    """
    분석 결과를 날짜별 MD 파일로 저장.
    파일명: 인스타분석_결과_{날짜}.md
    Returns: 저장된 파일 경로
    """
    today = datetime.now().strftime("%Y%m%d")
    filename = f"인스타분석_결과_{today}.md"
    filepath = os.path.join(LIANCP_ROOT, filename)

    # 기존 파일이 있으면 뒤에 타임스탬프 붙임
    if os.path.exists(filepath):
        ts = datetime.now().strftime("%H%M")
        filepath = os.path.join(LIANCP_ROOT, f"인스타분석_결과_{today}_{ts}.md")

    total = len(decoded_contents)
    insight_map = {i.get("post_id"): i for i in insights}

    lines = []
    lines.append(f"# 인스타분석팀 — 분석 결과")
    lines.append(f"> 분석일: {datetime.now().strftime('%Y-%m-%d')} | 총 {total}개 포스팅 | 필요 {len(needed)}개 / 불필요 {len(not_needed)}개\n")
    lines.append("---\n")

    # 즉시 적용
    immediate = [i for i in insights if i.get("steal_worthy") and i.get("priority") == "즉시"]
    if immediate:
        lines.append(f"## ✅ 즉시 적용 ({len(immediate)}개)\n")
        lines.append("---\n")
        for ins in immediate:
            pid = ins.get("post_id")
            content = decoded_contents[pid - 1] if pid and pid <= len(decoded_contents) else {}
            lines.append(f"### [{pid}] {ins.get('topic', '')}\n")
            lines.append(f"**포스팅 내용**")
            full_text = content.get("full_text", "")
            if full_text:
                for line in full_text.split("\n")[:20]:  # 최대 20줄
                    if line.strip():
                        lines.append(f"- {line.strip()}")
            key_items = content.get("key_items", [])
            if key_items:
                for item in key_items:
                    lines.append(f"- {item}")
            lines.append(f"\n**core-shell 적용 방법**")
            how = ins.get("how_to_apply", "")
            for line in how.split("\n"):
                if line.strip():
                    lines.append(f"- {line.strip()}")
            lines.append("\n---\n")

    # 나중에/참고
    later = [i for i in insights if i.get("steal_worthy") and i.get("priority") != "즉시"]
    if later:
        lines.append(f"## 🔜 나중에 / 참고 ({len(later)}개)\n")
        lines.append("---\n")
        for ins in later:
            pid = ins.get("post_id")
            content = decoded_contents[pid - 1] if pid and pid <= len(decoded_contents) else {}
            lines.append(f"### [{pid}] {ins.get('topic', '')}\n")
            lines.append(f"**포스팅 내용**")
            full_text = content.get("full_text", "")
            if full_text:
                for line in full_text.split("\n")[:10]:
                    if line.strip():
                        lines.append(f"- {line.strip()}")
            lines.append(f"\n**core-shell 적용 방법**")
            how = ins.get("how_to_apply", "")
            for line in how.split("\n"):
                if line.strip():
                    lines.append(f"- {line.strip()}")
            lines.append("\n---\n")

    # 불필요
    not_worthy = [i for i in insights if not i.get("steal_worthy")]
    if not_worthy:
        lines.append(f"## ❌ 불필요 ({len(not_worthy)}개)\n")
        lines.append("| 번호 | 내용 | 이유 |")
        lines.append("|------|------|------|")
        for ins in not_worthy:
            pid = ins.get("post_id")
            content = decoded_contents[pid - 1] if pid and pid <= len(decoded_contents) else {}
            topic = ins.get("topic") or content.get("main_topic", "불명")
            what = ins.get("what", "내용 없음") or "내용 없음"
            lines.append(f"| [{pid}] | {topic} | {what} |")
        lines.append("")

    # 우선순위 요약
    lines.append("\n## 우선순위 요약\n")
    lines.append("```")
    if immediate:
        lines.append("즉시 적용:")
        for i in immediate:
            lines.append(f"  [{i.get('post_id')}]  {i.get('topic', '')} — {i.get('what', '')[:60]}")
    if later:
        lines.append("\n나중에/참고:")
        for i in later:
            lines.append(f"  [{i.get('post_id')}]  {i.get('topic', '')} — {i.get('what', '')[:60]}")
    lines.append("```\n")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return filepath


# ──────────────────────────────────────────────────────────────
# 메인 파이프라인
# ──────────────────────────────────────────────────────────────

async def process_link(url: str, idx: int) -> dict:
    """
    한 개의 링크 처리.
    인스타/유튜브 모두 yt-dlp로 영상 다운로드 → Gemini 영상 직접 분석.
    """
    label = "유튜브" if is_youtube_url(url) else "인스타"
    print(f"\n[{idx}] 🎬 {label}: {url[:60]}...")

    video_path = download_video_for_analysis(url, idx)
    if not video_path:
        return {"url": url, "idx": idx, "error": "영상 다운로드 실패",
                "content_type": "오류", "main_topic": "다운로드 실패",
                "full_text": "", "key_items": [], "tools_mentioned": [],
                "has_actionable_content": False}

    decoded = decode_video_with_gemini(video_path)
    decoded["url"] = url
    decoded["idx"] = idx
    return decoded


async def main(txt_file: str):
    """메인 실행."""
    if not os.path.exists(txt_file):
        print(f"⚠️ 파일 없음: {txt_file}")
        return

    urls = load_urls_from_txt(txt_file)
    if not urls:
        print(f"⚠️ URL 없음: {txt_file}")
        return

    print(f"\n{'='*60}")
    print(f"🔍 인스타분석팀 파이프라인")
    print(f"URL {len(urls)}개 발견")
    print(f"{'='*60}")

    # STEP 1+2: 영상 다운로드 + Gemini 영상 분석
    print("\n[STEP 1/3] 영상 다운로드 + Gemini 분석...")
    decoded_contents = []
    for i, url in enumerate(urls, 1):
        result = await process_link(url, i)
        decoded_contents.append(result)

    # STEP 3: Claude로 인사이트 추출
    print("\n[STEP 2/3] Claude로 core-shell 인사이트 추출...")
    insights = extract_insights_with_claude(decoded_contents)

    # STEP 4: 터미널 출력
    needed, not_needed = print_results(insights, decoded_contents)

    # STEP 5: MD 파일 저장
    md_path = save_to_md(insights, decoded_contents, needed, not_needed)
    print(f"\n{'='*60}")
    print(f"✅ 완료 | MD 저장: {os.path.basename(md_path)}")
    print(f"{'='*60}\n")


async def process_link_clone(url: str, idx: int) -> dict:
    """클론 모드: video_cloner 파이프라인으로 디자인 스펙 + HTML 생성."""
    print(f"\n[{idx}] 🎨 클론 분석: {url[:70]}...")
    try:
        video_path, url_id = download_video(url)
        spec_json = extract_design_spec(video_path, url_id)
        html_code = generate_clone_code(spec_json)

        html_path = CLONE_OUTPUT_DIR / f"{url_id}_clone.html"
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_code)

        return {"url": url, "idx": idx, "url_id": url_id, "html_path": str(html_path), "error": None}
    except Exception as e:
        return {"url": url, "idx": idx, "error": str(e)}


async def main_clone(txt_file: str):
    """클론 모드 메인: URL 목록 → 디자인 스펙 JSON + 클론 HTML 생성."""
    if not os.path.exists(txt_file):
        print(f"⚠️ 파일 없음: {txt_file}")
        return

    urls = load_urls_from_txt(txt_file)
    if not urls:
        print(f"⚠️ URL 없음: {txt_file}")
        return

    print(f"\n{'='*60}")
    print(f"🎨 인스타분석팀 — 디자인 클론 모드")
    print(f"URL {len(urls)}개 → 디자인 스펙 추출 + HTML 클론 생성")
    print(f"{'='*60}")

    results = []
    for i, url in enumerate(urls, 1):
        result = await process_link_clone(url, i)
        results.append(result)

    ok = [r for r in results if not r.get("error")]
    fail = [r for r in results if r.get("error")]

    print(f"\n{'='*60}")
    print(f"✅ 완료 {len(ok)}개 / ❌ 실패 {len(fail)}개")
    for r in ok:
        print(f"  [{r['idx']}] {r['url_id']}")
        print(f"       스펙: {CLONE_OUTPUT_DIR}/{r['url_id']}_spec.json")
        print(f"       HTML: {r['html_path']}")
    for r in fail:
        print(f"  [{r['idx']}] 실패: {r['error']}")
    print(f"{'='*60}\n")


def run(txt_file: str = "", clone_mode: bool = False):
    """
    CLI 인터페이스.
    CLI 인자가 없으면 input() 호출하지 말 것.
    """
    if not txt_file:
        print("사용법: python run_인스타분석팀.py 'C:/path/to/links.txt' [--clone]")
        sys.exit(1)

    if clone_mode:
        asyncio.run(main_clone(txt_file))
    else:
        asyncio.run(main(txt_file))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python teams/인스타분석팀/pipeline.py 'C:/path/to/links.txt'")
        sys.exit(1)

    txt_file = sys.argv[1]
    asyncio.run(main(txt_file))
