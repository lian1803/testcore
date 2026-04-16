import os
import re
import sys
import anthropic
from dotenv import load_dotenv
from teams.education import curriculum_designer, trainer, team_generator

# 상태 추적
try:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from utils.status_tracker import update_status, clear_status
    HAS_STATUS_TRACKER = True
except ImportError:
    HAS_STATUS_TRACKER = False

load_dotenv()

BASE_PATH = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))  # company/


def _slugify(name: str) -> str:
    name = name.strip().replace(" ", "_")
    return re.sub(r'[^\w가-힣]', '', name)


def get_client() -> anthropic.Anthropic:
    return anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def run(team_name: str, team_purpose: str):
    client = get_client()

    print(f"\n{'='*60}")
    print(f"🎓 교육팀 가동 — {team_name} 신설")
    print(f"{'='*60}")

    # Step 0: 기존 지식 확인
    print("\n[0/4] 기존 지식 확인...")
    try:
        from knowledge.manager import get_knowledge_for_team
        slug = _slugify(team_name)
        existing = get_knowledge_for_team(slug)
        if existing:
            print(f"  📚 관련 지식 {len(existing)}자 발견 → 교육에 반영")
        else:
            print("  📚 관련 지식 없음 → 처음부터 수집")
    except Exception:
        existing = ""

    # Step 1: Opus가 커리큘럼 설계
    print("\n[1/4] 커리큘럼 설계 (Claude Opus)...")
    if HAS_STATUS_TRACKER:
        update_status("curriculum_designer", "education", "running", "커리큘럼 설계 중")
    try:
        curriculum = curriculum_designer.run(team_name, team_purpose, client)
    finally:
        if HAS_STATUS_TRACKER:
            clear_status("curriculum_designer")

    # Step 2: Perplexity로 전문 지식 방대 수집
    print("\n[2/4] 전문 지식 수집 (Perplexity)...")
    if HAS_STATUS_TRACKER:
        update_status("trainer", "education", "running", "전문 지식 수집 중")
    try:
        agent_knowledge = trainer.run(curriculum)
    finally:
        if HAS_STATUS_TRACKER:
            clear_status("trainer")

    # 기존 지식이 있으면 각 에이전트에 추가
    if existing:
        for agent_name in agent_knowledge:
            agent_knowledge[agent_name] += f"\n\n=== 기존 축적 지식 ===\n{existing[:2000]}"

    # Step 3: 수집된 지식을 knowledge/base에 저장
    print("\n[3/4] 지식 저장...")
    try:
        from knowledge.manager import save_base_knowledge
        for agent_name, knowledge in agent_knowledge.items():
            tags = [_slugify(team_name), agent_name]
            save_base_knowledge(
                f"{_slugify(team_name)}_{agent_name}.md",
                knowledge,
                tags=tags,
                useful_for=[_slugify(team_name)],
                source=f"교육팀 수집 ({team_name})"
            )
    except Exception as e:
        print(f"  ⚠️ 지식 저장 실패 (계속 진행): {e}")

    # Step 4: 팀 파일 자동 생성
    print("\n[4/4] 팀 파일 생성...")
    if HAS_STATUS_TRACKER:
        update_status("team_generator", "education", "running", "팀 파일 생성 중")
    try:
        team_dir = team_generator.generate(curriculum, agent_knowledge, BASE_PATH)
    finally:
        if HAS_STATUS_TRACKER:
            clear_status("team_generator")

    return team_dir
