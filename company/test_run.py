#!/usr/bin/env python3
"""
리안 컴퍼니 풀 파이프라인 테스트 — 비인터랙티브 자동 실행
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

from core.pipeline import run_pipeline, get_client
from agents import sieun

IDEA = """소상공인 사장님들(카페, 네일샵, 식당)이 매일 인스타 올려야 하는데
지피티로 글 쓰고 → 캔바 가서 디자인하고 → 인스타 가서 올리는
이 루틴이 존나 귀찮음.
업종 선택하면 매일 자동으로 캡션+이미지 생성해서
인스타에 자동 발행해주는 월 9,900원 구독 서비스"""

def main():
    print("=" * 60)
    print("  리안 컴퍼니 풀 파이프라인 테스트 (자동 실행)")
    print("=" * 60)
    print(f"\n💡 아이디어: {IDEA[:50]}...\n")

    client = get_client()

    # sieun 결과를 직접 구성 (명확화 단계 스킵 — 아이디어가 이미 명확)
    sieun_result = {
        "idea": IDEA,
        "clarified": IDEA,
        "is_commercial": True,  # 월 9,900원 구독 서비스 = 상용화
    }

    print("✅ 시은: 아이디어 명확함 — 상용화 서비스로 판단, 이사팀 바로 시작\n")

    # 파이프라인 실행 (input() 호출 부분을 모두 자동 통과하도록 monkeypatch)
    import builtins
    original_input = builtins.input

    call_count = [0]

    def auto_input(prompt=""):
        call_count[0] += 1
        print(f"[자동응답 #{call_count[0]}] ㅇㅇ")
        return "ㅇㅇ"

    builtins.input = auto_input

    try:
        run_pipeline(sieun_result)
    finally:
        builtins.input = original_input

    print("\n\n✅ 풀 파이프라인 완료!")


if __name__ == "__main__":
    main()
