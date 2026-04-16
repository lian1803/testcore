#!/usr/bin/env python3
"""
인스타분석팀 실행 진입점

사용법:
  python run_인스타분석팀.py "C:/path/to/links.txt"
"""
import sys
import os
import io

sys.path.insert(0, os.path.dirname(__file__))
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from dotenv import load_dotenv
load_dotenv()

from teams.인스타분석팀.pipeline import run

if __name__ == "__main__":
    txt_file = sys.argv[1] if len(sys.argv) > 1 else ""
    clone_mode = "--clone" in sys.argv
    run(txt_file, clone_mode)
