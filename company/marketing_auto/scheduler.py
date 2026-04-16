"""
마케팅 자동 스케줄러 — 최적 시간에 자동 포스팅

인스타 최적 시간 (한국 기준):
- 평일: 오전 7-9시, 오후 12-1시, 오후 7-9시
- 주말: 오전 10-11시, 오후 3-5시

실행:
  python scheduler.py           # 스케줄러 시작 (백그라운드)
  python scheduler.py --once    # 지금 바로 큐 실행 1회
  python scheduler.py --dry-run # 실제 발행 없이 미리보기
"""
import os
import sys
import time
import schedule
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# 경로 설정
BASE_DIR = os.path.dirname(__file__)
QUEUE_FILE = os.path.join(BASE_DIR, "content_queue.json")
LOG_FILE = os.path.join(BASE_DIR, "post_log.jsonl")

# 포스팅 간격 (분) — API 제한 방어
MIN_INTERVAL_MINUTES = 30


def _log(event: str, data: dict):
    import json
    entry = {"ts": datetime.now().isoformat(), "event": event, **data}
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def run_queue(dry_run: bool = False):
    """큐에서 예약된 콘텐츠 처리"""
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M')}] 큐 처리 시작...")
    try:
        from instagram_poster import post_from_queue
        results = post_from_queue(QUEUE_FILE, dry_run=dry_run)
        for r in results:
            _log("post", {"status": r.get("status"), "post_id": r.get("post_id", "")})
    except ValueError as e:
        print(f"⚠️  {e}")
    except Exception as e:
        print(f"❌ 오류: {e}")
        _log("error", {"msg": str(e)})


def start_scheduler(dry_run: bool = False):
    """인스타 최적 시간 스케줄 등록"""
    print("📅 마케팅 스케줄러 시작")
    print("인스타 최적 시간: 오전 7시, 오후 12시, 오후 7시 (평일)")
    print("Ctrl+C로 종료\n")

    # 평일 + 주말 커버
    for t in ["07:00", "12:00", "19:00"]:
        schedule.every().monday.at(t).do(run_queue, dry_run=dry_run)
        schedule.every().tuesday.at(t).do(run_queue, dry_run=dry_run)
        schedule.every().wednesday.at(t).do(run_queue, dry_run=dry_run)
        schedule.every().thursday.at(t).do(run_queue, dry_run=dry_run)
        schedule.every().friday.at(t).do(run_queue, dry_run=dry_run)

    for t in ["10:00", "15:00"]:
        schedule.every().saturday.at(t).do(run_queue, dry_run=dry_run)
        schedule.every().sunday.at(t).do(run_queue, dry_run=dry_run)

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv

    if "--once" in sys.argv:
        run_queue(dry_run=dry_run)
    else:
        # schedule 패키지 확인
        try:
            import schedule
        except ImportError:
            print("설치: pip install schedule")
            sys.exit(1)
        start_scheduler(dry_run=dry_run)
