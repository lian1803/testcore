"""
git_review.py — Git 리뷰 자동화 시스템

팀원들이 core-shell에 push한 변경사항을 자동으로 감지하고,
Claude Sonnet으로 리뷰한 후, 리안이 승인한 것만 선택적으로 머지한다.

사용법:
    python -m core.git_review scan          # 새 변경사항 스캔 + 리뷰
    python -m core.git_review review-branch feature/travel-guide
    python -m core.git_review apply 862923a  # 특정 커밋 체리픽
    python -m core.git_review report        # 리뷰 보고서 보기
    python -m core.git_review push          # 최종본 push (리안 확인 필수)
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path
import anthropic

# Windows 인코딩 처리
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


# ═════════════════════════════════════════════════════════════════
# 설정
# ═════════════════════════════════════════════════════════════════

REPO_ROOT = Path(__file__).parent.parent.parent  # C:/Users/lian1/Documents/Work/core
LIAN_COMPANY_ROOT = Path(__file__).parent.parent  # C:/Users/lian1/Documents/Work/core/company
REVIEWS_DIR = LIAN_COMPANY_ROOT / "reviews"
REMOTE_NAME = "core-shell"
MAIN_BRANCH = "main"

REVIEWS_DIR.mkdir(exist_ok=True)


# ═════════════════════════════════════════════════════════════════
# Git 유틸리티
# ═════════════════════════════════════════════════════════════════

def git_cmd(cmd: str, cwd: str = None) -> str:
    """Git 커맨드 실행."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            cwd=cwd or str(REPO_ROOT)
        )
        return result.stdout.strip()
    except Exception as e:
        return f"[ERROR] {e}"


def fetch_remote():
    """core-shell fetch."""
    print(f"🔄 Fetching {REMOTE_NAME}...")
    output = git_cmd(f"git fetch {REMOTE_NAME}")
    print(output if output else "✅ Fetch complete")


def get_new_commits() -> list:
    """main에 없는 새 커밋 가져오기 (core-shell/main)."""
    output = git_cmd(
        f"git log {MAIN_BRANCH}..{REMOTE_NAME}/{MAIN_BRANCH} "
        "--pretty=format:%H|%an|%ae|%s|%aI"
    )

    if not output or "ERROR" in output:
        return []

    commits = []
    for line in output.split("\n"):
        if line.strip():
            parts = line.split("|")
            if len(parts) >= 5:
                commits.append({
                    "hash": parts[0],
                    "author": parts[1],
                    "email": parts[2],
                    "message": parts[3],
                    "date": parts[4],
                })
    return commits


def get_commit_diff(commit_hash: str) -> str:
    """특정 커밋의 diff 가져오기."""
    output = git_cmd(f"git show {commit_hash}")
    return output[:3000] if output else ""  # 처음 3000자만


def get_changed_files(commit_hash: str) -> list:
    """특정 커밋에서 변경된 파일 목록."""
    output = git_cmd(f"git diff-tree --no-commit-id --name-only -r {commit_hash}")
    return output.split("\n") if output else []


def get_new_branches() -> list:
    """새로운 원격 브랜치 목록."""
    output = git_cmd(f"git branch -r --list '{REMOTE_NAME}/*'")

    branches = []
    for line in output.split("\n"):
        line = line.strip()
        if line and "HEAD" not in line:
            # "  core-shell/feature/travel-guide" 형태
            branch_full = line.replace("remotes/", "")
            branch_name = branch_full.replace(f"{REMOTE_NAME}/", "")

            # main/master 제외
            if branch_name not in [MAIN_BRANCH, "master"]:
                branches.append(branch_name)

    return branches


def get_branch_commit_count(branch_name: str) -> int:
    """브랜치의 커밋 수 (main과의 비교)."""
    output = git_cmd(
        f"git log {MAIN_BRANCH}..{REMOTE_NAME}/{branch_name} --oneline"
    )
    return len([x for x in output.split("\n") if x.strip()]) if output else 0


def get_branch_commits(branch_name: str) -> list:
    """특정 브랜치의 모든 커밋."""
    output = git_cmd(
        f"git log {MAIN_BRANCH}..{REMOTE_NAME}/{branch_name} "
        "--pretty=format:%H|%an|%s"
    )

    commits = []
    for line in output.split("\n"):
        if line.strip():
            parts = line.split("|")
            if len(parts) >= 3:
                commits.append({
                    "hash": parts[0],
                    "author": parts[1],
                    "message": parts[2],
                })
    return commits


# ═════════════════════════════════════════════════════════════════
# AI 리뷰
# ═════════════════════════════════════════════════════════════════

def review_commit(commit_hash: str, author: str, message: str, diff: str, files: list) -> dict:
    """Claude Sonnet으로 커밋 리뷰."""

    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    prompt = f"""당신은 리안 컴퍼니의 Git 리뷰 담당자다.
팀원이 core-shell에 push한 이 커밋을 평가하고, 우리 main 브랜치에 도입할지 결정해라.

커밋 정보:
- 작성자: {author}
- 메시지: {message}
- 변경 파일: {', '.join(files[:10])}
- 해시: {commit_hash}

변경 내용 (Diff):
```
{diff}
```

리뷰 기준:
1. **우리 시스템(company)에 도움 되는가?**
   - 버그 수정, 성능 개선, 기능 추가 = ADOPT
   - 우리와 무관한 개인 설정 = SKIP

2. **기존 코드를 깨뜨리지 않는가?**
   - 충돌 가능성이 있으면 = CONFLICT

3. **아이디어만 좋고 구현이 다르면 = ADAPT**
   - 수정이 필요하다는 구체적 피드백

JSON으로 답해라:
{
  "verdict": "ADOPT|SKIP|ADAPT|CONFLICT",
  "reason": "한 문장 설명",
  "details": "자세한 피드백",
  "impact_score": 1-10,
  "tags": ["버그수정"|"성능"|"기능"|"문서"|"테스트"|"설정"|"타입"]
}"""

    try:
        message_obj = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = message_obj.content[0].text

        # JSON 추출
        import re
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
            return result
        else:
            return {
                "verdict": "SKIP",
                "reason": "리뷰 실패",
                "details": response_text,
                "impact_score": 0,
                "tags": []
            }
    except Exception as e:
        return {
            "verdict": "SKIP",
            "reason": f"API 호출 실패: {e}",
            "details": str(e),
            "impact_score": 0,
            "tags": []
        }


def review_branch(branch_name: str) -> dict:
    """특정 브랜치 전체 리뷰."""
    commits = get_branch_commits(branch_name)

    if not commits:
        return {
            "branch": branch_name,
            "status": "EMPTY",
            "commits": [],
            "summary": "변경사항 없음"
        }

    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    commit_messages = "\n".join([f"- {c['author']}: {c['message']}" for c in commits])

    prompt = f"""당신은 리안 컴퍼니의 Git 리뷰 담당자다.
팀원이 만든 새 브랜치를 평가해라.

브랜치: {branch_name}
커밋 수: {len(commits)}
작업 내용:
{commit_messages}

이 브랜치의 목적, 완성도, 우리 시스템에 도입할 가치를 평가해라.

JSON으로 답해라:
{
  "verdict": "ADOPT|REVIEW|SKIP",
  "summary": "브랜치 목적 요약",
  "quality_score": 1-10,
  "recommendation": "도입 권고사항",
  "next_steps": ["step1", "step2"]
}"""

    try:
        message_obj = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = message_obj.content[0].text

        import re
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
        else:
            result = {"summary": response_text}

        result["branch"] = branch_name
        result["commits"] = commits
        return result
    except Exception as e:
        return {
            "branch": branch_name,
            "verdict": "REVIEW",
            "summary": f"리뷰 실패: {e}",
            "commits": commits
        }


# ═════════════════════════════════════════════════════════════════
# 스캔 및 보고서 생성
# ═════════════════════════════════════════════════════════════════

def scan_remote() -> dict:
    """core-shell의 새 변경사항 감지 및 리뷰."""
    print("\n" + "="*60)
    print("🔍 Git 변경사항 스캔 및 리뷰 시작")
    print("="*60)

    fetch_remote()

    new_commits = get_new_commits()
    new_branches = get_new_branches()

    print(f"\n📊 발견: {len(new_commits)}개 커밋, {len(new_branches)}개 브랜치")

    # 커밋 리뷰
    reviewed_commits = []
    for commit in new_commits:
        print(f"\n📝 리뷰: {commit['hash'][:7]} by {commit['author']}")
        print(f"   메시지: {commit['message']}")

        diff = get_commit_diff(commit['hash'])
        files = get_changed_files(commit['hash'])

        review = review_commit(
            commit['hash'],
            commit['author'],
            commit['message'],
            diff,
            files
        )

        commit['review'] = review
        reviewed_commits.append(commit)
        print(f"   결론: {review['verdict']} - {review['reason']}")

    # 브랜치 리뷰
    reviewed_branches = []
    for branch in new_branches:
        print(f"\n🌿 리뷰: {branch}")
        review = review_branch(branch)
        reviewed_branches.append(review)
        print(f"   결론: {review.get('verdict', 'UNKNOWN')}")

    # 결과 저장
    timestamp = datetime.now().strftime("%Y-%m-%d")
    result = {
        "scan_date": timestamp,
        "remote": REMOTE_NAME,
        "new_commits": reviewed_commits,
        "new_branches": reviewed_branches,
        "summary": {
            "total_commits": len(new_commits),
            "adopt": sum(1 for c in reviewed_commits if c.get('review', {}).get('verdict') == 'ADOPT'),
            "adapt": sum(1 for c in reviewed_commits if c.get('review', {}).get('verdict') == 'ADAPT'),
            "skip": sum(1 for c in reviewed_commits if c.get('review', {}).get('verdict') == 'SKIP'),
            "conflict": sum(1 for c in reviewed_commits if c.get('review', {}).get('verdict') == 'CONFLICT'),
        }
    }

    return result


def save_review_result(result: dict):
    """리뷰 결과 저장."""
    timestamp = result.get("scan_date", datetime.now().strftime("%Y-%m-%d"))

    # JSON 저장
    json_path = REVIEWS_DIR / f"{timestamp}_review.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"✅ 리뷰 결과 저장: {json_path}")

    # Markdown 리포트 생성
    md_path = REVIEWS_DIR / f"{timestamp}_review.md"
    report = generate_review_report(result)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"✅ 리포트 생성: {md_path}")


def generate_review_report(result: dict) -> str:
    """리뷰 결과를 사람이 읽을 수 있는 Markdown으로 변환."""

    lines = [
        f"# Git 리뷰 보고서",
        f"",
        f"**스캔 날짜**: {result['scan_date']}",
        f"**원격 저장소**: {result['remote']}",
        f"",
    ]

    summary = result.get("summary", {})
    lines.extend([
        f"## 요약",
        f"",
        f"| 카테고리 | 개수 |",
        f"|---------|------|",
        f"| 총 커밋 | {summary.get('total_commits', 0)} |",
        f"| 도입(ADOPT) | {summary.get('adopt', 0)} |",
        f"| 수정 필요(ADAPT) | {summary.get('adapt', 0)} |",
        f"| 스킵(SKIP) | {summary.get('skip', 0)} |",
        f"| 충돌(CONFLICT) | {summary.get('conflict', 0)} |",
        f"",
    ])

    # 커밋별 리뷰
    commits = result.get("new_commits", [])
    if commits:
        lines.append(f"## 새 커밋 ({len(commits)}개)")
        lines.append("")

        for commit in commits:
            review = commit.get("review", {})
            lines.extend([
                f"### {commit['hash'][:7]} - {commit['message']}",
                f"",
                f"**작성자**: {commit['author']}",
                f"**날짜**: {commit['date']}",
                f"**결론**: **{review.get('verdict', '?')}**",
                f"**이유**: {review.get('reason', 'N/A')}",
                f"**평가**: {review.get('impact_score', 0)}/10",
                f"",
                f"```",
                f"{review.get('details', 'N/A')}",
                f"```",
                f"",
            ])

    # 브랜치 리뷰
    branches = result.get("new_branches", [])
    if branches:
        lines.append(f"## 새 브랜치 ({len(branches)}개)")
        lines.append("")

        for branch in branches:
            lines.extend([
                f"### {branch.get('branch', '?')}",
                f"",
                f"**결론**: {branch.get('verdict', 'UNKNOWN')}",
                f"**요약**: {branch.get('summary', 'N/A')}",
                f"**품질 점수**: {branch.get('quality_score', 0)}/10",
                f"**권고**: {branch.get('recommendation', 'N/A')}",
                f"",
                f"커밋 ({len(branch.get('commits', []))}):",
                f"",
            ])

            for commit in branch.get('commits', []):
                lines.append(f"- `{commit['hash'][:7]}` {commit['author']}: {commit['message']}")

            lines.append("")

    # 다음 단계
    lines.extend([
        f"## 다음 단계",
        f"",
        f"1. **ADOPT 커밋 체리픽**:",
        f"   ```bash",
        f"   python -m core.git_review apply <commit_hash>",
        f"   ```",
        f"",
        f"2. **ADAPT 항목 검토**:",
        f"   브랜치를 체크아웃해서 수정한 후 다시 리뷰",
        f"",
        f"3. **최종 push**:",
        f"   ```bash",
        f"   python -m core.git_review push",
        f"   ```",
        f"",
    ])

    return "\n".join(lines)


# ═════════════════════════════════════════════════════════════════
# 머지 및 푸시
# ═════════════════════════════════════════════════════════════════

def apply_commit(commit_hash: str) -> bool:
    """특정 커밋을 cherry-pick으로 적용."""
    print(f"\n🔧 Cherry-pick {commit_hash}...")

    output = git_cmd(f"git cherry-pick {commit_hash}")

    if "error" in output.lower() or "conflict" in output.lower():
        print(f"❌ 체리픽 실패: {output}")
        return False
    else:
        print(f"✅ 체리픽 성공")
        return True


def push_final():
    """최종본을 core-shell에 push."""
    print("\n" + "="*60)
    print("⚠️  최종 push는 리안 확인 후에만 진행")
    print("="*60)

    confirm = input("\n정말 push하시겠습니까? (yes/no): ").strip().lower()

    if confirm != "yes":
        print("❌ Push 취소됨")
        return False

    print(f"\n📤 Push {MAIN_BRANCH} → {REMOTE_NAME}...")
    output = git_cmd(f"git push {REMOTE_NAME} {MAIN_BRANCH}")

    if "error" in output.lower():
        print(f"❌ Push 실패: {output}")
        return False
    else:
        print(f"✅ Push 성공")
        return True


# ═════════════════════════════════════════════════════════════════
# CLI
# ═════════════════════════════════════════════════════════════════

def main():
    import sys

    if len(sys.argv) < 2:
        print("""
사용법:
  python -m core.git_review scan              # 새 변경사항 스캔 + 리뷰
  python -m core.git_review review-branch <name>  # 특정 브랜치 리뷰
  python -m core.git_review apply <hash>     # 특정 커밋 적용
  python -m core.git_review report           # 리뷰 보고서 보기
  python -m core.git_review push             # 최종본 push
        """)
        return

    command = sys.argv[1]

    if command == "scan":
        result = scan_remote()
        save_review_result(result)
        print("\n✅ 스캔 완료")

    elif command == "review-branch":
        if len(sys.argv) < 3:
            print("❌ 브랜치 이름을 지정하세요")
            return
        branch_name = sys.argv[2]
        result = review_branch(branch_name)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "apply":
        if len(sys.argv) < 3:
            print("❌ 커밋 해시를 지정하세요")
            return
        commit_hash = sys.argv[2]
        apply_commit(commit_hash)

    elif command == "report":
        # 최신 리뷰 리포트 보기
        json_files = sorted(REVIEWS_DIR.glob("*_review.json"), reverse=True)
        if not json_files:
            print("❌ 리뷰 기록이 없습니다")
            return

        latest = json_files[0]
        with open(latest, "r", encoding="utf-8") as f:
            result = json.load(f)

        report = generate_review_report(result)
        print(report)

    elif command == "push":
        push_final()

    else:
        print(f"❌ 알 수 없는 커맨드: {command}")


if __name__ == "__main__":
    main()
