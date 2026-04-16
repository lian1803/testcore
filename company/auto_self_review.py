"""
지호 (COO) — 주간 시스템 자기 개선 리뷰

매주 에이전트 아웃풋을 분석해서 시스템 약점을 스스로 발견하고 보고.
실행: company/venv/Scripts/python.exe company/auto_self_review.py
"""
import os
import sys
import re
from datetime import datetime, timedelta
from dotenv import load_dotenv

# company/ 기준 경로
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)

load_dotenv(os.path.join(THIS_DIR, ".env"))

# core 모듈 사용을 위해 company/ 경로 추가
sys.path.insert(0, THIS_DIR)

import anthropic
from core.models import CLAUDE_SONNET
from knowledge.manager import write_report

KNOWLEDGE_TEAMS_DIR = os.path.join(THIS_DIR, "knowledge", "teams")
REPORT_FILE = os.path.join(ROOT_DIR, "보고사항들.md")

REVIEW_WINDOW_DAYS = 7


def _safe(text: str) -> str:
    return re.sub(r'[\ud800-\udfff]', '', text)


def _collect_recent_team_outputs() -> str:
    """knowledge/teams/ 아래 최근 7일 파일들 읽어서 합치기."""
    cutoff = datetime.now() - timedelta(days=REVIEW_WINDOW_DAYS)
    collected = []

    if not os.path.exists(KNOWLEDGE_TEAMS_DIR):
        return "(knowledge/teams/ 폴더 없음 — 아직 팀 결과물이 없습니다)"

    for team_name in os.listdir(KNOWLEDGE_TEAMS_DIR):
        team_path = os.path.join(KNOWLEDGE_TEAMS_DIR, team_name)
        if not os.path.isdir(team_path):
            continue

        for subdir in ("results", "feedback"):
            subpath = os.path.join(team_path, subdir)
            if not os.path.exists(subpath):
                continue

            for fname in os.listdir(subpath):
                fpath = os.path.join(subpath, fname)
                try:
                    mtime = datetime.fromtimestamp(os.path.getmtime(fpath))
                    if mtime < cutoff:
                        continue
                    with open(fpath, encoding="utf-8") as f:
                        content = f.read()[:1500]
                    label = f"[{team_name}/{subdir}/{fname}] (수정: {mtime.strftime('%Y-%m-%d')})"
                    collected.append(f"{label}\n{content}")
                except Exception:
                    continue

    if not collected:
        return f"(최근 {REVIEW_WINDOW_DAYS}일 내 팀 결과물 없음)"

    return "\n\n" + "="*50 + "\n\n".join(collected)


def _collect_recent_reports() -> str:
    """보고사항들.md 최근 내용 읽기 (최대 4000자)."""
    if not os.path.exists(REPORT_FILE):
        return "(보고사항들.md 없음)"
    with open(REPORT_FILE, encoding="utf-8") as f:
        content = f.read()
    # 최신 내용이 위에 있으니 앞부분만 가져옴
    return content[:4000]


REVIEW_SYSTEM_PROMPT = """너는 지호야. 리안 컴퍼니의 COO (최고운영책임자).

리안은 비개발자 CEO야. 에이전트들이 일주일 동안 처리한 결과물을 네가 리뷰해서
시스템의 약점과 개선점을 발견하는 게 네 역할이야.

분석할 때 다음 세 가지를 반드시 포함해:
1. 이번 주 에이전트 아웃풋에서 아쉬운 점
2. 반복되는 패턴이나 개선할 수 있는 플로우
3. 리안이 직접 개입한 횟수가 많았던 부분 (자동화가 덜 된 부분)

말투: 간결하고 실무적으로. 리안이 바로 행동할 수 있는 수준으로.
형식: 마크다운. 섹션별로 깔끔하게.
길이: 너무 길면 안 읽어. 핵심만 300~500자 이내."""


def run_review(client: anthropic.Anthropic) -> str:
    """지호 주간 리뷰 실행. 리뷰 텍스트 반환."""
    print("\n" + "="*60)
    print("지호 | COO 주간 시스템 리뷰")
    print("="*60)

    team_outputs = _collect_recent_team_outputs()
    recent_reports = _collect_recent_reports()

    today = datetime.now().strftime("%Y-%m-%d")
    week_ago = (datetime.now() - timedelta(days=REVIEW_WINDOW_DAYS)).strftime("%Y-%m-%d")

    user_msg = f"""리뷰 기간: {week_ago} ~ {today}

━━━ 최근 팀 결과물 ━━━
{team_outputs}

━━━ 보고사항들.md 최근 내용 ━━━
{recent_reports}

위 내용을 바탕으로 주간 시스템 리뷰를 작성해줘.
세 가지 질문에 답해:
1. 이번 주 에이전트 아웃풋에서 아쉬운 점은?
2. 반복되는 패턴이나 개선할 수 있는 플로우가 있나?
3. 리안이 직접 개입한 횟수가 많았던 부분은?"""

    full_response = ""
    with client.messages.stream(
        model=CLAUDE_SONNET,
        max_tokens=800,
        system=REVIEW_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_msg}],
        temperature=0.3,
    ) as stream:
        for text in stream.text_stream:
            text = _safe(text)
            print(text, end="", flush=True)
            full_response += text

    print()
    return _safe(full_response)


def main():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("[오류] ANTHROPIC_API_KEY가 .env에 없습니다.")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    review_text = run_review(client)

    # 보고사항들.md에 추가
    today_str = datetime.now().strftime("%Y-%m-%d")
    report_content = f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
주간 시스템 자기 개선 리뷰 — {today_str}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{review_text}

---
다음 리뷰: {(datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')} 예정
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

    write_report("지호", "COO 주간 시스템 리뷰", report_content)
    print("\n[완료] 보고사항들.md 업데이트 완료")


if __name__ == "__main__":
    main()
