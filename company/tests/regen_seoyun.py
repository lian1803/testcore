#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""서윤 시장조사 재생성 (기존 파이프라인 output 재활용).

사용법:
    python -m tests.regen_seoyun                          # 최신 output
    python -m tests.regen_seoyun outputs/2026-04-13_xxx/  # 특정 폴더
"""
import os
import sys
import io
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    except Exception:
        pass

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from dotenv import load_dotenv

load_dotenv()

from agents import seoyun


def regen(output_dir: Path):
    if not output_dir.exists():
        print(f"❌ 폴더 없음: {output_dir}")
        sys.exit(1)

    # idea 추출 (이사팀 보고서 or 폴더명)
    idea = ""
    report_path = output_dir / "00_이사팀_보고서.md"
    if report_path.exists():
        content = report_path.read_text(encoding="utf-8")
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if "■ 아이디어" in line or line.strip() == "■ 아이디어":
                # 다음 비어있지 않은 줄
                for j in range(i + 1, min(i + 5, len(lines))):
                    stripped = lines[j].strip()
                    if stripped and not stripped.startswith("━") and not stripped.startswith("■"):
                        idea = stripped
                        break
                break
    if not idea:
        import re
        idea = re.sub(r"^\d{4}-\d{2}-\d{2}_\d{6}_", "", output_dir.name).replace("_", " ")

    context = {
        "idea": idea,
        "clarified": idea,
    }

    print(f"🔄 서윤 시장조사 재생성 중... (아이디어: {idea[:60]})")
    print("=" * 60)

    result = seoyun.run(context)

    seoyun_path = output_dir / "01_시장조사_서윤.md"
    # 백업
    backup_path = output_dir / "01_시장조사_서윤.backup.md"
    if seoyun_path.exists():
        backup_path.write_text(seoyun_path.read_text(encoding="utf-8"), encoding="utf-8")
    seoyun_path.write_text(result, encoding="utf-8")

    print(f"\n\n✅ 재생성 완료: {seoyun_path}")
    print(f"   이전 백업: {backup_path}")
    print(f"   새 서윤 길이: {len(result)}자")

    # Level 4-5 카운트 확인 (인라인 + 표 형식 둘 다)
    import re
    count = len(re.findall(
        r"(?:Level\s*[45](?!\s*[0-9])|Pain\s*Level\s*\|?\s*[45]\b|pain[_ ]level\s*\|?\s*[45]\b)",
        result, re.IGNORECASE
    ))
    print(f"   Level 4-5 카운트: {count}개 (기준: 7개 이상)")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        target = Path(sys.argv[1])
        if not target.is_absolute():
            outputs = Path(__file__).resolve().parent.parent / "outputs"
            target = outputs / target.name
    else:
        outputs = Path(__file__).resolve().parent.parent / "outputs"
        dirs = sorted([d for d in outputs.iterdir() if d.is_dir()], key=lambda d: d.stat().st_mtime, reverse=True)
        if not dirs:
            print("❌ outputs 폴더 비어 있음")
            sys.exit(1)
        target = dirs[0]
        print(f"  (최신 output 자동 선택: {target.name})")

    regen(target)
