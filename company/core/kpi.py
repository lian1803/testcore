"""
kpi.py — 팀별 월간 목표 설정 + 달성률 추적

각 팀의 KPI를 중앙에서 관리하고,
daily_log.jsonl의 성과 데이터를 자동으로 집계.

autopilot planner가 이 KPI를 참고해서 우선순위 결정.

사용 예시:
    from core.kpi import (
        get_kpi_status,
        get_kpi_summary,
        update_kpi,
        get_team_kpi
    )

    # 현재 KPI 상태 조회
    status = get_kpi_status()
    print(status)

    # autopilot 프롬프트에 주입할 텍스트
    summary = get_kpi_summary()
    print(summary)

    # 팀 성과 수동 업데이트
    update_kpi("온라인영업팀", "상담 신청", 2)
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from pathlib import Path

# 기본 KPI 설정
DEFAULT_KPIS = {
    "온라인영업팀": {
        "metric": "상담 신청",
        "monthly_target": 5,
        "unit": "건",
        "description": "영업 DM 아웃리치로 얻은 상담 신청"
    },
    "오프라인마케팅팀": {
        "metric": "대행 계약",
        "monthly_target": 1,
        "unit": "건",
        "description": "오프라인 영업을 통한 마케팅 대행 계약"
    },
    "온라인납품팀": {
        "metric": "콘텐츠 발행",
        "monthly_target": 20,
        "unit": "개",
        "description": "블로그/인스타그램 콘텐츠 발행"
    },
    "온라인마케팅팀": {
        "metric": "리드 발굴",
        "monthly_target": 30,
        "unit": "개",
        "description": "마케팅 채널에서 발굴한 리드/잠재고객"
    },
}

# KPI 저장 경로
KPI_FILE = "/c/Users/lian1/Documents/Work/core/company/knowledge/kpi.json"
DAILY_LOG_FILE = "/c/Users/lian1/Documents/Work/core/company/core/daily_log.jsonl"


def _load_kpi_data() -> Dict:
    """
    KPI 파일에서 데이터 로드.
    없으면 기본값으로 초기화.
    """
    if os.path.exists(KPI_FILE):
        try:
            with open(KPI_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"KPI 파일 로드 실패: {str(e)}")
            return _init_kpi_file()
    else:
        return _init_kpi_file()


def _init_kpi_file() -> Dict:
    """
    KPI 파일 초기화.
    """
    os.makedirs(os.path.dirname(KPI_FILE), exist_ok=True)

    # 현재 월 계산
    today = datetime.now()
    month_key = today.strftime("%Y-%m")

    kpi_data = {
        "current_month": month_key,
        "last_updated": datetime.now().isoformat(),
        "teams": {}
    }

    for team_name, config in DEFAULT_KPIS.items():
        kpi_data["teams"][team_name] = {
            "config": config,
            "current": 0,
            "history": []  # [{"date": "2026-04-04", "value": 2}]
        }

    _save_kpi_data(kpi_data)
    return kpi_data


def _save_kpi_data(data: Dict):
    """
    KPI 데이터를 파일로 저장.
    """
    os.makedirs(os.path.dirname(KPI_FILE), exist_ok=True)
    with open(KPI_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_team_kpi(team_name: str) -> Optional[Dict]:
    """
    특정 팀의 KPI 조회.

    Args:
        team_name: 팀 이름

    Returns:
        {
            "team": "온라인영업팀",
            "metric": "상담 신청",
            "target": 5,
            "current": 2,
            "progress": 40.0,  # 백분율
            "remaining": 3,
            "unit": "건",
            "status": "진행 중"  # "진행 중" / "목표 달성" / "미달"
        }
    """

    kpi_data = _load_kpi_data()
    team_data = kpi_data["teams"].get(team_name)

    if not team_data:
        return None

    config = team_data["config"]
    current = team_data["current"]
    target = config["monthly_target"]

    progress = (current / target * 100) if target > 0 else 0
    remaining = max(0, target - current)

    # 상태 판정
    if current >= target:
        status = "목표 달성"
    elif current > 0:
        status = "진행 중"
    else:
        status = "미달"

    return {
        "team": team_name,
        "metric": config["metric"],
        "target": target,
        "current": current,
        "progress": round(progress, 1),
        "remaining": remaining,
        "unit": config["unit"],
        "status": status,
        "description": config["description"]
    }


def get_kpi_status() -> Dict:
    """
    전체 팀의 KPI 달성률 반환.

    Returns:
        {
            "current_month": "2026-04",
            "teams": {
                "온라인영업팀": {...},
                ...
            },
            "summary": {
                "total_teams": 4,
                "achieved": 1,
                "in_progress": 2,
                "behind": 1
            }
        }
    """

    kpi_data = _load_kpi_data()
    teams_status = {}
    summary = {
        "total_teams": 0,
        "achieved": 0,
        "in_progress": 0,
        "behind": 0
    }

    for team_name in DEFAULT_KPIS.keys():
        team_kpi = get_team_kpi(team_name)
        if team_kpi:
            teams_status[team_name] = team_kpi
            summary["total_teams"] += 1

            if team_kpi["status"] == "목표 달성":
                summary["achieved"] += 1
            elif team_kpi["status"] == "진행 중":
                summary["in_progress"] += 1
            else:
                summary["behind"] += 1

    return {
        "current_month": kpi_data["current_month"],
        "teams": teams_status,
        "summary": summary,
        "last_updated": kpi_data["last_updated"]
    }


def get_kpi_summary() -> str:
    """
    autopilot planner 프롬프트에 주입할 KPI 요약 텍스트.

    Returns:
        마크다운 형식의 요약 텍스트
    """

    status = get_kpi_status()
    lines = []

    lines.append(f"## 팀별 KPI 현황 ({status['current_month']})")
    lines.append("")

    for team_name, kpi in status["teams"].items():
        progress_bar = _make_progress_bar(kpi["progress"])
        lines.append(
            f"### {team_name} - {kpi['metric']}"
        )
        lines.append(
            f"{kpi['current']}{kpi['unit']} / {kpi['target']}{kpi['unit']} {progress_bar} ({kpi['status']})"
        )
        lines.append("")

    # 요약
    summary = status["summary"]
    lines.append("## 우선순위")
    lines.append(
        f"- 목표 달성한 팀 ({summary['achieved']}): 유지 모드"
    )
    lines.append(
        f"- 진행 중인 팀 ({summary['in_progress']}): 계획 수행"
    )
    lines.append(
        f"- 미달한 팀 ({summary['behind']}): 우선 지원 + 추진력 강화"
    )

    return "\n".join(lines)


def update_kpi(team_name: str, metric: str, value: int, reason: str = ""):
    """
    팀의 KPI를 수동으로 업데이트.

    Args:
        team_name: 팀 이름
        metric: 메트릭 이름 (검증용)
        value: 증가값 (음수 가능)
        reason: 업데이트 사유 (선택)
    """

    kpi_data = _load_kpi_data()

    if team_name not in kpi_data["teams"]:
        print(f"팀을 찾을 수 없습니다: {team_name}")
        return False

    team_data = kpi_data["teams"][team_name]

    # 메트릭 검증
    if team_data["config"]["metric"] != metric:
        print(
            f"메트릭 불일치: {team_data['config']['metric']} != {metric}"
        )
        return False

    # 값 업데이트
    team_data["current"] += value
    team_data["current"] = max(0, team_data["current"])  # 음수 방지

    # 히스토리에 기록
    today = datetime.now().strftime("%Y-%m-%d")
    team_data["history"].append({
        "date": today,
        "delta": value,
        "total": team_data["current"],
        "reason": reason
    })

    kpi_data["last_updated"] = datetime.now().isoformat()

    _save_kpi_data(kpi_data)

    print(
        f"✓ {team_name}: {metric} +{value} → 총 {team_data['current']}{team_data['config']['unit']}"
    )
    return True


def aggregate_from_daily_log() -> Dict:
    """
    daily_log.jsonl에서 팀별 성과 자동 집계.

    daily_log.jsonl 형식:
    {"date": "2026-04-04", "team": "온라인영업팀", "action": "상담신청획득", "count": 2, "details": "..."}

    이 함수는 당월의 모든 로그를 읽어서 팀별 KPI에 반영.
    """

    if not os.path.exists(DAILY_LOG_FILE):
        return {}

    try:
        aggregated = {}
        current_month = datetime.now().strftime("%Y-%m")

        with open(DAILY_LOG_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                log = json.loads(line)

                # 당월 데이터만
                if not log.get("date", "").startswith(current_month):
                    continue

                team = log.get("team")
                action = log.get("action")
                count = log.get("count", 1)

                if not team or not action:
                    continue

                if team not in aggregated:
                    aggregated[team] = {}

                aggregated[team][action] = aggregated[team].get(action, 0) + count

        return aggregated

    except Exception as e:
        print(f"daily_log 집계 실패: {str(e)}")
        return {}


def sync_kpi_from_logs():
    """
    daily_log.jsonl의 데이터를 KPI에 동기화.

    매일 아침이나 정해진 시간에 자동 실행되어야 함.
    """

    aggregated = aggregate_from_daily_log()

    # action과 KPI metric 매핑
    action_to_metric = {
        "상담신청획득": ("온라인영업팀", "상담 신청"),
        "대행계약체결": ("오프라인마케팅팀", "대행 계약"),
        "콘텐츠발행": ("온라인납품팀", "콘텐츠 발행"),
        "리드발굴": ("온라인마케팅팀", "리드 발굴"),
    }

    for team, actions in aggregated.items():
        for action, count in actions.items():
            if action in action_to_metric:
                target_team, metric = action_to_metric[action]

                # 이미 반영된 것 제외 (여러 번 동기화 방지)
                team_kpi = get_team_kpi(target_team)
                if team_kpi and team_kpi["current"] < count:
                    delta = count - team_kpi["current"]
                    update_kpi(target_team, metric, delta, reason="자동 집계")


def _make_progress_bar(percentage: float, width: int = 20) -> str:
    """
    시각적인 진행률 바 생성.

    예: [████████░░░░░░░░░░] 40%
    """
    filled = int(width * percentage / 100)
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}] {percentage:.0f}%"


def get_kpi_summary_for_planner() -> str:
    """
    autopilot planner에 주입하기 위한 KPI 정보.

    PLANNING_RULES에 추가될 텍스트.
    """

    status = get_kpi_status()
    lines = []

    lines.append("## KPI 기반 우선순위")
    lines.append("")

    # 달성률 낮은 팀부터 나열
    teams_by_progress = sorted(
        status["teams"].items(),
        key=lambda x: x[1]["progress"]
    )

    for team_name, kpi in teams_by_progress:
        if kpi["progress"] < 50:
            lines.append(
                f"- {team_name}: 달성률 {kpi['progress']:.0f}% (목표까지 {kpi['remaining']}{kpi['unit']}) -> 우선 지원"
            )
        elif kpi["progress"] < 100:
            lines.append(
                f"- {team_name}: 달성률 {kpi['progress']:.0f}% (진행 중) -> 계획 수행"
            )
        else:
            lines.append(
                f"- {team_name}: 목표 달성 ({kpi['current']}{kpi['unit']}) -> 유지 모드"
            )

    lines.append("")
    lines.append("우선순위가 낮은 팀의 태스크는 나중으로 미루고, 미달한 팀의 태스크를 먼저 추진합니다.")

    return "\n".join(lines)


if __name__ == "__main__":
    # 테스트 예시

    print("=== KPI 초기화 ===")
    kpi_data = _init_kpi_file()
    print("KPI 파일 생성 완료")
    print()

    print("=== 현재 KPI 상태 ===")
    status = get_kpi_status()
    print(json.dumps(status, ensure_ascii=False, indent=2))
    print()

    print("=== KPI 요약 ===")
    summary = get_kpi_summary()
    print(summary)
    print()

    print("=== 플래너용 KPI 요약 ===")
    planner_summary = get_kpi_summary_for_planner()
    print(planner_summary)
    print()

    print("=== 수동 업데이트 테스트 ===")
    update_kpi("온라인영업팀", "상담 신청", 2, reason="테스트")
    print()

    print("=== 업데이트 후 상태 ===")
    team_kpi = get_team_kpi("온라인영업팀")
    print(json.dumps(team_kpi, ensure_ascii=False, indent=2))
