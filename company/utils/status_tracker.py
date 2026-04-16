"""
에이전트 실시간 상태 추적 시스템

사용법:
  from utils.status_tracker import update_status, clear_status

  update_status("박탐정", "온라인영업팀", "running", "경쟁사 광고 분석 중")
  # ... 에이전트 작업
  clear_status("박탐정")
"""

import json
import time
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any


STATUS_FILE = Path(__file__).parent.parent / ".agent_status.json"


def _load_status() -> Dict[str, Any]:
    """상태 파일에서 현재 상태 로드"""
    if STATUS_FILE.exists():
        try:
            with open(STATUS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {"agents": {}, "last_updated": datetime.now().isoformat()}
    return {"agents": {}, "last_updated": datetime.now().isoformat()}


def _save_status(data: Dict[str, Any]) -> None:
    """상태를 파일에 저장"""
    try:
        STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(STATUS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except IOError as e:
        print(f"⚠️ 상태 파일 저장 실패: {e}")


def update_status(
    agent_name: str,
    team: str,
    status: str,
    detail: str = "",
) -> None:
    """
    에이전트 현재 상태 업데이트

    Args:
        agent_name: 에이전트 이름 (예: "박탐정")
        team: 팀 이름 (예: "온라인영업팀")
        status: 상태 ("running", "completed", "error")
        detail: 상세 설명 (예: "경쟁사 광고 분석 중")
    """
    data = _load_status()
    now = datetime.now().isoformat()

    # 이전에 실행중이던 에이전트면 started_at 유지, 아니면 새로 생성
    if agent_name not in data["agents"]:
        data["agents"][agent_name] = {
            "team": team,
            "status": status,
            "detail": detail,
            "started_at": now,
            "updated_at": now,
        }
    else:
        # started_at 유지, 나머지만 업데이트
        data["agents"][agent_name].update({
            "team": team,
            "status": status,
            "detail": detail,
            "updated_at": now,
        })

    data["last_updated"] = now
    _save_status(data)


def clear_status(agent_name: Optional[str] = None) -> None:
    """
    에이전트 상태 초기화 (완료 시)

    Args:
        agent_name: 초기화할 에이전트 이름. None이면 전체 초기화
    """
    data = _load_status()

    if agent_name is None:
        data["agents"] = {}
    elif agent_name in data["agents"]:
        del data["agents"][agent_name]

    data["last_updated"] = datetime.now().isoformat()
    _save_status(data)


def get_status() -> Dict[str, Any]:
    """전체 에이전트 상태 조회"""
    return _load_status()


def get_elapsed(agent_name: str) -> str:
    """에이전트 경과 시간 반환 (예: "32초", "2분 15초")"""
    data = _load_status()
    if agent_name not in data["agents"]:
        return "—"

    try:
        started = datetime.fromisoformat(data["agents"][agent_name]["started_at"])
        elapsed_seconds = int((datetime.now() - started).total_seconds())

        if elapsed_seconds < 60:
            return f"{elapsed_seconds}초"
        elif elapsed_seconds < 3600:
            minutes = elapsed_seconds // 60
            seconds = elapsed_seconds % 60
            if seconds == 0:
                return f"{minutes}분"
            return f"{minutes}분 {seconds}초"
        else:
            hours = elapsed_seconds // 3600
            minutes = (elapsed_seconds % 3600) // 60
            if minutes == 0:
                return f"{hours}시간"
            return f"{hours}시간 {minutes}분"
    except (ValueError, KeyError):
        return "—"


def print_status() -> None:
    """현재 상태를 터미널에 이쁘게 출력"""
    data = _load_status()

    if not data["agents"]:
        print("🟢 모든 에이전트 대기 중")
        return

    print("\n" + "="*70)
    print("📊 에이전트 상태")
    print("="*70)

    for agent_name, info in sorted(data["agents"].items()):
        team = info.get("team", "—")
        status = info.get("status", "—")
        detail = info.get("detail", "")
        elapsed = get_elapsed(agent_name)

        # 상태별 이모지
        status_emoji = {
            "running": "🟠",
            "completed": "🟢",
            "error": "🔴",
        }.get(status, "⚪")

        status_text = {
            "running": "실행 중",
            "completed": "완료",
            "error": "에러",
        }.get(status, status)

        # 포맷팅
        print(f"\n{status_emoji} {agent_name} ({team})")
        print(f"   상태: {status_text} | 경과: {elapsed}")
        if detail:
            print(f"   작업: {detail}")

    print("\n" + "="*70 + "\n")


def format_status_line(agent_name: str) -> str:
    """한 줄 상태 포맷팅 (로깅용)"""
    data = _load_status()
    if agent_name not in data["agents"]:
        return f"[{agent_name}] —"

    info = data["agents"][agent_name]
    team = info.get("team", "—")
    detail = info.get("detail", "")
    elapsed = get_elapsed(agent_name)

    status_emoji = {
        "running": "🟠",
        "completed": "🟢",
        "error": "🔴",
    }.get(info.get("status", "—"), "⚪")

    if detail:
        return f"{status_emoji} {agent_name} ({team}) | {detail} | {elapsed}"
    else:
        return f"{status_emoji} {agent_name} ({team}) | {elapsed}"
