#!/usr/bin/env python3
"""
디자인팀 실행 v2

사용법:
  python run_디자인팀.py "프로젝트 설명"
  python run_디자인팀.py "꽃집 랜딩페이지" --pick A    # 자동으로 A 선택
  python run_디자인팀.py "꽃집 랜딩페이지" --pick B
"""
import sys, os, io
sys.path.insert(0, os.path.dirname(__file__))
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except:
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from dotenv import load_dotenv
load_dotenv()
from teams.디자인팀.pipeline import run

if __name__ == "__main__":
    args = sys.argv[1:]

    # --pick A/B/C 파싱
    auto_pick = None
    if "--pick" in args:
        idx = args.index("--pick")
        if idx + 1 < len(args):
            auto_pick = args[idx + 1].upper()
            args = args[:idx] + args[idx+2:]

    project_desc = " ".join(args).strip()

    if not project_desc:
        print("프로젝트 설명 입력 (어떤 사이트 만들거야?):")
        project_desc = input("> ").strip()

    run(project_desc, auto_pick=auto_pick)
