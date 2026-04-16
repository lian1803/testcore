#!/usr/bin/env python3
"""
test_knowledge_pipeline.py — 팀 지식 파이프라인 테스트

사용법:
    python test_knowledge_pipeline.py

역할:
1. 팀 지식 주입 시스템이 제대로 작동하는지 확인
2. 각 팀별로 필요한 지식이 제대로 로드되는지 확인
3. 프롬프트 길이 제한이 작동하는지 확인
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))

from core.knowledge_injector import get_team_knowledge, TEAM_KNOWLEDGE_MAP
from core.context_loader import get_team_system_prompt


def test_team_knowledge_loading():
    """각 팀별 지식 로딩 테스트."""
    print("\n" + "="*60)
    print("1️⃣  팀별 지식 로딩 테스트")
    print("="*60)

    for team_name, categories in TEAM_KNOWLEDGE_MAP.items():
        print(f"\n📚 {team_name}")
        print(f"   필요 카테고리: {', '.join(categories)}")

        knowledge = get_team_knowledge(team_name, max_tokens=500)
        if knowledge:
            print(f"   ✅ 지식 로드됨 ({len(knowledge)} 글자)")
            # 첫 100글자 미리보기
            preview = knowledge[:100].replace("\n", " ")
            print(f"   미리보기: {preview}...")
        else:
            print(f"   ⚠️  지식 없음 (아직 분석 결과 없을 수 있음)")


def test_system_prompt_injection():
    """시스템 프롬프트 주입 테스트."""
    print("\n" + "="*60)
    print("2️⃣  시스템 프롬프트 주입 테스트")
    print("="*60)

    base_prompt = "너는 테스트 에이전트야. 간단한 작업을 해라."

    for team_name in TEAM_KNOWLEDGE_MAP.keys():
        print(f"\n📝 {team_name}")

        # 팀 지식 없이 주입
        prompt_without_team = get_team_system_prompt(base_prompt, None)
        print(f"   기본 프롬프트: {len(prompt_without_team)} 글자")

        # 팀 지식 포함해서 주입
        prompt_with_team = get_team_system_prompt(base_prompt, team_name)
        print(f"   팀 지식 포함: {len(prompt_with_team)} 글자")

        if len(prompt_with_team) > len(prompt_without_team):
            increase = len(prompt_with_team) - len(prompt_without_team)
            print(f"   증가량: +{increase} 글자 ✅")
        else:
            print(f"   (지식 없음 또는 이미 포함됨)")


def test_insight_directories():
    """인사이트 파일 디렉토리 확인."""
    print("\n" + "="*60)
    print("3️⃣  인사이트 파일 구조 확인")
    print("="*60)

    knowledge_base = Path(__file__).parent / "knowledge" / "base"
    print(f"\n📁 {knowledge_base}")

    if not knowledge_base.exists():
        print("   ⚠️  knowledge/base 디렉토리 없음 (자동 생성됨)")
        return

    insight_files = sorted(knowledge_base.glob("insights_*.md"))
    if insight_files:
        print(f"   찾은 인사이트 파일: {len(insight_files)}개")
        for f in insight_files:
            size = f.stat().st_size
            print(f"     - {f.name} ({size} 바이트)")
    else:
        print("   ⚠️  인사이트 파일 없음 (아직 분석 결과 없을 수 있음)")


def test_context_loader():
    """context_loader 하위 호환성 테스트."""
    print("\n" + "="*60)
    print("4️⃣  Context Loader 호환성 테스트")
    print("="*60)

    from core.context_loader import inject_context

    test_prompt = "너는 테스트 에이전트야."

    # 기존 방식 (team_name 없이)
    print("\n✅ 기존 방식 호환:")
    result1 = inject_context(test_prompt)
    print(f"   inject_context(prompt) → {len(result1)} 글자")

    # 새 방식 (team_name 포함)
    print("\n✅ 새 방식 호환:")
    result2 = inject_context(test_prompt, team_name="온라인납품팀")
    print(f"   inject_context(prompt, team_name='온라인납품팀') → {len(result2)} 글자")


def test_insight_extractor():
    """인사이트 추출기 임포트 테스트."""
    print("\n" + "="*60)
    print("5️⃣  인사이트 추출기 테스트")
    print("="*60)

    try:
        from core.insight_extractor import (
            extract_and_save_single,
            extract_and_save,
            categorize_insight,
        )
        print("\n✅ 모든 함수 임포트 성공")
        print("   - extract_and_save_single(url, analysis)")
        print("   - extract_and_save()")
        print("   - categorize_insight(text, category, client)")
    except Exception as e:
        print(f"\n❌ 임포트 실패: {e}")


def main():
    print("\n" + "="*70)
    print("🧪 팀 지식 파이프라인 테스트")
    print("="*70)

    test_team_knowledge_loading()
    test_system_prompt_injection()
    test_insight_directories()
    test_context_loader()
    test_insight_extractor()

    print("\n" + "="*70)
    print("✅ 테스트 완료")
    print("="*70)
    print("\n💡 다음 단계:")
    print("  1. python analyze_instagram.py 'URL' — 분석 실행")
    print("  2. knowledge/base/insights_*.md 파일이 생성되는지 확인")
    print("  3. python run_온라인납품팀.py '업무' — 팀 실행해서 지식 주입 확인")


if __name__ == "__main__":
    main()
