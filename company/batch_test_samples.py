#!/usr/bin/env python3
"""
오프라인 마케팅팀 샘플 4개 생성 배치
각 업종/상황으로 파이프라인을 실행하고 결과를 평가
"""
import os
import sys
import subprocess
import time
from datetime import datetime

samples = [
    {"name": "양주_미용실", "input": "네이버 플레이스 영업 - 양주 미용실 (D등급, 순위 13위, 월손실 557명)"},
    {"name": "의정부_식당", "input": "네이버 플레이스 영업 - 의정부 식당 (C등급, 순위 8위, 월손실 280명)"},
    {"name": "포천_학원", "input": "네이버 플레이스 영업 - 포천 학원 (D등급, 순위 20위, 월손실 450명)"},
    {"name": "양주_피부관리", "input": "네이버 플레이스 영업 - 양주 피부관리 (B등급, 순위 5위, 월손실 120명)"},
]

def run_sample(sample_info):
    """샘플 1개 실행"""
    name = sample_info["name"]
    input_text = sample_info["input"]

    print(f"\n{'='*70}")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 샘플 시작: {name}")
    print(f"{'='*70}")

    cmd = [
        sys.executable,
        "offline_sales.py",
        input_text
    ]

    try:
        result = subprocess.run(
            cmd,
            cwd="/c/Users/lian1/Documents/Work/core/company",
            capture_output=False,
            timeout=300,
            text=True
        )
        print(f"✅ {name} 완료")
        return True
    except subprocess.TimeoutExpired:
        print(f"❌ {name} 타임아웃 (300초)")
        return False
    except Exception as e:
        print(f"❌ {name} 에러: {e}")
        return False

if __name__ == "__main__":
    print("\n🚀 오프라인 마케팅팀 샘플 4개 생성 배치 시작")
    print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    results = {}
    for sample in samples:
        results[sample["name"]] = run_sample(sample)
        time.sleep(2)  # 각 실행 사이 2초 대기

    print(f"\n{'='*70}")
    print("🏁 배치 완료")
    print(f"{'='*70}")
    for name, success in results.items():
        status = "✅ 성공" if success else "❌ 실패"
        print(f"  {name}: {status}")

    print(f"\n종료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
