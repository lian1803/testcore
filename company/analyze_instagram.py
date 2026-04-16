"""
인스타그램 피드 분석기
사용법: python analyze_instagram.py "https://www.instagram.com/p/XXX/"
"""
import sys
import os
import re
import json
import subprocess
import tempfile
import shutil
import base64
import requests
from pathlib import Path
from dotenv import load_dotenv
import google.genai as genai

# Windows 터미널 UTF-8 강제
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

load_dotenv()

COOKIE_FILE = Path(__file__).parent / "instagram_cookies.txt"
GALLERY_DL = [sys.executable, "-m", "gallery_dl"]


def download_post(url: str, output_dir: Path) -> list[Path]:
    """gallery-dl로 이미지/영상 다운로드"""
    result = subprocess.run(
        [*GALLERY_DL, "--cookies", str(COOKIE_FILE),
         "-D", str(output_dir), "--filename", "{num}.{extension}",
         url],
        capture_output=True, text=True
    )
    if result.returncode != 0 and "error" in result.stderr.lower():
        print(f"[오류] {result.stderr[:200]}")

    files = sorted(output_dir.glob("*"))
    return [f for f in files if f.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp", ".mp4", ".mov"}]


def get_caption(url: str) -> str:
    """캡션 텍스트 추출"""
    result = subprocess.run(
        [*GALLERY_DL, "--cookies", str(COOKIE_FILE),
         "--print", "{description}", url],
        capture_output=True, text=True
    )
    return result.stdout.strip() or "(캡션 없음)"


def upload_video(client, video_path: Path):
    """Gemini Files API로 영상 업로드"""
    import time
    print(f"   [영상 업로드] {video_path.name} ({video_path.stat().st_size // 1024 // 1024}MB)...")
    uploaded = client.files.upload(file=video_path)
    # 처리 완료 대기
    while uploaded.state.name == "PROCESSING":
        time.sleep(2)
        uploaded = client.files.get(name=uploaded.name)
    if uploaded.state.name == "FAILED":
        raise RuntimeError(f"영상 업로드 실패: {uploaded.name}")
    print(f"   [영상 완료] 업로드됨")
    return uploaded


def analyze_with_gemini(files: list[Path], caption: str, url: str) -> str:
    """Gemini Vision으로 콘텐츠 분석 (이미지 + 영상)"""
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

    image_files = [f for f in files if f.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}]
    video_files = [f for f in files if f.suffix.lower() in {".mp4", ".mov", ".avi", ".webm"}]

    parts = []

    # 이미지
    for img_path in image_files[:10]:
        with open(img_path, "rb") as f:
            data = f.read()
        parts.append(genai.types.Part.from_bytes(data=data, mime_type="image/jpeg"))

    # 영상 — Files API로 업로드
    uploaded_files = []
    for vid_path in video_files[:3]:
        uploaded = upload_video(client, vid_path)
        parts.append(genai.types.Part.from_uri(file_uri=uploaded.uri, mime_type=uploaded.mime_type))
        uploaded_files.append(uploaded)

    content_type = []
    if image_files:
        content_type.append(f"이미지 {len(image_files)}장")
    if video_files:
        content_type.append(f"영상 {len(video_files)}개")

    prompt = f"""인스타그램 피드 분석. ({', '.join(content_type)})

[캡션]
{caption}

[우리 시스템이 뭔지 먼저 알아야 함]
- core-shell: 소상공인 대상 AI 자동화 대행 서비스
- Claude Code로 멀티 에이전트 파이프라인 구동 (이사팀/영업팀/마케팅팀/납품팀)
- 주요 기능: PDF 진단서 자동생성, DM 자동발송, CRM, 카드뉴스 자동생성
- 사용 AI: Claude(메인), GPT, Gemini, Perplexity
- 지금 당장 필요한 것: Claude Code 워크플로우 개선, 비용 절감, 에이전트 품질 향상, 디자인/UI 레퍼런스, 실제 쓸 수 있는 GitHub 레포/툴

[판단 기준 — 엄격하게]
이 포스트가 위 시스템에 실제로 적용 가능한 구체적인 것을 담고 있는가?
- YES: 특정 기술/설정/코드/툴/GitHub 레포/워크플로우가 있고, 우리가 실제로 따라할 수 있음
- NO: 일반적인 AI 조언, 동기부여, 밈/유머, CTA 패턴("댓글→DM"), 뻔한 내용

**NO면 한 줄만 쓰고 끝내: "적용 불가 — [이유 10자]"**

[YES일 때만 아래 형식 — 총 5줄 이내]
**내용**: (한 줄)
**훔칠 것**: (설정값/코드/명령어/순서 그대로. 추상적 설명 금지)
**적용**: (core-shell 어느 에이전트/기능에, 무슨 파일/설정을 어떻게 바꾸는지)
**우선순위**: 즉시 / 나중에
**리소스**: (GitHub URL / 툴명 / 사이트 URL 있을 때만)

절대 금지: 없는 걸 있다고 하기, "~할 수 있음" 식 가능성 나열, 범용 AI 조언, CTA 패턴"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[prompt] + parts
    )

    # 업로드된 파일 정리
    for uf in uploaded_files:
        try:
            client.files.delete(name=uf.name)
        except Exception:
            pass

    return response.text


def extract_urls_from_text(text: str) -> list[str]:
    pattern = r'https?://[^\s\)\]\'"<>]+'
    return list(set(re.findall(pattern, text)))


def fetch_github_readme(github_url: str) -> str:
    """GitHub 레포 → README 원본 (최대 3000자)"""
    match = re.match(r'https?://github\.com/([^/\s]+)/([^/\s\?#]+)', github_url)
    if not match:
        return ""
    user, repo = match.group(1), match.group(2).rstrip('/')
    for branch in ["main", "master"]:
        for fname in ["README.md", "readme.md"]:
            raw = f"https://raw.githubusercontent.com/{user}/{repo}/{branch}/{fname}"
            try:
                r = requests.get(raw, timeout=10)
                if r.status_code == 200:
                    return f"[GitHub {user}/{repo}]\n{r.text[:3000]}"
            except Exception:
                continue
    # API 폴백 — 설명이라도
    try:
        r = requests.get(f"https://api.github.com/repos/{user}/{repo}", timeout=10)
        if r.status_code == 200:
            d = r.json()
            return f"[GitHub {user}/{repo}]\n설명: {d.get('description','없음')} | 스타: {d.get('stargazers_count',0)}"
    except Exception:
        pass
    return ""


def fetch_page_content(url: str) -> str:
    """일반 URL → 페이지 텍스트 요약 (최대 2000자)"""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        r = requests.get(url, timeout=10, headers=headers)
        if r.status_code == 200:
            text = re.sub(r'<[^>]+>', ' ', r.text)
            text = re.sub(r'\s+', ' ', text).strip()
            return f"[사이트 {url}]\n{text[:2000]}"
    except Exception as e:
        return f"[사이트 {url}] 접속 실패: {e}"
    return ""


def perplexity_search(query: str) -> str:
    """Perplexity로 도구/스킬/레포 검색"""
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        return ""
    try:
        r = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": "sonar",
                "messages": [{"role": "user", "content": f"{query}\n\nGitHub 링크나 공식 URL 포함해서 300자 이내로 요약해줘."}]
            },
            timeout=15
        )
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"검색 실패: {e}"
    return ""


def deepdive_resources(caption: str, analysis: str) -> str:
    """분석 텍스트 → 리소스 추출 → 실제 내용 수집"""
    import anthropic as ant
    all_text = caption + "\n" + analysis

    # Claude Haiku로 구조적 추출
    try:
        client = ant.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        resp = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=600,
            messages=[{"role": "user", "content": f"""아래 텍스트에서 언급된 GitHub 레포, 웹사이트, 도구/스킬 이름을 추출해줘.
CTA("댓글 달면 DM") 관련은 무시.

텍스트:
{all_text[:2500]}

JSON으로만 답해:
{{"github_urls": [], "site_urls": [], "tool_names": []}}"""}]
        )
        text = resp.content[0].text.strip()
        m = re.search(r'\{.*\}', text, re.DOTALL)
        refs = json.loads(m.group()) if m else {}
    except Exception:
        refs = {}

    # URL에서도 직접 추출 (중복 제거)
    raw_urls = extract_urls_from_text(all_text)
    github_urls = list(set(refs.get("github_urls", []) + [u for u in raw_urls if "github.com" in u and "instagram.com" not in u]))
    site_urls = list(set(refs.get("site_urls", []) + [u for u in raw_urls if "github.com" not in u and "instagram.com" not in u]))
    tool_names = refs.get("tool_names", [])

    results = []

    for url in github_urls[:5]:
        content = fetch_github_readme(url)
        if content:
            results.append(content)
            print(f"   [딥다이브] GitHub 읽음: {url}")

    for url in site_urls[:3]:
        content = fetch_page_content(url)
        if content:
            results.append(content)
            print(f"   [딥다이브] 사이트 읽음: {url}")

    for name in tool_names[:3]:
        result = perplexity_search(f"{name} GitHub OR 공식사이트 OR 설치방법 2024 2025")
        if result:
            results.append(f"[Perplexity 검색: {name}]\n{result}")
            print(f"   [딥다이브] Perplexity 검색: {name}")

    if not results:
        return ""

    return "\n\n---\n\n".join(results)


def save_report(url: str, analysis: str, caption: str):
    """보고사항들.md에 저장 + 인사이트 자동 추출"""
    report_path = Path(__file__).parent.parent / "보고사항들.md"

    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    entry = f"""
---
## [인스타 분석] 인스타 분석 — {timestamp}
**URL**: {url}

**원본 캡션**:
{caption[:300]}{"..." if len(caption) > 300 else ""}

**분석**:
{analysis}

"""
    with open(report_path, "a", encoding="utf-8") as f:
        f.write(entry)

    print(f"\n[완료] 보고사항들.md에 저장됨")

    # 인사이트 자동 추출 (배경 작업)
    try:
        from core.insight_extractor import extract_and_save_single
        extract_and_save_single(url, analysis)
    except Exception as e:
        print(f"⚠️  인사이트 추출 실패: {e}")


def get_analyzed_urls() -> set:
    """보고사항들.md에서 이미 분석된 URL 목록 추출"""
    report_path = Path(__file__).parent.parent / "보고사항들.md"
    if not report_path.exists():
        return set()
    content = report_path.read_text(encoding="utf-8", errors="replace")
    import re
    return set(re.findall(r'\*\*URL\*\*:\s*(https://www\.instagram\.com/\S+)', content))


def analyze_one(url: str):
    """단일 URL 분석 (모듈로 임포트 가능)"""
    print(f"[다운로드] {url}")
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        files = download_post(url, tmp_path)
        print(f"   → {len(files)}개 파일")
        caption = get_caption(url)
        print(f"   → 캡션: {caption[:60]}...")
        print("[분석] Gemini 분석 중...")
        analysis = analyze_with_gemini(files, caption, url)

        print("[딥다이브] 링크/도구 추적 중...")
        deep = deepdive_resources(caption, analysis)
        if deep:
            analysis += f"\n\n## 딥다이브 — 실제 리소스\n{deep}"

        save_report(url, analysis, caption)


def batch_analyze(urls: list[str]):
    """URL 목록 배치 분석 — 이미 완료된 건 자동 스킵"""
    done = get_analyzed_urls()
    todo = [u for u in urls if u.strip() and u.strip() not in done]

    print(f"\n[배치] 전체 {len(urls)}개 | 완료 {len(done) & len(urls)}개 스킵 | 남은 {len(todo)}개 분석")

    for i, url in enumerate(todo, 1):
        print(f"\n[{i}/{len(todo)}] ", end="")
        try:
            analyze_one(url)
        except Exception as e:
            print(f"오류 ({url}): {e}")

    print(f"\n[배치 완료] {len(todo)}개 분석 → 보고사항들.md 저장됨")


def main():
    if len(sys.argv) < 2:
        print("사용법: python analyze_instagram.py 'https://www.instagram.com/p/XXX/'")
        sys.exit(1)

    url = sys.argv[1]
    print(f"[다운로드] 다운로드 중: {url}")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        # 다운로드
        files = download_post(url, tmp_path)
        print(f"   → {len(files)}개 파일 다운로드됨")

        # 캡션
        caption = get_caption(url)
        print(f"   → 캡션: {caption[:80]}...")

        # 분석
        print("[분석] Gemini 분석 중...")
        analysis = analyze_with_gemini(files, caption, url)

        # 출력
        print("\n" + "="*60)
        print(analysis)
        print("="*60)

        # 저장
        save_report(url, analysis, caption)


if __name__ == "__main__":
    main()
