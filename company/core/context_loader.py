"""
context_loader.py — 모든 에이전트에 회사 DNA + 팀 지식 자동 주입

사용법:
    from core.context_loader import get_company_context, inject_context

    # 회사 DNA 텍스트 가져오기
    context = get_company_context()

    # 시스템 프롬프트에 회사 DNA 주입
    full_prompt = inject_context(my_system_prompt)

    # 팀 지식까지 포함해서 주입 (선택)
    full_prompt = inject_context(my_system_prompt, team_name="온라인납품팀")
"""
import os

_CONTEXT_CACHE = None
_COMPANY_CONTEXT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "company_context.md")

# 파이프라인 캐시 통합
try:
    from core.cache import get_pipeline_cache
    _pipeline_cache = get_pipeline_cache()
    HAS_PIPELINE_CACHE = True
except ImportError:
    HAS_PIPELINE_CACHE = False
    _pipeline_cache = None


def get_company_context() -> str:
    """회사 핵심 컨텍스트 반환 (경량화). 파이프라인 캐시 사용 (있으면)."""
    # 파이프라인 캐시가 있으면 그것부터 확인
    if HAS_PIPELINE_CACHE:
        cached = _pipeline_cache.get("company_context")
        if cached is not None:
            return cached

    # 그 다음 전역 캐시 확인
    global _CONTEXT_CACHE
    if _CONTEXT_CACHE is not None:
        if HAS_PIPELINE_CACHE:
            _pipeline_cache.set("company_context", _CONTEXT_CACHE)
        return _CONTEXT_CACHE

    # 경량화: 전체 company_context.md 대신 핵심만 주입
    _CONTEXT_CACHE = """리안 컴퍼니: 온·오프라인 마케팅 대행 + AI SaaS
CEO 리안: 마케팅 전문가, 비개발자. "돈이 되냐"가 기준.
원칙: 실행>완벽, 데이터기반, 자동화우선
타겟: 소상공인(뷰티/카페), 스마트스토어 셀러
패키지: 주목(29만), 집중(49만), 시선(89만)"""

    # 파이프라인 캐시에도 저장
    if HAS_PIPELINE_CACHE:
        _pipeline_cache.set("company_context", _CONTEXT_CACHE)

    return _CONTEXT_CACHE


def inject_context(system_prompt: str, team_name: str = None) -> str:
    """시스템 프롬프트에 회사 DNA + 팀 지식을 주입한다.

    Args:
        system_prompt: 에이전트 고유 시스템 프롬프트
        team_name: (선택) 팀 이름. 있으면 팀 관련 학습 지식도 함께 주입

    Returns:
        회사 DNA + (팀 지식) + 원래 프롬프트가 합쳐진 전체 프롬프트
    """
    company = get_company_context()
    result = f"""=== 회사 컨텍스트 (모든 업무의 기반) ===
{company}
=== 끝 ===

{system_prompt}"""

    # 팀 지식 주입 (선택적)
    if team_name:
        try:
            from core.knowledge_injector import get_team_knowledge
            knowledge = get_team_knowledge(team_name, max_tokens=1500)
            if knowledge:
                result += f"""

=== 학습된 지식 ({team_name} 팀) ===
{knowledge}
=== 끝 ===
"""
        except Exception as e:
            print(f"⚠️  팀 지식 주입 실패 ({team_name}): {e}")

    return result


def reset_cache():
    """캐시 초기화 (company_context.md 수정 후 다시 읽을 때)."""
    global _CONTEXT_CACHE
    _CONTEXT_CACHE = None


def get_team_system_prompt(base_prompt: str, team_name: str = None) -> str:
    """팀 에이전트용 시스템 프롬프트 생성.

    기존 SYSTEM_PROMPT에 팀 지식을 자동으로 주입합니다.

    Args:
        base_prompt: 에이전트의 기본 시스템 프롬프트 (SYSTEM_PROMPT)
        team_name: 팀 이름 (예: "온라인납품팀")

    Returns:
        팀 지식이 포함된 전체 시스템 프롬프트

    사용법:
        from core.context_loader import get_team_system_prompt

        def run(context: dict, client):
            system_prompt = get_team_system_prompt(SYSTEM_PROMPT, "온라인납품팀")
            client.messages.stream(
                model=MODEL,
                messages=[...],
                system=system_prompt,
            )
    """
    if not team_name:
        return base_prompt

    try:
        from core.knowledge_injector import get_team_knowledge
        knowledge = get_team_knowledge(team_name, max_tokens=1200)
        if knowledge:
            return f"""{base_prompt}

=== 팀 학습 지식 (최신 분석 결과 기반) ===
{knowledge}
==="""
    except Exception as e:
        print(f"⚠️  팀 지식 주입 실패 ({team_name}): {e}")

    return base_prompt


def get_design_trends(days: int = 3) -> str:
    """최근 N일치 디자인 트렌드 반환 (Awwwards SOTD 분석 결과).

    Args:
        days: 최근 몇 일치를 가져올지 (기본값 3)

    Returns:
        디자인 트렌드 마크다운 문서 문자열. 없으면 빈 문자열.

    사용법:
        from core.context_loader import get_design_trends

        trends = get_design_trends(days=7)
        if trends:
            full_prompt = f"{system_prompt}\n\n{trends}"
    """
    from pathlib import Path

    trends_dir = Path(__file__).parent.parent / "knowledge" / "base" / "design" / "trends"

    if not trends_dir.exists():
        return ""

    # 최신 파일부터 역순 정렬
    files = sorted(trends_dir.glob("*.md"), reverse=True)[:days]

    if not files:
        return ""

    try:
        content_parts = []
        for f in files:
            content = f.read_text(encoding='utf-8')
            content_parts.append(content)

        combined = "\n\n".join(content_parts)
        return f"\n\n## 최근 디자인 트렌드 (Awwwards SOTD)\n\n{combined}"
    except Exception as e:
        print(f"⚠️  디자인 트렌드 로드 실패: {e}")
        return ""


# ── 계층형 지식 주입 (Layer-based Context Injection) ─────────────

def load_context_for_agent(agent_role: str, client_id: str = None) -> str:
    """에이전트 역할에 필요한 레이어만 포함한 클라이언트 컨텍스트 반환.

    Args:
        agent_role: 에이전트 역할 (예: "pdf_generator", "dm_writer", "strategist")
        client_id: 고유 클라이언트 ID. None이면 빈 문자열 반환.

    Returns:
        마크다운 형식의 클라이언트 컨텍스트 (필요한 레이어만 포함)

    사용법:
        from core.context_loader import load_context_for_agent

        # PDF 생성자가 필요한 레이어만 받기 (entities + analyses + concepts)
        client_context = load_context_for_agent("pdf_generator", client_id="client_123")

        # DM 작성자는 entities + concepts만 받기
        dm_context = load_context_for_agent("dm_writer", client_id="client_123")

        # 전체 프롬프트에 추가
        full_prompt = f"{system_prompt}\n\n{client_context}"
    """
    if not client_id:
        return ""

    try:
        from knowledge.layers import get_layers_for_role
        from knowledge.manager import get_client_layers, format_layers_for_agent

        # 1. 에이전트 역할에 맞는 레이어 확인
        required_layers = get_layers_for_role(agent_role)

        # 2. 클라이언트 데이터 로드 (필요한 레이어만)
        layers_data = get_client_layers(client_id, required_layers)

        # 3. 에이전트가 읽기 좋은 형식으로 포맷팅
        formatted = format_layers_for_agent(layers_data)

        return f"\n\n=== 클라이언트 데이터 (역할: {agent_role}) ===\n{formatted}\n==="

    except Exception as e:
        print(f"⚠️  계층형 컨텍스트 로드 실패 ({agent_role}, {client_id}): {e}")
        return ""


# ── 기획문서 로더 (Phase 1) ────────────────────────────────────────
# 이사팀이 생성한 기획 산출물을 실행팀 에이전트가 역할에 맞게 읽도록 한다.
# handoff.py ROLE_REQUIRED_FILES와 동기화 필수.

_PLANNING_ROLE_FILES = {
    "fe":        ["05_PRD_지훈.md", "02c_비즈니스모델_설계자.md"],
    "be":        ["05_PRD_지훈.md", "02c_비즈니스모델_설계자.md"],
    "cto":       ["05_PRD_지훈.md", "02b_전략브리프_설계자.md"],
    "marketing": ["02c_비즈니스모델_설계자.md", "01_시장조사_서윤.md"],
    "sales":     ["02c_비즈니스모델_설계자.md", "01_시장조사_서윤.md"],
    "qa":        ["05_PRD_지훈.md", "03_검증_하은.md"],
}


def load_planning_docs(project_dir: str, role: str = None, max_chars: int = 30000) -> str:
    """team/{프로젝트}/기획문서/ 에서 역할에 필요한 파일 로드.

    Args:
        project_dir: team/{프로젝트명}/ 경로 (절대 or 상대)
        role: 역할 키 (fe, be, cto, marketing, sales, qa). None이면 INDEX.md만 반환.
        max_chars: 합쳐진 내용 최대 길이 (토큰 보호)

    Returns:
        마크다운 형식으로 합쳐진 기획 문서. 없으면 빈 문자열.

    사용법:
        from core.context_loader import load_planning_docs

        docs = load_planning_docs(
            project_dir="team/토지분석_시스템",
            role="marketing",
        )
        full_prompt = f"{system_prompt}\\n\\n{docs}"
    """
    from pathlib import Path

    planning_dir = Path(project_dir) / "기획문서"
    if not planning_dir.exists():
        return ""

    # 역할 지정 없으면 INDEX.md만
    if not role:
        index_path = planning_dir / "INDEX.md"
        if index_path.exists():
            return index_path.read_text(encoding="utf-8")
        return ""

    role_key = role.lower().strip()
    target_files = _PLANNING_ROLE_FILES.get(role_key)
    if not target_files:
        # 알 수 없는 역할 → INDEX.md만 반환
        index_path = planning_dir / "INDEX.md"
        if index_path.exists():
            return index_path.read_text(encoding="utf-8")
        return ""

    # 필독 파일 로드
    contents = []
    total_len = 0
    for fname in target_files:
        fpath = planning_dir / fname
        if not fpath.exists():
            continue
        text = fpath.read_text(encoding="utf-8")
        section = f"## {fname}\n\n{text}"
        if total_len + len(section) > max_chars:
            # 초과분 잘라서 마지막 추가
            remaining = max_chars - total_len
            if remaining > 500:
                contents.append(section[:remaining] + "\n\n...(잘림)")
            break
        contents.append(section)
        total_len += len(section)

    if not contents:
        return ""

    header = f"=== 기획문서 (역할: {role_key}) ===\n\n"
    footer = "\n\n=== 기획문서 끝 ==="
    return header + "\n\n---\n\n".join(contents) + footer


def inject_planning_context(system_prompt: str, project_dir: str, role: str = None) -> str:
    """시스템 프롬프트에 기획 문서 주입.

    사용법:
        from core.context_loader import inject_planning_context

        full_prompt = inject_planning_context(
            system_prompt=SYSTEM_PROMPT,
            project_dir="team/토지분석_시스템",
            role="marketing",
        )
    """
    docs = load_planning_docs(project_dir, role=role)
    if not docs:
        return system_prompt

    return f"{system_prompt}\n\n{docs}"


def load_planning_summary(project_dir: str) -> str:
    """team/{프로젝트}/기획문서/INDEX.md 의 요약 블록 로드.

    4 도메인 × 3 역할 실측 결과 최선 방식:
    - 품질 2배 (29% → 58%)
    - 토큰 1/4 절감
    - 역할 구분 없이 전체 기획 요약 INDEX 하나만 박음

    Args:
        project_dir: team/{프로젝트명}/ 경로

    Returns:
        INDEX.md 내용 문자열. 없으면 빈 문자열.

    사용법:
        from core.context_loader import load_planning_summary
        summary = load_planning_summary("team/토지분석_시스템")
        full_prompt = f"{system_prompt}\\n\\n{summary}"
    """
    from pathlib import Path

    index_path = Path(project_dir) / "기획문서" / "INDEX.md"
    if not index_path.exists():
        return ""
    return index_path.read_text(encoding="utf-8")


def inject_planning_summary(system_prompt: str, project_dir: str) -> str:
    """시스템 프롬프트에 기획문서 INDEX(요약) 주입.

    실측 기반 권장 방식. 모든 실행팀 에이전트가 이걸 사용.

    사용법:
        full_prompt = inject_planning_summary(SYSTEM_PROMPT, "team/토지분석_시스템")
    """
    summary = load_planning_summary(project_dir)
    if not summary:
        return system_prompt
    return f"{system_prompt}\n\n=== 기획문서 요약 INDEX (단일 진실 공급원) ===\n\n{summary}"


def inject_layer_context(system_prompt: str, agent_role: str, client_id: str = None) -> str:
    """시스템 프롬프트에 계층형 클라이언트 데이터를 주입.

    Args:
        system_prompt: 에이전트 고유 시스템 프롬프트
        agent_role: 에이전트 역할
        client_id: 클라이언트 ID (선택, None이면 주입 안 함)

    Returns:
        회사 DNA + 클라이언트 데이터 + 원래 프롬프트가 합쳐진 전체 프롬프트

    사용법:
        from core.context_loader import inject_layer_context

        full_prompt = inject_layer_context(
            system_prompt=SYSTEM_PROMPT,
            agent_role="pdf_generator",
            client_id="client_123"
        )

        client.messages.create(
            model="claude-opus",
            system=full_prompt,
            messages=[...]
        )
    """
    company = get_company_context()
    result = f"""=== 회사 컨텍스트 (모든 업무의 기반) ===
{company}
=== 끝 ===

{system_prompt}"""

    # 클라이언트 데이터 주입 (선택적)
    if client_id:
        client_context = load_context_for_agent(agent_role, client_id)
        if client_context:
            result += client_context

    return result
