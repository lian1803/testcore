"""
pipeline_cache.py — 파이프라인 인메모리 캐싱 레이어

리안 컴퍼니 파이프라인에서 반복되는 데이터 조회(회사 컨텍스트, Perplexity 쿼리, CRM 조회 등)를
캐싱해서 토큰과 시간을 절감하는 모듈.

캐시는 파이프라인 실행 단위(run)별로 유효하며, 실행 완료 후 자동 초기화.
TTL 지원으로 오래된 데이터는 자동 제거 가능.

사용법:
    from core.cache import PipelineCache

    # 글로벌 캐시 인스턴스
    cache = PipelineCache()

    # 데코레이터 사용
    @cache.cache_it()
    def load_company_context():
        # 첫 호출: 실제 로드 → 캐시
        # 재호출: 캐시에서 바로 반환
        ...

    # 또는 수동 사용
    result = cache.get("key")
    if result is None:
        result = expensive_operation()
        cache.set("key", result)

    # 캐시 통계
    stats = cache.get_stats()
    print(f"Hit: {stats['hits']}, Miss: {stats['misses']}")
"""

import hashlib
import time
from functools import wraps
from typing import Any, Callable, Optional
from datetime import datetime, timedelta


class PipelineCache:
    """파이프라인 실행 단위 인메모리 캐시."""

    def __init__(self, default_ttl_seconds: int = 300):
        """
        Args:
            default_ttl_seconds: 기본 TTL (초). 기본값 300초(5분)
        """
        self.store: dict[str, dict[str, Any]] = {}
        self.default_ttl = default_ttl_seconds
        self.hits = 0
        self.misses = 0

    def _make_key(self, func_or_key: str | Callable, *args, **kwargs) -> str:
        """
        함수명 + 인자를 기반으로 캐시 키 생성.

        Args:
            func_or_key: 함수 이름(str) 또는 문자열 키
            *args: 위치 인자
            **kwargs: 키워드 인자

        Returns:
            캐시 키 (해시된 문자열)
        """
        if isinstance(func_or_key, str):
            # 직접 키 지정 (cache.get("company_context") 등)
            return func_or_key

        # 함수 기반 키 생성: 함수명 + 인자 조합
        func_name = getattr(func_or_key, "__name__", "unknown")
        arg_str = f"{args}:{kwargs}"
        combined = f"{func_name}:{arg_str}"

        # SHA256으로 축약
        hash_obj = hashlib.sha256(combined.encode("utf-8"))
        return f"{func_name}:{hash_obj.hexdigest()[:12]}"

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        캐시에 값 저장.

        Args:
            key: 캐시 키
            value: 저장할 값
            ttl: TTL (초). None이면 default_ttl 사용.
        """
        ttl = ttl if ttl is not None else self.default_ttl
        self.store[key] = {
            "value": value,
            "expires_at": time.time() + ttl,
            "created_at": datetime.now().isoformat(),
        }

    def get(self, key: str) -> Optional[Any]:
        """
        캐시에서 값 조회. 만료됐으면 None 반환 후 삭제.

        Args:
            key: 캐시 키

        Returns:
            캐시된 값, 또는 None
        """
        if key not in self.store:
            self.misses += 1
            return None

        entry = self.store[key]

        # TTL 확인
        if time.time() > entry["expires_at"]:
            del self.store[key]
            self.misses += 1
            return None

        self.hits += 1
        return entry["value"]

    def cache_it(self, ttl: Optional[int] = None) -> Callable:
        """
        데코레이터: 함수 결과를 자동으로 캐싱.

        Args:
            ttl: TTL (초). None이면 default_ttl 사용.

        Returns:
            데코레이터 함수

        Example:
            @cache.cache_it(ttl=600)
            def load_company_context():
                return "..."

            result = load_company_context()  # 첫 호출: 실행 → 캐시
            result = load_company_context()  # 재호출: 캐시에서 반환
        """

        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                # 동일 함수명 + 인자 조합으로 키 생성
                key = self._make_key(func, *args, **kwargs)

                # 캐시 확인
                cached = self.get(key)
                if cached is not None:
                    return cached

                # 캐시 미스 → 함수 실행
                result = func(*args, **kwargs)

                # 결과 캐싱
                self.set(key, result, ttl)

                return result

            return wrapper

        return decorator

    def clear(self) -> None:
        """캐시 초기화."""
        self.store.clear()
        self.hits = 0
        self.misses = 0

    def invalidate(self, key: str) -> None:
        """특정 캐시 항목 삭제."""
        if key in self.store:
            del self.store[key]

    def get_stats(self) -> dict[str, Any]:
        """
        캐시 통계 반환.

        Returns:
            {
                "hits": int,
                "misses": int,
                "hit_rate": float (0.0~1.0),
                "total_keys": int,
                "size_bytes": int (대략)
            }
        """
        total = self.hits + self.misses
        hit_rate = self.hits / total if total > 0 else 0.0

        # 저장된 데이터 크기 추정 (매우 대략적)
        size_bytes = sum(
            len(str(entry.get("value", "")))
            for entry in self.store.values()
        )

        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": round(hit_rate * 100, 1),
            "total_keys": len(self.store),
            "size_bytes": size_bytes,
            "efficiency_percent": round(
                (self.hits / max(total, 1)) * 100, 1
            ),
        }

    def print_stats(self) -> None:
        """캐시 통계를 터미널에 출력."""
        stats = self.get_stats()
        print("\n" + "=" * 60)
        print("📊 캐시 통계")
        print("=" * 60)
        print(f"캐시 Hit: {stats['hits']}")
        print(f"캐시 Miss: {stats['misses']}")
        print(f"Hit Rate: {stats['hit_rate']}%")
        print(f"저장된 항목: {stats['total_keys']}개")
        print(f"예상 메모리: ~{stats['size_bytes'] / 1024:.1f} KB")
        if stats['hits'] + stats['misses'] > 0:
            print(f"효율: {stats['efficiency_percent']}%")
        print("=" * 60)

    def summary_line(self) -> str:
        """한 줄 요약 (로그용)."""
        stats = self.get_stats()
        total = stats["hits"] + stats["misses"]
        if total == 0:
            return "캐시: 미사용"
        return f"캐시 통계: {stats['hits']} hits / {stats['misses']} misses / 효율 {stats['efficiency_percent']}%"


# 글로벌 싱글톤 인스턴스
_global_cache = None


def get_pipeline_cache() -> PipelineCache:
    """글로벌 파이프라인 캐시 인스턴스 반환 (싱글톤)."""
    global _global_cache
    if _global_cache is None:
        _global_cache = PipelineCache()
    return _global_cache


def reset_pipeline_cache() -> None:
    """글로벌 캐시 초기화 (파이프라인 실행 시작 전 호출)."""
    global _global_cache
    if _global_cache is not None:
        _global_cache.clear()
    _global_cache = PipelineCache()
