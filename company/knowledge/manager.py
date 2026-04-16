"""
지식 관리 시스템 — 교육팀이 관장

역할:
- 팀 결과물을 지식으로 저장
- 리안 피드백 수집 + 저장
- 새 팀 만들 때 관련 지식 자동 추출
- 팀 간 지식 공유 (index.json 기반)
- 에이전트 → 리안 보고 (보고사항들.md)
"""
import os
import json
from datetime import datetime

REPORT_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "보고사항들.md"
)

KNOWLEDGE_DIR = os.path.dirname(__file__)
BASE_DIR = os.path.join(KNOWLEDGE_DIR, "base")
TEAMS_DIR = os.path.join(KNOWLEDGE_DIR, "teams")
INDEX_PATH = os.path.join(KNOWLEDGE_DIR, "index.json")


def _load_index() -> dict:
    try:
        with open(INDEX_PATH, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"base": {}, "team_results": {}, "feedback": {}}


def _save_index(index: dict):
    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)


# ── 지식 저장 ────────────────────────────────────────────────

def save_base_knowledge(filename: str, content: str, tags: list[str], useful_for: list[str], source: str = ""):
    """기본 지식 저장 (여러 팀이 공유 가능)."""
    path = os.path.join(BASE_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    index = _load_index()
    index["base"][filename] = {
        "tags": tags,
        "useful_for": useful_for,
        "source": source,
        "saved_at": datetime.now().isoformat(),
    }
    _save_index(index)
    print(f"[지식] 기본 지식 저장: {filename} (태그: {tags})")


def save_team_result(team_name: str, filename: str, content: str, tags: list[str] = None):
    """팀 결과물을 지식으로 저장."""
    team_dir = os.path.join(TEAMS_DIR, team_name, "results")
    os.makedirs(team_dir, exist_ok=True)
    path = os.path.join(team_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    index = _load_index()
    key = f"{team_name}/{filename}"
    index["team_results"][key] = {
        "tags": tags or [],
        "saved_at": datetime.now().isoformat(),
    }
    _save_index(index)
    print(f"[지식] 팀 결과 저장: {key}")


def save_feedback(team_name: str, content: str, result_file: str = ""):
    """리안 피드백 저장."""
    team_dir = os.path.join(TEAMS_DIR, team_name, "feedback")
    os.makedirs(team_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"feedback_{ts}.md"
    path = os.path.join(team_dir, filename)

    feedback_content = f"# 리안 피드백\n\n날짜: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    if result_file:
        feedback_content += f"대상: {result_file}\n"
    feedback_content += f"\n{content}\n"

    with open(path, "w", encoding="utf-8") as f:
        f.write(feedback_content)

    index = _load_index()
    key = f"{team_name}/{filename}"
    index["feedback"][key] = {
        "target": result_file,
        "saved_at": datetime.now().isoformat(),
    }
    _save_index(index)
    print(f"[피드백] 저장: {key}")


# ── 지식 검색 ────────────────────────────────────────────────

def get_knowledge_for_team(team_name: str, tags: list[str] = None) -> str:
    """특정 팀에 유용한 지식 전부 모아서 반환."""
    index = _load_index()
    knowledge_parts = []

    # 1. base에서 이 팀에 유용한 지식
    for filename, meta in index.get("base", {}).items():
        useful = meta.get("useful_for", [])
        file_tags = meta.get("tags", [])
        if team_name in useful or (tags and any(t in file_tags for t in tags)):
            path = os.path.join(BASE_DIR, filename)
            if os.path.exists(path):
                with open(path, encoding="utf-8") as f:
                    content = f.read()
                knowledge_parts.append(f"### [기본 지식] {filename}\n{content[:1500]}")

    # 2. 이 팀의 과거 결과물
    results_dir = os.path.join(TEAMS_DIR, team_name, "results")
    if os.path.exists(results_dir):
        for fname in os.listdir(results_dir):
            path = os.path.join(results_dir, fname)
            with open(path, encoding="utf-8") as f:
                content = f.read()
            knowledge_parts.append(f"### [과거 결과] {fname}\n{content[:1000]}")

    # 3. 이 팀의 피드백
    feedback_dir = os.path.join(TEAMS_DIR, team_name, "feedback")
    if os.path.exists(feedback_dir):
        for fname in sorted(os.listdir(feedback_dir)):
            path = os.path.join(feedback_dir, fname)
            with open(path, encoding="utf-8") as f:
                content = f.read()
            knowledge_parts.append(f"### [리안 피드백] {fname}\n{content[:500]}")

    # 4. 다른 팀 결과 중 태그가 겹치는 것
    if tags:
        for key, meta in index.get("team_results", {}).items():
            if key.startswith(team_name):
                continue
            result_tags = meta.get("tags", [])
            if any(t in result_tags for t in tags):
                team, fname = key.split("/", 1)
                path = os.path.join(TEAMS_DIR, team, "results", fname)
                if os.path.exists(path):
                    with open(path, encoding="utf-8") as f:
                        content = f.read()
                    knowledge_parts.append(f"### [다른 팀 참고] {key}\n{content[:800]}")

    return "\n\n".join(knowledge_parts) if knowledge_parts else ""


def share_knowledge(from_team: str, filename: str, to_teams: list[str]):
    """특정 팀의 지식을 다른 팀에도 유용하다고 태깅."""
    index = _load_index()
    key = f"{from_team}/{filename}"
    if key in index.get("team_results", {}):
        index["team_results"][key]["shared_to"] = to_teams
        _save_index(index)
        print(f"[공유] 지식 공유: {key} -> {to_teams}")


# ── 피드백 수집 ──────────────────────────────────────────────

def collect_feedback(team_name: str):
    """리안한테 직접 피드백 받기."""
    print(f"\n{'='*60}")
    print(f"📝 {team_name} 결과물 피드백")
    print(f"{'='*60}")
    print("리안, 이번 결과물 어땠어?")
    print("  - 뭐가 좋았어?")
    print("  - 뭐가 구렸어?")
    print("  - 다음에 바꿔야 할 거 있어?")
    print("  (없으면 엔터)")
    print("\n리안: ", end="")
    try:
        feedback = input().strip()
    except EOFError:
        feedback = ""

    if feedback:
        save_feedback(team_name, feedback)
        return feedback
    return ""


# ── 보고사항들.md ────────────────────────────────────────────

def write_report(agent_name: str, role: str, content: str):
    """에이전트 → 리안 보고. 보고사항들.md에 최신 항목이 위로 추가."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    section = f"## {agent_name} ({role}) — {now}\n\n{content.strip()}\n\n---\n\n"

    if os.path.exists(REPORT_FILE):
        with open(REPORT_FILE, encoding="utf-8") as f:
            existing = f.read()
        parts = existing.split("---\n", 1)
        if len(parts) == 2:
            result = parts[0] + "---\n\n" + section + parts[1]
        else:
            result = existing + "\n" + section
    else:
        header = (
            "# 보고사항들\n\n"
            "> 에이전트들이 리안한테 직접 보고하는 공간.\n"
            "> 리안이 읽고 지시사항 있으면 해당 에이전트한테 전달.\n\n"
            "---\n\n"
        )
        result = header + section

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(result)
    print(f"[보고] {agent_name} → 보고사항들.md 업데이트")


# ── 계층형 지식 접근 (Layer-based Knowledge Retrieval) ───────────

def save_client_layer(client_id: str, layer_name: str, data: dict):
    """클라이언트 데이터의 특정 레이어를 저장.

    Args:
        client_id: 고유 클라이언트 ID
        layer_name: 레이어 이름 ("raw", "entities", "analyses", "concepts")
        data: 저장할 데이터 (딕셔너리)
    """
    from knowledge.layers import validate_layer

    if not validate_layer(layer_name):
        raise ValueError(f"Invalid layer: {layer_name}")

    layers_dir = os.path.join(KNOWLEDGE_DIR, "layers", "data")
    client_dir = os.path.join(layers_dir, client_id)
    os.makedirs(client_dir, exist_ok=True)

    layer_file = os.path.join(client_dir, f"{layer_name}.json")
    with open(layer_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[레이어] {client_id}/{layer_name} 저장 완료")


def get_client_layers(client_id: str, layers: list[str]) -> dict:
    """특정 클라이언트의 특정 레이어들만 반환.

    Args:
        client_id: 고유 클라이언트 ID
        layers: 가져올 레이어 이름 리스트 (예: ["entities", "concepts"])

    Returns:
        {layer_name: layer_data} 딕셔너리
        없는 레이어는 빈 dict 반환
    """
    from knowledge.layers import validate_layer

    result = {}
    layers_dir = os.path.join(KNOWLEDGE_DIR, "layers", "data", client_id)

    if not os.path.exists(layers_dir):
        print(f"⚠️  클라이언트 데이터 없음: {client_id}")
        return result

    for layer_name in layers:
        if not validate_layer(layer_name):
            continue

        layer_file = os.path.join(layers_dir, f"{layer_name}.json")
        if os.path.exists(layer_file):
            try:
                with open(layer_file, encoding="utf-8") as f:
                    result[layer_name] = json.load(f)
            except Exception as e:
                print(f"⚠️  레이어 읽기 실패 ({layer_name}): {e}")
        else:
            result[layer_name] = {}

    return result


def format_layers_for_agent(layers_data: dict) -> str:
    """레이어 데이터를 에이전트 읽기 좋은 텍스트로 포맷팅.

    Args:
        layers_data: {layer_name: layer_data} 딕셔너리

    Returns:
        마크다운 형식의 포맷된 텍스트
    """
    if not layers_data:
        return "[클라이언트 데이터 없음]"

    parts = []
    layer_order = ["entities", "analyses", "concepts", "raw"]

    for layer_name in layer_order:
        if layer_name not in layers_data:
            continue

        data = layers_data[layer_name]
        if not data:
            continue

        parts.append(f"\n### {layer_name.upper()}\n")

        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, list):
                    parts.append(f"- **{key}**: {', '.join(str(v) for v in value)}")
                elif isinstance(value, dict):
                    parts.append(f"- **{key}**: {json.dumps(value, ensure_ascii=False, indent=2)}")
                else:
                    parts.append(f"- **{key}**: {value}")

    return "\n".join(parts) if parts else "[빈 데이터]"

