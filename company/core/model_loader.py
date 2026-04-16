"""
모델 설정 로더
- 역할(role)에 따른 모델 매핑
- 에이전트명으로 자동 조회
- config 파일 없으면 기본값 사용 (fallback)
"""

import json
import os
from pathlib import Path
from typing import Optional

# 기본값 (config 파일 없을 때 사용)
DEFAULT_CONFIG = {
    "roles": {
        "judge": "claude-opus-4-6",
        "strategist": "claude-sonnet-4-6",
        "content": "claude-haiku-4-5-20251001",
        "data": "claude-haiku-4-5-20251001",
        "research": "sonar-pro",
        "factcheck": "gemini-2.5-flash",
        "budget_strategy": "gpt-4o-mini",
        "prd": "claude-haiku-4-5-20251001",
        "curriculum": "claude-sonnet-4-6"
    }
}

# 에이전트명 → 역할 매핑
AGENT_ROLE_MAP = {
    "minsu": "budget_strategy",           # GPT-4o → GPT-4o-mini
    "jihun": "prd",                       # Sonnet → Haiku
    "copywriter": "content",              # Sonnet → Haiku
    "validator": "strategist",            # Opus → Sonnet
    "curriculum_designer": "curriculum",  # Opus → Sonnet
    "sieun": "strategist",
    "seoyun": "research",
    "taeho": "data",
    "haeun": "factcheck",
    "junhyeok": "judge",
}


class ModelLoader:
    """모델 설정 로더"""

    def __init__(self, config_file: Optional[str] = None):
        self.config = DEFAULT_CONFIG.copy()
        self.config_file = config_file

        # config 파일 경로 결정
        if not config_file:
            # 기본 경로: company/config/model_config.json
            base_dir = Path(__file__).parent.parent
            config_file = base_dir / "config" / "model_config.json"

        # config 파일 로드
        if Path(config_file).exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    # 기본값과 병합 (로드된 값이 우선)
                    if "roles" in loaded:
                        self.config["roles"].update(loaded["roles"])
                    if "cache" in loaded:
                        self.config["cache"] = loaded["cache"]
                    if "tracking" in loaded:
                        self.config["tracking"] = loaded["tracking"]
                    if "overrides" in loaded:
                        self.config["overrides"] = loaded["overrides"]
            except Exception as e:
                print(f"⚠️  모델 설정 로드 실패: {e}, 기본값 사용")

    def get_model_for_role(self, role: str) -> str:
        """
        역할(role)에 따른 모델명 반환

        Args:
            role: judge, strategist, content, data, research, factcheck, etc.

        Returns:
            모델명 문자열
        """
        return self.config["roles"].get(role, "claude-sonnet-4-6")

    def get_model_by_agent(self, agent_name: str) -> str:
        """
        에이전트명으로 모델 조회 (자동 매핑)

        Args:
            agent_name: minsu, jihun, copywriter, etc.

        Returns:
            모델명 문자열
        """
        role = AGENT_ROLE_MAP.get(agent_name, "strategist")
        return self.get_model_for_role(role)

    def get_model(self, agent_or_role: str) -> str:
        """
        에이전트명 또는 역할명으로 모델 조회 (자동 감지)

        Args:
            agent_or_role: minsu (에이전트) 또는 strategist (역할)

        Returns:
            모델명 문자열
        """
        # 에이전트 매핑에 있으면 에이전트로 판단
        if agent_or_role in AGENT_ROLE_MAP:
            return self.get_model_by_agent(agent_or_role)
        # 아니면 역할로 판단
        elif agent_or_role in self.config["roles"]:
            return self.get_model_for_role(agent_or_role)
        # 기본값
        else:
            return "claude-sonnet-4-6"

    def override_model(self, agent_or_role: str, model: str):
        """
        특정 에이전트/역할의 모델 임시 변경 (런타임)

        Args:
            agent_or_role: minsu, strategist, etc.
            model: 바꿀 모델명
        """
        if agent_or_role in AGENT_ROLE_MAP:
            role = AGENT_ROLE_MAP[agent_or_role]
            self.config["roles"][role] = model
        else:
            self.config["roles"][agent_or_role] = model

    def get_cache_config(self) -> dict:
        """캐시 설정 조회"""
        return self.config.get("cache", {"enabled": False})

    def get_tracking_config(self) -> dict:
        """비용 트래킹 설정 조회"""
        return self.config.get("tracking", {"enabled": False})

    def print_config(self):
        """현재 모델 설정 출력 (디버깅용)"""
        print("\n" + "="*60)
        print("📊 모델 설정 현황")
        print("="*60)
        for role, model in self.config["roles"].items():
            print(f"  {role:20s} → {model}")
        print("="*60)


# 글로벌 인스턴스 (편의용)
_loader = None

def get_loader() -> ModelLoader:
    """글로벌 모델 로더 인스턴스 획득"""
    global _loader
    if _loader is None:
        _loader = ModelLoader()
    return _loader

def get_model(agent_or_role: str) -> str:
    """편의 함수: get_loader().get_model()"""
    return get_loader().get_model(agent_or_role)
