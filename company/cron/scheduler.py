#!/usr/bin/env python3
"""
리안 컴퍼니 크론 스케줄러

Windows에서 백그라운드 실행:
  pythonw cron/scheduler.py

또는 Windows Task Scheduler에 등록:
  트리거: 시스템 부팅
  작업: pythonw "C:\...path\...\cron\scheduler.py"
"""

import schedule
import time
import sys
import os
from datetime import datetime

# 프로젝트 루트를 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from cron import sentinel, mijeong, doctor
from core.notifier import notify_error


def job_sentinel():
    """30분마다 헬스체크 실행"""
    try:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 센티넬 실행...")
        sentinel.run_health_check()
    except Exception as e:
        print(f"❌ 센티넬 오류: {e}")
        notify_error("SENTINEL", str(e))


def job_mijeong():
    """매일 08:00 일일 보고 실행"""
    try:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 미정 실행...")
        mijeong.run_daily_report()
    except Exception as e:
        print(f"❌ 미정 오류: {e}")
        notify_error("MIJEONG", str(e))


def schedule_jobs():
    """스케줄 등록"""
    schedule.every(30).minutes.do(job_sentinel)
    schedule.every().day.at("08:00").do(job_mijeong)

    print("📅 크론 작업 등록 완료:")
    print("  - 센티넬: 30분마다")
    print("  - 미정: 매일 08:00")
    print("\n🔄 스케줄러 대기 중... (Ctrl+C로 종료)")


def run_scheduler():
    """메인 루프"""
    schedule_jobs()

    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # 1분마다 체크
        except KeyboardInterrupt:
            print("\n⏹️  스케줄러 종료")
            sys.exit(0)
        except Exception as e:
            print(f"❌ 스케줄러 오류: {e}")
            notify_error("SCHEDULER", str(e))
            time.sleep(60)


if __name__ == "__main__":
    # 의존성 확인
    try:
        import schedule
    except ImportError:
        print("❌ schedule 라이브러리 미설치")
        print("  설치: pip install schedule")
        sys.exit(1)

    run_scheduler()
