#!/usr/bin/env python3
"""
Kello 팀 — 외국인 K-뷰티 예약 플랫폼 실행

사용법:
  python run_Kello_팀__외국인_K뷰티_예약_플랫폼.py
  python run_Kello_팀__외국인_K뷰티_예약_플랫폼.py "업무 내용"
"""
import sys, os, io
sys.path.insert(0, os.path.dirname(__file__))
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from dotenv import load_dotenv
load_dotenv()
from teams.Kello_팀__외국인_K뷰티_예약_플랫폼.pipeline import run

if __name__ == "__main__":
    task = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else ""
    if not task:
        print("업무 내용 입력:")
        task = input("> ").strip()
    run(task)
