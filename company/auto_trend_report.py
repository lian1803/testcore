"""
자동 트렌드 브리핑 시스템
재원(리서처)이 다음 3가지를 Perplexity로 조사하고 보고사항들.md에 올림:
  1. 이번 주 한국 디지털 마케팅 트렌드 + SaaS 업계 동향
  2. Databox, Whatagraph, AgencyAnalytics 최근 업데이트/변경사항
  3. GA4, Meta Ads, 네이버SA 플랫폼 최근 변경사항

실행: python company/auto_trend_report.py
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

# .env 로드
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

MODEL = "sonar-pro"
REPORT_PATH = Path(__file__).parent.parent / "보고사항들.md"

QUERIES = [
    {
        "label": "한국 디지털 마케팅 + SaaS 업계 동향",
        "prompt": (
            "이번 주 한국 디지털 마케팅 트렌드와 SaaS 업계 동향을 조사해줘. "
            "주요 변화, 새로운 전략, 화제가 된 사례를 포함해서 실무에 바로 쓸 수 있는 인사이트 위주로 정리해줘. "
            "출처 URL 포함."
        ),
    },
    {
        "label": "경쟁 SaaS 업데이트 (Databox / Whatagraph / AgencyAnalytics)",
        "prompt": (
            "Databox, Whatagraph, AgencyAnalytics 세 서비스의 최근 업데이트나 변경사항을 조사해줘. "
            "신규 기능, 요금제 변경, UI 개편, 공식 발표 등 실제 변화가 있는 것만 정리해줘. "
            "출처 URL 포함."
        ),
    },
    {
        "label": "플랫폼 변경사항 (GA4 / Meta Ads / 네이버SA)",
        "prompt": (
            "GA4, Meta Ads, 네이버 검색광고(네이버SA) 세 플랫폼의 최근 변경사항을 조사해줘. "
            "알고리즘 업데이트, 정책 변경, 인터페이스 개편, 새로운 광고 포맷 등을 포함해서 마케터 관점에서 중요한 것 위주로 정리해줘. "
            "출처 URL 포함."
        ),
    },
]

SYSTEM_PROMPT = """너는 재원이야. 리안 컴퍼니 오프라인 마케팅팀 리서처야.
매주 최신 트렌드와 업계 동향을 조사해서 리안 CEO에게 보고하는 역할이야.

보고 형식:
- 핵심 내용 3~5줄 불릿 요약
- 상세 내용 (수치나 구체적 사례 포함)
- 리안에게 바로 쓸 수 있는 액션 포인트 1~2개
- 출처 URL

간결하고 실무 중심으로. 불필요한 서론 없이 바로 본론으로."""


def call_perplexity(query: str) -> str:
    client = OpenAI(
        api_key=os.getenv("PERPLEXITY_API_KEY"),
        base_url="https://api.perplexity.ai",
        timeout=90.0,
    )

    full_response = ""
    stream = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query},
        ],
        stream=True,
    )
    for chunk in stream:
        text = chunk.choices[0].delta.content or ""
        print(text, end="", flush=True)
        full_response += text

    print()
    return full_response


def append_to_report(content: str) -> None:
    """보고사항들.md 상단 구분선 바로 아래에 새 보고 삽입."""
    if not REPORT_PATH.exists():
        print(f"[경고] 보고사항들.md를 찾을 수 없음: {REPORT_PATH}")
        return

    original = REPORT_PATH.read_text(encoding="utf-8")
    marker = "<!-- 새 보고는 이 선 바로 아래에 자동 추가됨 (최신이 위로) -->"

    if marker in original:
        updated = original.replace(marker, marker + "\n\n" + content)
    else:
        # 마커 없으면 파일 맨 끝에 추가
        updated = original + "\n\n" + content

    REPORT_PATH.write_text(updated, encoding="utf-8")
    print(f"\n[완료] 보고사항들.md 업데이트: {REPORT_PATH}")


def main():
    print("\n" + "=" * 60)
    print("📡 재원 | 자동 트렌드 브리핑 시작")
    print("=" * 60)

    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        print("[오류] PERPLEXITY_API_KEY가 .env에 없습니다.")
        sys.exit(1)

    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d %H:%M")
    sections = []

    for i, item in enumerate(QUERIES, 1):
        print(f"\n[{i}/3] {item['label']}")
        print("-" * 40)
        result = call_perplexity(item["prompt"])
        sections.append(f"### {i}. {item['label']}\n\n{result.strip()}")

    body = "\n\n---\n\n".join(sections)

    report = f"""## 재원 — 자동 트렌드 브리핑 ({date_str})

{body}

---
"""

    append_to_report(report)
    print("\n[재원] 트렌드 브리핑 완료. 보고사항들.md를 확인해줘.")


if __name__ == "__main__":
    main()
