"""
daily_log.py — 자율 실행 기록

모든 autopilot 실행의 로그. 주간 리뷰의 데이터 소스.
"""
import os
import json
from datetime import datetime, timedelta

LOG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "knowledge", "daily_log.jsonl")


def log_execution(task_id: str, task_type: str, project: str, result: str, success: bool, cost_estimate: str = "low"):
    """실행 기록 한 줄 추가."""
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    entry = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.now().strftime("%H:%M"),
        "task_id": task_id,
        "type": task_type,
        "project": project,
        "result_summary": result[:500],
        "success": success,
        "cost": cost_estimate,
    }
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"  [daily_log] 기록 실패: {e}")


def get_recent(days: int = 7) -> list[dict]:
    """최근 N일 로그 반환."""
    if not os.path.exists(LOG_PATH):
        return []
    cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    results = []
    try:
        with open(LOG_PATH, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    if entry.get("date", "") >= cutoff:
                        results.append(entry)
                except json.JSONDecodeError:
                    continue
    except Exception:
        pass
    return results


def get_stats(days: int = 7) -> dict:
    """통계: total, success_rate, by_type, by_project."""
    recent = get_recent(days)
    if not recent:
        return {"total": 0, "success_rate": 0.0, "by_type": {}, "by_project": {}}

    total = len(recent)
    success = sum(1 for r in recent if r.get("success"))
    by_type = {}
    by_project = {}
    for r in recent:
        t = r.get("type", "unknown")
        p = r.get("project", "unknown")
        by_type[t] = by_type.get(t, 0) + 1
        by_project[p] = by_project.get(p, 0) + 1

    return {
        "total": total,
        "success_rate": round(success / total, 2) if total else 0.0,
        "by_type": by_type,
        "by_project": by_project,
    }


def get_last_run(project: str, task_type: str) -> dict | None:
    """특정 프로젝트+타입의 마지막 실행."""
    recent = get_recent(days=30)
    for entry in reversed(recent):
        if entry.get("project") == project and entry.get("type") == task_type:
            return entry
    return None


def get_approval_count(project: str, task_type: str) -> int:
    """특정 카테고리의 성공 실행 횟수 (자율 전환 판단용).
    project가 비어있으면 카테고리 전체 카운트."""
    recent = get_recent(days=90)
    count = 0
    for r in recent:
        if not r.get("success"):
            continue
        type_match = r.get("type") == task_type or r.get("category") == task_type
        if not type_match:
            continue
        if project:
            if r.get("project") == project:
                count += 1
        else:
            count += 1
    return count
