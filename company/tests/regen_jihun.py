#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""지훈 PRD 재생성 (기존 파이프라인 output 재활용).

사용법:
    python -m tests.regen_jihun outputs/2026-04-13_xxx/
"""
import os
import sys
import io
import json
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

import anthropic
from agents import jihun


def regen(output_dir: Path):
    if not output_dir.exists():
        print(f"❌ 폴더 없음: {output_dir}")
        sys.exit(1)

    # 기존 산출물 읽기
    minsu = (output_dir / "02_전략_민수.md").read_text(encoding="utf-8")
    haeun = (output_dir / "03_검증_하은.md").read_text(encoding="utf-8")

    junhyeok_path = output_dir / "04_최종판단_준혁.json"
    junhyeok_text = ""
    if junhyeok_path.exists():
        try:
            data = json.loads(junhyeok_path.read_text(encoding="utf-8"))
            junhyeok_text = data.get("text", "")
        except Exception:
            junhyeok_text = junhyeok_path.read_text(encoding="utf-8")

    # idea는 보고서에서 추출
    idea = ""
    report_path = output_dir / "00_이사팀_보고서.md"
    if report_path.exists():
        content = report_path.read_text(encoding="utf-8")
        for line in content.split("\n"):
            if "아이디어" in line or line.strip().startswith("■"):
                continue
            if line.strip() and "===" not in line:
                idea = line.strip()
                break
    if not idea:
        idea = output_dir.name

    context = {
        "idea": idea,
        "clarified": idea,
        "minsu": minsu,
        "haeun": haeun,
        "junhyeok_text": junhyeok_text,
        "is_commercial": True,
    }

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY 없음")
        sys.exit(1)
    client = anthropic.Anthropic(api_key=api_key)

    print(f"🔄 지훈 PRD 재생성 중... (아이디어: {idea[:60]}...)")
    print("=" * 60)
    prd = jihun.run(context, client)

    prd_path = output_dir / "05_PRD_지훈.md"
    # 백업
    backup_path = output_dir / "05_PRD_지훈.truncated_backup.md"
    if prd_path.exists():
        backup_path.write_text(prd_path.read_text(encoding="utf-8"), encoding="utf-8")
    prd_path.write_text(prd, encoding="utf-8")

    print(f"\n\n✅ 재생성 완료: {prd_path}")
    print(f"   이전(잘린) 백업: {backup_path}")
    print(f"   새 PRD 길이: {len(prd)}자")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        target = Path(sys.argv[1])
    else:
        outputs = Path(__file__).resolve().parent.parent / "outputs"
        dirs = sorted([d for d in outputs.iterdir() if d.is_dir()], key=lambda d: d.stat().st_mtime, reverse=True)
        if not dirs:
            print("❌ outputs 폴더 비어 있음")
            sys.exit(1)
        target = dirs[0]
        print(f"  (최신 output 자동 선택: {target.name})")

    regen(target)
