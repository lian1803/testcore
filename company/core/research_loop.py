"""
research_loop.py — 에이전트 작업 전 최신 리서치 자동 수집

모든 에이전트가 작업 시작 전에 관련 최신 자료를 Perplexity로 수집.
수집된 자료는 knowledge/trends/에 저장되고, 에이전트 프롬프트에 주입.

파이프라인 캐시와 파일 캐시 이중 레이어:
- 파이프라인 캐시 (인메모리, 같은 실행 내 중복 제거, 빠름)
- 파일 캐시 (디스크, 24시간 TTL, 장기 저장)

사용법:
    from core.research_loop import research_before_task

    # 작업 전 리서치 (결과를 프롬프트에 붙여서 쓰면 됨)
    fresh_knowledge = research_before_task(
        role="마케팅 전략가",
        task="소상공인 대상 인스타그램 마케팅 전략",
        queries=["2026 인스타그램 마케팅 트렌드", "소상공인 SNS 마케팅 성공 사례"]
    )
"""
import os
import json
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

TRENDS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "knowledge", "trends")
CACHE_HOURS = 24  # 같은 쿼리는 24시간 내 재수집 안 함

# 파이프라인 캐시 통합
try:
    from core.cache import get_pipeline_cache
    _pipeline_cache = get_pipeline_cache()
    HAS_PIPELINE_CACHE = True
except ImportError:
    HAS_PIPELINE_CACHE = False
    _pipeline_cache = None


def _ensure_dirs():
    os.makedirs(TRENDS_DIR, exist_ok=True)


def _cache_path(query: str) -> str:
    """쿼리를 파일명으로 변환."""
    safe = "".join(c if c.isalnum() or c in "가-힣_ " else "_" for c in query)[:80]
    return os.path.join(TRENDS_DIR, f"{safe}.json")


def _is_cached(query: str) -> bool:
    """최근 CACHE_HOURS 내에 수집한 적 있으면 캐시 사용."""
    path = _cache_path(query)
    if not os.path.exists(path):
        return False
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        cached_time = datetime.fromisoformat(data.get("timestamp", "2000-01-01"))
        return datetime.now() - cached_time < timedelta(hours=CACHE_HOURS)
    except Exception:
        return False


def _load_cache(query: str) -> str:
    """캐시된 결과 로드."""
    try:
        with open(_cache_path(query), encoding="utf-8") as f:
            data = json.load(f)
        return data.get("content", "")
    except Exception:
        return ""


def _save_cache(query: str, content: str):
    """결과 캐싱."""
    _ensure_dirs()
    try:
        with open(_cache_path(query), "w", encoding="utf-8") as f:
            json.dump({
                "query": query,
                "content": content,
                "timestamp": datetime.now().isoformat(),
            }, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def _query_perplexity(query: str) -> str | None:
    """
    Perplexity에 단일 쿼리 실행. 실패 시 None 반환.

    먼저 파이프라인 캐시를 확인 (같은 실행 내 중복 제거)
    없으면 Perplexity 호출 (API 요청)
    """
    # 파이프라인 캐시 먼저 확인 (같은 실행 내 중복 제거)
    if HAS_PIPELINE_CACHE:
        cache_key = f"perplexity:{query[:50]}"
        cached = _pipeline_cache.get(cache_key)
        if cached is not None:
            return cached

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
                    "content": "최신 트렌드와 실전 사례 위주로 답해. 이론 최소화. 수치/사례/구체적 방법 위주. 한국어로."
                },
                {"role": "user", "content": query}
            ],
            max_tokens=800,
        )
        result = resp.choices[0].message.content

        # 파이프라인 캐시에 저장 (같은 실행 내 재사용)
        if HAS_PIPELINE_CACHE:
            cache_key = f"perplexity:{query[:50]}"
            _pipeline_cache.set(cache_key, result, ttl=300)

        return result
    except Exception as e:
        # 실패 시 None 반환 (context에 "[수집 실패]" 문자열 들어가지 않게)
        return None


def research_before_task(role: str, task: str, queries: list[str] = None, auto_generate: bool = True) -> str:
    """
    에이전트 작업 전 최신 리서치 수집.

    Args:
        role: 에이전트 역할 (예: "마케팅 전략가")
        task: 현재 작업 설명
        queries: 수집할 쿼리 목록. None이면 자동 생성.
        auto_generate: queries가 None일 때 자동으로 쿼리 생성할지

    Returns:
        수집된 최신 지식 텍스트 (프롬프트에 붙여서 쓸 것)
    """
    _ensure_dirs()

    # 쿼리가 없으면 자동 생성
    if not queries and auto_generate:
        queries = [
            f"2026 최신 {task} 트렌드 베스트 프랙티스",
            f"{task} 성공 사례 레퍼런스 2025-2026",
        ]

    if not queries:
        return ""

    print(f"\n  📚 리서치 루프: {len(queries)}개 쿼리 수집 중...")

    results = []
    uncached_queries = []

    # 캐시 확인
    for q in queries:
        if _is_cached(q):
            cached = _load_cache(q)
            results.append(f"### {q}\n{cached}")
            print(f"    ✅ 캐시: {q[:40]}...")
        else:
            uncached_queries.append(q)

    # 캐시 안 된 것만 수집
    if uncached_queries:
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {executor.submit(_query_perplexity, q): q for q in uncached_queries}
            for future in as_completed(futures):
                q = futures[future]
                content = future.result()
                # None 결과는 제외 (실패한 쿼리)
                if content is not None:
                    _save_cache(q, content)
                    results.append(f"### {q}\n{content}")
                    print(f"    🔍 수집: {q[:40]}...")
                else:
                    print(f"    ❌ 수집 실패: {q[:40]}...")

    if not results:
        return ""

    header = f"=== 최신 리서치 ({role}, {datetime.now().strftime('%Y-%m-%d')}) ===\n"
    return header + "\n\n".join(results) + "\n=== 리서치 끝 ===" if results else ""


def auto_research_queries(topic: str, count: int = 3) -> list[str]:
    """주제에 맞는 리서치 쿼리 자동 생성."""
    return [
        f"{topic} 2026 최신 트렌드",
        f"{topic} 성공 사례 레퍼런스",
        f"{topic} 경쟁사 분석 벤치마크",
    ][:count]
