#!/usr/bin/env python3
"""
오프라인 자영업자 마케팅 대행 실행팀 실행

사용법:
  python run_오프라인_자영업자_마케팅_대행_실행팀.py
  python run_오프라인_자영업자_마케팅_대행_실행팀.py "업무 내용"
"""
import sys, os, io
sys.path.insert(0, os.path.dirname(__file__))
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from dotenv import load_dotenv
load_dotenv()
from teams.오프라인_자영업자_마케팅_대행_실행팀.pipeline import run

if __name__ == "__main__":
    task = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else ""
    if not task:
        print("업무 내용 입력:")
        task = input("> ").strip()
    run(task)
