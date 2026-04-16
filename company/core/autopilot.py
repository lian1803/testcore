"""
autopilot.py — 회사의 두뇌

매일 자동 실행되는 메인 컨트롤러.
1. 자산 스캔 → 2. 오늘 할 일 결정 → 3. 에스컬레이션 체크 → 4. 실행 → 5. 기록

사용법:
    cd company
    ./venv/Scripts/python.exe -m core.autopilot daily       # 데일리
    ./venv/Scripts/python.exe -m core.autopilot weekly      # 위클리
    ./venv/Scripts/python.exe -m core.autopilot status      # 현재 상태만
    ./venv/Scripts/python.exe -m core.autopilot daily --dry  # 계획만 (실행 안 함)
"""
import os
import sys
import io
import subprocess
import json
from datetime import datetime
from dotenv import load_dotenv

# Windows UTF-8
if sys.platform == "win32":
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass

load_dotenv()

from core.asset_scanner import scan_all, format_summary
from core.planner import plan_daily, plan_weekly, ROUTES
from core.escalation import should_escalate, escalate, get_unanswered, archive_answered
from core.daily_log import log_execution, get_recent, get_stats, get_approval_count
from core.notifier import send as discord_send
from core.self_improve import post_run_review
from knowledge.manager import write_report

_ROOT = os.path.dirname(os.path.dirname(__file__))  # company/
_PROJECT_ROOT = os.path.dirname(_ROOT)  # LIANCP 루트
VENV_PYTHON = os.path.join(_ROOT, "venv", "Scripts", "python.exe")

# 일일 비용 상한 (안전장치)
DAILY_COST_LIMIT = 10  # 달러


class Autopilot:
    """회사 자율 실행 루프."""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.assets = None
        self.today = datetime.now().strftime("%Y-%m-%d")

    def run_daily(self) -> dict:
        """매일 아침 실행."""
        print(f"\n{'='*60}")
        print(f"  AUTOPILOT — {self.today}")
        print(f"{'='*60}")

        # 1. 자산 스캔
        print("\n[1/5] 자산 스캔...")
        self.assets = scan_all()
        print(format_summary(self.assets))

        # 2. 미답변 질문 체크
        unanswered = get_unanswered()
        if unanswered:
            print(f"\n  미답변 질문 {len(unanswered)}개 — 리안 답변 대기 중")
            for q in unanswered:
                print(f"    - {q.get('question', '?')}")
            discord_send(
                "Autopilot 대기 중",
                f"미답변 질문 {len(unanswered)}개. 답변 후 다시 실행해주세요.",
                color=0xFFD700,
            )
            return {"status": "waiting", "unanswered": unanswered, "executed": [], "skipped": [], "escalated": []}

        # 답변된 질문 아카이브
        archive_answered()

        # 3. 오늘 할 일 결정
        print("\n[2/5] 오늘 할 일 계획 중...")
        tasks = plan_daily(self.assets)
        print(f"  계획된 태스크: {len(tasks)}개")
        for t in tasks:
            print(f"    [{t.get('priority', '?')}] {t.get('description', '?')} ({t.get('type', '?')})")

        if self.dry_run:
            print("\n  [DRY RUN] 계획만 출력하고 종료.")
            return {"status": "dry_run", "planned": tasks, "executed": [], "skipped": [], "escalated": []}

        # 4. 실행
        print("\n[3/5] 태스크 실행...")
        executed = []
        skipped = []
        escalated = []
        cost_total = 0

        for task in tasks:
            task_id = task.get("id", "unknown")
            task_type = task.get("type", "unknown")
            description = task.get("description", "")

            # 비용 체크
            cost_map = {"low": 0.5, "medium": 2, "high": 5}
            est_cost = cost_map.get(task.get("estimated_cost", "low"), 1)
            if cost_total + est_cost > DAILY_COST_LIMIT:
                print(f"  [SKIP] 비용 상한 도달 — {description}")
                skipped.append({"task": task, "reason": "cost_limit"})
                continue

            # 에스컬레이션 체크
            project = task.get("target_project", "") or ""
            approval_count = get_approval_count(project, task.get("category", "")) if project else 0
            needs_esc, reason = should_escalate(task, approval_count)

            if needs_esc:
                print(f"  [ESCALATE] {description} — {reason}")
                escalate(
                    question=f"이 태스크를 실행할까? {description}",
                    category=task.get("category", "unknown"),
                    options=["진행", "스킵", "수정 후 진행"],
                )
                escalated.append({"task": task, "reason": reason})
                continue

            # 실행
            print(f"\n  --- 실행: {description} ---")
            result = self._execute_task(task)
            cost_total += est_cost

            if result["success"]:
                executed.append(result)
                print(f"  [OK] {description}")
            else:
                executed.append(result)
                print(f"  [FAIL] {description}: {result.get('error', '?')}")

            # 로그 기록
            log_execution(
                task_id=task_id,
                task_type=task_type,
                project=project,
                result=result.get("result_summary", ""),
                success=result["success"],
                cost_estimate=task.get("estimated_cost", "low"),
            )

        # 5. 결과 보고
        print("\n[4/5] 결과 보고...")
        summary = self._format_daily_summary(executed, skipped, escalated)
        write_report("Autopilot", "자율 실행 루프", summary)
        discord_send("Autopilot 완료", summary[:1500], color=0x27AE60)

        # 자기 점검
        print("\n[5/5] 자기 점검...")
        try:
            post_run_review("Autopilot Daily", {"tasks": len(tasks), "executed": len(executed)}, summary)
        except Exception:
            pass

        print(f"\n{'='*60}")
        print(f"  완료: 실행 {len(executed)} / 스킵 {len(skipped)} / 에스컬레이션 {len(escalated)}")
        print(f"{'='*60}")

        return {
            "status": "done",
            "executed": executed,
            "skipped": skipped,
            "escalated": escalated,
        }

    def run_weekly(self) -> dict:
        """주간 리뷰."""
        print(f"\n{'='*60}")
        print(f"  AUTOPILOT WEEKLY REVIEW — {self.today}")
        print(f"{'='*60}")

        self.assets = scan_all()
        stats = get_stats(7)
        recent = get_recent(7)

        print(f"\n  이번 주 실행: {stats['total']}회")
        print(f"  성공률: {stats['success_rate']*100:.0f}%")

        # ops_loop.weekly_loop 호출
        from core.ops_loop import weekly_loop

        # 가장 활발한 프로젝트 찾기
        by_project = stats.get("by_project", {})
        if by_project:
            top_project = max(by_project, key=by_project.get)
            print(f"\n  가장 활발한 프로젝트: {top_project}")

            perf_data = json.dumps(stats, ensure_ascii=False)
            try:
                review_result = weekly_loop(top_project, perf_data)
            except Exception as e:
                review_result = f"주간 리뷰 실행 실패: {e}"
        else:
            review_result = "이번 주 실행 기록 없음. 첫 프로젝트를 시작해야 합니다."

        # 에이전트 자기 개선 제안
        try:
            from core.agent_improver import propose_improvements
            propose_improvements()
        except Exception as e:
            print(f"  ⚠️  에이전트 개선 제안 실패: {e}")

        # 피벗 판단
        pivot_recommendation = self._check_pivot(stats, recent)
        if pivot_recommendation:
            escalate(
                question=pivot_recommendation,
                category="stop_project",
                options=["계속", "피벗", "중단"],
            )

        return {
            "stats": stats,
            "review": review_result,
            "pivot": pivot_recommendation,
        }

    def run_status(self) -> dict:
        """현재 상태만 출력."""
        self.assets = scan_all()
        print(format_summary(self.assets))

        stats = get_stats(7)
        print(f"\n=== 최근 7일 통계 ===")
        print(f"  실행: {stats['total']}회 | 성공률: {stats['success_rate']*100:.0f}%")

        unanswered = get_unanswered()
        if unanswered:
            print(f"\n  미답변 질문: {len(unanswered)}개")

        return {"assets": self.assets, "stats": stats}

    # ── 내부 메서드 ──

    def _execute_task(self, task: dict) -> dict:
        """단일 태스크 실행. 기존 시스템 라우팅."""
        task_type = task.get("type", "")
        project = task.get("target_project", "")
        team = task.get("target_team", "")

        try:
            if task_type == "content" and project:
                from core.ops_loop import daily_loop
                result = daily_loop(project)
                return {"task": task, "success": True, "result_summary": result[:300] if result else "생성 완료"}

            elif task_type == "outreach":
                # team 없으면 온라인영업팀 기본값
                target = team or "온라인영업팀"
                run_task = task.get("description", "영업 DM 생성")
                return self._run_team_script_with_task(target, run_task)

            elif task_type == "research":
                from core.research_loop import research_before_task
                result = research_before_task(
                    role="트렌드 리서처",
                    task=task.get("description", "최신 트렌드"),
                )
                return {"task": task, "success": bool(result), "result_summary": result[:300] if result else "리서치 결과 없음"}

            elif task_type == "launch" and project:
                from core.launch_prep import run_launch_prep
                import anthropic as _anthropic
                _client = _anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
                result = run_launch_prep({"project": project, "idea": project}, _client)
                return {"task": task, "success": True, "result_summary": str(result)[:300]}

            elif task_type == "team_run" and team:
                return self._run_team_script(team)

            elif task_type == "review":
                # 주간 리뷰는 weekly에서 처리
                return {"task": task, "success": True, "result_summary": "리뷰 스킵 (weekly에서 처리)"}

            else:
                return {"task": task, "success": False, "error": f"알 수 없는 타입: {task_type}", "result_summary": ""}

        except Exception as e:
            return {"task": task, "success": False, "error": str(e), "result_summary": f"실행 실패: {e}"}

    def _run_team_script_with_task(self, team_name: str, task_desc: str) -> dict:
        """팀 스크립트를 태스크 설명과 함께 실행."""
        SCRIPT_MAP = {
            "offline_marketing": "offline_sales.py",
        }
        script_name = SCRIPT_MAP.get(team_name, f"run_{team_name}.py")
        script = os.path.join(_ROOT, script_name)
        if not os.path.exists(script):
            return {"success": False, "error": f"스크립트 없음: {script_name}", "result_summary": ""}
        try:
            result = subprocess.run(
                [VENV_PYTHON, script, task_desc],
                capture_output=True, text=True, timeout=300, cwd=_ROOT,
                env={**os.environ, "PYTHONIOENCODING": "utf-8"},
            )
            output = result.stdout[-500:] if result.stdout else ""
            success = result.returncode == 0
            return {"success": success, "result_summary": output, "error": result.stderr[-200:] if not success else ""}
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "타임아웃 (5분)", "result_summary": ""}
        except Exception as e:
            return {"success": False, "error": str(e), "result_summary": ""}

    def _run_team_script(self, team_name: str) -> dict:
        """run_{팀명}.py 실행."""
        # 팀명 → 스크립트명 매핑 (예외 처리)
        SCRIPT_MAP = {
            "offline_marketing": "offline_sales.py",
        }
        script_name = SCRIPT_MAP.get(team_name, f"run_{team_name}.py")
        script = os.path.join(_ROOT, script_name)
        if not os.path.exists(script):
            return {"success": False, "error": f"스크립트 없음: run_{team_name}.py", "result_summary": ""}

        try:
            result = subprocess.run(
                [VENV_PYTHON, script],
                capture_output=True,
                text=True,
                timeout=300,
                cwd=_ROOT,
                env={**os.environ, "PYTHONIOENCODING": "utf-8"},
            )
            output = result.stdout[-500:] if result.stdout else ""
            success = result.returncode == 0
            return {"success": success, "result_summary": output, "error": result.stderr[-200:] if not success else ""}
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "타임아웃 (5분)", "result_summary": ""}
        except Exception as e:
            return {"success": False, "error": str(e), "result_summary": ""}

    def _check_pivot(self, stats: dict, recent: list[dict]) -> str | None:
        """피벗이 필요한지 판단."""
        if stats["total"] < 5:
            return None  # 데이터 부족

        # 성공률 30% 미만이면 피벗 제안
        if stats["success_rate"] < 0.3:
            return f"최근 7일 성공률 {stats['success_rate']*100:.0f}%. 현재 방향에 문제가 있을 수 있습니다. 피벗할까요?"

        # 특정 프로젝트가 계속 실패
        project_failures = {}
        for r in recent:
            if not r.get("success"):
                p = r.get("project", "unknown")
                project_failures[p] = project_failures.get(p, 0) + 1

        for p, count in project_failures.items():
            if count >= 3:
                return f"프로젝트 '{p}'이 7일간 {count}회 실패. 세분화하거나 방향을 바꿀까요?"

        return None

    def _format_daily_summary(self, executed: list, skipped: list, escalated: list) -> str:
        """일일 결과 요약."""
        lines = [f"## Autopilot 일일 보고 — {self.today}\n"]

        if executed:
            lines.append(f"### 실행 완료 ({len(executed)}건)")
            for r in executed:
                task = r.get("task", {})
                status = "O" if r.get("success") else "X"
                lines.append(f"- [{status}] {task.get('description', '?')}")

        if skipped:
            lines.append(f"\n### 스킵 ({len(skipped)}건)")
            for s in skipped:
                lines.append(f"- {s['task'].get('description', '?')} (사유: {s.get('reason', '?')})")

        if escalated:
            lines.append(f"\n### 리안 승인 대기 ({len(escalated)}건)")
            for e in escalated:
                lines.append(f"- {e['task'].get('description', '?')} (사유: {e.get('reason', '?')})")

        return "\n".join(lines)


# ── CLI ──

def main():
    if len(sys.argv) < 2:
        print("사용법:")
        print("  python -m core.autopilot daily        # 매일 실행")
        print("  python -m core.autopilot daily --dry   # 계획만 (실행 안 함)")
        print("  python -m core.autopilot weekly        # 주간 리뷰")
        print("  python -m core.autopilot status        # 현재 상태")
        sys.exit(1)

    mode = sys.argv[1]
    dry = "--dry" in sys.argv

    pilot = Autopilot(dry_run=dry)

    if mode == "daily":
        pilot.run_daily()
    elif mode == "weekly":
        pilot.run_weekly()
    elif mode == "status":
        pilot.run_status()
    else:
        print(f"알 수 없는 모드: {mode}")
        sys.exit(1)


if __name__ == "__main__":
    main()
