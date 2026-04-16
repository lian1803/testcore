"""
model_updater.py -- 주 1회 최신 모델 목록 자동 갱신

각 provider API에서 사용 가능한 모델 목록을 가져와서
core/models.py의 상수들이 여전히 유효한지 검증하고,
새로 추가된 주요 모델이 있으면 보고사항들.md에 알림.

실행:
    python -m core.model_updater          # 즉시 실행
    python -m core.model_updater --update # models.py 자동 덮어쓰기 (위험, 확인 후 사용)
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

MODELS_PY = Path(__file__).parent / "models.py"
REPORT_PATH = Path(__file__).parent.parent.parent / "보고사항들.md"

# 우리가 관심있는 모델 패턴 (새 버전 감지용)
WATCH_PATTERNS = {
    "anthropic": ["claude-opus", "claude-sonnet", "claude-haiku"],
    "openai":    ["gpt-4o", "gpt-4.1", "gpt-4.2", "o1", "o3", "o4"],
    "google":    ["gemini-2.5", "gemini-3", "gemini-2.0"],
    "perplexity": ["sonar"],
}

# 현재 models.py에 정의된 값들 (검증 기준)
CURRENT_MODELS = {
    "anthropic": [
        "claude-opus-4-6",
        "claude-sonnet-4-6",
        "claude-haiku-4-5-20251001",
    ],
    "openai": [
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4.1",
        "gpt-4.1-mini",
        "gpt-4.1-nano",
    ],
    "google": [
        "gemini-2.5-flash",
        "gemini-2.5-pro",
    ],
    "perplexity": [
        "sonar-pro",
        "sonar",
    ],
}


# ── Provider별 모델 목록 가져오기 ──────────────────────────────────

def fetch_anthropic_models() -> list[str]:
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        models = client.models.list()
        return [m.id for m in models.data]
    except Exception as e:
        return [f"ERROR: {e}"]


def fetch_openai_models() -> list[str]:
    try:
        import openai
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        models = client.models.list()
        # GPT 계열만 필터 (dall-e, whisper 등 제외)
        gpt_models = [
            m.id for m in models.data
            if any(p in m.id for p in ["gpt-4", "gpt-3.5", "o1", "o3", "o4"])
        ]
        return sorted(gpt_models, reverse=True)
    except Exception as e:
        return [f"ERROR: {e}"]


def fetch_google_models() -> list[str]:
    try:
        import google.genai as genai
        client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        models = client.models.list()
        gemini_models = [
            m.name.replace("models/", "")
            for m in models
            if "gemini" in m.name.lower()
        ]
        return sorted(gemini_models, reverse=True)
    except Exception as e:
        return [f"ERROR: {e}"]


def fetch_perplexity_models() -> list[str]:
    # Perplexity는 공개 목록 API 없음 — 알려진 모델 하드코딩
    return [
        "sonar-pro",
        "sonar",
        "sonar-reasoning-pro",
        "sonar-reasoning",
        "r1-1776",
    ]


# ── 검증 + 리포트 ──────────────────────────────────────────────────

def check_validity(provider: str, available: list[str]) -> dict:
    """현재 models.py의 상수가 실제로 사용 가능한지 체크."""
    current = CURRENT_MODELS.get(provider, [])
    errors = [m for m in current if not any(m in a for a in available) and "ERROR" not in m]
    return {"valid": len(errors) == 0, "invalid": errors}


def find_new_models(provider: str, available: list[str]) -> list[str]:
    """우리가 아직 models.py에 안 넣은 새 모델 감지."""
    current_flat = set(CURRENT_MODELS.get(provider, []))
    patterns = WATCH_PATTERNS.get(provider, [])
    new = []
    for model in available:
        if "ERROR" in model:
            continue
        if any(p in model for p in patterns) and model not in current_flat:
            new.append(model)
    return new


def run_check(verbose: bool = True) -> dict:
    """전체 검증 실행. 결과 dict 반환."""
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    print("[model_updater] Fetching available models...")

    results = {}

    fetchers = {
        "anthropic": fetch_anthropic_models,
        "openai":    fetch_openai_models,
        "google":    fetch_google_models,
        "perplexity": fetch_perplexity_models,
    }

    for provider, fetcher in fetchers.items():
        print(f"  [{provider}] fetching...", end=" ", flush=True)
        available = fetcher()

        has_error = any("ERROR" in m for m in available)
        validity = check_validity(provider, available)
        new_models = find_new_models(provider, available)

        results[provider] = {
            "available": available,
            "error": has_error,
            "invalid_current": validity["invalid"],
            "new_models": new_models,
        }

        if has_error:
            print(f"ERROR: {available[0]}")
        else:
            print(f"OK ({len(available)} models)")

    return results


def build_report(results: dict) -> str:
    lines = ["## 모델 상태 점검 결과\n"]
    has_issues = False

    for provider, data in results.items():
        lines.append(f"### {provider.upper()}")

        if data["error"]:
            lines.append(f"- API 오류: {data['available'][0]}")
            has_issues = True
        else:
            lines.append(f"- 사용 가능 모델: {len(data['available'])}개")

            if data["invalid_current"]:
                has_issues = True
                lines.append(f"- **[주의] 더 이상 없는 모델:** {', '.join(data['invalid_current'])}")
                lines.append(f"  -> core/models.py 업데이트 필요")

            if data["new_models"]:
                lines.append(f"- **[신규] 새 모델 감지됨:**")
                for m in data["new_models"][:5]:
                    lines.append(f"  - `{m}`")
                lines.append(f"  -> core/models.py에 추가 검토 권장")

            if not data["invalid_current"] and not data["new_models"]:
                lines.append(f"- 이상 없음")

        lines.append("")

    if not has_issues:
        lines.insert(1, "> 모든 모델 정상. 업데이트 불필요.\n")
    else:
        lines.insert(1, "> **주의 사항 있음. 아래 확인.**\n")

    return "\n".join(lines)


def save_report(content: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"\n\n## 모델 목록 업데이트 점검 -- {ts}\n\n{content}\n\n---\n"
    try:
        existing = REPORT_PATH.read_text(encoding="utf-8") if REPORT_PATH.exists() else ""
        if "---" in existing:
            parts = existing.split("---", 1)
            new_content = parts[0] + "---\n" + entry + parts[1]
        else:
            new_content = existing + entry
        REPORT_PATH.write_text(new_content, encoding="utf-8")
        print(f"[model_updater] 보고사항들.md에 저장 완료")
    except Exception as e:
        print(f"[model_updater] 저장 실패: {e}")


# ── CLI ───────────────────────────────────────────────────────────

def main():
    auto_update = "--update" in sys.argv

    results = run_check()
    report = build_report(results)

    print("\n" + "=" * 60)
    print(report)
    print("=" * 60)

    save_report(report)

    # 이슈 있으면 요약 출력
    for provider, data in results.items():
        if data["invalid_current"]:
            print(f"\n[!] {provider}: 다음 모델이 더 이상 없음 → {data['invalid_current']}")
            print(f"    -> core/models.py 수동 업데이트 필요")
        if data["new_models"]:
            print(f"\n[+] {provider}: 신규 모델 감지 → {data['new_models'][:3]}")
            print(f"    -> 필요하면 core/models.py에 추가하고 model_router.py 라우팅 업데이트")

    return results


if __name__ == "__main__":
    main()
