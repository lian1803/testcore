#!/usr/bin/env python3
"""
온라인영업팀 실행

사용법:
  python run_온라인영업팀.py
  python run_온라인영업팀.py "업무 내용"
"""
import sys, os, io
sys.path.insert(0, os.path.dirname(__file__))
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, Exception):
        pass
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, Exception):
        pass
os.environ["_LIANCP_UTF8_DONE"] = "1"  # prevent double-wrapping in submodules

from dotenv import load_dotenv
load_dotenv()
from teams.온라인영업팀.pipeline import run

if __name__ == "__main__":
    task = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else ""
    if not task:
        print("업무 내용 입력:")
        task = input("> ").strip()
    run(task)
