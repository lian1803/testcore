#!/usr/bin/env python3
"""
오프라인 마케팅 팀 — 소상공인 영업툴 전용

사용법:
  python offline_sales.py
  python offline_sales.py "미용실 네이버 플레이스 대행"
"""
import sys
import os
import io

sys.path.insert(0, os.path.dirname(__file__))

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from dotenv import load_dotenv
load_dotenv()

from teams.offline_marketing.pipeline import run

BANNER = """
======================================================
     리안 컴퍼니 — 오프라인 마케팅 팀
  영업 전문가 자료 수집 → 전략 → 스크립트 생성
======================================================
"""

if __name__ == "__main__":
    print(BANNER)

    if len(sys.argv) > 1:
        industry = " ".join(sys.argv[1:])
    else:
        print("영업 대상 업종/서비스 입력 (엔터 = 기본값: 소상공인 네이버 플레이스 대행):")
        print("> ", end="")
        industry = input().strip()
        if not industry:
            industry = "소상공인 네이버 플레이스 마케팅 대행"

    run(industry)
