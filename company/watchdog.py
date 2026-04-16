"""
참모 워치독 — 지호가 전체 프로젝트 상황 보고 빠진 것 찾아줌.

사용법:
  ./venv/Scripts/python.exe watchdog.py
"""
import sys
import os
import io
from pathlib import Path
from dotenv import load_dotenv

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

ROOT = Path(__file__).parent
LIANCP_ROOT = ROOT.parent
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env")

import anthropic
from core.models import CLAUDE_OPUS


COOS_PROMPT = """너는 지호야. 리안 컴퍼니의 참모(Chief of Staff)야.

리안은 여러 프로젝트를 동시에 돌리는 CEO야. 바빠서 전체 그림을 놓치는 경우가 많아.
네 역할: 전체 현황을 보고 "빠진 것", "연결 고리", "지금 당장 해야 하는 것"을 찾아내는 것.

분석 관점:
1. 인프라 갭: 홈페이지, SNS, 포트폴리오 등 기본 인프라가 빠져 있나?
2. 연결 갭: 프로젝트 간 시너지를 놓치고 있나?
3. 타이밍 갭: 완성됐는데 홍보 안 한 것, 지금 해야 하는데 미루는 것?
4. 리소스 갭: 같은 일을 두 팀이 따로 하고 있나?

출력 형식:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
지호 참모 보고서
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[현황 요약]

🔴 지금 당장 해야 할 것:
1. [항목] — [이유]

🔗 연결하면 시너지:
1. [A]의 [무엇]을 [B]에 활용

💡 리안이 놓치고 있는 것:
[발견]

📋 우선순위 액션 (최대 3개):
1. [무엇을, 왜 지금]
2. [무엇을, 왜 지금]
3. [무엇을, 왜 지금]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
짧고 핵심만."""


def read_file_safe(path: Path, max_chars: int = 1000) -> str:
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()[:max_chars]
    except Exception:
        return ""


def gather_context() -> str:
    """전체 프로젝트 현황 수집."""
    parts = []

    # PROJECTS.md
    projects = read_file_safe(LIANCP_ROOT / "PROJECTS.md")
    if projects:
        parts.append(f"## PROJECTS.md\n{projects}")

    # STATUS.md (최근 부분만)
    status = read_file_safe(LIANCP_ROOT / "STATUS.md", max_chars=800)
    if status:
        parts.append(f"## STATUS.md (최근)\n{status}")

    # 진행중 프로젝트 폴더 스캔
    team_dir = LIANCP_ROOT / "team"
    active_projects = []
    if team_dir.exists():
        for folder in team_dir.iterdir():
            if folder.is_dir() and "[중단]" not in folder.name:
                claude_md = folder / "CLAUDE.md"
                prd_md = folder / "PRD.md"
                project_info = f"### {folder.name}\n"
                if claude_md.exists():
                    content = read_file_safe(claude_md, max_chars=300)
                    project_info += content
                if prd_md.exists():
                    project_info += "\n[PRD.md 있음]"
                active_projects.append(project_info)

    if active_projects:
        parts.append("## 진행중 프로젝트\n" + "\n\n".join(active_projects))

    # 최근 보고사항들.md
    report = read_file_safe(LIANCP_ROOT / "보고사항들.md", max_chars=600)
    if report:
        parts.append(f"## 최근 보고사항\n{report}")

    return "\n\n".join(parts)


def main():
    print("\n" + "="*60)
    print("지호 | 참모 전체 현황 분석")
    print("="*60)
    print("전체 프로젝트 스캔 중...")

    context = gather_context()
    if not context:
        print("분석할 프로젝트 정보가 없어.")
        return

    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    full_response = ""
    with client.messages.stream(
        model=CLAUDE_OPUS,
        max_tokens=800,
        system=COOS_PROMPT,
        messages=[{"role": "user", "content": f"현재 리안 컴퍼니 전체 현황:\n\n{context}"}],
        temperature=0.7,
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
            full_response += text

    print("\n")

    # 보고사항들.md에 자동 기록
    try:
        report_path = LIANCP_ROOT / "보고사항들.md"
        from datetime import datetime
        with open(report_path, "a", encoding="utf-8") as f:
            f.write(f"\n\n---\n## 지호 참모 보고 ({datetime.now().strftime('%Y-%m-%d %H:%M')})\n\n")
            f.write(full_response)
        print(f"\n보고사항들.md에 저장 완료.")
    except Exception as e:
        print(f"\n저장 실패: {e}")


if __name__ == "__main__":
    main()
