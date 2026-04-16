r"""
디자인스카우팅팀 Pipeline
Orchestrates all team members in parallel, then generates final briefing

Usage:
  python teams/디자인스카우팅팀/pipeline.py

Daily Cron Setup (Windows Task Scheduler):
  Windows Task Scheduler → Create Basic Task
  Name: "Design Scouting Team Daily"
  Trigger: Daily at 9:00 AM
  Action: Start a program
    Program: C:\Users\lian1\Documents\Work\core\company\venv\Scripts\python.exe
    Arguments: teams/디자인스카우팅팀/pipeline.py
    Start in: C:\Users\lian1\Documents\Work\core\company
"""

import sys
import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from teams.디자인스카우팅팀.박어워즈 import AwwardsScout
from teams.디자인스카우팅팀.서트렌드 import TrendResearcher
from teams.디자인스카우팅팀.김레포 import DesignSystemScanner
from teams.디자인스카우팅팀.디자인정보 import DesignBriefingGenerator
from teams.디자인스카우팅팀 import 업종별리서치


def run_scout(scout_name: str, scout_class, *args):
    """Run a single scout"""
    try:
        print(f"[START] {scout_name}...")
        scout = scout_class(*args)
        result = scout.run()
        print(f"[SUCCESS] {scout_name} completed")
        return (scout_name, result, None)
    except Exception as e:
        print(f"[ERROR] {scout_name} failed: {e}")
        return (scout_name, None, str(e))


def main():
    """Main pipeline execution"""
    print("\n" + "=" * 60)
    print("[DESIGN SCOUTING TEAM] Pipeline started")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60 + "\n")

    # Run scouts in parallel
    scouts = [
        ("박어워즈", AwwardsScout),
        ("서트렌드", TrendResearcher),
        ("김레포", DesignSystemScanner),
    ]

    results = {}
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(run_scout, name, scout_class): name
            for name, scout_class in scouts
        }

        for future in as_completed(futures):
            scout_name, result, error = future.result()
            results[scout_name] = {"result": result, "error": error}

    # Check if all scouts completed
    failed_scouts = [name for name, data in results.items() if data["error"]]
    if failed_scouts:
        print(f"\n[WARNING] Failed scouts: {', '.join(failed_scouts)}")
    else:
        print(f"\n[SUCCESS] All scouts completed")

    # 업종별 리서치 (주 1회 — 월요일만 실행, 평일은 스킵)
    if datetime.now().weekday() == 0:  # 0 = Monday
        print("\n[INFO] 업종별리서치 실행 (월요일)...")
        try:
            업종별리서치.run()
            print("[SUCCESS] 업종패턴DB 업데이트 완료")
        except Exception as e:
            print(f"[WARNING] 업종별리서치 실패: {e}")
    else:
        print("[INFO] 업종별리서치 스킵 (월요일만 실행)")

    # Generate briefing
    print("\n[INFO] Generating briefing...")
    try:
        generator = DesignBriefingGenerator()
        briefing = generator.run()
        print(f"[SUCCESS] Briefing generated")
    except Exception as e:
        print(f"[ERROR] Briefing generation failed: {e}")
        return 1

    # Summary
    print("\n" + "=" * 60)
    print("[SUCCESS] Design Scouting Team pipeline completed")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
