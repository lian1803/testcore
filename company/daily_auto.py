"""
daily_auto.py — 리안 컴퍼니 매일 자동 실행 스크립트

Windows 작업 스케줄러에 등록하면 매일 아침 자동 실행.
리안이 직접 돌릴 필요 없음.
"""
import os
import sys
import io
from datetime import datetime

# 인코딩 설정
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(__file__))
from dotenv import load_dotenv
load_dotenv()

# 실패 시 디스코드 자동 알림
from core.notifier import install_crash_notifier
install_crash_notifier("daily_auto")

LOG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "보고사항들.md")
# 실행 로그 — 스케줄러가 실제로 돌았는지 확인용
RUN_LOG_PATH = os.path.join(os.path.dirname(__file__), "daily_run.log")


def log(msg: str):
    timestamp = datetime.now().strftime("%H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    # 로그 파일에도 기록
    try:
        with open(RUN_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    except Exception:
        pass


def main():
    log(f"=== 리안 컴퍼니 자동 실행 시작 ({datetime.now().strftime('%Y-%m-%d')}) ===")
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    results = []

    # ── 0단계: Git 리뷰 (새 변경사항 감지) ────────────────
    log("0단계: Git 리뷰 (core-shell 변경사항 확인)")
    try:
        from core.git_review import scan_remote, save_review_result
        result = scan_remote()
        save_review_result(result)

        # 새 변경사항 있으면 보고
        total_commits = result.get("summary", {}).get("total_commits", 0)
        if total_commits > 0:
            adopt = result.get("summary", {}).get("adopt", 0)
            adapt = result.get("summary", {}).get("adapt", 0)
            skip = result.get("summary", {}).get("skip", 0)
            results.append(f"Git 리뷰: {total_commits}개 커밋 발견 (도입:{adopt}, 수정필요:{adapt}, 스킵:{skip})")
            log(f"Git 리뷰 완료 — {total_commits}개 커밋")
        else:
            results.append("Git 리뷰: 새 변경사항 없음")
            log("Git 리뷰 완료 — 변경사항 없음")
    except Exception as e:
        results.append(f"Git 리뷰: 실패 ({e})")
        log(f"Git 리뷰 실패: {e}")

    # ── 1단계: 디자인 트렌드 수집 ──────────────
    log("1단계: 디자인 트렌드 수집 (Awwwards)")
    try:
        import asyncio
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        from tools.design_scraper import main as scrape_design
        asyncio.run(scrape_design())
        results.append("디자인 트렌드: 수집 완료")
        log("디자인 트렌드 수집 완료")
    except Exception as e:
        results.append(f"디자인 트렌드: 실패 ({e})")
        log(f"디자인 트렌드 수집 실패: {e}")

    # ── 1.5단계: 디자인스카우팅팀 ──────────────
    log("1.5단계: 디자인스카우팅팀 실행")
    try:
        import subprocess
        scout_result = subprocess.run(
            [sys.executable, "run_디자인스카우팅팀.py"],
            cwd=os.path.dirname(__file__),
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=300
        )
        if scout_result.returncode == 0:
            results.append("디자인스카우팅: 브리핑 생성 완료")
            log("디자인스카우팅팀 완료")
        else:
            results.append(f"디자인스카우팅: 실패 ({scout_result.stderr[:100]})")
            log(f"디자인스카우팅팀 실패")
    except Exception as e:
        results.append(f"디자인스카우팅: 실패 ({e})")
        log(f"디자인스카우팅팀 실패: {e}")

    # ── 2단계: 전 팀 학습 ──────────────────────
    log("2단계: 전 팀 학습")
    try:
        from core.continuous_learning import learn_all_teams
        learn_all_teams()
        results.append("학습: 전 팀 학습 완료")
        log("학습 완료")
    except Exception as e:
        results.append(f"학습: 실패 ({e})")
        log(f"학습 실패: {e}")

    # ── 3단계: 운영 중인 프로젝트 일일 콘텐츠 생성 ────
    log("3단계: 일일 콘텐츠 생성")
    try:
        from core.ops_loop import daily_loop
        # team/ 폴더에서 활성 프로젝트 자동 감지
        team_root = os.path.join(os.path.dirname(os.path.dirname(__file__)), "team")
        active_projects = []
        if os.path.exists(team_root):
            for folder in os.listdir(team_root):
                folder_path = os.path.join(team_root, folder)
                # CLAUDE.md 또는 PRD.md 있으면 활성 프로젝트
                if os.path.isdir(folder_path) and any(
                    os.path.exists(os.path.join(folder_path, f))
                    for f in ["CLAUDE.md", "PRD.md", "런칭준비.md"]
                ):
                    active_projects.append(folder)

        if active_projects:
            for proj in active_projects[:3]:  # 하루 최대 3개 프로젝트
                log(f"  콘텐츠 생성: {proj}")
                try:
                    daily_loop(proj)
                    results.append(f"콘텐츠: {proj} 완료")
                except Exception as e:
                    results.append(f"콘텐츠: {proj} 실패 ({e})")
        else:
            log("  활성 프로젝트 없음 — 스킵")
            results.append("콘텐츠: 활성 프로젝트 없어서 스킵")
    except Exception as e:
        results.append(f"콘텐츠: 실패 ({e})")
        log(f"콘텐츠 생성 실패: {e}")

    # ── 3.3단계: 온라인마케팅팀 일일 리드 발굴 ────────────
    log("3.3단계: 온라인마케팅팀 일일 리드 발굴")
    try:
        import subprocess
        team_root_m = os.path.join(os.path.dirname(os.path.dirname(__file__)), "team")
        active_projects_m = []
        if os.path.exists(team_root_m):
            for folder in os.listdir(team_root_m):
                folder_path = os.path.join(team_root_m, folder)
                if os.path.isdir(folder_path) and any(
                    os.path.exists(os.path.join(folder_path, f))
                    for f in ["CLAUDE.md", "PRD.md"]
                ):
                    active_projects_m.append(folder)

        if active_projects_m:
            proj = active_projects_m[0]  # 하루 1개 프로젝트만
            task = f"{proj} — 오늘의 마케팅 콘텐츠 생성 (블로그 1개 + 인스타 캡션 3개)"
            log(f"  마케팅팀: {proj}")
            r = subprocess.run(
                [sys.executable, "run_온라인마케팅팀.py", task],
                cwd=os.path.dirname(__file__),
                capture_output=True, text=True, encoding="utf-8", errors="replace",
                timeout=600
            )
            results.append(f"마케팅: {proj} " + ("완료" if r.returncode == 0 else f"실패({r.stderr[:80]})"))
            log(f"마케팅팀 {proj} " + ("완료" if r.returncode == 0 else "실패"))
        else:
            log("  활성 프로젝트 없음 — 스킵")
            results.append("마케팅: 활성 프로젝트 없어서 스킵")
    except Exception as e:
        results.append(f"마케팅: 실패 ({e})")
        log(f"마케팅팀 실패: {e}")

    # ── 3.5단계: KPI 동기화 ─────────────────────
    log("3.5단계: KPI 동기화")
    try:
        from core.kpi import sync_kpi_from_logs
        sync_kpi_from_logs()
        results.append("KPI 동기화: 완료")
        log("KPI 동기화 완료")
    except Exception as e:
        results.append(f"KPI 동기화: 실패 ({e})")
        log(f"KPI 동기화 실패: {e}")

    # ── 4단계: 보고 ─────────────────────────────
    log("4단계: 보고 저장")
    report = f"\n\n## 자동 실행 — {date_str}\n\n"
    report += "\n".join(f"- {r}" for r in results)
    report += "\n\n---\n"

    try:
        existing = ""
        if os.path.exists(LOG_PATH):
            with open(LOG_PATH, encoding="utf-8") as f:
                existing = f.read()
        if "---\n\n## " in existing:
            parts = existing.split("---\n\n## ", 1)
            if len(parts) >= 2:
                new_content = parts[0] + "---\n" + report + "\n## " + parts[1]
            else:
                new_content = existing + report
        else:
            new_content = existing + report
        with open(LOG_PATH, "w", encoding="utf-8") as f:
            f.write(new_content)
        log("보고 저장 완료")
    except Exception as e:
        log(f"보고 저장 실패: {e}")

    # ── 4.5단계: 자동 리포트/모니터링 ────────────────
    log("4.5단계: 자동 리포트/모니터링")
    today = datetime.now().weekday()  # 0=월, 6=일

    # 트렌드 리포트 — 매일
    try:
        import subprocess
        r = subprocess.run(
            [sys.executable, "auto_trend_report.py"],
            cwd=os.path.dirname(__file__),
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=300
        )
        results.append("트렌드 리포트: " + ("완료" if r.returncode == 0 else f"실패({r.stderr[:80]})"))
        log("트렌드 리포트 완료" if r.returncode == 0 else "트렌드 리포트 실패")
    except Exception as e:
        results.append(f"트렌드 리포트: 실패 ({e})")

    # 경쟁사 모니터링 — 월요일
    if today == 0:
        try:
            r = subprocess.run(
                [sys.executable, "auto_competitor_watch.py"],
                cwd=os.path.dirname(__file__),
                capture_output=True, text=True, encoding="utf-8", errors="replace",
                timeout=300
            )
            results.append("경쟁사 모니터링: " + ("완료" if r.returncode == 0 else f"실패({r.stderr[:80]})"))
            log("경쟁사 모니터링 완료" if r.returncode == 0 else "경쟁사 모니터링 실패")
        except Exception as e:
            results.append(f"경쟁사 모니터링: 실패 ({e})")

    # 시각 QA 리뷰 — 수요일
    if today == 2:
        try:
            r = subprocess.run(
                [sys.executable, "auto_visual_review.py"],
                cwd=os.path.dirname(__file__),
                capture_output=True, text=True, encoding="utf-8", errors="replace",
                timeout=600
            )
            results.append("시각 QA: " + ("완료" if r.returncode == 0 else f"실패({r.stderr[:80]})"))
            log("시각 QA 완료" if r.returncode == 0 else "시각 QA 실패")
        except Exception as e:
            results.append(f"시각 QA: 실패 ({e})")

    # 자기 개선 리뷰 — 일요일
    if today == 6:
        try:
            r = subprocess.run(
                [sys.executable, "auto_self_review.py"],
                cwd=os.path.dirname(__file__),
                capture_output=True, text=True, encoding="utf-8", errors="replace",
                timeout=600
            )
            results.append("자기 개선: " + ("완료" if r.returncode == 0 else f"실패({r.stderr[:80]})"))
            log("자기 개선 완료" if r.returncode == 0 else "자기 개선 실패")
        except Exception as e:
            results.append(f"자기 개선: 실패 ({e})")

    # ── 5단계: 대시보드 데이터 생성 ─────────────
    log("5단계: 대시보드 데이터 생성")
    try:
        from core.dashboard_data import DashboardDataCollector
        collector = DashboardDataCollector()
        collector.save()
        log("대시보드 데이터 생성 완료")
    except Exception as e:
        log(f"대시보드 데이터 생성 실패: {e}")

    # ── 6단계: 디스코드 알림 (Phase 6: 리안은 디스코드만 확인) ──
    log("6단계: 디스코드 알림")
    try:
        from core.notifier import send
        summary = "\n".join(f"• {r}" for r in results)
        failures = [r for r in results if "실패" in r]
        if failures:
            send(
                f"⚠️ 자동 실행 완료 ({len(failures)}건 실패)",
                f"**{date_str}**\n\n{summary}",
                color=0xF39C12
            )
        else:
            send(
                f"✅ 자동 실행 완료",
                f"**{date_str}**\n\n{summary}",
                color=0x2ECC71
            )
        log("디스코드 알림 전송 완료")
    except Exception as e:
        log(f"디스코드 알림 실패: {e}")

    log(f"=== 자동 실행 완료 ===")


if __name__ == "__main__":
    main()
