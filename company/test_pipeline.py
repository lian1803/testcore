#!/usr/bin/env python3
"""
전체 파이프라인 자동 테스트
input()을 자동 응답으로 대체해서 전체 플로우 검증
"""
import sys
import os
import io
from unittest.mock import patch, MagicMock
from collections import deque

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(__file__))
from dotenv import load_dotenv
load_dotenv()

# ── 자동 응답 큐 ─────────────────────────────────────────────
# 순서: 시은 질문들 → 이사팀 진행여부 → PRD 토론 ok → 마케팅 토론 ok
AUTO_INPUTS = deque([
    "마케터-고객 실시간 채팅 MVP, 채팅 안에 결제 링크 연동, 국내 타겟",  # 시은 Q1
    "B",          # 시은 Q2 (있는 플랫폼 개편)
    "B",          # 시은 Q3 (결제·채팅 없음)
    "상용화",      # 시은 Q4 (상용화 여부)
    "ㅇㅇ",        # 이사팀 실행 여부
    "ㅇㅇ",        # 실행팀 진행 여부 (GO 판정 시)
    "ok",          # PRD 토론
    "ok",          # 마케팅 토론
])

def auto_input(prompt=""):
    if AUTO_INPUTS:
        answer = AUTO_INPUTS.popleft()
        print(f"{prompt}{answer}")
        return answer
    return "ok"

# ── 결과 추적 ────────────────────────────────────────────────
results = {
    "agents": {},
    "files": [],
    "verdict": None,
    "errors": []
}

def run_test():
    print("\n" + "="*60)
    print("  LAINCP 전체 파이프라인 자동 테스트")
    print("="*60)

    # subprocess.Popen 모킹 (터미널 자동 실행 스킵)
    mock_popen = MagicMock()

    with patch('builtins.input', side_effect=auto_input), \
         patch('subprocess.Popen', mock_popen):

        try:
            from agents import sieun
            from core.pipeline import run_pipeline, get_client

            # API 키 확인
            print("\n[API 키 확인]")
            client = get_client()
            print("  Anthropic ✅")

            import os
            checks = [
                ("OpenAI", os.getenv("OPENAI_API_KEY")),
                ("Google", os.getenv("GOOGLE_API_KEY")),
                ("Perplexity", os.getenv("PERPLEXITY_API_KEY")),
            ]
            for name, key in checks:
                print(f"  {name} {'✅' if key else '❌ 없음'}")

            # 시은 실행
            print("\n[시은 — 아이디어 명확화]")
            idea = "마케터-고객 실시간 채팅 MVP 채팅 안에 결제 링크 연동"
            sieun_result = sieun.run(idea, client)
            results["agents"]["sieun"] = "✅"
            print(f"\n  → verdict: {sieun_result.get('verdict', 'N/A')}")
            print(f"  → is_commercial: {sieun_result.get('is_commercial', 'N/A')}")

            # 전체 파이프라인
            print("\n[파이프라인 실행]")
            run_pipeline(sieun_result)

            # 터미널 자동 실행 확인
            if mock_popen.called:
                print("\n  새 터미널 자동 실행 ✅")
            else:
                print("\n  새 터미널 자동 실행 — NO-GO로 스킵됨")

        except Exception as e:
            results["errors"].append(str(e))
            print(f"\n❌ 오류: {e}")
            import traceback
            traceback.print_exc()

    # ── 결과 요약 ──────────────────────────────────────────
    print("\n" + "="*60)
    print("  테스트 완료 — 산출물 확인")
    print("="*60)

    output_base = os.path.join(os.path.dirname(__file__), "outputs")
    if os.path.exists(output_base):
        folders = sorted(os.listdir(output_base))
        if folders:
            latest = folders[-1]
            latest_path = os.path.join(output_base, latest)
            files = os.listdir(latest_path)
            print(f"\n  폴더: {latest}")
            for f in sorted(files):
                print(f"  {'✅' if f.endswith('.md') or f.endswith('.json') else '  '} {f}")

    if results["errors"]:
        print(f"\n❌ 오류 {len(results['errors'])}건:")
        for e in results["errors"]:
            print(f"  - {e}")
    else:
        print("\n✅ 오류 없음")

if __name__ == "__main__":
    run_test()
