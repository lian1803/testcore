#!/usr/bin/env python3
"""
교육팀 — 신설 팀 자동 생성

사용법:
  python build_team.py "팀 이름" "팀이 해야 할 일"
  python build_team.py "구매대행 팀" "소싱, 주문 수집, 발주 자동화"
"""
import sys, os, io
sys.path.insert(0, os.path.dirname(__file__))
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from dotenv import load_dotenv
load_dotenv()

from teams.education.pipeline import run
from utils.team_templates import (
    list_templates,
    get_similar_template,
    import_team,
    export_team,
    print_templates,
)

BANNER = """
======================================================
     리안 컴퍼니 — 교육팀 (팀 신설 시스템)
  Opus 커리큘럼 설계 → Perplexity 교육 → 팀 생성
======================================================
"""

def check_template_suggestion(team_name: str) -> bool:
    """
    유사한 템플릿이 있으면 제안하고, 사용할지 묻기.
    자동파일럿 모드면 자동으로 사용.
    """
    is_interactive = sys.stdin.isatty() if hasattr(sys.stdin, 'isatty') else True

    # 기존 템플릿 확인
    templates = list_templates()
    if not templates:
        return False

    # 키워드로 비슷한 템플릿 찾기
    for keyword in team_name.split():
        similar = get_similar_template(keyword)
        if similar:
            if is_interactive:
                print(f"\n💡 '{similar}' 템플릿을 빠르게 사용할까요? [y/n]")
                try:
                    choice = input("> ").strip().lower()
                    if choice in ("y", "yes", "ㅇ", "응"):
                        print(f"\n📋 템플릿에서 {team_name} 생성 중...")
                        try:
                            import_team(similar, team_name)
                            print(f"✅ {team_name} 생성 완료 (템플릿 기반)")
                            return True
                        except Exception as e:
                            print(f"⚠️ 템플릿 사용 실패 (일반 방식 진행): {e}")
                            return False
                except EOFError:
                    return False
            else:
                # 자동파일럿 모드 → 자동으로 템플릿 사용
                print(f"\n🚀 자동파일럿: '{similar}' 템플릿 사용 중...")
                try:
                    import_team(similar, team_name)
                    print(f"✅ {team_name} 생성 완료 (템플릿 기반)")
                    return True
                except Exception as e:
                    print(f"⚠️ 템플릿 사용 실패 (일반 방식 진행): {e}")
                    return False

    return False


if __name__ == "__main__":
    print(BANNER)

    # 템플릿 목록 옵션 (--templates, -t)
    if "--templates" in sys.argv or "-t" in sys.argv:
        print_templates()
        sys.exit(0)

    if len(sys.argv) >= 3:
        team_name = sys.argv[1]
        team_purpose = " ".join(sys.argv[2:])
    elif len(sys.argv) == 2:
        team_name = sys.argv[1]
        print("이 팀이 해야 할 일:")
        team_purpose = input("> ").strip()
    else:
        print("신설할 팀 이름:")
        team_name = input("> ").strip()
        print("이 팀이 해야 할 일 (구체적으로):")
        team_purpose = input("> ").strip()

    # 템플릿 사용 여부 확인
    if check_template_suggestion(team_name):
        # 템플릿으로 팀 생성됨 — 교육팀 스킵
        pass
    else:
        # 일반 방식: 교육팀 → Opus + Perplexity 거쳐서 생성
        run(team_name, team_purpose)
