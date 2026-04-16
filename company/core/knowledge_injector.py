"""
knowledge_injector.py — 팀 실행 시 학습된 지식 자동 주입

사용법:
    from core.knowledge_injector import inject_team_knowledge, get_team_knowledge

    # 팀별 학습 지식 가져오기
    knowledge = get_team_knowledge("온라인납품팀", max_tokens=2000)

    # 기존 시스템 프롬프트에 주입
    full_prompt = inject_team_knowledge(system_prompt, "온라인납품팀")
"""

import os
from pathlib import Path

# 팀별 필요한 지식 카테고리 매핑
TEAM_KNOWLEDGE_MAP = {
    "온라인영업팀": ["영업전략", "카피패턴"],
    "온라인납품팀": ["카피패턴", "콘텐츠구조", "광고자동화"],
    "온라인마케팅팀": ["영업전략", "광고자동화", "콘텐츠구조"],
    "오프라인마케팅팀": ["영업전략", "카피패턴"],
    "이사팀": ["시스템설계"],
    "교육팀": ["시스템설계", "영업전략"],
}

# 팀별 마케팅 ops_templates 매핑 (자동 주입)
TEAM_MARKETING_TEMPLATES = {
    "온라인영업팀": ["콜드아웃리치", "카피라이팅"],
    "온라인납품팀": ["블로그_SEO_네이버", "카피라이팅", "EEAT_콘텐츠분석", "SEO_GEO_AEO"],
    "온라인마케팅팀": ["SNS_콘텐츠전략", "카피라이팅", "마케팅분석_성과추적"],
    "오프라인마케팅팀": ["콜드아웃리치", "카피라이팅", "CRO_페이지최적화"],
}

_KNOWLEDGE_BASE_DIR = Path(__file__).parent.parent / "knowledge" / "base"


def get_team_knowledge(team_name: str, max_tokens: int = 2000) -> str:
    """팀 관련 지식을 자동으로 수집해서 반환.

    Args:
        team_name: 팀 이름 (e.g. "온라인납품팀")
        max_tokens: 최대 토큰 수 (프롬프트 오버플로우 방지)

    Returns:
        구조화된 지식 텍스트. 없으면 빈 문자열.
    """
    if team_name not in TEAM_KNOWLEDGE_MAP:
        return ""

    categories = TEAM_KNOWLEDGE_MAP[team_name]
    knowledge_parts = []
    token_count = 0

    for category in categories:
        if token_count > max_tokens:
            break

        # 카테고리별 파일 찾기: insights_{카테고리}.md
        insight_file = _KNOWLEDGE_BASE_DIR / f"insights_{category}.md"

        if insight_file.exists():
            try:
                with open(insight_file, encoding="utf-8") as f:
                    content = f.read()

                # 토큰 수 제한 (대략 4글자 = 1토큰)
                remaining = max_tokens - token_count
                if len(content) > remaining * 4:
                    content = content[:remaining * 4] + "..."

                knowledge_parts.append(f"### [{category}]\n{content}")
                token_count += len(content) // 4
            except Exception as e:
                print(f"⚠️  {category} 지식 읽기 실패: {e}")

        # 팀 전용 결과물도 있으면 추가
        team_dir = _KNOWLEDGE_BASE_DIR / "teams" / team_name
        if team_dir.exists():
            try:
                for md_file in team_dir.glob("*.md"):
                    if token_count > max_tokens:
                        break
                    with open(md_file, encoding="utf-8") as f:
                        content = f.read()
                    remaining = max_tokens - token_count
                    if len(content) > remaining * 4:
                        content = content[:remaining * 4] + "..."
                    knowledge_parts.append(f"### [{md_file.stem}]\n{content}")
                    token_count += len(content) // 4
            except Exception:
                pass

    # 마케팅 ops_templates 지식 주입
    if team_name in TEAM_MARKETING_TEMPLATES:
        templates_dir = Path(__file__).parent.parent / "knowledge" / "ops_templates" / "marketing"
        for template_name in TEAM_MARKETING_TEMPLATES[team_name]:
            if token_count > max_tokens:
                break
            template_file = templates_dir / f"{template_name}.md"
            if template_file.exists():
                try:
                    with open(template_file, encoding="utf-8") as f:
                        content = f.read()
                    remaining = max_tokens - token_count
                    if len(content) > remaining * 4:
                        content = content[:remaining * 4] + "..."
                    knowledge_parts.append(f"### [마케팅:{template_name}]\n{content}")
                    token_count += len(content) // 4
                except Exception as e:
                    print(f"⚠️  마케팅 템플릿 읽기 실패 ({template_name}): {e}")

    if not knowledge_parts:
        return ""

    return "\n\n".join(knowledge_parts)


def inject_team_knowledge(system_prompt: str, team_name: str) -> str:
    """기존 시스템 프롬프트에 팀 관련 지식 주입.

    Args:
        system_prompt: 에이전트 고유 시스템 프롬프트
        team_name: 팀 이름 (없으면 지식 주입 안 함)

    Returns:
        지식이 포함된 전체 프롬프트. 지식이 없으면 원본 그대로.
    """
    if not team_name:
        return system_prompt

    knowledge = get_team_knowledge(team_name)

    if not knowledge:
        return system_prompt

    return f"""{system_prompt}

=== 학습된 지식 (최신 분석 결과 기반) ===
팀: {team_name}

{knowledge}

=== 지식 활용 지침 ===
위 지식은 지난 분석 결과에서 추출한 "바로 써먹을 수 있는 인사이트"입니다.
이 지식을 바탕으로 작업을 진행하되, 각 상황에 맞게 유연하게 적용하세요.
=== 끝 ===
"""
