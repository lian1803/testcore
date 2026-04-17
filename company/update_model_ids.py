"""
update_model_ids.py — 구버전 모델 ID 일괄 최신화

Opus 4.6/4.1 → 4.7
Sonnet 4.5 → 4.6

일회성 스크립트. 실행 후 삭제.
"""
import os
import sys
import re
from pathlib import Path

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = Path(__file__).parent.parent

# 치환 매핑 (구 → 신)
REPLACEMENTS = [
    ("claude-opus-4-6", "claude-opus-4-7"),
    ("claude-opus-4-1-20250805", "claude-opus-4-7"),
    ("claude-opus-4-20250514", "claude-opus-4-7"),
    ("claude-sonnet-4-5-20250929", "claude-sonnet-4-6"),
    ('"claude-sonnet-4-5"', '"claude-sonnet-4-6"'),
    ("'claude-sonnet-4-5'", "'claude-sonnet-4-6'"),
    ("claude-sonnet-4-20250514", "claude-sonnet-4-6"),
]

# 대상 폴더
TARGET_DIRS = [
    ROOT / ".claude" / "agents",
    ROOT / "company",
]

# 제외 경로
EXCLUDE_PARTS = {"venv", "__pycache__", "node_modules", ".git", "archive"}


def should_skip(path: Path) -> bool:
    return any(part in EXCLUDE_PARTS for part in path.parts)


def update_file(path: Path) -> list[tuple[str, str, int]]:
    """파일 내 모든 치환 적용. 변경된 (old, new, count) 리턴."""
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return []

    changes = []
    new_text = text
    for old, new in REPLACEMENTS:
        if old in new_text:
            count = new_text.count(old)
            new_text = new_text.replace(old, new)
            changes.append((old, new, count))

    if changes:
        path.write_text(new_text, encoding="utf-8")
    return changes


def main():
    total_files = 0
    total_changes = 0
    change_log = {}

    for target in TARGET_DIRS:
        if not target.exists():
            continue
        for path in target.rglob("*"):
            if not path.is_file() or should_skip(path):
                continue
            if path.suffix not in {".py", ".md"}:
                continue

            changes = update_file(path)
            if changes:
                total_files += 1
                for old, new, count in changes:
                    total_changes += count
                    key = f"{old} → {new}"
                    change_log[key] = change_log.get(key, 0) + count
                rel = path.relative_to(ROOT)
                print(f"  ✏️  {rel}")
                for old, new, count in changes:
                    print(f"       {old} → {new} ({count}회)")

    print(f"\n=== 요약 ===")
    print(f"수정된 파일: {total_files}개")
    print(f"총 치환 횟수: {total_changes}회")
    print(f"\n치환별 통계:")
    for k, v in change_log.items():
        print(f"  {k}: {v}회")


if __name__ == "__main__":
    main()
