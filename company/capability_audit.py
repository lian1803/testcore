"""
capability_audit.py — .claude/CAPABILITIES.md drift 감지

주간 실행 (weekly_runner.py 연결):
- .claude/skills/, agents/, commands/, rules/ 스캔
- company/tools/, utils/ 스캔
- .mcp.json 파싱
- CAPABILITIES.md에 없는 것 발견 시 보고사항들.md에 경고
"""
import os
import re
import sys
import json
from pathlib import Path
from datetime import datetime

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

ROOT = Path(__file__).parent.parent
CAPS = ROOT / ".claude" / "CAPABILITIES.md"
REPORT = ROOT / "보고사항들.md"


def scan_dir(path: Path, suffix: str = ".md") -> set[str]:
    if not path.exists():
        return set()
    names = set()
    for item in path.iterdir():
        if item.is_file() and item.suffix == suffix:
            names.add(item.stem)
        elif item.is_dir() and not item.name.startswith("__"):
            names.add(item.name)
    return names


def scan_py(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return {f.stem for f in path.glob("*.py") if not f.name.startswith("__")}


def parse_mcp() -> set[str]:
    mcp_file = ROOT / ".mcp.json"
    if not mcp_file.exists():
        return set()
    try:
        data = json.loads(mcp_file.read_text(encoding="utf-8"))
        return set(data.get("mcpServers", {}).keys())
    except Exception:
        return set()


def extract_from_capabilities() -> dict[str, set[str]]:
    """CAPABILITIES.md에 나열된 것 추출"""
    if not CAPS.exists():
        return {}
    text = CAPS.read_text(encoding="utf-8")
    found = {"skills": set(), "agents": set(), "commands": set(), "rules": set(), "mcp": set(), "tools": set()}

    # 백틱으로 감싼 항목 전부 추출
    for match in re.finditer(r'`([a-zA-Z0-9_\-]+(?:\.py|\.md)?)`', text):
        name = match.group(1).replace(".md", "").replace(".py", "")
        for key in found:
            found[key].add(name)
    return found


def audit():
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    actual = {
        "skills": scan_dir(ROOT / ".claude" / "skills"),
        "agents": scan_dir(ROOT / ".claude" / "agents"),
        "commands": scan_dir(ROOT / ".claude" / "commands"),
        "rules": scan_dir(ROOT / ".claude" / "rules"),
        "tools": scan_py(ROOT / "company" / "tools") | scan_py(ROOT / "company" / "utils"),
        "mcp": parse_mcp(),
    }

    registered = extract_from_capabilities()

    missing_from_caps = {}
    for key, actual_set in actual.items():
        reg = registered.get(key, set()) if registered else set()
        # 모든 백틱 항목에서 찾기
        all_registered = set()
        for s in registered.values():
            all_registered |= s
        missing = actual_set - all_registered
        if missing:
            missing_from_caps[key] = missing

    if not missing_from_caps:
        print(f"[{now}] CAPABILITIES.md 최신 상태 — 드리프트 없음")
        return

    # 콘솔 출력만 (보고사항들.md 오염 제거 — audit_hub이 JSON 로그로 관리)
    print(f"[{now}] 드리프트 발견:")
    for key, items in missing_from_caps.items():
        print(f"  {key}: {sorted(items)}")
    print("→ CAPABILITIES.md에 추가 필요.")


if __name__ == "__main__":
    audit()
