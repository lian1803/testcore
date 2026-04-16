#!/usr/bin/env python3
"""
기존 팀들을 자동으로 템플릿으로 내보내기

사용법:
  python export_team_templates.py

설명:
  - 온라인영업팀, 온라인납품팀, 온라인마케팅팀을 templates/ 폴더에 저장
  - 이후에 build_team.py에서 템플릿으로 빠르게 재사용 가능
"""

import sys
import os
import io

sys.path.insert(0, os.path.dirname(__file__))

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from utils.team_templates import export_team, print_templates

TEAMS_TO_EXPORT = [
    "온라인영업팀",
    "온라인납품팀",
    "온라인마케팅팀",
]

BANNER = """
======================================================
     팀 템플릿 내보내기 (Export)
  기존 팀을 재사용 가능한 템플릿으로 저장
======================================================
"""


if __name__ == "__main__":
    print(BANNER)

    print(f"\n📦 {len(TEAMS_TO_EXPORT)}개 팀을 템플릿으로 내보내는 중...\n")

    exported = []
    failed = []

    for team_name in TEAMS_TO_EXPORT:
        try:
            print(f"[{team_name}] 내보내기 중...")
            template_path = export_team(team_name)
            exported.append(team_name)
            print(f"  ✅ 완료: {template_path}")
        except Exception as e:
            print(f"  ❌ 실패: {e}")
            failed.append((team_name, str(e)))

    print(f"\n{'='*60}")
    print(f"📊 결과")
    print(f"{'='*60}")
    print(f"✅ 성공: {len(exported)}개")
    for team in exported:
        print(f"   - {team}")

    if failed:
        print(f"\n❌ 실패: {len(failed)}개")
        for team, error in failed:
            print(f"   - {team}: {error}")

    print(f"\n{'='*60}")
    print(f"📦 사용 가능한 템플릿")
    print(f"{'='*60}")
    print_templates()

    print(f"\n다음에 새 팀을 만들 때:")
    print(f"  python build_team.py \"팀이름\" \"팀 설명\"")
    print(f"\n비슷한 이름의 템플릿이 있으면 자동으로 제안됨!")
