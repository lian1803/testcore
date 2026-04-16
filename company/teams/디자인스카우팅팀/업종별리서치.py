"""
업종별리서치 — 무형 사업 업종별 TOP 디자인 패턴 Perplexity 리서치
결과 → 업종패턴DB.json 저장 → 디자인정보.py 브리핑에 주입
"""

import os
import json
from datetime import datetime
from pathlib import Path

import openai

BASE_DIR = Path(__file__).parent

INDUSTRIES = [
    {
        "id": "consulting",
        "label": "컨설팅/법무/B2B",
        "palette": {"bg": "#0A0E1A", "accent": "#C9A84C", "text": "#F0EDE6"},
        "query": (
            "Top consulting firm and law firm websites 2025 with outstanding design. "
            "List 5 specific sites (URLs). For each: color palette, font choices, "
            "hero section style, trust-building elements used, key design patterns."
        ),
    },
    {
        "id": "saas",
        "label": "SaaS/테크 스타트업",
        "palette": {"bg": "#030308", "accent": "#2563EB", "text": "#E2E8F0"},
        "query": (
            "Best SaaS startup landing pages 2025. "
            "List 5 specific sites (URLs). For each: dark/light mode preference, "
            "particle or 3D effects used, feature grid layout, pricing section style, "
            "CTA placement strategy, color palette."
        ),
    },
    {
        "id": "coaching",
        "label": "코칭/교육/개인브랜드",
        "palette": {"bg": "#100E0A", "accent": "#C25A3A", "text": "#F5F0E8"},
        "query": (
            "Best personal coaching, online education, personal brand websites 2025. "
            "List 5 specific sites (URLs). For each: warm color palette, "
            "journey/transformation storytelling style, testimonial section design, "
            "trust indicators, lead magnet strategy."
        ),
    },
    {
        "id": "marketing",
        "label": "마케팅/퍼포먼스 광고대행사",
        "palette": {"bg": "#020202", "accent": "#10B981", "text": "#F0F0F0"},
        "query": (
            "Top digital marketing and performance advertising agency websites 2025. "
            "List 5 specific sites (URLs). For each: bold design choices, "
            "how they display results/ROAS/metrics, portfolio showcase method, "
            "color choices, typography style, scroll animations used."
        ),
    },
    {
        "id": "medical",
        "label": "의료/헬스케어/웰니스",
        "palette": {"bg": "#F8FAFC", "accent": "#0EA5E9", "text": "#1E293B"},
        "query": (
            "Best medical clinic, healthcare, wellness website designs 2025. "
            "List 5 specific sites (URLs). For each: color palette (trustworthy blues/greens), "
            "how they handle accessibility, patient journey UX, "
            "appointment booking integration, trust badges."
        ),
    },
]


def research_industry(client: openai.OpenAI, industry: dict) -> dict:
    """Perplexity로 업종별 디자인 패턴 리서치"""
    print(f"  [RESEARCH] {industry['label']}...")
    try:
        response = client.chat.completions.create(
            model="sonar-pro",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a professional web design analyst. "
                        "Provide specific, actionable design intelligence. "
                        "Focus on actual design patterns, not generic advice."
                    ),
                },
                {"role": "user", "content": industry["query"]},
            ],
        )
        content = response.choices[0].message.content
        return {
            "id": industry["id"],
            "label": industry["label"],
            "palette": industry["palette"],
            "research": content,
            "updated": datetime.now().isoformat(),
        }
    except Exception as e:
        print(f"  [ERROR] {industry['label']}: {e}")
        return {
            "id": industry["id"],
            "label": industry["label"],
            "palette": industry["palette"],
            "research": f"리서치 실패: {e}",
            "updated": datetime.now().isoformat(),
        }


def run() -> dict:
    """전체 업종 리서치 실행 → DB 저장"""
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        print("[업종별리서치] PERPLEXITY_API_KEY 없음 — 스킵")
        return {}

    client = openai.OpenAI(
        api_key=api_key,
        base_url="https://api.perplexity.ai",
    )

    print(f"\n[업종별리서치] {len(INDUSTRIES)}개 업종 리서치 시작")
    results = {}

    for industry in INDUSTRIES:
        data = research_industry(client, industry)
        results[industry["id"]] = data

    # 기존 DB 불러오기 + 업데이트
    db = {}
    if PATTERN_DB_PATH.exists():
        try:
            with open(PATTERN_DB_PATH, encoding="utf-8") as f:
                db = json.load(f)
        except Exception:
            db = {}

    db.update(results)
    db["last_updated"] = datetime.now().isoformat()

    with open(PATTERN_DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    print(f"[업종별리서치] DB 저장: {PATTERN_DB_PATH}")
    return results


PATTERN_DB_PATH = BASE_DIR / "업종패턴DB.json"

if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(BASE_DIR.parent.parent.parent))
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR.parent.parent / ".env")
    run()
