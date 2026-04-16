#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
os.environ.setdefault("PYTHONUTF8", "1")
"""
리안 컴퍼니 — AI 멀티에이전트 기획 자동화 시스템

사용법:
  python main.py                          # 대화형 모드 (시은과 대화)
  python main.py "소상공인 AI 상세페이지"   # 자동파일럿 모드 (한마디 → 보고서)
"""
import sys
import os
import io

# 프로젝트 루트를 경로에 추가
sys.path.insert(0, os.path.dirname(__file__))

# Windows UTF-8 강제 설정 (robust하게)
if sys.platform == "win32":
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass  # 이미 설정되어 있거나 실패했으면 무시

from dotenv import load_dotenv
load_dotenv()

from agents import sieun
from core.pipeline import run_pipeline, get_client
from core.notifier import notify_pipeline_start
# from core.cost_estimator import confirm_proceed  # Phase 2: 비용 확인 자동 통과


BANNER = """
======================================================
          리안 컴퍼니 (LIAN COMPANY)
    아이디어 -> 설계서 자동 완성 AI 시스템
======================================================
"""


def main():
    print(BANNER)

    # API 키 확인
    try:
        client = get_client()
    except ValueError as e:
        print(f"❌ {e}")
        sys.exit(1)

    # 아이디어 받기
    if len(sys.argv) > 1:
        idea = " ".join(sys.argv[1:])
        print(f"💡 아이디어: {idea}")
        print(f"🚀 자동파일럿 모드 — 리안 개입 없이 보고서까지 자동 진행\n")

        # 자동파일럿: input() 없이 시은이 자동 명확화
        sieun_result = sieun.autopilot_run(idea, client)

        # 이사팀 자동 실행 (자동파일럿)
        print(f"\n{'='*60}")
        print("이사팀 자동파일럿 실행 중...")
        notify_pipeline_start(idea)
        run_pipeline(sieun_result, autopilot=True)

    else:
        print("💡 아이디어를 입력해줘 (엔터로 제출):")
        print("리안: ", end="")
        idea = input().strip()
        if not idea:
            print("아이디어를 입력해야 해.")
            sys.exit(1)

        # 대화형: 시은과 대화하며 명확화
        sieun_result = sieun.run(idea, client, interactive=True)

        # 이사팀 대화형 실행
        print(f"\n{'='*60}")
        print("이사팀 자동 실행 중...")
        notify_pipeline_start(idea)
        run_pipeline(sieun_result, autopilot=False)


if __name__ == "__main__":
    main()
