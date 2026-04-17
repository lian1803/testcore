"""
audit_dead_teams.py — company/teams/ 각 팀 활성 여부 감사

활성 기준:
1. run_{팀명}.py 존재 (company/ 루트)
2. 다른 .py 파일에서 import 됨
3. daily_auto.py나 weekly_runner.py에서 참조됨

모두 해당 안되면 '죽은 팀' 후보.
"""
import sys
import re
from pathlib import Path

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = Path(__file__).parent.parent
TEAMS = ROOT / "company" / "teams"
COMPANY = ROOT / "company"
EXCLUDE = {"venv", "__pycache__", ".git", "archive"}


def check_team(name: str) -> dict:
    result = {"name": name, "run_script": False, "imports": [], "mentions": 0}

    # 1. run_{name}.py 확인
    for variant in [name, name.replace("-", "_")]:
        if (COMPANY / f"run_{variant}.py").exists():
            result["run_script"] = True
            break

    # 2-3. import 및 언급 검색
    patterns = [
        rf"from\s+teams\.{re.escape(name)}",
        rf"import\s+teams\.{re.escape(name)}",
        rf"teams/{re.escape(name)}",
        rf'"{re.escape(name)}"',
        rf"'{re.escape(name)}'",
    ]
    for py in COMPANY.rglob("*.py"):
        if any(p in py.parts for p in EXCLUDE):
            continue
        if py.parent.name == name:
            continue  # 팀 자기 자신 파일 제외
        try:
            text = py.read_text(encoding="utf-8", errors="ignore")
            for p in patterns[:3]:
                if re.search(p, text):
                    result["imports"].append(str(py.relative_to(ROOT)))
                    break
            if name in text:
                result["mentions"] += 1
        except Exception:
            continue

    result["imports"] = sorted(set(result["imports"]))
    return result


def main():
    if not TEAMS.exists():
        print("company/teams/ 없음")
        return

    teams = [d.name for d in TEAMS.iterdir() if d.is_dir() and not d.name.startswith("__")]
    dead = []
    weak = []
    active = []

    print(f"=== company/teams/ 활성 감사 ({len(teams)}개) ===\n")

    for t in sorted(teams):
        r = check_team(t)
        if r["run_script"] or r["imports"]:
            active.append(r)
        elif r["mentions"] > 0:
            weak.append(r)
        else:
            dead.append(r)

    print(f"[활성 {len(active)}개] run_script 또는 import 있음:")
    for r in active:
        tags = []
        if r["run_script"]:
            tags.append("run")
        if r["imports"]:
            tags.append(f"import {len(r['imports'])}")
        print(f"  ✅ {r['name']} ({', '.join(tags)})")

    if weak:
        print(f"\n[약함 {len(weak)}개] 단순 언급만 있음:")
        for r in weak:
            print(f"  ⚠️  {r['name']} (mentions: {r['mentions']})")

    if dead:
        print(f"\n[죽은 팀 후보 {len(dead)}개] 어디서도 참조 안 됨:")
        for r in dead:
            print(f"  ❌ {r['name']}")
    else:
        print(f"\n[죽은 팀] 없음")


if __name__ == "__main__":
    main()
