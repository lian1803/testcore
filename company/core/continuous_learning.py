"""
continuous_learning.py — 팀별 지속 학습 엔진

각 팀의 mission.md에서 '학습 주제'를 읽어서 Perplexity로 최신 자료를 수집하고,
에이전트 프롬프트에 주입할 수 있는 형태로 반환.

사용법 (파이프라인에서):
    from core.continuous_learning import learn_before_run
    fresh_knowledge = learn_before_run("offline_marketing")
    # → context["fresh_knowledge"] = fresh_knowledge

자동 실행 (스케줄러에서):
    python -m core.continuous_learning 온라인영업팀
    python -m core.continuous_learning all
"""
import os
import re
import sys
from datetime import datetime
from core.research_loop import research_before_task

TEAMS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "teams")
KNOWLEDGE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "knowledge", "teams")


def _parse_learning_topics(mission_path: str) -> list[str]:
    """mission.md에서 '## 학습 주제' 섹션의 쿼리 목록을 파싱."""
    try:
        with open(mission_path, encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        return []

    # '## 학습 주제' 섹션 찾기
    match = re.search(r'## 학습 주제.*?\n(.*?)(?=\n## |\Z)', content, re.DOTALL)
    if not match:
        return []

    section = match.group(1)
    queries = []
    for line in section.strip().split('\n'):
        line = line.strip()
        if line.startswith('- "') and line.endswith('"'):
            queries.append(line[3:-1])
        elif line.startswith("- '") and line.endswith("'"):
            queries.append(line[3:-1])
    return queries


def _find_team_dir(team_name: str) -> str | None:
    """팀 이름으로 디렉토리 찾기."""
    # 정확히 일치
    exact = os.path.join(TEAMS_DIR, team_name)
    if os.path.isdir(exact):
        return exact

    # 부분 일치
    for d in os.listdir(TEAMS_DIR):
        if team_name.lower() in d.lower():
            path = os.path.join(TEAMS_DIR, d)
            if os.path.isdir(path):
                return path
    return None


def learn_before_run(team_name: str) -> str:
    """팀별 학습 실행. mission.md의 학습 주제로 Perplexity 리서치 후 결과 반환.

    Args:
        team_name: 팀 폴더명 (예: "offline_marketing", "온라인영업팀")

    Returns:
        수집된 최신 지식 텍스트 (에이전트 프롬프트에 붙여서 쓸 것)
    """
    team_dir = _find_team_dir(team_name)
    if not team_dir:
        print(f"[학습] 팀 '{team_name}' 디렉토리 없음")
        return ""

    mission_path = os.path.join(team_dir, "mission.md")
    queries = _parse_learning_topics(mission_path)

    if not queries:
        print(f"[학습] {team_name}: mission.md에 학습 주제 없음")
        return ""

    print(f"\n{'='*60}")
    print(f"📚 {team_name} 학습 시작 ({len(queries)}개 주제)")
    print("="*60)

    # research_loop.py 활용 (캐싱 자동 적용)
    result = research_before_task(
        role=team_name,
        task="팀 전문성 강화",
        queries=queries,
        auto_generate=False,
    )

    # 팀별 지식 폴더에 저장
    if result:
        team_knowledge_dir = os.path.join(KNOWLEDGE_DIR, team_name.replace("/", "_"))
        os.makedirs(team_knowledge_dir, exist_ok=True)
        save_path = os.path.join(team_knowledge_dir, f"latest_learning_{datetime.now().strftime('%Y%m%d')}.md")
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"\n💾 학습 결과 저장: {save_path}")

    return result


def learn_all_teams():
    """모든 팀의 학습 실행."""
    for team_folder in os.listdir(TEAMS_DIR):
        team_path = os.path.join(TEAMS_DIR, team_folder)
        if not os.path.isdir(team_path):
            continue
        mission = os.path.join(team_path, "mission.md")
        if os.path.exists(mission):
            topics = _parse_learning_topics(mission)
            if topics:
                print(f"\n{'='*60}")
                print(f"팀: {team_folder} ({len(topics)}개 학습 주제)")
                learn_before_run(team_folder)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법:")
        print('  python -m core.continuous_learning 온라인영업팀')
        print('  python -m core.continuous_learning all')
        sys.exit(1)

    target = sys.argv[1]
    if target == "all":
        learn_all_teams()
    else:
        learn_before_run(target)
