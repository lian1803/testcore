"""
weekly_runner.py — 리안 컴퍼니 주간 리뷰 자동 실행 스크립트

Windows 작업 스케줄러에 등록하면 매주 월요일 자동 실행.
리안이 직접 돌릴 필요 없음.

실행: python weekly_runner.py
"""
import os
import sys
import io
from datetime import datetime

# 인코딩 설정 (daily_auto.py 동일)
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(__file__))
from dotenv import load_dotenv
load_dotenv()

# 실행 로그 — 스케줄러가 실제로 돌았는지 확인용
RUN_LOG_PATH = os.path.join(os.path.dirname(__file__), "weekly_run.log")
REPORT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "보고사항들.md")


def log(msg: str):
    timestamp = datetime.now().strftime("%H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    try:
        with open(RUN_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    except Exception:
        pass


def get_active_projects() -> list:
    """team/ 폴더에서 활성 프로젝트 자동 감지 (daily_auto.py 동일 방식)."""
    team_root = os.path.join(os.path.dirname(os.path.dirname(__file__)), "team")
    active = []
    if not os.path.exists(team_root):
        return active

    skip_prefixes = ["[중단]", "[나중에]"]
    for folder in os.listdir(team_root):
        # 중단/나중에 폴더 제외
        if any(folder.startswith(p) for p in skip_prefixes):
            continue
        folder_path = os.path.join(team_root, folder)
        if os.path.isdir(folder_path) and any(
            os.path.exists(os.path.join(folder_path, f))
            for f in ["CLAUDE.md", "PRD.md", "런칭준비.md"]
        ):
            active.append(folder)
    return active


def main():
    log(f"=== 리안 컴퍼니 주간 리뷰 시작 ({datetime.now().strftime('%Y-%m-%d')}) ===")
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    results = []

    # ── 주간 리뷰: 활성 프로젝트 전체 ──────────────
    log("활성 프로젝트 감지 중...")
    try:
        from core.ops_loop import weekly_loop

        active_projects = get_active_projects()
        if not active_projects:
            log("  활성 프로젝트 없음 — 스킵")
            results.append("주간 리뷰: 활성 프로젝트 없음")
        else:
            log(f"  감지된 프로젝트 {len(active_projects)}개: {', '.join(active_projects)}")
            for proj in active_projects:
                log(f"  주간 리뷰 실행: {proj}")
                try:
                    weekly_loop(proj)
                    results.append(f"주간 리뷰: {proj} 완료")
                    log(f"  완료: {proj}")
                except Exception as e:
                    results.append(f"주간 리뷰: {proj} 실패 ({e})")
                    log(f"  [오류] {proj} — {e}")

    except Exception as e:
        results.append(f"주간 리뷰 전체 실패: {e}")
        log(f"[오류] 주간 리뷰 모듈 로드 실패: {e}")

    # ── KPI 주간 리포트 ───────────────────────────
    log("KPI 주간 리포트 생성")
    try:
        from core.kpi import get_kpi_summary, get_kpi_status
        kpi_summary = get_kpi_summary()
        kpi_status = get_kpi_status()
        summary_line = kpi_status.get("summary", {})
        results.append(
            f"KPI: 달성 {summary_line.get('achieved', 0)}팀 / "
            f"진행 {summary_line.get('in_progress', 0)}팀 / "
            f"미달 {summary_line.get('behind', 0)}팀"
        )
        log("KPI 리포트 완료")
        # 보고사항들.md에 KPI 현황 추가
        try:
            kpi_entry = f"\n\n## KPI 주간 현황 ({date_str})\n\n{kpi_summary}\n\n---\n"
            existing_report = open(REPORT_PATH, encoding="utf-8").read() if os.path.exists(REPORT_PATH) else ""
            with open(REPORT_PATH, "w", encoding="utf-8") as f:
                f.write(existing_report + kpi_entry)
        except Exception:
            pass
    except Exception as e:
        results.append(f"KPI 리포트: 실패 ({e})")
        log(f"KPI 리포트 실패: {e}")

    # ── 지호 참모 전체 현황 분석 ──────────────────
    log("지호 참모 전체 현황 분석")
    try:
        import subprocess
        watchdog_result = subprocess.run(
            [sys.executable, "watchdog.py"],
            cwd=os.path.dirname(__file__),
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=120
        )
        if watchdog_result.returncode == 0:
            results.append("지호 참모 보고: 완료 (보고사항들.md 저장)")
            log("지호 참모 보고 완료")
        else:
            results.append(f"지호 참모 보고: 실패 ({watchdog_result.stderr[:80]})")
            log("지호 참모 보고 실패")
    except Exception as e:
        results.append(f"지호 참모 보고: 실패 ({e})")
        log(f"지호 참모 보고 실패: {e}")

    # ── 주간 감사 묶음 (CAPABILITIES + 팀 drift + 프롬프트 길이 + 죽은 팀) ─
    for script_name, label in [
        ("capability_audit.py", "CAPABILITIES 감사"),
        ("team_drift_analyzer.py", "team 폴더 drift"),
        ("audit_prompt_length.py", "프롬프트 150줄 감사"),
        ("audit_dead_teams.py", "죽은 팀 감사"),
    ]:
        log(label)
        try:
            r = subprocess.run(
                [sys.executable, script_name],
                cwd=os.path.dirname(__file__),
                capture_output=True, text=True, encoding="utf-8", errors="replace",
                timeout=60
            )
            if r.returncode == 0:
                first_line = r.stdout.strip().splitlines()[0] if r.stdout.strip() else "완료"
                results.append(f"{label}: {first_line}")
                log(f"{label} 완료")
            else:
                results.append(f"{label} 실패: {r.stderr[:80]}")
        except Exception as e:
            results.append(f"{label} 실패: {e}")
            log(f"{label} 실패: {e}")

    # ── 시스템 건강 진단 (Phase 6: 자동 진단) ─────────
    log("시스템 건강 진단 시작")
    try:
        health_issues = []
        base = os.path.dirname(__file__)
        agents_dir = os.path.join(os.path.dirname(base), ".claude", "agents")
        teams_dir = os.path.join(base, "teams")

        # 1. 에이전트 프롬프트 줄 수 체크 (150줄 넘으면 경고)
        bloated = []
        if os.path.isdir(agents_dir):
            for f in os.listdir(agents_dir):
                if f.endswith(".md"):
                    path = os.path.join(agents_dir, f)
                    lines = sum(1 for _ in open(path, encoding="utf-8"))
                    if lines > 150:
                        bloated.append(f"{f} ({lines}줄)")
        if bloated:
            health_issues.append(f"프롬프트 비대: {', '.join(bloated)}")

        # 2. 팀 에이전트 .py 줄 수 체크 (200줄 넘으면 경고 — 지식 다시 삽입된 것)
        fat_agents = []
        if os.path.isdir(teams_dir):
            for root, dirs, files in os.walk(teams_dir):
                for fname in files:
                    if fname.endswith(".py") and fname not in ("__init__.py", "pipeline.py"):
                        path = os.path.join(root, fname)
                        lines = sum(1 for _ in open(path, encoding="utf-8"))
                        if lines > 200:
                            team = os.path.basename(root)
                            fat_agents.append(f"{team}/{fname} ({lines}줄)")
        if fat_agents:
            health_issues.append(f"팀 에이전트 비대: {', '.join(fat_agents[:5])}")

        # 3. 문서 불일치 체크 (모델 config vs OPERATIONS.md)
        try:
            import json
            config_path = os.path.join(base, "config", "model_config.json")
            if os.path.exists(config_path):
                with open(config_path, encoding="utf-8") as f:
                    config = json.load(f)
                ops_path = os.path.join(os.path.dirname(base), "OPERATIONS.md")
                if os.path.exists(ops_path):
                    ops = open(ops_path, encoding="utf-8").read()
                    for role, model in config.get("roles", {}).items():
                        if model not in ops and role not in ("cache", "tracking"):
                            health_issues.append(f"모델 불일치: {role}={model} (OPERATIONS.md에 없음)")
        except Exception:
            pass

        # 4. 보고사항들.md 크기 체크
        if os.path.exists(REPORT_PATH):
            report_lines = sum(1 for _ in open(REPORT_PATH, encoding="utf-8"))
            if report_lines > 3000:
                health_issues.append(f"보고사항들.md 비대: {report_lines}줄 (archive 필요)")

        if health_issues:
            health_report = "시스템 건강: " + " / ".join(health_issues)
            results.append(health_report)
            log(f"건강 진단 완료 — 이슈 {len(health_issues)}개")
        else:
            results.append("시스템 건강: 이상 없음")
            log("건강 진단 완료 — 이상 없음")

    except Exception as e:
        results.append(f"시스템 건강 진단: 실패 ({e})")
        log(f"건강 진단 실패: {e}")

    # ── 주간 요약 보고사항들.md에 저장 ────────────
    log("주간 요약 저장...")
    report = f"\n\n## 주간 자동 실행 — {date_str}\n\n"
    report += "\n".join(f"- {r}" for r in results)
    report += "\n\n---\n"
    try:
        existing = ""
        if os.path.exists(REPORT_PATH):
            with open(REPORT_PATH, encoding="utf-8") as f:
                existing = f.read()
        if "---\n\n## " in existing:
            parts = existing.split("---\n\n## ", 1)
            if len(parts) >= 2:
                new_content = parts[0] + "---\n" + report + "\n## " + parts[1]
            else:
                new_content = existing + report
        else:
            new_content = existing + report
        with open(REPORT_PATH, "w", encoding="utf-8") as f:
            f.write(new_content)
        log("보고 저장 완료")
    except Exception as e:
        log(f"[오류] 보고 저장 실패: {e}")

    log(f"=== 주간 리뷰 완료 ===")


if __name__ == "__main__":
    main()
