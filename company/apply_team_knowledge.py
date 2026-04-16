#!/usr/bin/env python3
"""
apply_team_knowledge.py — 팀 에이전트들에 팀 지식 주입 자동 적용

사용법:
    python apply_team_knowledge.py <팀이름>

예시:
    python apply_team_knowledge.py 온라인납품팀
    python apply_team_knowledge.py 온라인영업팀
    python apply_team_knowledge.py 온라인마케팅팀
    python apply_team_knowledge.py 오프라인마케팍팀

역할:
- 팀의 모든 에이전트 .py 파일을 찾아서
- run() 함수 내에서 SYSTEM_PROMPT를 get_team_system_prompt()로 감싸기
- sys.path, 임포트 자동 추가
"""

import os
import re
import sys
from pathlib import Path

# 팀별 에이전트 디렉토리
TEAM_DIRS = {
    "온라인납품팀": "teams/온라인납품팀",
    "온라인영업팀": "teams/온라인영업팀",
    "온라인마케팅팀": "teams/온라인마케팅팀",
    "오프라인마케팅팀": "teams/offline_marketing",
}


def apply_knowledge_injection(team_name: str, team_dir: str):
    """팀의 모든 에이전트 파일에 팀 지식 주입 적용."""

    team_path = Path(__file__).parent / team_dir
    if not team_path.exists():
        print(f"❌ 팀 디렉토리 없음: {team_path}")
        return

    agent_files = [f for f in team_path.glob("*.py") if f.name != "pipeline.py" and f.name != "__init__.py"]

    print(f"\n🎯 {team_name}")
    print(f"📁 {team_path}")
    print(f"👥 에이전트 {len(agent_files)}개 찾음\n")

    for agent_file in agent_files:
        print(f"  📝 {agent_file.name}...", end=" ", flush=True)
        try:
            with open(agent_file, "r", encoding="utf-8") as f:
                content = f.read()

            # 이미 적용됐는지 확인
            if "get_team_system_prompt" in content:
                print("✅ 이미 적용됨")
                continue

            # 1. sys 임포트 확인 (없으면 추가)
            if "import sys" not in content:
                content = content.replace("import os\n", "import os\nimport sys\n")

            # 2. anthropic 임포트 후에 core 임포트 추가
            import_section = re.search(r"^(import .*?\n\n)", content, re.MULTILINE | re.DOTALL)
            if import_section:
                insert_pos = import_section.end()
                core_import = (
                    f'# 팀 지식 주입을 위해 core 임포트\n'
                    f'sys.path.insert(0, os.path.join(os.path.dirname(__file__), \'../../\'))\n'
                    f'from core.context_loader import get_team_system_prompt\n'
                )
                if core_import not in content:
                    content = content[:insert_pos] + core_import + "\n" + content[insert_pos:]

            # 3. TEAM_NAME 상수 추가
            model_line = re.search(r'^MODEL = ".*"$', content, re.MULTILINE)
            if model_line:
                insert_pos = model_line.end()
                team_const = f'TEAM_NAME = "{team_name}"'
                if f'TEAM_NAME = "{team_name}"' not in content:
                    content = content[:insert_pos] + f"\n{team_const}" + content[insert_pos:]

            # 4. run() 함수에서 SYSTEM_PROMPT → get_team_system_prompt()
            # system=SYSTEM_PROMPT 를 찾아서 system=team_system_prompt로 변경
            if "system=SYSTEM_PROMPT" in content and "system=team_system_prompt" not in content:
                # run 함수 찾기
                run_match = re.search(r'^def run\(.*?\):', content, re.MULTILINE)
                if run_match:
                    run_start = run_match.end()
                    # 함수 본문 찾기 (들여쓰기 기준)
                    lines = content[run_start:].split("\n")
                    func_body_start = None
                    for i, line in enumerate(lines):
                        if line.strip() and not line.startswith(" " * 4):
                            func_body_start = i
                            break

                    if func_body_start is None:
                        func_body_start = len(lines)

                    # 함수 본문 첫 줄에 팀 지식 주입 코드 추가
                    injection_code = (
                        "\n    # 팀 지식 자동 주입 (분석 결과 기반 학습)"
                        "\n    team_system_prompt = get_team_system_prompt(SYSTEM_PROMPT, TEAM_NAME)\n"
                    )
                    func_body = "\n".join(lines[:func_body_start])
                    rest_body = "\n".join(lines[func_body_start:])

                    new_func_body = func_body + injection_code + rest_body
                    content = content[:run_start] + new_func_body

                    # system=SYSTEM_PROMPT → system=team_system_prompt (함수 내에서만)
                    # 더 정확한 방법: run 함수만 대체
                    run_func_match = re.search(
                        r'(def run\(.*?\):.*?)(?=\ndef |\Z)',
                        content,
                        re.DOTALL
                    )
                    if run_func_match:
                        run_func = run_func_match.group(1)
                        new_run_func = run_func.replace("system=SYSTEM_PROMPT", "system=team_system_prompt")
                        content = content.replace(run_func, new_run_func)

            # 파일 저장
            with open(agent_file, "w", encoding="utf-8") as f:
                f.write(content)

            print("✅ 적용됨")

        except Exception as e:
            print(f"❌ 에러: {e}")


def main():
    if len(sys.argv) < 2:
        print("사용법: python apply_team_knowledge.py <팀이름>")
        print(f"\n가능한 팀: {', '.join(TEAM_DIRS.keys())}")
        sys.exit(1)

    team_name = sys.argv[1]

    if team_name not in TEAM_DIRS:
        print(f"❌ 팀 '{team_name}'을(를) 찾을 수 없습니다.")
        print(f"가능한 팀: {', '.join(TEAM_DIRS.keys())}")
        sys.exit(1)

    team_dir = TEAM_DIRS[team_name]
    apply_knowledge_injection(team_name, team_dir)

    print(f"\n✅ {team_name} 팀 지식 주입 적용 완료")
    print(f"\n다음 단계:")
    print(f"  python run_{team_name}.py '업무 설명'")


if __name__ == "__main__":
    main()
