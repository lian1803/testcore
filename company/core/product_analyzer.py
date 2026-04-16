"""
product_analyzer.py — 완성된 사이트/서비스 자동 분석

배포된 URL을 받아서:
1. 사이트 크롤링 (메타태그, 헤드라인, CTA, 가격)
2. Perplexity로 경쟁사 마케팅 채널 조사
3. Claude Sonnet으로 종합 분석 (타겟, 포지셔닝, 추천 채널)

사용법:
    from core.product_analyzer import analyze_product
    result = analyze_product("https://example.com", "프로젝트명", client)
"""
import os
import re
import json
import anthropic
from dotenv import load_dotenv
from core.context_loader import inject_context
from core.models import CLAUDE_SONNET

load_dotenv()

MODEL = CLAUDE_SONNET


def _crawl_site(url: str) -> dict:
    """requests + BeautifulSoup으로 사이트 크롤링."""
    try:
        import requests
        from bs4 import BeautifulSoup

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        resp = requests.get(url, headers=headers, timeout=15)
        resp.encoding = resp.apparent_encoding
        soup = BeautifulSoup(resp.text, "html.parser")

        # 메타 정보
        title = soup.find("title")
        desc = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", attrs={"property": "og:description"})
        og_title = soup.find("meta", attrs={"property": "og:title"})
        og_image = soup.find("meta", attrs={"property": "og:image"})

        # 주요 텍스트
        headings = [h.get_text(strip=True) for h in soup.find_all(["h1", "h2", "h3"])[:10]]
        hero_text = ""
        for hero_sel in ["#hero", ".hero", "[class*='hero']", "[class*='banner']", "section:first-of-type"]:
            hero = soup.select_one(hero_sel)
            if hero:
                hero_text = hero.get_text(separator=" ", strip=True)[:500]
                break

        # 가격 정보
        price_pattern = r'[\₩\$][\d,]+|[\d,]+원|[\d,]+\s*원'
        body_text = soup.get_text(separator=" ")[:5000]
        prices = re.findall(price_pattern, body_text)[:5]

        # CTA 버튼
        ctas = [btn.get_text(strip=True) for btn in soup.find_all(["button", "a"], class_=re.compile(r"btn|cta|contact|submit", re.I))[:5]]

        return {
            "url": url,
            "title": title.get_text(strip=True) if title else "",
            "description": desc.get("content", "") if desc else "",
            "og_title": og_title.get("content", "") if og_title else "",
            "og_image": og_image.get("content", "") if og_image else "",
            "headings": headings,
            "hero_text": hero_text,
            "prices": prices,
            "ctas": ctas,
            "body_snippet": body_text[:1500],
        }
    except Exception as e:
        print(f"  ⚠️  크롤링 실패 ({e}) — Perplexity 분석으로 전환")
        return {"url": url, "error": str(e), "title": "", "description": "", "headings": [], "body_snippet": ""}


def _research_competitors(keyword: str) -> str:
    """Perplexity로 경쟁사 마케팅 채널 조사."""
    try:
        import requests as req
        api_key = os.getenv("PERPLEXITY_API_KEY")
        if not api_key:
            return "Perplexity API 키 없음"

        queries = [
            f"{keyword} 경쟁사 마케팅 채널 2026 인스타 블로그",
            f"{keyword} 성공 사례 SNS 운영 전략",
        ]
        results = []
        for q in queries:
            resp = req.post(
                "https://api.perplexity.ai/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": "sonar",
                    "messages": [{"role": "user", "content": q}],
                    "max_tokens": 600,
                },
                timeout=30,
            )
            if resp.status_code == 200:
                results.append(resp.json()["choices"][0]["message"]["content"])
        return "\n\n".join(results)
    except Exception as e:
        return f"리서치 실패: {e}"


ANALYZE_PROMPT = """너는 디지털 마케팅 전문가야.
사이트 정보와 경쟁사 리서치를 보고 마케팅 분석을 해줘.

분석 결과를 JSON으로 출력해. 다른 텍스트 없이 JSON만:

{
  "target_persona": "구체적 타겟 (나이대, 특성, 니즈)",
  "key_message": "핵심 메시지 한 줄",
  "positioning": "경쟁사 대비 포지셔닝",
  "differentiator": "차별점",
  "recommended_channels": [
    {
      "name": "채널명 (인스타/블로그/유튜브/네이버카페/카카오/메타광고 중)",
      "priority": 1,
      "reason": "이 채널을 추천하는 이유",
      "format": "콘텐츠 포맷 (릴스/캐러셀/숏폼/SEO블로그 등)",
      "frequency": "주기 (매일/격일/주3회 등)",
      "tone": "톤앤매너",
      "team": "온라인마케팅팀 또는 온라인납품팀"
    }
  ],
  "week1_plan": [
    {"day": "Day 1", "action": "할 것", "output": "산출물"}
  ],
  "summary": "전체 마케팅 전략 요약 (한국어 3-4문장)"
}

채널은 최대 3개만 추천 (선택과 집중). 실행 가능한 것만."""


def analyze_product(url: str, project_name: str, client: anthropic.Anthropic) -> dict:
    """사이트 URL을 받아서 마케팅 분석 결과 반환."""
    print(f"\n{'='*60}")
    print(f"🔍 사이트 분석: {url}")
    print("="*60)

    # 1. 사이트 크롤링
    print("  [1/3] 사이트 크롤링...")
    site_info = _crawl_site(url)

    # 키워드 추출 (타이틀 + 프로젝트명 합산)
    keyword = f"{project_name} {site_info.get('title', '')}".strip()[:40]

    # 2. 경쟁사 리서치
    print("  [2/3] 경쟁사 리서치...")
    competitor_research = _research_competitors(keyword)

    # 3. Claude 종합 분석
    print("  [3/3] 마케팅 분석 중...")
    user_msg = f"""프로젝트명: {project_name}
URL: {url}

== 사이트 정보 ==
제목: {site_info.get('title', '')}
설명: {site_info.get('description', '')}
헤드라인: {', '.join(site_info.get('headings', []))}
히어로: {site_info.get('hero_text', '')}
가격: {', '.join(site_info.get('prices', []))}
CTA: {', '.join(site_info.get('ctas', []))}

== 사이트 본문 ==
{site_info.get('body_snippet', '')}

== 경쟁사 리서치 ==
{competitor_research[:2000]}

위 정보로 마케팅 분석 JSON을 출력해."""

    full_response = ""
    with client.messages.stream(
        model=MODEL,
        max_tokens=4000,
        system=inject_context(ANALYZE_PROMPT),
        messages=[{"role": "user", "content": user_msg}],
        temperature=0.3,
    ) as stream:
        for text in stream.text_stream:
            full_response += text

    # JSON 파싱 (코드블록 제거 후 시도)
    try:
        clean = re.sub(r'```json', '', full_response, flags=re.IGNORECASE)
        clean = re.sub(r'```', '', clean)
        json_match = re.search(r'\{[\s\S]*\}', clean, re.DOTALL)
        if json_match:
            analysis = json.loads(json_match.group(0))
        else:
            analysis = {"summary": full_response, "recommended_channels": [], "week1_plan": []}
    except json.JSONDecodeError:
        analysis = {"summary": full_response, "recommended_channels": [], "week1_plan": []}

    analysis["url"] = url
    analysis["project_name"] = project_name
    analysis["site_info"] = site_info

    print(f"\n  ✅ 분석 완료")
    print(f"  타겟: {analysis.get('target_persona', '?')}")
    print(f"  추천 채널: {[c['name'] for c in analysis.get('recommended_channels', [])]}")

    return analysis
