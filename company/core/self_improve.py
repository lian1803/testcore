"""
self_improve.py — 시스템 자기 개선 루프

모든 파이프라인 실행 후 자동으로 호출됨.
결과물 품질을 평가하고, 문제 발견 시 개선 제안을 보고사항들.md에 올림.

리안은 보고사항들.md만 보면 됨:
- 결과물 보고 + "이거 이렇게 바꾸면 어때?" 제안이 같이 올라옴
- 리안이 "ㅇㅇ" 하면 Claude가 수정

사용법:
    from core.self_improve import post_run_review

    # 파이프라인 실행 후
    post_run_review(
        pipeline_name="이사팀",
        context=context,
        output=result,
    )
"""
import os
import anthropic
from datetime import datetime
from dotenv import load_dotenv
from core.context_loader import inject_context
from core.models import CLAUDE_SONNET

load_dotenv()

MODEL = CLAUDE_SONNET
REPORT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "보고사항들.md")
IMPROVEMENTS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "knowledge", "improvements.jsonl")


REVIEW_PROMPT = """너는 리안 컴퍼니의 시스템 감시자야. 방금 파이프라인이 실행됐어.

네 역할:
1. 결과물 품질 평가 — 쓸 수 있는 수준인가? 뭐가 부족한가?
2. 프로세스 문제 감지 — 비효율적인 단계? 빠진 단계? 중복?
3. 개선 제안 — 구체적으로 어떻게 바꾸면 나아지는지

평가 기준:
- 결과물이 "내일 당장 쓸 수 있는" 수준인가?
- 에이전트가 회사 맥락을 잘 반영했는가?
- 불필요하게 긴 부분은 없는가?
- 빠진 정보가 있는가?
- 같은 말을 반복하는 에이전트가 있는가?

출력 형식:
## 품질 평가
- 전체 점수: X/10
- 바로 쓸 수 있는가: YES / 수정 필요 / NO

## 발견된 문제 (있으면)
1. [문제]: [구체적으로]
2. [문제]: [구체적으로]

## 개선 제안 (있으면)
| 제안 | 왜 | 어떻게 |
|------|-----|--------|

## 리안에게
[리안이 읽을 한 줄 요약. "이번 결과 괜찮아, 바로 써" 또는 "이거 좀 문제야, 이렇게 바꾸면 어때?"]

문제 없으면 "문제 없음. 결과물 품질 양호." 로 끝내. 괜히 문제 만들지 마."""


def _get_client():
    return anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def _save_to_report(content: str):
    """보고사항들.md에 추가."""
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"\n\n## 시스템 자기 점검 — {date_str}\n\n{content}\n\n---\n"
    try:
        existing = ""
        if os.path.exists(REPORT_PATH):
            with open(REPORT_PATH, encoding="utf-8") as f:
                existing = f.read()
        if "---" in existing:
            parts = existing.split("---", 1)
            new_content = parts[0] + "---\n" + entry + parts[1]
        else:
            new_content = existing + entry
        with open(REPORT_PATH, "w", encoding="utf-8") as f:
            f.write(new_content)
    except Exception as e:
        print(f"⚠️ 자기점검 보고 저장 실패: {e}")


def _save_improvement(improvement: dict):
    """개선 이력 기록 (나중에 패턴 분석용)."""
    import json
    os.makedirs(os.path.dirname(IMPROVEMENTS_PATH), exist_ok=True)
    try:
        with open(IMPROVEMENTS_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps({
                **improvement,
                "timestamp": datetime.now().isoformat(),
            }, ensure_ascii=False) + "\n")
    except Exception:
        pass


def post_run_review(pipeline_name: str, context: dict, output: str = "") -> str:
    """파이프라인 실행 후 자동 품질 평가 + 개선 제안."""
    client = _get_client()

    print(f"\n  🔍 시스템 자기 점검 ({pipeline_name})...")

    # 결과물 요약 (너무 길면 잘라서)
    if isinstance(context, dict):
        ctx_summary = "\n".join([
            f"- {k}: {str(v)[:200]}" for k, v in context.items()
            if isinstance(v, str) and len(v) > 50
        ])[:3000]
    else:
        ctx_summary = str(context)[:3000]

    user_msg = f"""방금 실행된 파이프라인: {pipeline_name}

결과물 요약:
{ctx_summary}

{f"최종 출력:{chr(10)}{output[:2000]}" if output else ""}

품질 평가하고, 문제 있으면 개선 제안해줘."""

    full_response = ""
    with client.messages.stream(
        model=MODEL,
        max_tokens=1000,
        system=inject_context(REVIEW_PROMPT),
        messages=[{"role": "user", "content": user_msg}],
        temperature=0.2,
    ) as stream:
        for text in stream.text_stream:
            full_response += text

    # "문제 없음" 이면 조용히 넘어감
    if "문제 없음" in full_response and "품질 양호" in full_response:
        print(f"  ✅ 품질 양호 — 보고 스킵")
        return full_response

    # 문제 있으면 보고사항들.md에 올림
    print(f"  📋 개선 제안 발견 → 보고사항들.md")
    _save_to_report(full_response)
    _save_improvement({
        "pipeline": pipeline_name,
        "review": full_response[:500],
    })

    return full_response
