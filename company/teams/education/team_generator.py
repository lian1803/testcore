import os
from core.pipeline_utils import summarize_context
import re

AGENT_TEMPLATE = '''import os
import sys
import anthropic
from core.pipeline_utils import summarize_context

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """{system_prompt}"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\\n" + "="*60)
    print("{print_label}")
    print("="*60)

    # 런타임 지식 로드
    try:
        from core.context_loader import get_team_system_prompt
        full_prompt = get_team_system_prompt(SYSTEM_PROMPT, "{team_slug}")
    except Exception:
        full_prompt = SYSTEM_PROMPT

    user_msg = {user_msg_code}

    full_response = ""
    with client.messages.stream(
        model=MODEL,
        max_tokens=3000,
        messages=[{{"role": "user", "content": user_msg}}],
        system=full_prompt,
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
            full_response += text

    print()
    return full_response
'''

INTERVIEW_PROMPT = "너는 {team_name}의 팀 리더야. 리안(CEO, 비개발자)한테 실제 업무를 파악해야 해. 구체적이고 실용적인 질문 3~5개를 한번에 물어봐. 짧고 친근하게."

PIPELINE_TEMPLATE = '''import os
import anthropic
from dotenv import load_dotenv
{agent_imports}

load_dotenv()

OUTPUT_BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "team")

def get_client() -> anthropic.Anthropic:
    return anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def save(output_dir: str, filename: str, content: str):
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"\\n💾 저장: {{path}}")

def team_interview(task: str, client: anthropic.Anthropic) -> str:
    """팀 시작 전 리안한테 디테일 인터뷰."""
    print("\\n" + "="*60)
    print("🎤 팀 인터뷰 | 리안한테 디테일 파악")
    print("="*60)

    interview_prompt = "{interview_prompt}"

    resp = ""
    with client.messages.stream(
        model="claude-sonnet-4-5",
        max_tokens=400,
        system=interview_prompt,
        messages=[{{"role": "user", "content": f"업무: {{task}}"}}],
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
            resp += text

    print("\\n\\n리안: ", end="")
    try:
        answer = input().strip()
    except EOFError:
        answer = ""

    return f"리안 답변:\\n{{answer}}"

def run(task: str = ""):
    client = get_client()
    context = {{"task": task}}

    print(f"\\n{{'='*60}}")
    print(f"🏢 {team_display_name} 가동")
    print(f"업무: {{task}}")
    print(f"{{'='*60}}")

    output_dir = os.path.join(OUTPUT_BASE, "{team_folder}")

    # 미션 로드
    mission_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mission.md")
    try:
        with open(mission_path, encoding="utf-8") as f:
            context["mission"] = f.read()
        print(f"\\n📋 미션 로드 완료")
    except FileNotFoundError:
        context["mission"] = ""

    # 학습 (Perplexity로 최신 자료 수집)
    try:
        import sys as _sys
        _sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        from core.continuous_learning import learn_before_run
        fresh_knowledge = learn_before_run("{team_slug}")
        if fresh_knowledge:
            context["fresh_knowledge"] = fresh_knowledge
    except Exception as e:
        print(f"\\n⚠️ 학습 스킵: {{e}}")

    # 팀 인터뷰 (리안한테 디테일 파악)
    interview = team_interview(task, client)
    context["interview"] = interview
    save(output_dir, "00_팀인터뷰.md", interview)

{pipeline_steps}

    # 결과물을 지식으로 저장 + 리안 피드백 수집
    try:
        import sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        from knowledge.manager import save_team_result, collect_feedback
        for key, val in context.items():
            if key not in ("task", "interview") and isinstance(val, str) and len(val) > 100:
                save_team_result("{team_slug}", f"{{key}}.md", val)
        collect_feedback("{team_slug}")
    except Exception as e:
        print(f"\\n⚠️ 지식 저장/피드백 수집 실패: {{e}}")

    print(f"\\n{{'='*60}}")
    print("✅ 완료")
    print(f"저장 위치: {{output_dir}}")
    print(f"{{'='*60}}")
    return context
'''

def _slugify(name: str) -> str:
    name = name.strip().replace(" ", "_")
    return re.sub(r'[^\w가-힣]', '', name)

def generate(curriculum: dict, agent_knowledge: dict, base_path: str):
    team_name = curriculum.get("team_name", "new_team")
    slug = _slugify(team_name)
    team_dir = os.path.join(base_path, "teams", slug)
    os.makedirs(team_dir, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"⚙️  팀 생성 | {team_name}")
    print(f"경로: {team_dir}")
    print("="*60)

    # __init__.py
    with open(os.path.join(team_dir, "__init__.py"), "w") as f:
        f.write("")

    agents = curriculum.get("agents", [])
    agent_module_names = []

    for agent in agents:
        name = agent["name"]
        role = agent.get("role", "")
        specialty = agent.get("specialty", "")
        principles = agent.get("core_principles", [])
        output_fmt = agent.get("output_format", "")
        knowledge = agent_knowledge.get(name, "")
        module_name = _slugify(name).lower()

        # Phase 5: 지식을 SYSTEM_PROMPT에 넣지 않고 별도 파일로 저장
        if knowledge:
            knowledge_dir = os.path.join(base_path, "knowledge", "teams", slug)
            os.makedirs(knowledge_dir, exist_ok=True)
            knowledge_path = os.path.join(knowledge_dir, f"{module_name}_지식.md")
            with open(knowledge_path, "w", encoding="utf-8") as kf:
                kf.write(knowledge)
            print(f"  📚 {name} 지식 저장: {knowledge_path}")
        agent_module_names.append((module_name, name))

        # 검증자 역할인지 감지
        is_validator = "검증" in role or "validator" in module_name.lower()

        # 시스템 프롬프트 구성
        principles_text = "\n".join(f"- {p}" for p in principles)

        # 검증자라면 검증 원칙 블록 자동 추가
        validator_context = ""
        if is_validator:
            validator_context = f"""[검증 원칙 — 변경 불가]
- 이 팀의 현재 제약을 먼저 확인하고, 그 안에서의 최선을 검증한다
- "조건을 먼저 바꿔라"류 결론은 출력하지 않는다
- 출력 형식: 가능여부(YES/조건부YES/NO) + 리스크 + 현재 조건에서 보완점 (이 세 가지 필수)

"""

        system_prompt = f"""너는 {name}이야. {team_name}의 {role}.
전문 분야: {specialty}

{validator_context}핵심 원칙:
{principles_text}

결과물: {output_fmt}

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

        # user_msg 코드 생성
        user_msg_code = 'f"""업무: {context[\'task\']}\\n\\n이전 결과:\\n{summarize_context(context)}"""'

        agent_code = AGENT_TEMPLATE.format(
            system_prompt=system_prompt.replace('"""', "'''"),
            print_label=f"🤖 {name} | {role}",
            user_msg_code=user_msg_code,
            team_slug=slug,
        )

        agent_path = os.path.join(team_dir, f"{module_name}.py")
        with open(agent_path, "w", encoding="utf-8") as f:
            f.write(agent_code)
        print(f"  ✅ {name} ({module_name}.py)")

    # pipeline.py 생성
    imports = "\n".join(
        f"from teams.{slug} import {mod}" for mod, _ in agent_module_names
    )

    steps = []
    for i, (mod, name) in enumerate(agent_module_names, 1):
        steps.append(f'    print("\\n[{i}/{len(agent_module_names)}] {name}...")')
        steps.append(f'    result_{mod} = {mod}.run(context, client)')
        steps.append(f'    context["{mod}"] = result_{mod}')
        # 파일명에서 괄호/슬래시 제거 (Windows 경로 호환)
        safe_name = name.replace("(", "").replace(")", "").replace("/", "_").replace(" ", "_").strip("_")
        steps.append(f'    save(output_dir, "{safe_name}_결과.md", result_{mod})')
        steps.append("")

    interview_prompt_str = INTERVIEW_PROMPT.format(team_name=team_name)
    pipeline_code = PIPELINE_TEMPLATE.format(
        agent_imports=imports,
        team_display_name=team_name,
        team_folder=team_name.replace("/", "_").replace("\\", "_"),
        team_slug=slug,
        pipeline_steps="\n".join(steps),
        interview_prompt=interview_prompt_str,
    )

    with open(os.path.join(team_dir, "pipeline.py"), "w", encoding="utf-8") as f:
        f.write(pipeline_code)
    print(f"  ✅ pipeline.py")

    # 실행 파일 생성 (base_path 루트에)
    runner_name = f"run_{slug}.py"
    runner_code = f'''#!/usr/bin/env python3
"""
{team_name} 실행

사용법:
  python {runner_name}
  python {runner_name} "업무 내용"
"""
import sys, os, io
sys.path.insert(0, os.path.dirname(__file__))
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from dotenv import load_dotenv
load_dotenv()
from teams.{slug}.pipeline import run

if __name__ == "__main__":
    task = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else ""
    if not task:
        print("업무 내용 입력:")
        task = input("> ").strip()
    run(task)
'''
    runner_path = os.path.join(base_path, runner_name)
    with open(runner_path, "w", encoding="utf-8") as f:
        f.write(runner_code)
    print(f"  ✅ {runner_name} (실행 파일)")

    print(f"\n팀 생성 완료: {team_dir}")
    print(f"실행: python {runner_name} \"업무 내용\"")

    # mission.md 자동 생성 (팀 목표 설정 — 없으면 붕뜸)
    _generate_mission(team_name, slug, team_dir, curriculum)

    # 조직도 자동 업데이트
    _update_org_chart(team_name, agents)

    # .claude/agents/ 파일 자동 생성
    _generate_claude_agents(team_name, slug, agents, base_path)

    return team_dir

def _generate_mission(team_name: str, slug: str, team_dir: str, curriculum: dict):
    """팀 목표(mission.md) 자동 생성 — 없으면 팀이 방향 없이 붕뜸."""
    mission_path = os.path.join(team_dir, "mission.md")
    if os.path.exists(mission_path):
        return  # 이미 있으면 스킵

    purpose = curriculum.get("team_purpose", curriculum.get("goal", ""))
    agents = curriculum.get("agents", [])
    agent_list = "\n".join(f"- {a['name']}: {a.get('role', '')}" for a in agents)

    mission_content = f"""# {team_name} — 우리는 {purpose[:30] if purpose else team_name}에 특화된 전문 회사다

## 존재 이유 (단 하나의 Pain)
{purpose if purpose else f"이 팀이 해결하는 핵심 Pain을 여기에 명시하라."}

## 우리 팀이 하는 일 (딱 하나)
> [팀 생성 후 이 줄을 한 줄로 채워라: "A → B → C → 결과"]

## 팀 구성
{agent_list}

## 핵심 KPI
1. [KPI 1: 측정 가능한 수치]
2. [KPI 2: 측정 가능한 수치]
3. [KPI 3: 측정 가능한 수치]

## 자기 평가 기준
매 실행 후: "이 결과물로 리안이 실제로 돈을 벌 수 있는가?"
8점 미만이면 세계 최고 자료 다시 수집 후 재작성.

## 절대 금지
- 두루뭉술한 결과물
- "이럴 수도 있고 저럴 수도 있어요" 식 조언
- 리안이 읽어서 바로 실행 불가능한 내용

## 피벗 트리거
3회 연속 KPI 미달 → 더 좁히거나 방향 바꿔라.
범용화 금지. 좁힐수록 전문성이 생긴다.

## 학습 주제 (매 실행 전 Perplexity로 자동 수집)
### 한국어
- "{purpose if purpose else team_name} 성공 사례 레퍼런스 2025 2026"
- "{purpose if purpose else team_name} 전문가 노하우 실전 적용 방법"
- "{purpose if purpose else team_name} 최신 트렌드 베스트 프랙티스"
### English
- "{purpose if purpose else team_name} best practices case study 2025 2026"
- "{purpose if purpose else team_name} expert techniques real world application"
"""
    with open(mission_path, "w", encoding="utf-8") as f:
        f.write(mission_content)
    print(f"  ✅ mission.md (팀 목표 설정)")

def _generate_claude_agents(team_name: str, slug: str, agents: list, base_path: str):
    """각 에이전트용 .claude/agents/{name}.md 생성."""
    # LIANCP 루트 = base_path의 부모 (company의 부모)
    liancp_root = os.path.dirname(os.path.dirname(base_path))
    agents_dir = os.path.join(liancp_root, ".claude", "agents")
    os.makedirs(agents_dir, exist_ok=True)

    for agent in agents:
        name = agent.get("name", "")
        role = agent.get("role", "")
        specialty = agent.get("specialty", "")
        principles = agent.get("core_principles", [])
        output_fmt = agent.get("output_format", "")
        module_name = _slugify(name).lower()

        principles_text = "\n".join(f"- {p}" for p in principles)

        md_content = f"""---
name: {name}
model: sonnet
description: {name} — {team_name}의 {role}. {specialty}
---

# {name} — {role}

## 팀
{team_name}

## 전문 분야
{specialty}

## 핵심 원칙
{principles_text}

## 결과물 형식
{output_fmt}

## 작동 방식
이 에이전트는 `company/teams/{slug}/{module_name}.py`로 구현되어 있어.
팀 파이프라인에서 자동으로 호출되며, 컨텍스트를 받아서 결과를 반환한다.

## 규칙
- 두루뭉술한 조언 금지
- 이론만 나열 금지
- 항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로
"""

        agent_md_path = os.path.join(agents_dir, f"{module_name}.md")
        with open(agent_md_path, "w", encoding="utf-8") as f:
            f.write(md_content)
        print(f"  .claude/agents/{module_name}.md 생성")

def _update_org_chart(team_name: str, agents: list):
    """회사 조직도.md에 새 팀 자동 추가."""
    org_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
        "회사 조직도.md"
    )
    if not os.path.exists(org_path):
        return

    try:
        with open(org_path, encoding="utf-8") as f:
            content = f.read()

        # 이미 이 팀이 있으면 스킵
        if team_name in content:
            return

        # 팀 섹션 생성
        from datetime import date
        team_section = f"\n\n## {team_name}\n\n"
        team_section += f"> 교육팀이 자동 생성 ({date.today()})\n\n"
        team_section += "| 이름 | AI | 하는 일 |\n|------|-----|--------|\n"
        names = []
        for agent in agents:
            name = agent.get("name", "")
            role = agent.get("role", "")
            specialty = agent.get("specialty", "")
            team_section += f"| **{name}** | Claude Sonnet | {role}. {specialty} |\n"
            names.append(name)

        # 전체 인원 테이블 업데이트 — 변경 이력 앞에 팀 섹션 삽입
        if "## 변경 이력" in content:
            content = content.replace(
                "## 변경 이력",
                f"{team_section}\n---\n\n## 변경 이력"
            )
        else:
            content += team_section

        # 변경 이력에 추가
        today = date.today().strftime("%Y-%m-%d")
        history_line = f"| {today} | {team_name} 신설 ({', '.join(names)} 입사) |"
        if "## 변경 이력" in content and "| 날짜 | 변경 |" in content:
            content = content.rstrip() + f"\n{history_line}\n"

        with open(org_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  조직도 업데이트 완료")
    except Exception as e:
        print(f"  조직도 업데이트 실패: {e}")
