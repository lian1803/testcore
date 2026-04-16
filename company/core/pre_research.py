"""
pre_research.py — 팀 실행 전 자동 레퍼런스 수집 + 분석

프로젝트 키워드만 주면:
1. Perplexity로 해당 업종 잘하는 인스타 계정/광고 사례 검색
2. 인스타 최신 피드 긁어서 Gemini로 패턴 분석
3. "이 업종에선 이런 게 먹힌다" 인사이트 추출
4. knowledge/base/에 저장 → 팀 프롬프트에 자동 주입

사용법:
    from core.pre_research import auto_research

    research = auto_research(keyword="소상공인 매장 인스타그램 마케팅")
    context["reference_research"] = research  # 에이전트 프롬프트에 주입
"""

import os
import re
import json
import subprocess
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    import google.genai as genai
except ImportError:
    genai = None

load_dotenv()

BASE_DIR = Path(__file__).parent.parent
KNOWLEDGE_DIR = BASE_DIR / "knowledge" / "base"
CACHE_HOURS = 24
GALLERY_DL = BASE_DIR / "venv" / "Scripts" / "gallery-dl.exe"
COOKIE_FILE = BASE_DIR / "instagram_cookies.txt"


def _ensure_dirs():
    """필요한 디렉토리 생성"""
    KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)


def _cache_path(keyword: str) -> Path:
    """키워드를 파일명으로 변환"""
    safe = "".join(c if c.isalnum() or c in "가-힣_-" else "_" for c in keyword)[:80]
    return KNOWLEDGE_DIR / f"research_{safe}.json"


def _is_cached(keyword: str) -> bool:
    """최근 CACHE_HOURS 내에 수집한 적 있으면 캐시 사용"""
    path = _cache_path(keyword)
    if not path.exists():
        return False
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        cached_time = datetime.fromisoformat(data.get("timestamp", "2000-01-01"))
        return datetime.now() - cached_time < timedelta(hours=CACHE_HOURS)
    except Exception:
        return False


def _load_cache(keyword: str) -> Optional[dict]:
    """캐시된 결과 로드"""
    try:
        with open(_cache_path(keyword), encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _save_cache(keyword: str, data: dict):
    """결과 캐싱"""
    _ensure_dirs()
    try:
        data["timestamp"] = datetime.now().isoformat()
        with open(_cache_path(keyword), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def _query_perplexity(query: str) -> Optional[str]:
    """Perplexity에 단일 쿼리 실행. 실패 시 None 반환."""
    if not OpenAI:
        return None

    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        return None

    try:
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.perplexity.ai",
            timeout=60.0,
        )
        resp = client.chat.completions.create(
            model="sonar-pro",
            messages=[
                {
                    "role": "system",
                    "content": "최신 사례와 실전 전략 위주로 답해. 구체적인 계정/광고사례/수치 위주. 한국어로."
                },
                {"role": "user", "content": query}
            ],
            max_tokens=1000,
        )
        return resp.choices[0].message.content
    except Exception as e:
        print(f"    ⚠️  Perplexity 쿼리 실패: {str(e)[:60]}")
        return None


def _extract_instagram_urls(text: str) -> list[str]:
    """텍스트에서 인스타그램 계정 URL 추출"""
    # instagram.com/계정명/ 형식의 URL만 추출
    urls = re.findall(r'https://www\.instagram\.com/([a-zA-Z0-9_.]+)/?', text)
    # 중복 제거 + URL 정리
    unique_accounts = list(set(urls))
    return [f"https://www.instagram.com/{acc}/" for acc in unique_accounts[:5]]


def _fetch_post_urls(account_url: str, count: int = 3) -> list[str]:
    """gallery-dl로 계정의 최신 포스트 URL 추출"""
    if not GALLERY_DL.exists() or not COOKIE_FILE.exists():
        return []

    try:
        result = subprocess.run(
            [str(GALLERY_DL), "--cookies", str(COOKIE_FILE),
             "--range", f"1-{count}", "--print", "{url}",
             account_url],
            capture_output=True,
            text=True,
            timeout=30,
            encoding="utf-8",
            errors="replace"
        )

        if result.returncode == 0:
            urls = [u.strip() for u in result.stdout.strip().split('\n') if u.strip()]
            return urls[:count]
    except Exception as e:
        print(f"    ⚠️  gallery-dl 오류: {str(e)[:60]}")

    return []


def _analyze_posts_with_gemini(posts_data: list[dict]) -> Optional[str]:
    """여러 포스트 정보를 Gemini로 분석해서 패턴 추출"""
    if not genai:
        return None

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return None

    try:
        client = genai.Client(api_key=api_key)

        # 포스트 정보를 텍스트로 정리
        posts_text = "\n\n".join([
            f"[포스트 {i+1}]\n"
            f"URL: {p.get('url', 'N/A')}\n"
            f"캡션: {p.get('caption', '(캡션 없음)')[:200]}...\n"
            for i, p in enumerate(posts_data[:5])
        ])

        prompt = f"""이 업종/분야의 인스타그램 마케팅 패턴을 분석해줘.

[수집된 포스트]
{posts_text}

[분석 항목 - 짧고 실용적으로]
1. 주요 콘텐츠 유형 — 이미지/영상/캐러셀 등 어떤 포맷이 먹히나
2. 카피 패턴 — 제목/설명/CTA 구조. 특별한 문구나 구조 있나
3. 비주얼 스타일 — 색감/분위기/구성 공통점
4. 후킹 방식 — 첫 글자/이미지로 어떻게 관심 끄는지
5. 우리가 즉시 적용할 수 있는 것 3가지 (구체적)

한국어로, 2000자 이내. 이론은 빼고 실전만."""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt]
        )

        return response.text
    except Exception as e:
        print(f"    ⚠️  Gemini 분석 실패: {str(e)[:60]}")
        return None


def search_reference_accounts(keyword: str) -> list[str]:
    """Perplexity로 레퍼런스 계정 URL 검색"""
    print(f"  🔍 Perplexity로 레퍼런스 계정 검색 중...")

    query = f"""{keyword}에서 성공하는 한국 인스타그램 계정이나 광고사례를 3~5개 추천해줘.
꼭 instagram.com/계정명 형태의 URL을 포함해서.
실제 사례와 수치 위주로."""

    result = _query_perplexity(query)
    if not result:
        return []

    urls = _extract_instagram_urls(result)
    print(f"    ✅ {len(urls)}개 계정 찾음")
    return urls


def scrape_and_analyze_posts(account_urls: list[str], posts_per_account: int = 3) -> list[dict]:
    """여러 계정에서 포스트 URL 수집 및 기본 정보 저장"""
    posts_data = []

    for i, url in enumerate(account_urls[:3], 1):
        print(f"  📸 [{i}/{min(3, len(account_urls))}] {url} 포스트 수집 중...")

        post_urls = _fetch_post_urls(url, posts_per_account)
        if post_urls:
            for post_url in post_urls:
                posts_data.append({
                    "url": post_url,
                    "account": url,
                    "caption": "(캡션 생략)"  # 전체 캡션은 저장하지 않음 (용량)
                })
            print(f"      → {len(post_urls)}개 포스트 추출")
        else:
            print(f"      → 포스트 추출 실패 (쿠키/계정 확인)")

    return posts_data


def analyze_patterns(posts_data: list[dict]) -> Optional[str]:
    """여러 포스트 분석 결과를 종합해서 패턴 추출"""
    if not posts_data:
        return None

    print(f"  🤖 Gemini로 패턴 분석 중 ({len(posts_data)}개 포스트)...")

    analysis = _analyze_posts_with_gemini(posts_data)
    if analysis:
        print(f"    ✅ 분석 완료")
    else:
        print(f"    ❌ 분석 실패 (API 확인)")

    return analysis


def save_research(keyword: str, research_result: dict) -> str:
    """knowledge/base/research_{keyword}.md 저장"""
    _ensure_dirs()

    path = KNOWLEDGE_DIR / f"research_{keyword[:80]}.md"

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    content = f"""# {keyword} — 레퍼런스 수집

**수집일**: {timestamp}

## 레퍼런스 계정
{chr(10).join([f"- {p.get('account', 'N/A')}" for p in research_result.get('posts', [])])}

## 포스트 URL
{chr(10).join([f"- {p.get('url', 'N/A')}" for p in research_result.get('posts', [])[:5]])}

## 패턴 분석

{research_result.get('analysis', '(분석 데이터 없음)')}

---

*자동 생성 — {timestamp}*
"""

    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  💾 저장: {path.name}")
        return content
    except Exception as e:
        print(f"  ❌ 저장 실패: {e}")
        return ""


def auto_research(keyword: str, max_accounts: int = 3, posts_per_account: int = 3) -> str:
    """
    키워드 기반 자동 레퍼런스 수집 + 분석

    Args:
        keyword: 연구할 키워드 (예: "소상공인 인스타그램 마케팅")
        max_accounts: 수집할 계정 수
        posts_per_account: 계정당 포스트 수

    Returns:
        요약 텍스트 (팀 프롬프트에 주입용)
    """
    _ensure_dirs()

    print(f"\n📋 [자동 레퍼런스 수집] {keyword}")
    print("=" * 60)

    # 1. 캐시 확인
    if _is_cached(keyword):
        cached = _load_cache(keyword)
        if cached:
            summary = cached.get("summary", "")
            print(f"  ✅ 24시간 내 수집한 캐시 사용")
            return summary

    # 2. Perplexity로 계정 검색
    account_urls = search_reference_accounts(keyword)
    if not account_urls:
        print(f"  ❌ 레퍼런스 계정을 찾을 수 없습니다.")
        return ""

    # 3. 포스트 수집
    posts_data = scrape_and_analyze_posts(account_urls, posts_per_account)
    if not posts_data:
        print(f"  ⚠️  포스트 수집 실패 (쿠키/gallery-dl 확인). 패턴 분석 스킵.")
        # gallery-dl 없어도 Perplexity 결과는 반환
        summary = f"""## {keyword} — 레퍼런스

**참고 계정**:
{chr(10).join([f"- {url}" for url in account_urls])}

*포스트 상세 분석은 gallery-dl 환경에서 실행됩니다.*
"""
        return summary

    # 4. 패턴 분석
    analysis = analyze_patterns(posts_data)

    # 5. 저장
    research_data = {
        "keyword": keyword,
        "posts": posts_data,
        "analysis": analysis or "(분석 데이터 없음)",
        "accounts": account_urls,
        "timestamp": datetime.now().isoformat()
    }

    content = save_research(keyword, research_data)
    _save_cache(keyword, research_data)

    # 6. 요약 반환
    summary = f"""## {keyword} — 자동 수집 레퍼런스

**수집 계정** ({len(account_urls)}개):
{chr(10).join([f"- {url}" for url in account_urls])}

**수집 포스트** ({len(posts_data)}개):
{chr(10).join([f"- {p['url']}" for p in posts_data[:5]])}
{f"- ... 외 {len(posts_data) - 5}개" if len(posts_data) > 5 else ""}

**패턴 분석**:
{analysis if analysis else "(분석 미지원 - gallery-dl 확인)"}

---
*자동 생성: {datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""

    print(f"=" * 60)
    print(f"  ✅ 완료: {len(posts_data)}개 포스트 분석, {len(account_urls)}개 계정 참고")

    return summary


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        keyword = sys.argv[1]
        result = auto_research(keyword)
        print("\n" + result)
    else:
        print("사용법: python pre_research.py '키워드'")
