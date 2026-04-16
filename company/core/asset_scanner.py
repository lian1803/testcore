"""
asset_scanner.py — 회사 자산 인식기

"지금 우리가 뭘 가지고 있고, 뭘 할 수 있는지" 스캔.
autopilot이 매일 아침 제일 먼저 호출.
"""
import os
import json
from dotenv import load_dotenv

load_dotenv()

_ROOT = os.path.dirname(os.path.dirname(__file__))  # company/
_PROJECT_ROOT = os.path.dirname(_ROOT)  # core/ (LIANCP 루트)


def scan_all() -> dict:
    """전체 자산 스캔."""
    return {
        "apis": scan_apis(),
        "teams": scan_teams(),
        "projects": scan_projects(),
        "channels": scan_channels(),
        "knowledge_count": _count_knowledge(),
        "pending_questions": scan_pending_questions(),
    }


def scan_apis() -> dict:
    """API 키 존재 여부 확인 (값은 확인 안 함, 존재만)."""
    keys = {
        "anthropic": "ANTHROPIC_API_KEY",
        "openai": "OPENAI_API_KEY",
        "google": "GOOGLE_API_KEY",
        "perplexity": "PERPLEXITY_API_KEY",
        "gmail": "GMAIL_ADDRESS",
        "discord": "DISCORD_WEBHOOK_URL",
        "meta_instagram": "META_ACCESS_TOKEN",
        "cloudflare": "CLOUDFLARE_API_TOKEN",
        "github": "GITHUB_PERSONAL_ACCESS_TOKEN",
        "supabase": "SUPABASE_URL",
    }
    result = {}
    for name, env_key in keys.items():
        val = os.getenv(env_key, "")
        # "여기에_" 로 시작하면 미설정
        result[name] = bool(val) and not val.startswith("여기에_")
    return result


def scan_teams() -> list[dict]:
    """company/teams/ 스캔. 각 팀의 pipeline.py 존재 여부."""
    teams_dir = os.path.join(_ROOT, "teams")
    if not os.path.exists(teams_dir):
        return []

    teams = []
    for name in os.listdir(teams_dir):
        if name.startswith("__") or name.startswith("."):
            continue
        team_path = os.path.join(teams_dir, name)
        if not os.path.isdir(team_path):
            continue
        has_pipeline = os.path.exists(os.path.join(team_path, "pipeline.py"))
        # run_{팀명}.py 존재 확인
        run_script = os.path.join(_ROOT, f"run_{name}.py")
        has_run_script = os.path.exists(run_script)
        teams.append({
            "name": name,
            "path": f"teams/{name}/",
            "has_pipeline": has_pipeline,
            "has_run_script": has_run_script,
        })
    return teams


def scan_projects() -> list[dict]:
    """team/ 폴더 스캔. 각 프로젝트의 상태 판단."""
    team_root = os.path.join(_PROJECT_ROOT, "team")
    if not os.path.exists(team_root):
        return []

    projects = []
    for name in os.listdir(team_root):
        proj_path = os.path.join(team_root, name)
        if not os.path.isdir(proj_path):
            continue

        has_claude = os.path.exists(os.path.join(proj_path, "CLAUDE.md"))
        has_prd = os.path.exists(os.path.join(proj_path, "PRD.md"))
        has_launch = os.path.exists(os.path.join(proj_path, "런칭준비.md"))

        if has_launch:
            status = "launched"
        elif has_prd:
            status = "ready"
        elif has_claude:
            status = "planning"
        else:
            status = "empty"

        projects.append({
            "name": name,
            "path": f"team/{name}/",
            "status": status,
        })
    return projects


def scan_channels() -> dict:
    """사용 가능한 채널 확인."""
    apis = scan_apis()
    return {
        "email": apis.get("gmail", False),
        "discord": apis.get("discord", False),
        "instagram": apis.get("meta_instagram", False),
        "cloudflare_deploy": apis.get("cloudflare", False),
        "playwright_browser": True,  # MCP로 연결돼 있음
    }


def scan_pending_questions() -> list[dict]:
    """.pending_questions.json 미답변 항목."""
    path = os.path.join(_ROOT, ".pending_questions.json")
    if not os.path.exists(path):
        return []
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return [q for q in data if not q.get("answered", False)]
        return []
    except Exception:
        return []


def _count_knowledge() -> int:
    """knowledge/base/ 파일 수."""
    base_dir = os.path.join(_ROOT, "knowledge", "base")
    if not os.path.exists(base_dir):
        return 0
    return len([f for f in os.listdir(base_dir) if os.path.isfile(os.path.join(base_dir, f))])


def format_summary(assets: dict) -> str:
    """자산 요약을 읽기 좋은 텍스트로."""
    lines = ["=== 회사 자산 현황 ===\n"]

    # API
    lines.append("## API 연결 상태")
    for name, connected in assets.get("apis", {}).items():
        status = "O" if connected else "X"
        lines.append(f"  [{status}] {name}")

    # 팀
    teams = assets.get("teams", [])
    lines.append(f"\n## 팀 ({len(teams)}개)")
    for t in teams:
        pipeline = "pipeline O" if t["has_pipeline"] else "pipeline X"
        lines.append(f"  - {t['name']} ({pipeline})")

    # 프로젝트
    projects = assets.get("projects", [])
    lines.append(f"\n## 프로젝트 ({len(projects)}개)")
    for p in projects:
        lines.append(f"  - {p['name']} [{p['status']}]")

    # 채널
    lines.append(f"\n## 채널")
    for ch, ok in assets.get("channels", {}).items():
        status = "O" if ok else "X"
        lines.append(f"  [{status}] {ch}")

    # 지식
    lines.append(f"\n## 지식: {assets.get('knowledge_count', 0)}개 문서")

    # 대기 질문
    pending = assets.get("pending_questions", [])
    if pending:
        lines.append(f"\n## 미답변 질문: {len(pending)}개")
        for q in pending[:3]:
            lines.append(f"  - {q.get('question', '?')}")

    return "\n".join(lines)
