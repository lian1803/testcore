"""
전사 팀 오케스트레이션 시스템

역할:
- 모든 팀의 status.json 읽기
- KPI 현황 요약
- 팀 간 방향 충돌 체크
- 개선이 필요한 팀 자동 실행
- 보고사항들.md에 1페이지 요약 업데이트

사용법:
  python orchestrate.py  # 수동 실행
  (또는 2주마다 자동 실행 — scheduler 별도)
"""

import os
import json
from datetime import datetime
import sys
import io

# Windows 콘솔 인코딩 수정
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, os.path.dirname(__file__))

from knowledge.manager import write_report


TEAMS_DIR = os.path.join(os.path.dirname(__file__), "teams")


def _load_team_status(team_name: str) -> dict:
    """팀의 status.json 로드."""
    status_path = os.path.join(TEAMS_DIR, team_name, "status.json")
    if os.path.exists(status_path):
        with open(status_path, encoding="utf-8") as f:
            return json.load(f)
    return None


def _get_all_team_statuses() -> dict:
    """모든 팀의 status 로드."""
    statuses = {}

    for team_name in os.listdir(TEAMS_DIR):
        team_path = os.path.join(TEAMS_DIR, team_name)
        if not os.path.isdir(team_path):
            continue

        status = _load_team_status(team_name)
        if status:
            statuses[team_name] = status

    return statuses


def _identify_weak_teams(statuses: dict) -> list:
    """
    KPI가 약한 팀 식별.
    - data_count가 5 이상인데 개선이 안 된 팀
    - 또는 성과가 zero인 팀
    """
    weak_teams = []

    for team_name, status in statuses.items():
        data_count = status.get("data_count", 0)
        kpi = status.get("kpi", {})

        # 데이터가 5건 이상이지만 아직 개선되지 않은 경우
        if data_count >= 5 and status.get("current_version", "v1") == "v1":
            weak_teams.append({
                "team": team_name,
                "reason": f"데이터 {data_count}건 누적, 아직 개선 미실행",
                "priority": "high"
            })

        # KPI가 모두 null이거나 0인 경우
        non_null_kpis = [v for v in kpi.values() if v is not None and v != 0]
        if not non_null_kpis and data_count > 0:
            weak_teams.append({
                "team": team_name,
                "reason": "데이터는 있으나 KPI 측정 부재",
                "priority": "medium"
            })

    return weak_teams


def _check_conflicts(statuses: dict) -> list:
    """
    팀 간 방향 충돌 체크.
    예: 동일 타겟 지역/업종에 서로 다른 전략을 쓰는 경우
    """
    conflicts = []

    # 현재는 단순 구조. 향후 복잡해지면 확대.
    # 예: offline_marketing과 온라인마케팅팀이 동일 대상인지 확인
    offline_teams = [t for t in statuses.keys() if "마케팅" in t or "영업" in t]

    if len(offline_teams) > 1:
        # 같은 대상을 다루는 경우 알림
        conflicts.append({
            "teams": offline_teams,
            "issue": "마케팅/영업 팀이 여러 개. 타겟 분리 또는 협력 확인 필요",
            "severity": "info"
        })

    return conflicts


def _generate_summary(statuses: dict, weak_teams: list, conflicts: list) -> str:
    """전체 현황 요약 생성."""
    summary = "# 전사 팀 현황 리포트\n\n"
    summary += f"**생성 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"

    # ── 팀별 KPI 현황 ──
    summary += "## 팀별 KPI 현황\n\n"
    summary += "| 팀 | 데이터 | 버전 | 주요 KPI | 상태 |\n"
    summary += "|---|---|---|---|---|\n"

    for team_name, status in sorted(statuses.items()):
        data_count = status.get("data_count", 0)
        version = status.get("current_version", "v1")
        kpi = status.get("kpi", {})

        # 주요 KPI 추출
        kpi_text = ""
        if "월계약건수" in kpi:
            kpi_text += f"계약: {kpi['월계약건수']}건"
        if "답장률" in kpi and kpi["답장률"]:
            kpi_text += f" / 답장: {kpi['답장률']}%"

        # 상태 판단
        if data_count == 0:
            status_emoji = "⏳ 데이터 대기"
        elif data_count >= 5 and version == "v1":
            status_emoji = "🚀 개선 준비"
        else:
            status_emoji = "✅ 진행 중"

        summary += f"| {team_name} | {data_count} | {version} | {kpi_text or 'N/A'} | {status_emoji} |\n"

    summary += "\n"

    # ── 약한 팀 ──
    if weak_teams:
        summary += "## 주의 필요 팀\n\n"
        for weak in weak_teams:
            summary += f"- **{weak['team']}**: {weak['reason']} (우선순위: {weak['priority']})\n"
        summary += "\n"

    # ── 팀 간 충돌 ──
    if conflicts:
        summary += "## 팀 간 협력 항목\n\n"
        for conflict in conflicts:
            summary += f"- {conflict['issue']}\n"
            summary += f"  관련 팀: {', '.join(conflict['teams'])}\n"
        summary += "\n"

    # ── 다음 액션 ──
    summary += "## 다음 액션\n\n"
    summary += "1. **약한 팀 개선**: 위 팀들에 대해 자동 improve() 실행\n"
    summary += "2. **데이터 수집**: 아직 데이터가 없는 팀은 영업 결과 입력 (input_results.py)\n"
    summary += "3. **팀 간 협력**: 충돌 항목은 리안과 함께 방향 정리\n"

    return summary


def run():
    """
    전사 오케스트레이션 실행.
    """
    print(f"\n{'='*60}")
    print("🏢 전사 팀 오케스트레이션")
    print(f"{'='*60}")

    # ── 모든 팀 상태 로드 ──
    print("\n[1] 모든 팀의 status.json 로드 중...")
    statuses = _get_all_team_statuses()
    print(f"    로드된 팀: {len(statuses)}개")

    if not statuses:
        print("    ⚠️  아직 status.json이 있는 팀이 없습니다.")
        print("    각 팀에서 input_results.py로 데이터 수집을 시작하세요.")
        return

    # ── 약한 팀 식별 ──
    print("\n[2] 약한 팀 식별 중...")
    weak_teams = _identify_weak_teams(statuses)
    if weak_teams:
        for weak in weak_teams:
            print(f"    ⚠️  {weak['team']}: {weak['reason']}")
    else:
        print("    ✅ 모든 팀이 양호합니다.")

    # ── 팀 간 충돌 체크 ──
    print("\n[3] 팀 간 충돌 체크 중...")
    conflicts = _check_conflicts(statuses)
    if conflicts:
        for conflict in conflicts:
            print(f"    ℹ️  {conflict['issue']}")
    else:
        print("    ✅ 충돌 없습니다.")

    # ── 요약 생성 ──
    print("\n[4] 현황 요약 생성 중...")
    summary = _generate_summary(statuses, weak_teams, conflicts)

    # ── 보고사항들.md 업데이트 ──
    print("\n[5] 보고사항들.md 업데이트 중...")
    try:
        write_report("오케스트레이션", "전사 팀 현황", summary)
    except Exception as e:
        print(f"    보고 실패: {e}")

    # ── 약한 팀 자동 개선 (선택적) ──
    if weak_teams:
        print(f"\n[6] 약한 팀 자동 개선 ({len(weak_teams)}개)")
        for weak in weak_teams:
            team_name = weak["team"]
            if weak["priority"] == "high":
                print(f"\n    🚀 {team_name} improve() 실행 중...")
                try:
                    # 동적 import
                    module = __import__(f"teams.{team_name}.pipeline", fromlist=["improve"])
                    if hasattr(module, "improve"):
                        module.improve()
                        print(f"    ✅ {team_name} 개선 완료")
                    else:
                        print(f"    ℹ️  {team_name}는 improve() 미지원")
                except Exception as e:
                    print(f"    ❌ {team_name} 개선 실패: {e}")

    # ── 요약 출력 ──
    print(f"\n{'='*60}")
    print("📊 현황 요약 (보고사항들.md에 저장됨)")
    print(f"{'='*60}")
    print(summary)
    print(f"{'='*60}\n")


if __name__ == "__main__":
    run()
