#!/usr/bin/env python3
"""
도윤 — 자료들/ 폴더 처리기

사용법:
  python process_inbox.py

자료들/ 폴더에 파일 던져넣으면:
1. 도윤(Opus)이 전부 읽고 분석
2. 유용한 지식 → knowledge/base/ 저장
3. 불필요한 파일 → 삭제
4. 처리 결과 → 보고사항들.md 업데이트
"""
import os
import sys
import io
import re
import json
import google.genai as genai
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from teams.analysis.analyzer import analyze as analyze_media, IMAGE_EXT, VIDEO_EXT

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

load_dotenv()

LIANCP_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INBOX_DIR    = os.path.join(LIANCP_ROOT, "자료들")
KNOWLEDGE_BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "knowledge", "base")
INDEX_PATH   = os.path.join(os.path.dirname(os.path.abspath(__file__)), "knowledge", "index.json")
REPORT_FILE  = os.path.join(LIANCP_ROOT, "보고사항들.md")

from core.models import GEMINI_FLASH
from core.context_loader import get_company_context
MODEL = GEMINI_FLASH  # 도윤 = Gemini (토큰 절약)

# 회사 DNA를 도윤 프롬프트에 동적 주입
_company_ctx = get_company_context()[:2000]

DOOYUN_SYSTEM = f"""너는 도윤이야. 리안 컴퍼니 교육팀 교장.

역할: 리안이 던져넣은 자료를 읽고 우리 회사에 쓸 수 있는 지식만 추출해서 저장.
그리고 **어떤 팀/에이전트에게 이 지식이 필요한지** 판단해서 라우팅해.

=== 회사 컨텍스트 ===
{_company_ctx}
=== 끝 ===

분석 시 판단 기준:
- 우리 팀 중 누가 써먹을 수 있나? 구체적으로 팀명+이름까지 지정
- 지금 당장 쓸 수 있는 구체적인 내용인가?
- 너무 일반적이거나 이미 아는 내용이면 버린다
- 경쟁사 사례, 성공한 플로우, 실제 수치, 검증된 방법론 → 무조건 저장
- 디자인/UI 관련 → CDO 나은에게
- 마케팅 트렌드 → 마케팅팀에게
- 영업 전략 → 오프라인마케팅팀 승현에게
- 카피/DM → 예진에게
- 기술/개발 → UltraProduct팀에게

출력은 반드시 JSON만. 다른 말 없이:
{
  "useful": true 또는 false,
  "reason": "왜 유용한지 또는 왜 버리는지 (1~2줄)",
  "filename": "저장할파일명.md",
  "content": "추출한 핵심 지식 (마크다운 형식, 상세하게)",
  "tags": ["태그1", "태그2"],
  "useful_for": ["이사팀" 또는 "오프라인마케팅팀" 또는 "교육팀" 또는 "all"],
  "report_to_lian": "리안한테 직접 말하는 보고 (구어체, 구체적으로. 뭘 봤고, 뭐가 쓸만하고, 필요한 게 있으면 요청)"
}

useful=false면 filename/content/tags/useful_for 생략 가능."""


def read_file(path: str) -> str | None:
    ext = Path(path).suffix.lower()
    try:
        if ext in (".txt", ".md"):
            with open(path, encoding="utf-8", errors="replace") as f:
                return f.read()
        elif ext in (".html", ".htm"):
            with open(path, encoding="utf-8", errors="replace") as f:
                html = f.read()
            text = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
            text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL)
            text = re.sub(r'<[^>]+>', ' ', text)
            text = re.sub(r'&nbsp;', ' ', text)
            text = re.sub(r'&[a-zA-Z0-9#]+;', '', text)
            text = re.sub(r'\s+', ' ', text).strip()
            return text[:9000]
    except Exception as e:
        print(f"  읽기 실패: {e}")
    return None


def load_index() -> dict:
    try:
        with open(INDEX_PATH, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"base": {}, "team_results": {}, "feedback": {}}


def save_index(index: dict):
    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)


def analyze(content: str, filename: str) -> dict:
    """Gemini로 자료 분석 (토큰 절약: 본문 5000자 제한)."""
    print(f"  도윤 분석 중...", end="", flush=True)
    try:
        client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        prompt = f"""[{DOOYUN_SYSTEM}]\n\n파일명: {filename}\n\n내용:\n{content[:5000]}"""
        resp = client.models.generate_content(model=MODEL, contents=prompt)
        raw = resp.text.strip()
        print(" 완료")
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception as e:
        print(f" 실패: {e}")
    return {"useful": False, "reason": "분석 실패", "report_to_lian": "분석 중 오류 발생"}


def write_report(entries: list):
    """보고사항들.md에 도윤 보고 추가 (최신 항목이 위로)."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines = [f"## 도윤 (교육팀 교장) — {now}\n"]

    if not entries:
        lines.append("자료들/ 폴더에 처리할 파일 없었음.\n")
    else:
        saved   = [e for e in entries if e.get("saved")]
        deleted = [e for e in entries if e.get("deleted") and not e.get("skip")]
        skipped = [e for e in entries if e.get("skip")]

        lines.append(f"자료들/ {len(entries)}개 파일 처리 완료.\n")

        if saved:
            for e in saved:
                lines.append(f"**{e['original']}** ✅ → `knowledge/base/{e['saved_as']}`")
                lines.append(f"- 태그: {', '.join(e.get('tags', []))}")
                if e.get("report"):
                    lines.append(f"- {e['report']}")
                lines.append("")

        if deleted:
            for e in deleted:
                lines.append(f"**{e['original']}** ❌ 버림 — {e.get('reason', '')}")
                if e.get("report"):
                    lines.append(f"  → {e['report']}")
                lines.append("")

        if skipped:
            lines.append("**처리 못한 파일 (리안 참고):**")
            for e in skipped:
                lines.append(f"- `{e['original']}` — {e['skip_reason']}")
            lines.append("")

    lines.append("---\n")
    new_section = "\n".join(lines)

    # 기존 파일 읽기
    if os.path.exists(REPORT_FILE):
        with open(REPORT_FILE, encoding="utf-8") as f:
            existing = f.read()
        # 헤더 끝 (첫 번째 --- 이후) 바로 다음에 삽입
        split = existing.split("---\n", 1)
        if len(split) == 2:
            result = split[0] + "---\n\n" + new_section + split[1]
        else:
            result = existing + "\n" + new_section
    else:
        header = (
            "# 보고사항들\n\n"
            "> 에이전트들이 리안한테 직접 보고하는 공간.\n"
            "> 리안이 읽고 지시사항 있으면 해당 에이전트한테 전달.\n\n"
            "---\n\n"
        )
        result = header + new_section

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(result)


def run():
    os.makedirs(INBOX_DIR, exist_ok=True)
    os.makedirs(KNOWLEDGE_BASE, exist_ok=True)

    files = [f for f in os.listdir(INBOX_DIR) if os.path.isfile(os.path.join(INBOX_DIR, f))]

    print(f"\n{'='*60}")
    print(f"도윤 | 교육팀 교장 — 자료들/ 처리 시작")
    print(f"파일 {len(files)}개 발견")
    print(f"{'='*60}")

    if not files:
        print("처리할 파일 없음.")
        write_report([])
        return

    index = load_index()
    entries = []

    TEXT_EXTS  = {".txt", ".md", ".html", ".htm"}

    for fname in files:
        fpath = os.path.join(INBOX_DIR, fname)
        ext = Path(fname).suffix.lower()

        print(f"\n[{fname}]")

        if ext in IMAGE_EXT or ext in VIDEO_EXT:
            print(f"  {'이미지' if ext in IMAGE_EXT else '영상'} — 분석팀 처리 중...")
            try:
                result = analyze_media(fpath)
            except Exception as e:
                print(f"  분석 실패: {e}")
                entries.append({"original": fname, "skip": True, "skip_reason": str(e)})
                continue

            if result.get("useful"):
                save_fname = result.get("filename") or (Path(fname).stem + ".md")
                save_fname = re.sub(r'[\\/:*?"<>|]', '_', save_fname)
                if not save_fname.endswith(".md"):
                    save_fname += ".md"
                save_path = os.path.join(KNOWLEDGE_BASE, save_fname)
                knowledge_md = (
                    f"# {Path(save_fname).stem}\n\n"
                    f"> 출처: {fname} (분석팀 처리 — {datetime.now().strftime('%Y-%m-%d')})\n\n"
                    + result.get("content", "")
                )
                with open(save_path, "w", encoding="utf-8") as f:
                    f.write(knowledge_md)
                index["base"][save_fname] = {
                    "tags": result.get("tags", []),
                    "useful_for": result.get("useful_for", []),
                    "source": fname,
                    "saved_at": datetime.now().isoformat(),
                }
                save_index(index)
                os.remove(fpath)
                print(f"  저장: knowledge/base/{save_fname} | 원본 삭제")
                entries.append({
                    "original": fname, "saved": True, "saved_as": save_fname,
                    "reason": result.get("reason", ""), "tags": result.get("tags", []),
                    "useful_for": result.get("useful_for", []),
                    "report": result.get("report_to_lian", ""),
                })
            else:
                os.remove(fpath)
                print(f"  불필요 → 삭제 ({result.get('reason', '')})")
                entries.append({
                    "original": fname, "deleted": True,
                    "reason": result.get("reason", "불필요"),
                    "report": result.get("report_to_lian", ""),
                })
            continue

        if ext == ".pdf":
            print(f"  PDF — pdfplumber 필요, 스킵")
            entries.append({"original": fname, "skip": True,
                             "skip_reason": "PDF (pip install pdfplumber 후 재실행)"})
            continue

        if ext not in TEXT_EXTS:
            print(f"  지원 안 하는 형식 ({ext}), 스킵")
            entries.append({"original": fname, "skip": True,
                             "skip_reason": f"지원 안 하는 형식 ({ext})"})
            continue

        content = read_file(fpath)
        if not content or len(content.strip()) < 30:
            print(f"  내용 없음 → 삭제")
            os.remove(fpath)
            entries.append({"original": fname, "deleted": True, "reason": "내용 없음"})
            continue

        # 인스타그램 URL 목록 파일 감지 → 배치 분석으로 라우팅
        insta_urls = re.findall(r'https://www\.instagram\.com/\S+', content)
        if len(insta_urls) >= 2:
            print(f"  인스타그램 URL {len(insta_urls)}개 감지 → 배치 분석 시작")
            from analyze_instagram import batch_analyze
            batch_analyze(insta_urls)
            os.remove(fpath)
            entries.append({
                "original": fname, "saved": True, "saved_as": "(보고사항들.md 직접 저장)",
                "reason": f"인스타그램 {len(insta_urls)}개 URL 배치 분석 완료",
                "tags": ["instagram", "분석"],
                "useful_for": ["all"],
                "report": f"인스타 {len(insta_urls)}개 분석 완료. 보고사항들.md 확인해."
            })
            continue

        result = analyze(content, fname)

        if result.get("useful"):
            save_fname = result.get("filename") or (Path(fname).stem + ".md")
            # 파일명 안전하게
            save_fname = re.sub(r'[\\/:*?"<>|]', '_', save_fname)
            if not save_fname.endswith(".md"):
                save_fname += ".md"

            save_path = os.path.join(KNOWLEDGE_BASE, save_fname)
            knowledge_md = (
                f"# {Path(save_fname).stem}\n\n"
                f"> 출처: {fname} (자료들/ 처리 — {datetime.now().strftime('%Y-%m-%d')})\n\n"
                + result.get("content", "")
            )
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(knowledge_md)

            index["base"][save_fname] = {
                "tags": result.get("tags", []),
                "useful_for": result.get("useful_for", []),
                "source": fname,
                "saved_at": datetime.now().isoformat(),
            }
            save_index(index)

            os.remove(fpath)
            print(f"  저장: knowledge/base/{save_fname} | 원본 삭제")

            entries.append({
                "original": fname,
                "saved": True,
                "saved_as": save_fname,
                "reason": result.get("reason", ""),
                "tags": result.get("tags", []),
                "useful_for": result.get("useful_for", []),
                "report": result.get("report_to_lian", ""),
            })
        else:
            os.remove(fpath)
            print(f"  불필요 → 삭제 ({result.get('reason', '')})")
            entries.append({
                "original": fname,
                "deleted": True,
                "reason": result.get("reason", "불필요"),
                "report": result.get("report_to_lian", ""),
            })

    # 라우팅: useful_for 기반으로 팀별 knowledge에도 저장
    _route_knowledge(entries)

    write_report(entries)

    print(f"\n{'='*60}")
    print(f"완료. 보고사항들.md 업데이트됨.")
    print(f"{'='*60}\n")


def _route_knowledge(entries: list):
    """useful_for 기반으로 팀별 knowledge 폴더에 복사."""
    TEAM_KNOWLEDGE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "knowledge", "teams")
    os.makedirs(TEAM_KNOWLEDGE, exist_ok=True)

    for entry in entries:
        if not entry.get("saved"):
            continue

        useful_for = entry.get("useful_for", [])
        if not useful_for or useful_for == ["all"]:
            continue

        saved_as = entry.get("saved_as", "")
        source_path = os.path.join(KNOWLEDGE_BASE, saved_as)
        if not os.path.exists(source_path):
            continue

        with open(source_path, encoding="utf-8") as f:
            content = f.read()

        for team in useful_for:
            team_dir = os.path.join(TEAM_KNOWLEDGE, team.replace(" ", "_"))
            os.makedirs(team_dir, exist_ok=True)
            dest = os.path.join(team_dir, saved_as)
            with open(dest, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"  📨 라우팅: {saved_as} → {team}")


if __name__ == "__main__":
    run()
