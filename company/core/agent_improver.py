"""
agent_improver.py — 에이전트 자기 개선 루프

작동 방식:
1. 매주 weekly review 시 각 에이전트 결과물 품질 평가
2. 품질 낮은 에이전트 탐지 (self_improve.py의 리뷰 결과 기반)
3. Perplexity로 해당 역할의 최신 베스트 프랙티스 수집
4. 수집된 지식으로 에이전트 프롬프트 자동 개선
5. 개선 전/후 비교해서 보고사항들.md에 올림 — 리안이 "ㅇㅇ" 하면 적용

핵심 원칙:
- 리안 승인 없이 프롬프트 변경 금지 (코드 파일 직접 수정 X)
- 개선안을 .pending_improvements.json에 저장 → 리안 승인 후 적용
- 승인되면 해당 agents/*.py 파일의 SYSTEM_PROMPT 또는 프롬프트 문자열 업데이트

사용법:
    from core.agent_improver import propose_improvements, apply_improvement

    # 주간 리뷰에서 자동 호출
    propose_improvements()

    # 리안 승인 후 수동으로 적용
    apply_improvement("minsu")
"""
import os
import json
import re
import anthropic
from datetime import datetime, timedelta
from typing import Optional
from dotenv import load_dotenv
from core.research_loop import _query_perplexity
from core.models import CLAUDE_SONNET
from core.context_loader import inject_context
from knowledge.manager import write_report

load_dotenv()

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # company/
IMPROVEMENTS_PENDING = os.path.join(
    os.path.dirname(_ROOT), ".pending_improvements.json"
)
IMPROVEMENTS_HISTORY = os.path.join(
    _ROOT, "knowledge", "improvements_history.jsonl"
)
REPORT_PATH = os.path.join(
    os.path.dirname(_ROOT), "보고사항들.md"
)


# ────── 에이전트 메타데이터 ──────
AGENTS_METADATA = {
    "sieun": {
        "name": "시은",
        "role": "오케스트레이터 및 팀 설계자",
        "model": "Claude Sonnet",
        "file": "agents/sieun.py",
        "prompt_var": "SYSTEM_PROMPT",
        "description": "리안의 아이디어 명확화, 이사팀 오케스트레이션, 팀 설계"
    },
    "seoyun": {
        "name": "서윤",
        "role": "시장 조사원",
        "model": "Perplexity API",
        "file": "agents/seoyun.py",
        "prompt_var": "SYSTEM_PROMPT",
        "description": "트렌드 스카우팅, 경쟁사 분석, 시장 기회 발굴"
    },
    "minsu": {
        "name": "민수",
        "role": "비즈니스 전략가",
        "model": "GPT-4o",
        "file": "agents/minsu.py",
        "prompt_var": "system",  # minsu는 동적으로 생성
        "description": "전략 수립, 수익 모델, 가격 전략, 로드맵"
    },
    "haeun": {
        "name": "하은",
        "role": "팩트 검증 및 반론자",
        "model": "Gemini",
        "file": "agents/haeun.py",
        "prompt_var": "system",  # haeun은 함수 내부에 정의
        "description": "사실 검증, 위험 요소 분석, 비판적 검토"
    },
    "junhyeok": {
        "name": "준혁",
        "role": "GO/NO-GO 판단",
        "model": "Claude Opus",
        "file": "agents/junhyeok.py",
        "prompt_var": "SYSTEM_PROMPT",
        "description": "최종 판단, 수익성/경쟁력/기술 난이도 평가"
    },
    "taeho": {
        "name": "태호",
        "role": "트렌드 스카우터",
        "model": "Claude Haiku",
        "file": "agents/taeho.py",
        "prompt_var": "SYSTEM_PROMPT",
        "description": "최신 비즈니스 트렌드, 신기술 동향"
    },
}


def _get_client():
    return anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def _load_improvements_pending() -> dict:
    """미승인 개선안 로드."""
    if not os.path.exists(IMPROVEMENTS_PENDING):
        return {}
    try:
        with open(IMPROVEMENTS_PENDING, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_improvements_pending(data: dict):
    """미승인 개선안 저장."""
    os.makedirs(os.path.dirname(IMPROVEMENTS_PENDING), exist_ok=True)
    try:
        with open(IMPROVEMENTS_PENDING, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️  개선안 저장 실패: {e}")


def _save_improvement_history(agent: str, improvement: dict):
    """개선 이력 기록."""
    os.makedirs(os.path.dirname(IMPROVEMENTS_HISTORY), exist_ok=True)
    try:
        with open(IMPROVEMENTS_HISTORY, "a", encoding="utf-8") as f:
            f.write(json.dumps({
                "agent": agent,
                "timestamp": datetime.now().isoformat(),
                **improvement
            }, ensure_ascii=False) + "\n")
    except Exception:
        pass


def _get_agent_current_prompt(agent_name: str) -> Optional[str]:
    """현재 에이전트 프롬프트 추출."""
    metadata = AGENTS_METADATA.get(agent_name)
    if not metadata:
        return None

    # file = "agents/sieun.py" 형태이므로 _ROOT에 붙임
    file_path = os.path.join(_ROOT, metadata["file"])
    if not os.path.exists(file_path):
        return None

    try:
        # UTF-8 BOM 감지 및 처리
        with open(file_path, "rb") as f:
            raw = f.read()

        # BOM 제거
        if raw.startswith(b'\xef\xbb\xbf'):
            content = raw[3:].decode('utf-8')
        else:
            try:
                content = raw.decode('utf-8')
            except UnicodeDecodeError:
                # UTF-8 실패 시 cp949 시도
                content = raw.decode('cp949', errors='replace')

        # SYSTEM_PROMPT = """...""" 패턴 추출
        prompt_var = metadata["prompt_var"]
        pattern = f'{prompt_var} = """(.+?)"""'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            return match.group(1).strip()

        # SYSTEM_PROMPT = '''...''' 패턴도 시도
        pattern = f"{prompt_var} = '''(.+?)'''"
        match = re.search(pattern, content, re.DOTALL)
        if match:
            return match.group(1).strip()

        # system = """...""" (minsu 같은 동적 생성 파일 시도하지 않음)
        return None
    except Exception as e:
        print(f"  {agent_name} 프롬프트 추출 실패: {e}")
        return None


def _extract_low_quality_agents() -> list[dict]:
    """
    improvements.jsonl에서 최근 2주간의 파이프라인 리뷰 분석.
    리뷰 텍스트에서 에이전트 언급 패턴 추출 + 품질 점수 추론.

    구체적으로: "## 품질 평가\n- **전체 점수: X/10**" 형식에서 점수 추출.
    """
    improvements_log = os.path.join(_ROOT, "knowledge", "improvements.jsonl")
    if not os.path.exists(improvements_log):
        return []

    pipeline_scores = []
    two_weeks_ago = datetime.now() - timedelta(days=14)

    try:
        with open(improvements_log, encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    entry = json.loads(line)
                    # timestamp 확인
                    ts_str = entry.get("timestamp", "")
                    try:
                        ts = datetime.fromisoformat(ts_str)
                        if ts < two_weeks_ago:
                            continue
                    except ValueError:
                        pass

                    # review 텍스트에서 점수 추출
                    review = entry.get("review", "")
                    if not review:
                        continue

                    # "## 품질 평가\n- **전체 점수: X/10**" 패턴
                    score_match = re.search(r"전체 점수:\s*(\d+(?:\.\d+)?)/10", review)
                    if not score_match:
                        continue

                    score = float(score_match.group(1))
                    pipeline = entry.get("pipeline", "unknown")

                    pipeline_scores.append({
                        "pipeline": pipeline,
                        "score": score,
                        "review": review[:300],
                    })
                except (json.JSONDecodeError, ValueError, TypeError):
                    continue
    except Exception as e:
        print(f"⚠️  improvements.jsonl 읽기 실패: {e}")
        return []

    # 파이프라인별 평균 점수 계산
    pipeline_avg = {}
    for item in pipeline_scores:
        p = item["pipeline"]
        if p not in pipeline_avg:
            pipeline_avg[p] = []
        pipeline_avg[p].append(item["score"])

    # 6점 미만 필터링 — 시스템 레벨 문제는 에이전트 개선으로 해결할 수 없으므로
    # 6점 이상이면서도 개선 여지가 있는 것들만 선택 (7~7.5)
    # 먼저는 정해진 에이전트들 중에서 샘플 선택
    low_quality = []

    # 이사팀 에이전트들이 참여한 파이프라인 확인
    for pipeline, scores in pipeline_avg.items():
        avg = sum(scores) / len(scores)
        # 평가 점수가 6~7.5 범위 = 개선 가능 영역
        if 6.0 <= avg < 7.5:
            # 파이프라인 이름에서 에이전트 추측 (예: "이사팀", "Autopilot")
            for agent_name, agent_meta in AGENTS_METADATA.items():
                # 간단한 휴리스틱: "이사팀" 파이프라인이면 모든 이사팀 에이전트 추천
                if "이사팀" in pipeline:
                    low_quality.append({
                        "agent": agent_name,
                        "score": avg,
                        "count": len(scores),
                        "pipeline": pipeline,
                        "metadata": AGENTS_METADATA.get(agent_name, {}),
                    })
                    break  # 파이프라인당 1개만 추천

    # 중복 제거 (같은 에이전트 여러 번 추천되었을 때)
    seen = set()
    unique = []
    for item in low_quality:
        key = item["agent"]
        if key not in seen:
            seen.add(key)
            unique.append(item)

    return sorted(unique, key=lambda x: x["score"])


def improve_agent(agent_name: str) -> Optional[dict]:
    """
    특정 에이전트의 프롬프트 개선안 생성.

    Returns:
        {
            "agent": "minsu",
            "current_prompt": "...",
            "improved_prompt": "...",
            "improvement_reason": "...",
            "research_findings": "..."
        }
    """
    metadata = AGENTS_METADATA.get(agent_name)
    if not metadata:
        print(f"⚠️  알 수 없는 에이전트: {agent_name}")
        return None

    print(f"\n  📚 {metadata['name']} 개선안 생성 중...")

    # 1. 현재 프롬프트 추출
    current_prompt = _get_agent_current_prompt(agent_name)
    if not current_prompt:
        print(f"  ⚠️  {metadata['name']} 프롬프트를 추출할 수 없음")
        return None

    # 2. Perplexity로 최신 베스트 프랙티스 수집
    research_queries = [
        f"{metadata['description']} 2026 최신 베스트 프랙티스",
        f"{metadata['role']} 효과적인 방법론 및 사례",
    ]

    research_findings = ""
    for query in research_queries:
        result = _query_perplexity(query)
        if result:
            research_findings += f"\n### {query}\n{result}\n"

    if not research_findings:
        print(f"  ⚠️  {metadata['name']}을(를) 위한 리서치 결과 없음")
        return None

    # 3. Claude Sonnet으로 개선된 프롬프트 생성
    client = _get_client()

    improvement_prompt = f"""너는 AI 시스템 설계자야.

현재 에이전트:
- 이름: {metadata['name']}
- 역할: {metadata['description']}
- 모델: {metadata['model']}

현재 프롬프트:
```
{current_prompt[:1500]}
```

최신 베스트 프랙티스:
```
{research_findings[:2000]}
```

이 에이전트의 프롬프트를 개선해줘.

개선할 때:
1. 역할과 책임을 더 명확히
2. 최신 베스트 프랙티스를 반영
3. 구체적인 예시 추가
4. 피해야 할 패턴 명시
5. 출력 형식을 더 구조화

출력 형식:
## 개선된 프롬프트
```
[전체 개선된 프롬프트]
```

## 개선 사항
- [구체적 개선 1]
- [구체적 개선 2]
- [구체적 개선 3]

## 기대 효과
[왜 이렇게 개선하면 결과물이 더 좋아지는지]
"""

    full_response = ""
    with client.messages.stream(
        model=CLAUDE_SONNET,
        max_tokens=3000,
        system=inject_context("너는 AI 에이전트 개선 전문가야. 프롬프트를 더 효과적으로 만드는 것이 목표야."),
        messages=[{"role": "user", "content": improvement_prompt}],
        temperature=0.7,
    ) as stream:
        for text in stream.text_stream:
            full_response += text

    # 개선된 프롬프트 추출
    prompt_match = re.search(r"## 개선된 프롬프트\n```\n(.+?)\n```", full_response, re.DOTALL)
    improved_prompt = prompt_match.group(1) if prompt_match else None

    if not improved_prompt:
        print(f"  ⚠️  {metadata['name']} 개선 프롬프트 추출 실패")
        return None

    return {
        "agent": agent_name,
        "agent_name": metadata["name"],
        "current_prompt": current_prompt[:500],  # 미리보기용
        "improved_prompt": improved_prompt,
        "improvement_reason": full_response,
        "research_findings": research_findings[:300],
        "timestamp": datetime.now().isoformat(),
    }


def propose_improvements():
    """
    낮은 평점 에이전트들 탐지 → 개선안 생성 → .pending_improvements.json 저장 → 보고.
    주간 리뷰에서 자동 호출.
    """
    print("\n" + "="*60)
    print("🔧 에이전트 자기 개선 루프")
    print("="*60)

    # 1. 낮은 품질 에이전트 탐지
    low_quality = _extract_low_quality_agents()
    if not low_quality:
        print("\n  ✅ 낮은 평점 에이전트 없음. 개선 제안 스킵.")
        return

    print(f"\n  📊 품질 개선 필요한 에이전트: {len(low_quality)}개")
    for agent_info in low_quality:
        print(f"    - {agent_info['metadata'].get('name', agent_info['agent'])}: {agent_info['score']:.1f}/10 ({agent_info['count']}회)")

    # 2. 상위 3개 에이전트만 개선 (비용 제한)
    improvements = {}
    for agent_info in low_quality[:3]:
        agent_name = agent_info["agent"]
        improvement = improve_agent(agent_name)
        if improvement:
            improvements[agent_name] = improvement

    if not improvements:
        print("\n  ⚠️  개선 가능한 에이전트 없음")
        return

    # 3. 미승인 개선안 저장
    pending = _load_improvements_pending()
    for agent_name, improvement_data in improvements.items():
        pending[agent_name] = {
            **improvement_data,
            "status": "pending_approval",
        }

    _save_improvements_pending(pending)
    print(f"\n  💾 {len(improvements)}개 개선안 저장됨: .pending_improvements.json")

    # 4. 보고
    report_content = _format_improvements_report(pending)
    write_report(
        "AgentImprover",
        "에이전트 자기 개선",
        report_content
    )

    print(f"\n  📋 보고사항들.md 업데이트 완료")


def _format_improvements_report(pending: dict) -> str:
    """개선안을 보고사항 형식으로 포맷."""
    lines = [
        "## 에이전트 자기 개선 제안\n",
        f"**생성 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    ]

    if not pending:
        lines.append("개선 제안이 없습니다.")
        return "\n".join(lines)

    lines.append(f"**대기 중인 개선안**: {len(pending)}개\n")

    for agent_name, improvement in pending.items():
        if improvement.get("status") != "pending_approval":
            continue

        metadata = AGENTS_METADATA.get(agent_name, {})
        lines.append(f"\n### {metadata.get('name', agent_name)}")
        lines.append(f"- 역할: {metadata.get('description', '?')}")
        lines.append(f"- 상태: {improvement.get('status', '?')}")

        # 개선 내용 요약
        reason = improvement.get("improvement_reason", "")
        # "## 개선 사항" 섹션 추출
        improvements_match = re.search(r"## 개선 사항\n(.+?)(?=##|\Z)", reason, re.DOTALL)
        if improvements_match:
            lines.append(f"- 개선 내용:\n{improvements_match.group(1).strip()}")

    lines.append("""
---

## 리안에게
위의 에이전트들이 자동 분석 결과 개선이 필요한 상태입니다.
각 개선안을 검토한 후 다음 중 하나를 선택해주세요:
- "적용" → 해당 에이전트 프롬프트 자동 업데이트
- "검토 후" → 수정 후 적용
- "스킵" → 이번에는 적용 안 함

적용 방법: `apply_improvement("에이전트명")`
""")

    return "\n".join(lines)


def apply_improvement(agent_name: str) -> bool:
    """
    리안이 승인한 개선안을 실제 agents/{agent_name}.py 파일에 적용.
    프롬프트 문자열만 교체. 로직은 건드리지 않음.
    """
    pending = _load_improvements_pending()

    if agent_name not in pending:
        print(f"⚠️  {agent_name}의 미승인 개선안이 없습니다")
        return False

    improvement = pending[agent_name]
    metadata = AGENTS_METADATA.get(agent_name)

    if not metadata:
        print(f"⚠️  알 수 없는 에이전트: {agent_name}")
        return False

    improved_prompt = improvement.get("improved_prompt", "")
    if not improved_prompt:
        print(f"⚠️  개선된 프롬프트가 없습니다")
        return False

    # 파일 경로
    file_path = os.path.join(_ROOT, metadata["file"])
    if not os.path.exists(file_path):
        print(f"⚠️  파일을 찾을 수 없습니다: {file_path}")
        return False

    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # 기존 프롬프트를 새 것으로 교체
        prompt_var = metadata["prompt_var"]
        # """...""" 패턴 찾기
        pattern = f'{prompt_var} = """(.+?)"""'
        match = re.search(pattern, content, re.DOTALL)

        if match:
            # 기존 프롬프트 삼중 큰따옴표로 감싸기
            improved_prompt_escaped = improved_prompt.replace('\\', '\\\\').replace('"""', '\\"\\"\\"')
            new_content = content[:match.start(1)] + improved_prompt_escaped + content[match.end(1):]
        else:
            # '''...''' 패턴 시도
            pattern = f"{prompt_var} = '''(.+?)'''"
            match = re.search(pattern, content, re.DOTALL)
            if match:
                new_content = content[:match.start(1)] + improved_prompt + content[match.end(1):]
            else:
                print(f"⚠️  {agent_name}의 프롬프트 패턴을 찾을 수 없습니다")
                return False

        # 파일 업데이트
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)

        # 승인된 것으로 마크
        improvement["status"] = "applied"
        improvement["applied_at"] = datetime.now().isoformat()
        _save_improvements_pending(pending)

        # 이력 저장
        _save_improvement_history(agent_name, improvement)

        print(f"✅ {metadata['name']} ({agent_name}) 개선안 적용 완료")
        return True

    except Exception as e:
        print(f"⚠️  개선안 적용 실패: {e}")
        return False


def get_pending_improvements() -> dict:
    """미승인 개선안 목록 조회."""
    return _load_improvements_pending()


# ── CLI ──

def main():
    import sys

    if len(sys.argv) < 2:
        print("사용법:")
        print("  python -m core.agent_improver propose    # 개선안 생성")
        print("  python -m core.agent_improver apply AGENT  # 개선안 적용")
        print("  python -m core.agent_improver list       # 미승인 개선안 목록")
        sys.exit(1)

    command = sys.argv[1]

    if command == "propose":
        propose_improvements()
    elif command == "apply" and len(sys.argv) > 2:
        agent = sys.argv[2]
        if apply_improvement(agent):
            print(f"적용 완료!")
        else:
            print(f"적용 실패!")
    elif command == "list":
        pending = get_pending_improvements()
        if not pending:
            print("미승인 개선안 없음")
        else:
            print("미승인 개선안:")
            for agent, info in pending.items():
                print(f"  - {agent}: {info.get('status', '?')}")
    else:
        print(f"알 수 없는 명령: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
