#!/usr/bin/env python3
"""
리안 컴퍼니 대시보드 데이터 수집 스크립트
daily_auto.py 완료 후 자동 호출됨

출력: company/dashboard_data.json
"""

import json
import re
import sys
import io
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

# Windows 인코딩 설정
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

class DashboardDataCollector:
    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.log_file = self.base_path / "daily_run.log"
        self.report_file = self.base_path.parent / "보고사항들.md"
        self.knowledge_path = self.base_path / "knowledge" / "teams"
        self.output_file = self.base_path / "dashboard_data.json"

    def parse_daily_run_log(self):
        """daily_run.log 파싱"""
        if not self.log_file.exists():
            return {"runs": [], "summary": {}}

        with open(self.log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        runs = []
        current_run = None

        for line in lines:
            # === 시작 라인
            if "자동 실행 시작" in line:
                match = re.search(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]', line)
                if match:
                    if current_run:
                        runs.append(current_run)
                    timestamp = match.group(1)
                    current_run = {
                        "timestamp": timestamp,
                        "date": timestamp.split()[0],
                        "time": timestamp.split()[1],
                        "status": "running",
                        "steps": []
                    }

            # === 완료 라인
            elif "자동 실행 완료" in line:
                if current_run:
                    current_run["status"] = "completed"
                    current_run["completed_at"] = datetime.now().isoformat()
                    runs.append(current_run)
                    current_run = None

            # 콘텐츠 생성 라인
            elif "콘텐츠 생성:" in line:
                match = re.search(r'콘텐츠 생성: \[(.*?)\] (.*?)$', line)
                if match and current_run:
                    status = match.group(1)
                    project = match.group(2)
                    current_run["steps"].append({
                        "type": "content_generation",
                        "status": status,
                        "project": project
                    })

        # 최근 7일 통계
        today = datetime.now().date()
        runs_by_date = defaultdict(int)
        for run in runs:
            if run["status"] == "completed":
                try:
                    run_date = datetime.strptime(run["date"], "%Y-%m-%d").date()
                    if (today - run_date).days <= 7:
                        runs_by_date[run["date"]] += 1
                except:
                    pass

        return {
            "runs": runs[-10:],  # 최근 10회
            "summary": {
                "total_runs": len([r for r in runs if r["status"] == "completed"]),
                "runs_this_week": sum(runs_by_date.values()),
                "runs_today": runs_by_date.get(str(today), 0),
                "last_run": runs[-1]["timestamp"] if runs else None
            }
        }

    def parse_reports(self):
        """보고사항들.md 파싱"""
        if not self.report_file.exists():
            return []

        with open(self.report_file, 'r', encoding='utf-8') as f:
            content = f.read()

        reports = []
        # ## 팀명 — YYYY-MM-DD HH:MM 형태로 파싱
        sections = re.split(r'## ', content)

        for section in sections[1:]:  # 첫 번째는 헤더
            lines = section.split('\n')
            if len(lines) < 1:
                continue

            # 첫 줄에서 팀명과 시간 추출
            header = lines[0]
            match = re.match(r'(.*?)\s*—\s*(\d{4}-\d{2}-\d{2})', header)
            if match:
                team_name = match.group(1).strip()
                date_str = match.group(2)

                # 본문 첫 문장 추출 (요약)
                summary = ""
                for line in lines[1:]:
                    cleaned = line.strip()
                    if cleaned and not cleaned.startswith('-') and not cleaned.startswith('**'):
                        summary = cleaned[:100]
                        break

                reports.append({
                    "team": team_name,
                    "date": date_str,
                    "summary": summary,
                    "order": len(reports)  # 최신순 (파일에서 위부터)
                })

        # 최신 5개만
        return sorted(reports, key=lambda x: x["date"], reverse=True)[:5]

    def collect_team_stats(self):
        """knowledge/teams/ 스캔하여 팀별 통계"""
        teams = {}

        if not self.knowledge_path.exists():
            return teams

        for team_dir in self.knowledge_path.iterdir():
            if not team_dir.is_dir():
                continue

            team_name = team_dir.name

            # results/ 폴더의 파일 수
            results_path = team_dir / "results"
            content_count = 0
            if results_path.exists():
                content_count = len(list(results_path.glob("*.md")))

            # latest_learning 파일 확인
            learning_files = list(team_dir.glob("latest_learning_*.md"))
            last_update = None
            if learning_files:
                last_file = sorted(learning_files)[-1]
                try:
                    timestamp = last_file.stat().st_mtime
                    last_update = datetime.fromtimestamp(timestamp).isoformat()
                except:
                    pass

            teams[team_name] = {
                "content_count": content_count,
                "last_update": last_update,
                "status": "active" if content_count > 0 else "idle"
            }

        return teams

    def estimate_api_costs(self):
        """API 호출 비용 추정 (일반적인 가격 기준)"""
        # 실제로는 usage.json이나 로그에서 수집해야 함
        # 현재는 대시보드 구조만 제공
        return {
            "models": {
                "claude_opus": {"calls": 0, "estimate_usd": 0.0},
                "claude_sonnet": {"calls": 0, "estimate_usd": 0.0},
                "claude_haiku": {"calls": 0, "estimate_usd": 0.0},
                "gpt_4o": {"calls": 0, "estimate_usd": 0.0},
                "gemini": {"calls": 0, "estimate_usd": 0.0},
                "perplexity": {"calls": 0, "estimate_usd": 0.0}
            },
            "total_estimate_usd": 0.0,
            "last_updated": datetime.now().isoformat()
        }

    def get_publish_queue(self):
        """publish_queue.json 확인"""
        queue_file = self.base_path / "publish_queue.json"

        if not queue_file.exists():
            return {"items": [], "count": 0}

        try:
            with open(queue_file, 'r', encoding='utf-8') as f:
                queue = json.load(f)
            return {
                "items": queue.get("items", [])[:10],  # 최근 10개
                "count": len(queue.get("items", []))
            }
        except:
            return {"items": [], "count": 0}

    def collect_all(self):
        """모든 데이터 수집"""
        now = datetime.now()

        data = {
            "timestamp": now.isoformat(),
            "last_updated": now.strftime("%Y-%m-%d %H:%M:%S"),
            "system_status": "healthy",
            "daily_runs": self.parse_daily_run_log(),
            "recent_reports": self.parse_reports(),
            "team_stats": self.collect_team_stats(),
            "publish_queue": self.get_publish_queue(),
            "api_costs": self.estimate_api_costs()
        }

        return data

    def save(self):
        """JSON으로 저장"""
        data = self.collect_all()

        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return self.output_file

def main():
    collector = DashboardDataCollector()
    output = collector.save()
    print(f"[OK] Dashboard data saved: {output}")

if __name__ == "__main__":
    main()
