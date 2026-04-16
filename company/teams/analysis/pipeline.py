#!/usr/bin/env python3
"""
분석팀 독립 실행 — 폴더 직접 스캔 + knowledge/base/ 저장

사용법:
  python teams/analysis/pipeline.py              # 기본: 자료들/ 폴더
  python teams/analysis/pipeline.py [폴더경로]   # 특정 폴더

기존 core/video_analyzer.py 기능 통합.
"""
import os
import sys
import io
import json
import re
from pathlib import Path
from datetime import datetime

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"))

from teams.analysis.analyzer import analyze, IMAGE_EXT, VIDEO_EXT

# 상태 추적
try:
    from utils.status_tracker import update_status, clear_status
    HAS_STATUS_TRACKER = True
except ImportError:
    HAS_STATUS_TRACKER = False

LIANCP_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
KNOWLEDGE_BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "knowledge", "base")
INDEX_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "knowledge", "index.json")
REPORT_FILE = os.path.join(LIANCP_ROOT, "보고사항들.md")
DEFAULT_ROOT = os.path.join(LIANCP_ROOT, "자료들")

MEDIA_EXT = IMAGE_EXT | VIDEO_EXT


def load_index() -> dict:
    try:
        with open(INDEX_PATH, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"base": {}, "team_results": {}, "feedback": {}}


def save_index(index: dict):
    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)


def write_report(entries: list):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [f"## 도윤 (분석팀) — {now}\n"]

    saved = [e for e in entries if e.get("saved")]
    deleted = [e for e in entries if e.get("deleted") and not e.get("skip")]
    skipped = [e for e in entries if e.get("skip")]

    lines.append(f"미디어 파일 {len(entries)}개 처리.\n")
    for e in saved:
        lines.append(f"**{e['original']}** ✅ → `knowledge/base/{e['saved_as']}`")
        lines.append(f"- 태그: {', '.join(e.get('tags', []))}")
        if e.get("report"):
            lines.append(f"- {e['report']}")
        lines.append("")
    for e in deleted:
        lines.append(f"**{e['original']}** ❌ — {e.get('reason', '')}")
        lines.append("")
    for e in skipped:
        lines.append(f"**{e['original']}** ⏭️ 스킵 — {e['skip_reason']}")
    lines.append("---\n")
    new_section = "\n".join(lines)

    if os.path.exists(REPORT_FILE):
        with open(REPORT_FILE, encoding="utf-8") as f:
            existing = f.read()
        split = existing.split("---\n", 1)
        result = (split[0] + "---\n\n" + new_section + split[1]) if len(split) == 2 else (existing + "\n" + new_section)
    else:
        header = "# 보고사항들\n\n> 에이전트들이 리안한테 직접 보고하는 공간.\n\n---\n\n"
        result = header + new_section

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(result)


def run(root: str = DEFAULT_ROOT, delete_after: bool = True) -> list:
    """
    root 폴더의 이미지/영상을 전부 분석해서 knowledge/base/에 저장.
    delete_after=True면 처리한 원본 파일 삭제.
    """
    os.makedirs(KNOWLEDGE_BASE, exist_ok=True)

    files = [f for f in sorted(os.listdir(root))
             if os.path.isfile(os.path.join(root, f))
             and Path(f).suffix.lower() in MEDIA_EXT]

    print(f"\n{'='*60}")
    print(f"분석팀 | 미디어 파일 {len(files)}개 발견")
    print(f"{'='*60}")

    if not files:
        print("처리할 파일 없음.")
        return []

    index = load_index()
    entries = []

    for fname in files:
        fpath = os.path.join(root, fname)
        print(f"\n[{fname}]")

        if HAS_STATUS_TRACKER:
            update_status("analyzer", "analysis", "running", f"{fname} 분석 중")

        try:
            result = analyze(fpath)
        except Exception as e:
            print(f"  오류: {e}")
            entries.append({"original": fname, "skip": True, "skip_reason": str(e)})
            if HAS_STATUS_TRACKER:
                clear_status("analyzer")
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

            if delete_after:
                os.remove(fpath)
            print(f"  저장: knowledge/base/{save_fname}")

            entries.append({
                "original": fname,
                "saved": True,
                "saved_as": save_fname,
                "reason": result.get("reason", ""),
                "tags": result.get("tags", []),
                "report": result.get("report_to_lian", ""),
            })
            if HAS_STATUS_TRACKER:
                clear_status("analyzer")
        else:
            if delete_after:
                os.remove(fpath)
            print(f"  불필요 → {'삭제' if delete_after else '유지'} ({result.get('reason', '')})")
            entries.append({
                "original": fname,
                "deleted": True,
                "reason": result.get("reason", "불필요"),
                "report": result.get("report_to_lian", ""),
            })

    write_report(entries)
    print(f"\n{'='*60}")
    print(f"완료. 보고사항들.md 업데이트됨.")
    print(f"{'='*60}\n")
    return entries


if __name__ == "__main__":
    root = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_ROOT
    if not os.path.isdir(root):
        print(f"폴더 없음: {root}")
        sys.exit(1)
    run(root)
