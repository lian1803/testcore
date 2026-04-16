import os
import anthropic
from . import notify
from core.models import CLAUDE_SONNET

DOCTOR_MODEL = CLAUDE_SONNET
DOCTOR_SYSTEM_PROMPT = """너는 닥터야. 리안 컴퍼니의 자동 수정담당이야.

센티넬(헬스체크)이나 마케팅 시스템에서 이상이 감지되면,
- 문제가 뭔지 분석하고
- 즉시 수정 가능한 방안을 제시해
- (가능하면) PR 또는 스크립트 형태로 제안해

원칙:
1. "이 문제는 손으로 해야 합니다" — 자동화 불가 판단
2. "기술적 한계입니다" — 아키텍처 문제 등
3. 구체적인 수정 코드 또는 명령어 제공

형식:
```
## 문제 분석
[뭐가 잘못됐는가]

## 근본 원인
[왜 그런가]

## 수정 방안
[어떻게 고칠까]

## 실행 명령
```
[명령어 또는 코드]
```

## 예상 결과
[고치고 나면 뭐가 나아질까]
```"""


def analyze_and_fix(error_type: str, error_details: str) -> dict:
    """이상을 분석하고 수정 방안 제시

    Args:
        error_type: 이상 유형 (e.g., "HEALTH_CHECK_FAILED", "DB_CONNECTION_ERROR")
        error_details: 상세 에러 메시지

    Returns:
        {"fix": str, "pr_url": Optional[str], "executable": bool}
    """
    client = anthropic.Anthropic()

    prompt = f"""【이상 감지】
타입: {error_type}
상세: {error_details}

이 문제를 분석하고 수정 방안을 제시해줘."""

    try:
        message = client.messages.create(
            model=DOCTOR_MODEL,
            max_tokens=1500,
            system=DOCTOR_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )

        fix_description = message.content[0].text

        return {
            "fix": fix_description,
            "pr_url": None,  # 실제 GitHub PR 생성은 별도 구현 필요
            "executable": "실행 명령" in fix_description,
        }

    except Exception as e:
        return {
            "fix": f"❌ 분석 실패: {e}",
            "pr_url": None,
            "executable": False,
        }


def handle_error(error_type: str, error_details: str):
    """이상 처리 주요 로직"""
    print(f"🚨 이상 감지: {error_type}")
    print(f"📋 상세: {error_details}")

    # 디스코드 알림
    notify.notify_error_detected(error_type, error_details)

    # 자동 수정 분석
    result = analyze_and_fix(error_type, error_details)

    # 결과 전송
    notify.notify_fix_applied(result["fix"], result.get("pr_url"))

    return result


if __name__ == "__main__":
    # 테스트
    test_result = handle_error(
        "HEALTH_CHECK_FAILED",
        "Project URL returned HTTP 503 — service unavailable"
    )
    print("\n" + "=" * 60)
    print(test_result["fix"])
