"""
model_router.py — 작업 타입별 최적 모델 자동 라우팅

사용법:
    from core.model_router import route, call_routed

    # 어떤 모델이 선택되는지 확인
    model_name, provider = route("vision")
    print(model_name)  # "gemini-2.5-flash"

    # 바로 호출
    result = call_routed("creative_writing", prompt="블로그 글 써줘")
    result = call_routed("vision", prompt="이 이미지 분석해줘", image_path="img.png")

라우팅 원칙:
- Claude 구독 중 → Claude를 주력으로
- 각 AI의 강점이 명확한 경우 → 해당 AI로
- 실시간 정보 필요 → Perplexity
- 멀티모달(이미지/영상) → Gemini
- 코딩/구조화 출력 → GPT-4.1
- 크리티컬 판단 → Claude Opus
"""

import os
import base64
from enum import Enum
from typing import Optional
from dataclasses import dataclass
from core.models import (
    CLAUDE_OPUS, CLAUDE_SONNET, CLAUDE_HAIKU,
    GEMINI_FLASH, GEMINI_PRO, GEMINI_31_PRO, GEMINI_31_FLASH,
    GPT4O, GPT4O_MINI, GPT41, GPT41_MINI, GPT41_NANO,
    O4_MINI, O3_MINI,
    SONAR_PRO, SONAR, SONAR_REASONING,
)


# ── 작업 타입 정의 ──────────────────────────────────────────────

class TaskType(str, Enum):
    # Claude 주력
    CRITICAL_DECISION   = "critical_decision"    # GO/NO-GO, 최종 판단 → Opus
    STRATEGY            = "strategy"             # 전략 수립, 기획 → Sonnet
    LONG_WRITING        = "long_writing"         # 긴 글쓰기, 보고서 → Sonnet
    SHORT_WRITING       = "short_writing"        # 짧은 캡션, DM → Haiku
    ORCHESTRATION       = "orchestration"        # 에이전트 오케스트레이션 → Sonnet
    DEBATE              = "debate"               # 토론·검증 → Sonnet
    WEEKLY_REVIEW       = "weekly_review"        # 주간 리뷰 → Sonnet

    # Gemini 강점
    VISION              = "vision"               # 이미지 분석 → Gemini Flash
    VIDEO_ANALYSIS      = "video_analysis"       # 영상 분석 → Gemini Flash
    LONG_DOC            = "long_doc"             # 긴 문서 분석(1M token) → Gemini Pro
    FACT_CHECK          = "fact_check"           # 팩트 검증 → Gemini Pro

    # GPT 강점
    CODING              = "coding"               # 코드 작성 → GPT-4.1
    STRUCTURED_OUTPUT   = "structured_output"    # JSON/표 등 구조화 → GPT-4.1
    CREATIVE_WRITING    = "creative_writing"     # 창의적 카피 → GPT-4o
    TRANSLATION         = "translation"          # 번역·다국어 → GPT-4o

    # Perplexity 강점
    REALTIME_RESEARCH   = "realtime_research"    # 실시간 웹 검색 → Sonar Pro
    TREND_SCOUTING      = "trend_scouting"       # 트렌드 탐색 → Sonar Pro
    COMPETITOR_RESEARCH = "competitor_research"  # 경쟁사 조사 → Sonar Pro

    # 추론 특화 (수학·논리·복잡한 계획)
    REASONING           = "reasoning"            # 복잡한 추론 → o4-mini
    RESEARCH_REASONING  = "research_reasoning"   # 실시간 검색 + 추론 → Sonar Reasoning

    # 속도/비용 최적화
    FAST_CHEAP          = "fast_cheap"           # 빠름+저렴 → GPT-4.1-nano
    DAILY_CONTENT       = "daily_content"        # 매일 반복 콘텐츠 → Haiku


# ── 라우팅 테이블 ────────────────────────────────────────────────

@dataclass
class ModelConfig:
    model: str
    provider: str   # "anthropic" | "openai" | "google" | "perplexity"
    max_tokens: int
    temperature: float
    reason: str     # 왜 이 모델인지 (디버깅용)


ROUTING_TABLE: dict[TaskType, ModelConfig] = {
    # ── Claude 주력 ─────────────────────────────────────────
    TaskType.CRITICAL_DECISION: ModelConfig(
        CLAUDE_OPUS, "anthropic", 2000, 0.2,
        "최종 의사결정 — 정확도 최우선, Opus만 쓴다"
    ),
    TaskType.STRATEGY: ModelConfig(
        CLAUDE_SONNET, "anthropic", 3000, 0.5,
        "전략 수립 — Sonnet이 비용/성능 균형 최고"
    ),
    TaskType.LONG_WRITING: ModelConfig(
        CLAUDE_SONNET, "anthropic", 4000, 0.6,
        "긴 보고서/기획서 — Sonnet이 일관성 좋음"
    ),
    TaskType.SHORT_WRITING: ModelConfig(
        CLAUDE_HAIKU, "anthropic", 500, 0.8,
        "짧은 캡션/DM — Haiku로 충분, 빠름"
    ),
    TaskType.ORCHESTRATION: ModelConfig(
        CLAUDE_SONNET, "anthropic", 2000, 0.3,
        "에이전트 오케스트레이션 — Sonnet이 지시 이해력 최고"
    ),
    TaskType.DEBATE: ModelConfig(
        CLAUDE_SONNET, "anthropic", 2000, 0.4,
        "토론/검증 — Sonnet이 논리 구조 탄탄"
    ),
    TaskType.WEEKLY_REVIEW: ModelConfig(
        CLAUDE_SONNET, "anthropic", 2500, 0.3,
        "주간 리뷰 — Sonnet이 데이터 해석 좋음"
    ),
    TaskType.DAILY_CONTENT: ModelConfig(
        CLAUDE_HAIKU, "anthropic", 800, 0.8,
        "매일 반복 콘텐츠 — Haiku로 비용 절감"
    ),

    # ── Gemini 강점 ──────────────────────────────────────────
    TaskType.VISION: ModelConfig(
        GEMINI_FLASH, "google", 2000, 0.4,
        "이미지 분석 — Gemini Flash가 멀티모달 최고 가성비"
    ),
    TaskType.VIDEO_ANALYSIS: ModelConfig(
        GEMINI_FLASH, "google", 3000, 0.4,
        "영상 분석 — Gemini만 Files API로 영상 직접 처리"
    ),
    TaskType.LONG_DOC: ModelConfig(
        GEMINI_PRO, "google", 4000, 0.3,
        "긴 문서 분석 — Gemini Pro 1M token context"
    ),
    TaskType.FACT_CHECK: ModelConfig(
        GEMINI_PRO, "google", 2000, 0.1,
        "팩트 검증 — Gemini Pro가 정확도 높음"
    ),

    # ── GPT 강점 ─────────────────────────────────────────────
    TaskType.CODING: ModelConfig(
        GPT41, "openai", 4000, 0.2,
        "코드 작성 — GPT-4.1이 코딩 벤치마크 최고"
    ),
    TaskType.STRUCTURED_OUTPUT: ModelConfig(
        GPT41, "openai", 3000, 0.1,
        "구조화 출력 — GPT-4.1 JSON mode 신뢰성 높음"
    ),
    TaskType.CREATIVE_WRITING: ModelConfig(
        GPT4O, "openai", 2000, 0.9,
        "창의적 카피 — GPT-4o가 한국어 뉘앙스 자연스러움"
    ),
    TaskType.TRANSLATION: ModelConfig(
        GPT4O, "openai", 2000, 0.3,
        "번역/다국어 — GPT-4o 한국어 품질 최상"
    ),

    # ── Perplexity 강점 ──────────────────────────────────────
    TaskType.REALTIME_RESEARCH: ModelConfig(
        SONAR_PRO, "perplexity", 2000, 0.3,
        "실시간 웹 검색 — Perplexity만 최신 정보 접근"
    ),
    TaskType.TREND_SCOUTING: ModelConfig(
        SONAR_PRO, "perplexity", 1500, 0.3,
        "트렌드 탐색 — 실시간 + 출처 인용"
    ),
    TaskType.COMPETITOR_RESEARCH: ModelConfig(
        SONAR_PRO, "perplexity", 2000, 0.2,
        "경쟁사 조사 — 최신 공개 정보 수집"
    ),

    # ── 추론 특화 ────────────────────────────────────────────
    TaskType.REASONING: ModelConfig(
        O4_MINI, "openai", 4000, 1.0,
        "복잡한 추론/수학/논리 — o4-mini가 추론 벤치마크 최상"
    ),
    TaskType.RESEARCH_REASONING: ModelConfig(
        SONAR_REASONING, "perplexity", 3000, 0.3,
        "실시간 검색 + 깊은 추론 — Sonar Reasoning Pro"
    ),

    # ── 속도/비용 최적화 ──────────────────────────────────────
    TaskType.FAST_CHEAP: ModelConfig(
        GPT41_NANO, "openai", 500, 0.5,
        "빠름+저렴 최우선 — GPT-4.1-nano"
    ),
}


# ── 라우팅 함수 ──────────────────────────────────────────────────

def route(task_type: str | TaskType) -> ModelConfig:
    """
    작업 타입 → ModelConfig 반환.

    예:
        cfg = route("vision")
        cfg = route(TaskType.CRITICAL_DECISION)
    """
    if isinstance(task_type, str):
        try:
            task_type = TaskType(task_type)
        except ValueError:
            # 모르는 타입이면 기본값 Sonnet
            return ModelConfig(
                CLAUDE_SONNET, "anthropic", 2000, 0.5,
                f"알 수 없는 task_type '{task_type}' — Sonnet 기본값 사용"
            )
    return ROUTING_TABLE[task_type]


def route_info(task_type: str | TaskType) -> str:
    """라우팅 결과를 사람이 읽기 좋은 형식으로 반환."""
    cfg = route(task_type)
    return (
        f"[{task_type}]\n"
        f"  모델: {cfg.model} ({cfg.provider})\n"
        f"  이유: {cfg.reason}\n"
        f"  max_tokens: {cfg.max_tokens}, temperature: {cfg.temperature}"
    )


# ── 실제 호출 래퍼 ────────────────────────────────────────────────

def call_routed(
    task_type: str | TaskType,
    system: str = "",
    prompt: str = "",
    image_path: Optional[str] = None,
    stream: bool = False,
) -> str:
    """
    라우팅된 모델로 실제 API 호출.

    Args:
        task_type: 작업 타입 (TaskType enum 또는 문자열)
        system: 시스템 프롬프트
        prompt: 사용자 메시지
        image_path: 이미지 파일 경로 (vision 작업에만)
        stream: True면 스트리밍 출력

    Returns:
        응답 텍스트
    """
    cfg = route(task_type)
    print(f"[라우터] {cfg.model} ({cfg.provider}) — {cfg.reason}")

    if cfg.provider == "anthropic":
        return _call_anthropic(cfg, system, prompt, image_path, stream)
    elif cfg.provider == "google":
        return _call_google(cfg, system, prompt, image_path)
    elif cfg.provider == "openai":
        return _call_openai(cfg, system, prompt, image_path)
    elif cfg.provider == "perplexity":
        return _call_perplexity(cfg, system, prompt)
    else:
        raise ValueError(f"알 수 없는 provider: {cfg.provider}")


def _call_anthropic(cfg: ModelConfig, system: str, prompt: str,
                    image_path: Optional[str], stream: bool) -> str:
    import anthropic
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    content = []
    if image_path:
        with open(image_path, "rb") as f:
            img_data = base64.b64encode(f.read()).decode()
        ext = image_path.rsplit(".", 1)[-1].lower()
        mime = {"jpg": "image/jpeg", "jpeg": "image/jpeg",
                "png": "image/png", "gif": "image/gif",
                "webp": "image/webp"}.get(ext, "image/jpeg")
        content.append({"type": "image", "source": {
            "type": "base64", "media_type": mime, "data": img_data
        }})
    content.append({"type": "text", "text": prompt})

    kwargs = dict(
        model=cfg.model,
        max_tokens=cfg.max_tokens,
        system=system,
        messages=[{"role": "user", "content": content}],
        temperature=cfg.temperature,
    )

    if stream:
        result = ""
        with client.messages.stream(**kwargs) as s:
            for text in s.text_stream:
                print(text, end="", flush=True)
                result += text
        print()
        return result
    else:
        resp = client.messages.create(**kwargs)
        return resp.content[0].text


def _call_google(cfg: ModelConfig, system: str, prompt: str,
                 image_path: Optional[str]) -> str:
    import google.genai as genai
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

    parts = []
    if system:
        parts.append(f"[시스템]\n{system}\n\n[사용자]\n{prompt}")
    else:
        parts.append(prompt)

    if image_path:
        with open(image_path, "rb") as f:
            img_bytes = f.read()
        ext = image_path.rsplit(".", 1)[-1].lower()
        mime = {"jpg": "image/jpeg", "jpeg": "image/jpeg",
                "png": "image/png", "webp": "image/webp"}.get(ext, "image/jpeg")
        parts.append(genai.types.Part.from_bytes(data=img_bytes, mime_type=mime))

    resp = client.models.generate_content(
        model=cfg.model,
        contents=parts,
        config=genai.types.GenerateContentConfig(
            max_output_tokens=cfg.max_tokens,
            temperature=cfg.temperature,
        )
    )
    return resp.text


def _call_openai(cfg: ModelConfig, system: str, prompt: str,
                 image_path: Optional[str]) -> str:
    import openai
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    messages = []
    if system:
        messages.append({"role": "system", "content": system})

    if image_path:
        with open(image_path, "rb") as f:
            img_data = base64.b64encode(f.read()).decode()
        ext = image_path.rsplit(".", 1)[-1].lower()
        mime = {"jpg": "image/jpeg", "jpeg": "image/jpeg",
                "png": "image/png", "webp": "image/webp"}.get(ext, "image/jpeg")
        messages.append({"role": "user", "content": [
            {"type": "image_url", "image_url": {
                "url": f"data:{mime};base64,{img_data}"
            }},
            {"type": "text", "text": prompt}
        ]})
    else:
        messages.append({"role": "user", "content": prompt})

    resp = client.chat.completions.create(
        model=cfg.model,
        messages=messages,
        max_tokens=cfg.max_tokens,
        temperature=cfg.temperature,
    )
    return resp.choices[0].message.content


def _call_perplexity(cfg: ModelConfig, system: str, prompt: str) -> str:
    import requests
    headers = {
        "Authorization": f"Bearer {os.getenv('PERPLEXITY_API_KEY')}",
        "Content-Type": "application/json",
    }
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": cfg.model,
        "messages": messages,
        "max_tokens": cfg.max_tokens,
        "temperature": cfg.temperature,
    }
    resp = requests.post(
        "https://api.perplexity.ai/chat/completions",
        headers=headers, json=payload, timeout=30
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


# ── CLI: 라우팅 테이블 출력 ───────────────────────────────────────

if __name__ == "__main__":
    print("=" * 65)
    print("  [LIANCP] Model Routing Table")
    print("=" * 65)
    for task in TaskType:
        cfg = ROUTING_TABLE.get(task)
        if cfg:
            provider_tag = {
                "anthropic": "[Claude]",
                "google":    "[Gemini]",
                "openai":    "[GPT  ]",
                "perplexity": "[Perpl]",
            }.get(cfg.provider, "[?????]")
            print(f"{provider_tag} {task.value:<25} -> {cfg.model}")
    print()
    print("Usage: from core.model_router import route, call_routed")
