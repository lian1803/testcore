"""
planning_summarizer.py — 이사팀 기획 산출물 자동 요약기.

목적:
    실행팀 에이전트가 전체 기획 문서를 "한 글자씩 다 읽지는 않지만 최소한 각 파일 뭔지+핵심"
    파악할 수 있도록, 각 md 파일을 고정 템플릿으로 4~6줄 요약.

사용법:
    from core.planning_summarizer import summarize_planning_dir

    summaries = summarize_planning_dir(
        outputs_dir="company/outputs/2026-04-13_xxx",
        client=anthropic_client,
    )
    # → dict: {filename: {"핵심결론": str, "타겟": str, "숫자": str, "팀전달포인트": str}}

    # INDEX.md 블록 생성
    index_block = format_summaries_as_index(summaries)
"""
from pathlib import Path
import json
import re

SUMMARIZE_MODEL = "claude-sonnet-4-5-20250929"

SUMMARIZE_SYSTEM = """너는 이사팀 기획 산출물을 실행팀이 빠르게 훑을 수 있도록 요약하는 편집자.

입력: 기획 문서 1개 (md)
출력: 아래 4개 필드만. **각 필드 반드시 120자 이내**. 초과 금지.

반드시 이 JSON 형식만 반환 (마크다운 코드블록 감싸지 말 것):

{"핵심결론": "...", "타겟": "...", "핵심숫자": "...", "팀전달포인트": "..."}

필드 설명:
- 핵심결론: 이 파일의 한 줄 결론 (120자 이내)
- 타겟: 주요 페르소나/고객 (120자 이내)
- 핵심숫자: 중요 숫자 2~3개 (금액/비율/시간/수량) (120자 이내)
- 팀전달포인트: FE/BE/마케팅/영업 중 누가 뭘 알아야 하는지 (120자 이내)

규칙:
- 각 필드 120자 절대 초과 금지. 길면 잘라내라.
- 추상 표현 금지. 구체 명사·숫자·고유명 중심.
- "중요하다", "효과적이다" 같은 수식어 금지.
- 원문에 없는 내용 지어내지 마라.
- 원문이 짧거나 비어있으면 해당 필드 "(해당 없음)" 표기.
- 마크다운 코드블록(```) 금지. 순수 JSON만.
"""


def summarize_single_file(
    file_path: Path,
    client,
    max_input_chars: int = 20000,
) -> dict:
    """단일 md 파일 요약.

    Returns:
        dict with keys: 핵심결론, 타겟, 핵심숫자, 팀전달포인트
        에러 시 {"error": "..."}
    """
    try:
        text = file_path.read_text(encoding="utf-8")
    except Exception as e:
        return {"error": f"파일 읽기 실패: {e}"}

    # 파일이 너무 길면 앞부분만 (대부분 결론/요약 앞쪽)
    text = text[:max_input_chars]

    user_msg = f"# 파일명: {file_path.name}\n\n{text}"

    try:
        resp = client.messages.create(
            model=SUMMARIZE_MODEL,
            max_tokens=800,
            system=SUMMARIZE_SYSTEM,
            messages=[{"role": "user", "content": user_msg}],
        )
        raw = resp.content[0].text.strip()

        # JSON 파싱
        # Claude가 ```json ... ``` 으로 감쌀 수도 있음
        json_match = re.search(r"\{[\s\S]*\}", raw)
        if json_match:
            data = json.loads(json_match.group())
            # 필수 필드 체크
            for key in ["핵심결론", "타겟", "핵심숫자", "팀전달포인트"]:
                if key not in data:
                    data[key] = "(누락)"
            return data
        return {"error": f"JSON 파싱 실패: {raw[:200]}"}
    except Exception as e:
        return {"error": f"API 호출 실패: {e}"}


def summarize_planning_dir(
    outputs_dir: str,
    client,
    skip_files: list = None,
) -> dict:
    """outputs/{프로젝트}/ 폴더의 모든 md 파일 요약.

    Returns:
        dict: {filename: summary_dict}
    """
    if skip_files is None:
        skip_files = []

    path = Path(outputs_dir)
    if not path.exists():
        return {}

    summaries = {}
    md_files = sorted(path.glob("*.md"))

    for md_file in md_files:
        if md_file.name in skip_files:
            continue
        # 사업기획서.html 같은 결과물 스킵 (이미 md 아니지만)
        print(f"  요약 중: {md_file.name}")
        summaries[md_file.name] = summarize_single_file(md_file, client)

    return summaries


def format_summaries_as_index(
    summaries: dict,
    file_descriptions: dict = None,
) -> str:
    """요약 dict → INDEX.md에 박을 마크다운 블록.

    각 파일의 요약을 사람이 읽기 쉬운 형태로 표시.
    """
    if file_descriptions is None:
        file_descriptions = {}

    lines = [
        "## 파일별 핵심 요약 (자동 생성)",
        "",
        "> 각 파일의 4줄 요약. 깊이 봐야 할 파일은 원본 파일명 지정해서 로드.",
        "",
    ]

    for fname in sorted(summaries.keys()):
        summary = summaries[fname]
        desc = file_descriptions.get(fname, "")

        lines.append(f"### `{fname}`")
        if desc:
            lines.append(f"*{desc}*")
        lines.append("")

        if "error" in summary:
            lines.append(f"- ⚠️ 요약 실패: {summary['error']}")
        else:
            lines.append(f"- **핵심 결론**: {summary.get('핵심결론', '-')}")
            lines.append(f"- **타겟**: {summary.get('타겟', '-')}")
            lines.append(f"- **핵심 숫자**: {summary.get('핵심숫자', '-')}")
            lines.append(f"- **팀 전달**: {summary.get('팀전달포인트', '-')}")
        lines.append("")

    return "\n".join(lines)


def save_summaries(summaries: dict, outputs_dir: str) -> Path:
    """요약 결과를 outputs/{프로젝트}/_summaries.json 으로 저장."""
    path = Path(outputs_dir) / "_summaries.json"
    path.write_text(
        json.dumps(summaries, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return path


def load_summaries(outputs_dir: str) -> dict:
    """저장된 요약 불러오기. 없으면 빈 dict."""
    path = Path(outputs_dir) / "_summaries.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))
