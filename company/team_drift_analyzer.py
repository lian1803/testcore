"""
team_drift_analyzer.py — team/ vs company/teams/ 중복/drift 분석

두 폴더 비교:
1. 이름 매칭 (언더스코어/하이픈/공백 정규화)
2. 각 폴더의 최근 수정일, 파일 개수
3. 해당 팀 이름이 실제 import/참조되는지 검색
4. 리포트를 보고사항들.md에 저장

위험 없음 — 읽기 전용. 실제 이동은 별도 스크립트.
"""
import os
import sys
import re
import json
from pathlib import Path
from datetime import datetime

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

ROOT = Path(__file__).parent.parent
TEAM_DIR = ROOT / "team"
TEAMS_DIR = ROOT / "company" / "teams"
REPORT = ROOT / "보고사항들.md"


def normalize(name: str) -> str:
    """이름 정규화 — 언더스코어/하이픈/공백/[태그] 제거"""
    s = re.sub(r'^\[.*?\]\s*', '', name)  # [진행중], [중단] 등 제거
    s = re.sub(r'[\s_\-]+', '', s)
    return s.lower()


def folder_stats(path: Path) -> dict:
    """폴더의 파일 개수, 최근 수정일, 총 크기"""
    if not path.exists():
        return {"exists": False}
    try:
        files = list(path.rglob("*"))
        files = [f for f in files if f.is_file() and "__pycache__" not in f.parts and "venv" not in f.parts]
        if not files:
            return {"exists": True, "file_count": 0, "last_modified": None, "total_kb": 0}
        last_mod = max(f.stat().st_mtime for f in files)
        total_size = sum(f.stat().st_size for f in files)
        return {
            "exists": True,
            "file_count": len(files),
            "last_modified": datetime.fromtimestamp(last_mod).strftime("%Y-%m-%d"),
            "total_kb": round(total_size / 1024, 1),
        }
    except Exception as e:
        return {"exists": True, "error": str(e)}


def search_references(team_name: str) -> dict:
    """이 팀 이름이 어디서 import/참조되는지 탐색"""
    refs = {"import": [], "run_script": [], "mention": 0}
    # run_{팀명}.py 존재 확인
    for candidate in [team_name, team_name.replace("-", "_"), team_name.replace(" ", "_")]:
        run_file = ROOT / "company" / f"run_{candidate}.py"
        if run_file.exists():
            refs["run_script"].append(str(run_file.relative_to(ROOT)))

    # company/ 하위에서 import 문 검색
    import_patterns = [
        rf"from\s+teams\.{re.escape(team_name)}",
        rf"import\s+teams\.{re.escape(team_name)}",
        rf"teams/{re.escape(team_name)}",
    ]
    try:
        for py_file in (ROOT / "company").rglob("*.py"):
            if "venv" in py_file.parts or "__pycache__" in py_file.parts:
                continue
            try:
                text = py_file.read_text(encoding="utf-8", errors="ignore")
                for p in import_patterns:
                    if re.search(p, text):
                        refs["import"].append(str(py_file.relative_to(ROOT)))
                        break
                # 단순 문자열 언급 (덜 강한 신호)
                if team_name in text:
                    refs["mention"] += 1
            except Exception:
                continue
    except Exception:
        pass
    return refs


def analyze():
    if not TEAM_DIR.exists() or not TEAMS_DIR.exists():
        print("team/ 또는 company/teams/ 폴더 없음")
        return

    team_items = {d.name: d for d in TEAM_DIR.iterdir() if d.is_dir()}
    teams_items = {d.name: d for d in TEAMS_DIR.iterdir() if d.is_dir() and not d.name.startswith("__")}

    # 정규화 매칭
    team_norm = {normalize(n): n for n in team_items}
    teams_norm = {normalize(n): n for n in teams_items}
    common_keys = set(team_norm.keys()) & set(teams_norm.keys())

    only_in_team = set(team_norm.keys()) - set(teams_norm.keys())
    only_in_teams = set(teams_norm.keys()) - set(team_norm.keys())

    lines = [
        f"\n---\n## 🗂️ team/ vs company/teams/ 중복 분석 — {datetime.now().strftime('%Y-%m-%d %H:%M')}\n",
        f"**요약**: 중복 {len(common_keys)}개 | team/ 전용 {len(only_in_team)}개 | company/teams/ 전용 {len(only_in_teams)}개\n",
        "## 중복 팀 (양쪽 다 존재)\n",
        "| 팀 | team/ 상태 | company/teams/ 상태 | 실행 스크립트 | import 참조 | 판단 |",
        "|---|---|---|---|---|---|",
    ]

    for key in sorted(common_keys):
        t_name = team_norm[key]
        ts_name = teams_norm[key]
        t_stats = folder_stats(team_items[t_name])
        ts_stats = folder_stats(teams_items[ts_name])
        refs_t = search_references(t_name)
        refs_ts = search_references(ts_name)

        t_desc = f"{t_stats.get('file_count','?')}개, {t_stats.get('last_modified','?')}" if t_stats.get("exists") else "없음"
        ts_desc = f"{ts_stats.get('file_count','?')}개, {ts_stats.get('last_modified','?')}"
        run_scripts = ", ".join(sorted(set(refs_t["run_script"] + refs_ts["run_script"]))) or "-"
        imports = ", ".join(sorted(set(refs_t["import"] + refs_ts["import"]))[:3]) or "-"

        # 판단 로직
        ts_active = len(refs_ts["import"]) > 0 or len(refs_ts["run_script"]) > 0
        t_has_project = t_stats.get("file_count", 0) > 3

        if ts_active and t_has_project:
            judgment = "✅ 둘 다 필요 (설계대로)"
        elif ts_active and not t_has_project:
            judgment = "⚠️ team/ 쪽 거의 비어있음 — 확인"
        elif not ts_active and t_has_project:
            judgment = "⚠️ teams/ 쪽 import 없음 — 확인"
        else:
            judgment = "❌ 둘 다 사용 흔적 적음 — archive 후보"

        lines.append(f"| `{t_name}` \\| `{ts_name}` | {t_desc} | {ts_desc} | {run_scripts[:40]} | {imports[:40]} | {judgment} |")

    lines.append("\n## team/ 전용 (결과물만, 엔진 없음)")
    for key in sorted(only_in_team):
        n = team_norm[key]
        s = folder_stats(team_items[n])
        desc = f"{s.get('file_count','?')}개, 최근 {s.get('last_modified','?')}"
        lines.append(f"- `{n}` — {desc}")

    lines.append("\n## company/teams/ 전용 (엔진만, 결과물 없음)")
    for key in sorted(only_in_teams):
        n = teams_norm[key]
        s = folder_stats(teams_items[n])
        refs = search_references(n)
        desc = f"{s.get('file_count','?')}개, 최근 {s.get('last_modified','?')}"
        active = "활성" if refs["import"] or refs["run_script"] else "⚠️ 참조 없음"
        lines.append(f"- `{n}` — {desc} ({active})")

    lines.append("\n**다음 단계**: ❌/⚠️ 표시된 팀들 → 리안 확인 후 `archive/` 이동 또는 유지 결정\n")

    # 콘솔 출력만 (보고사항들.md 오염 제거)
    print("\n".join(lines))
    print(f"\n[요약] 중복 {len(common_keys)}개 | team/ 전용 {len(only_in_team)}개 | company/teams/ 전용 {len(only_in_teams)}개")


if __name__ == "__main__":
    analyze()
