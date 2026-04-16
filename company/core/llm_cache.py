"""
LLM 캐시 시스템
- 프롬프트 + 모델 기반 해시 캐싱
- TTL 설정 가능 (기본 24시간)
- 파일 기반 저장
- 캐시 실패해도 계속 동작 (graceful)
"""

import hashlib
import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Any, Optional, Callable
import functools


class LLMCache:
    """LLM 응답 캐싱"""

    def __init__(self, cache_dir: str = "./cache", ttl_hours: int = 24):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = timedelta(hours=ttl_hours)

    def _get_key(self, prompt: str, model: str) -> str:
        """프롬프트 + 모델로 고유 키 생성"""
        content = f"{model}:{prompt}".encode('utf-8')
        return hashlib.md5(content).hexdigest()

    def get(self, prompt: str, model: str) -> Optional[str]:
        """
        캐시에서 조회

        Args:
            prompt: 프롬프트
            model: 모델명

        Returns:
            캐시된 응답 또는 None
        """
        key = self._get_key(prompt, model)
        cache_file = self.cache_dir / f"{key}.json"

        if not cache_file.exists():
            return None

        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # TTL 확인
            created_at = datetime.fromisoformat(data["timestamp"])
            if datetime.now() - created_at > self.ttl:
                cache_file.unlink()  # 만료된 캐시 삭제
                return None

            return data["response"]
        except Exception:
            return None

    def set(self, prompt: str, model: str, response: str) -> bool:
        """
        캐시에 저장

        Args:
            prompt: 프롬프트
            model: 모델명
            response: 응답 텍스트

        Returns:
            저장 성공 여부
        """
        key = self._get_key(prompt, model)
        cache_file = self.cache_dir / f"{key}.json"

        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "timestamp": datetime.now().isoformat(),
                    "prompt": prompt[:200],  # 디버깅용 프롬프트 일부 저장
                    "model": model,
                    "response": response
                }, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False

    def clear_expired(self):
        """만료된 캐시 정리"""
        count = 0
        try:
            for cache_file in self.cache_dir.glob("*.json"):
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    created_at = datetime.fromisoformat(data["timestamp"])
                    if datetime.now() - created_at > self.ttl:
                        cache_file.unlink()
                        count += 1
                except Exception:
                    pass
        except Exception:
            pass
        return count

    def clear_all(self):
        """전체 캐시 삭제"""
        count = 0
        try:
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
                count += 1
        except Exception:
            pass
        return count

    def get_stats(self) -> dict:
        """캐시 통계"""
        count = 0
        total_size = 0
        try:
            for cache_file in self.cache_dir.glob("*.json"):
                count += 1
                total_size += cache_file.stat().st_size
        except Exception:
            pass

        return {
            "cache_files": count,
            "total_size_mb": round(total_size / 1024 / 1024, 2),
            "cache_dir": str(self.cache_dir)
        }


# 글로벌 캐시 인스턴스
_cache = None

def get_cache(cache_dir: str = "./cache", ttl_hours: int = 24) -> LLMCache:
    """글로벌 캐시 인스턴스 획득"""
    global _cache
    if _cache is None:
        _cache = LLMCache(cache_dir, ttl_hours)
    return _cache


def cached_llm_call(
    cache_enabled: bool = True,
    ttl_hours: int = 24
) -> Callable:
    """
    LLM 호출 결과를 자동으로 캐싱하는 데코레이터

    사용 예:
        @cached_llm_call()
        def get_strategy(idea: str, model: str) -> str:
            # LLM 호출 로직
            ...

    Args:
        cache_enabled: 캐싱 활성화 여부
        ttl_hours: 캐시 유효 시간 (시간)

    Returns:
        데코레이터 함수
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not cache_enabled:
                return func(*args, **kwargs)

            # 캐시 키 생성용 텍스트 추출
            # args[0]를 프롬프트로 가정 (함수마다 다를 수 있음)
            cache = get_cache(ttl_hours=ttl_hours)

            # 프롬프트 재구성 (간단한 예시)
            try:
                prompt_text = str(args[0]) if args else ""
                model_text = kwargs.get("model", args[1] if len(args) > 1 else "")

                # 캐시 조회
                cached = cache.get(prompt_text, str(model_text))
                if cached:
                    return cached
            except Exception:
                pass

            # 캐시 미스 → 함수 실행
            result = func(*args, **kwargs)

            # 캐시 저장
            try:
                prompt_text = str(args[0]) if args else ""
                model_text = kwargs.get("model", args[1] if len(args) > 1 else "")
                cache.set(prompt_text, str(model_text), str(result))
            except Exception:
                pass

            return result

        return wrapper

    return decorator
