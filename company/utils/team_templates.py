"""
팀 템플릿 관리 시스템 — 기존 팀 저장 / 템플릿에서 새 팀 빠르게 생성

사용법:
  from utils.team_templates import export_team, import_team, list_templates, get_similar_template

  # 기존 팀을 템플릿으로 내보내기
  export_team("온라인영업팀")

  # 템플릿에서 새 팀 빠르게 생성
  import_team("온라인영업팀", "새로운영업팀")

  # 템플릿 목록 확인
  list_templates()

  # 비슷한 팀 템플릿 찾기
  get_similar_template("영업")
"""

import json
import os
import re
from pathlib import Path
from typing import Optional, List, Dict, Any
from shutil import copytree, ignore_patterns


TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
TEAMS_DIR = Path(__file__).parent.parent / "teams"


def _ensure_templates_dir() -> None:
    """templates 폴더 생성"""
    TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)


def _extract_agent_info(agent_file: Path) -> Dict[str, Any]:
    """에이전트 .py 파일에서 메타 정보 추출"""
    try:
        with open(agent_file, "r", encoding="utf-8") as f:
            content = f.read()

        # role, model 정보 추출 (주석이나 상수에서)
        role = None
        model = None

        # 주석에서 role 찾기 (예: "# 역할: 잠재고객 분석")
        role_match = re.search(r"#\s*역할\s*:\s*([^\n]+)", content)
        if role_match:
            role = role_match.group(1).strip()

        # 모델 정보 찾기 (예: "model='claude-opus'" or "claude-opus-4-1")
        model_match = re.search(r"model\s*=\s*['\"]([^'\"]+)['\"]", content)
        if model_match:
            model = model_match.group(1).strip()

        # system 프롬프트 추출 (처음 1000자)
        system_match = re.search(r'system\s*=\s*["\']([^"\']+)["\']', content)
        system_prompt = None
        if system_match:
            system_prompt = system_match.group(1).strip()[:500]

        return {
            "role": role,
            "model": model,
            "system_preview": system_prompt,
        }
    except Exception as e:
        print(f"⚠️ {agent_file} 파싱 실패: {e}")
        return {}


def _extract_pipeline_structure(pipeline_file: Path) -> Dict[str, Any]:
    """pipeline.py에서 구조 정보 추출"""
    try:
        with open(pipeline_file, "r", encoding="utf-8") as f:
            content = f.read()

        # import 라인에서 에이전트 이름 추출
        import_pattern = r"from teams\.\S+ import (.+)|from \. import (.+)"
        imports = re.findall(import_pattern, content)
        agent_names = []
        for imp in imports:
            agent_name = imp[0] or imp[1]
            if agent_name:
                agent_names.extend([a.strip() for a in agent_name.split(",")])

        # run() 함수의 에이전트 호출 순서 추출
        run_pattern = r"([가-힣\w]+)\.run\(|result_([가-힣\w]+)\s*="
        agent_calls = re.findall(run_pattern, content)

        return {
            "agents": agent_names,
            "call_order": agent_calls,
            "has_interview": "team_interview" in content,
            "has_self_critique": "self_critique" in content,
        }
    except Exception as e:
        print(f"⚠️ {pipeline_file} 파싱 실패: {e}")
        return {}


def export_team(team_name: str) -> str:
    """
    기존 팀을 JSON 템플릿으로 내보내기

    Args:
        team_name: 팀 이름 (예: "온라인영업팀")

    Returns:
        템플릿 파일 경로
    """
    _ensure_templates_dir()

    team_path = TEAMS_DIR / team_name
    if not team_path.exists():
        raise FileNotFoundError(f"팀 폴더를 찾을 수 없어: {team_path}")

    # 팀 구성 파악
    template_data = {
        "team_name": team_name,
        "created_at": __import__("datetime").datetime.now().isoformat(),
        "agents": [],
        "pipeline_structure": {},
    }

    # 에이전트 파일 스캔
    agent_files = list(team_path.glob("*.py"))
    for agent_file in agent_files:
        if agent_file.name in ("pipeline.py", "__init__.py", "run_*.py"):
            continue

        agent_name = agent_file.stem
        info = _extract_agent_info(agent_file)
        info["filename"] = agent_file.name

        with open(agent_file, "r", encoding="utf-8") as f:
            info["content_preview"] = f.read()[:2000]  # 처음 2000자만 저장

        template_data["agents"].append({
            "name": agent_name,
            "info": info,
        })

    # pipeline.py 구조 추출
    pipeline_file = team_path / "pipeline.py"
    if pipeline_file.exists():
        template_data["pipeline_structure"] = _extract_pipeline_structure(pipeline_file)
        with open(pipeline_file, "r", encoding="utf-8") as f:
            template_data["pipeline_code"] = f.read()

    # 템플릿 저장
    template_file = TEMPLATES_DIR / f"{team_name}.json"
    with open(template_file, "w", encoding="utf-8") as f:
        json.dump(template_data, f, ensure_ascii=False, indent=2)

    print(f"✅ 템플릿 저장 완료: {template_file}")
    return str(template_file)


def import_team(
    template_name: str,
    new_team_name: str,
    customize_callback: Optional[callable] = None,
) -> str:
    """
    JSON 템플릿에서 새 팀 빠르게 생성

    Args:
        template_name: 템플릿 이름 (예: "온라인영업팀" 또는 "온라인영업팀.json")
        new_team_name: 새 팀 이름
        customize_callback: 커스터마이징 함수 (선택)

    Returns:
        생성된 팀 폴더 경로
    """
    _ensure_templates_dir()

    # 템플릿 파일 찾기
    if template_name.endswith(".json"):
        template_file = TEMPLATES_DIR / template_name
    else:
        template_file = TEMPLATES_DIR / f"{template_name}.json"

    if not template_file.exists():
        raise FileNotFoundError(f"템플릿을 찾을 수 없어: {template_file}")

    # 템플릿 로드
    with open(template_file, "r", encoding="utf-8") as f:
        template_data = json.load(f)

    # 새 팀 폴더 생성
    new_team_path = TEAMS_DIR / new_team_name
    if new_team_path.exists():
        raise FileExistsError(f"팀 폴더가 이미 존재해: {new_team_path}")

    new_team_path.mkdir(parents=True, exist_ok=True)

    # 에이전트 파일들 생성
    agent_mapping = {}  # 이전 이름 -> 새 이름 매핑
    for agent_info in template_data.get("agents", []):
        old_name = agent_info["name"]
        # 새 팀 이름에 맞게 에이전트 이름 변환 (예: "박탐정" → "박탐정")
        # customize_callback이 있으면 사용, 아니면 그대로
        if customize_callback:
            new_name = customize_callback(old_name, new_team_name)
        else:
            new_name = old_name

        agent_mapping[old_name] = new_name

        # 에이전트 파일 생성
        agent_file = new_team_path / f"{new_name}.py"
        with open(agent_file, "w", encoding="utf-8") as f:
            # 전체 content가 있으면 사용, 없으면 preview만 사용
            content = agent_info["info"].get("content", "")
            if not content and "content_preview" in agent_info["info"]:
                content = agent_info["info"]["content_preview"]
                content += "\n\n# [템플릿에서 생성됨 — 상단 주석만 포함]\n"

            f.write(content)

    # pipeline.py 생성/복사
    pipeline_code = template_data.get("pipeline_code", "")
    if pipeline_code:
        # 에이전트 이름 변환
        for old_name, new_name in agent_mapping.items():
            pipeline_code = re.sub(
                rf"\b{old_name}\b",
                new_name,
                pipeline_code
            )
            pipeline_code = re.sub(
                rf"from teams\.[^\s]+ import {old_name}",
                f"from teams.{new_team_name} import {new_name}",
                pipeline_code
            )

        # 팀 이름 변환
        pipeline_code = re.sub(
            r"온라인영업팀|온라인납품팀|온라인마케팅팀",
            new_team_name,
            pipeline_code
        )

        pipeline_file = new_team_path / "pipeline.py"
        with open(pipeline_file, "w", encoding="utf-8") as f:
            f.write(pipeline_code)

    # run_{팀명}.py 생성
    run_file = Path(__file__).parent.parent / f"run_{new_team_name}.py"
    run_template = f'''#!/usr/bin/env python3
"""
{new_team_name} 실행 스크립트

사용법:
  python run_{new_team_name}.py "작업"
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from teams.{new_team_name}.pipeline import run

if __name__ == "__main__":
    if len(sys.argv) > 1:
        task = " ".join(sys.argv[1:])
    else:
        print("{new_team_name} 작업:")
        task = input("> ").strip()

    run(task)
'''

    with open(run_file, "w", encoding="utf-8") as f:
        f.write(run_template)

    print(f"✅ 팀 생성 완료: {new_team_path}")
    print(f"   에이전트: {', '.join(agent_mapping.values())}")
    print(f"   실행: python run_{new_team_name}.py \"작업\"")

    return str(new_team_path)


def list_templates() -> List[str]:
    """사용 가능한 템플릿 목록 반환"""
    _ensure_templates_dir()

    templates = []
    for template_file in TEMPLATES_DIR.glob("*.json"):
        try:
            with open(template_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                template_name = template_file.stem
                agent_count = len(data.get("agents", []))
                templates.append({
                    "name": template_name,
                    "agent_count": agent_count,
                    "created_at": data.get("created_at", "—"),
                })
        except json.JSONDecodeError:
            pass

    return templates


def get_similar_template(keyword: str) -> Optional[str]:
    """
    키워드와 비슷한 템플릿 찾기

    Args:
        keyword: 검색 키워드 (예: "영업", "납품", "마케팅")

    Returns:
        가장 비슷한 템플릿 이름, 없으면 None
    """
    templates = list_templates()
    keyword_lower = keyword.lower()

    for template in templates:
        if keyword_lower in template["name"].lower():
            return template["name"]

    return None


def print_templates() -> None:
    """템플릿 목록을 보기 좋게 출력"""
    templates = list_templates()

    if not templates:
        print("📦 사용 가능한 템플릿이 없어. 먼저 export_team()으로 템플릿을 만들어줘.")
        return

    print("\n" + "="*60)
    print("📦 사용 가능한 팀 템플릿")
    print("="*60)

    for template in templates:
        print(f"\n  📋 {template['name']}")
        print(f"     에이전트: {template['agent_count']}명")
        print(f"     생성일: {template['created_at']}")

    print("\n" + "="*60 + "\n")
