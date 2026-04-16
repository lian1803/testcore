#!/usr/bin/env python3
"""
인하우스 마케터·프리랜서용 통합 마케팅 대시보드 SaaS 팀 실행

사용법:
  python run_인하우스_마케터프리랜서용_통합_마케팅_대시보드_SaaS_팀.py
  python run_인하우스_마케터프리랜서용_통합_마케팅_대시보드_SaaS_팀.py "업무 내용"
"""
import sys, os, io
sys.path.insert(0, os.path.dirname(__file__))
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from dotenv import load_dotenv
load_dotenv()
from teams.인하우스_마케터프리랜서용_통합_마케팅_대시보드_SaaS_팀.pipeline import run

if __name__ == "__main__":
    task = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else ""
    if not task:
        print("업무 내용 입력:")
        task = input("> ").strip()
    run(task)
