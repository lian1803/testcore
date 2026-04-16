#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 1 드라이런 — handoff.py 확장 + context_loader.py 확장 검증.

확인 항목:
1. handoff.py가 outputs/ 의 md+json 전부 team/{프로젝트}/기획문서/ 로 복사하는가
2. INDEX.md가 생성되고 역할별 가이드가 들어가는가
3. context_loader.load_planning_docs() 가 역할별로 맞는 파일을 반환하는가
"""
import sys
import os
import io
from pathlib import Path

# Windows UTF-8
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# company 경로 추가
COMPANY_DIR = Path(__file__).resolve().parents[2] / "company"
sys.path.insert(0, str(COMPANY_DIR))

from core.handoff import PipelineHandoff
from core.context_loader import load_planning_docs


def main():
    # ── 입력 설정 ──
    output_dir = str(
        COMPANY_DIR / "outputs" / "2026-04-14_phase1_test_토지분석"
    )

    context = {
        "idea": "phase1_test_토지분석",  # team/ 폴더명 되는 값
        "prd": "# 테스트 PRD\n\n(실제 PRD는 outputs에서 로드됨)",
        "verdict": "GO",
        "score": 7.75,
        "is_commercial": True,
        "is_software": True,
        "clarified": "토지 사업성 분석 자동화 SaaS",
        "taeho": "",
        "seoyun": "",
        "minsu": "",
        "haeun": "",
        "junhyeok_text": "",
    }

    print("=" * 70)
    print("Phase 1 드라이런 시작")
    print("=" * 70)
    print(f"\n입력 output_dir: {output_dir}")
    print(f"입력 project_name: {context['idea']}")

    # ── 1단계: PipelineHandoff 실행 ──
    print("\n[1/3] PipelineHandoff.generate() 실행")
    handoff = PipelineHandoff(context, output_dir)
    project_dir = handoff.generate()
    print(f"    → project_dir: {project_dir}")

    # ── 2단계: 파일 복사 검증 ──
    print("\n[2/3] 기획문서/ 폴더 검증")
    planning_dir = Path(project_dir) / "기획문서"
    if not planning_dir.exists():
        print("    ❌ 기획문서/ 폴더 생성 실패")
        return 1

    copied_files = sorted(p.name for p in planning_dir.iterdir() if p.is_file())
    print(f"    복사된 파일 수: {len(copied_files)}")
    for f in copied_files:
        print(f"      - {f}")

    # INDEX.md 확인
    index_path = planning_dir / "INDEX.md"
    if not index_path.exists():
        print("    ❌ INDEX.md 생성 실패")
        return 1

    index_content = index_path.read_text(encoding="utf-8")
    print(f"\n    INDEX.md 길이: {len(index_content)} 자")
    print("    INDEX.md 첫 20줄:")
    for line in index_content.split("\n")[:20]:
        print(f"      | {line}")

    # ── 3단계: context_loader.load_planning_docs 검증 ──
    print("\n[3/3] context_loader.load_planning_docs() 역할별 테스트")

    roles = ["marketing", "fe", "be", "cto", "sales", "qa", None]
    for role in roles:
        docs = load_planning_docs(project_dir, role=role)
        label = role if role else "(None=INDEX만)"
        if docs:
            # 첫 100자만 미리보기
            preview = docs[:100].replace("\n", " ")
            print(f"    [{label:12}] len={len(docs):6d} | {preview}...")
        else:
            print(f"    [{label:12}] ❌ 빈 결과")

    print("\n" + "=" * 70)
    print("드라이런 종료")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
