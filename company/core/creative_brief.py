"""
creative_brief.py — 프로젝트 컨셉 → 크리에이티브 오더 자동 생성

프로젝트 설명을 받아서:
1. 브랜드 컨셉 (메타포, 감정, 비주얼 세계관)
2. 색상 팔레트 (DESIGN.md 58개 레퍼런스 참고)
3. 이펙트 선택 (배경 40 + 텍스트 23 + 커서/애니메이션 30 + 컴포넌트 37)
4. 도구 오더 (nano-banana 프롬프트, Stitch 섹션, Veo 스타일, Anime.js 커스텀)
5. 사이트 구조

사용법:
    from core.creative_brief import generate, print_brief

    brief = generate("웰니스 코칭, 40대 여성, 따뜻한 성장")
    print_brief(brief)

경쟁사 URL 분석 (dembrandt 설치 시):
    brief = generate("꽃집 사이트", competitor_urls=["https://competitor.com"])
"""

import os
import json
import subprocess
import shutil
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

BASE_DIR = Path(__file__).parent.parent
DS_DIR = Path(__file__).parent.parent.parent / "design_system"

_CLIENT = None


def _get_client():
    global _CLIENT
    if _CLIENT is None:
        _CLIENT = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    return _CLIENT


# ===== DESIGN.md 레퍼런스 매핑 =====

STYLE_TO_REFS = {
    "clean_futuristic": ["stripe", "linear.app", "vercel", "cursor", "supabase"],
    "bold_expressive": ["framer", "figma", "nvidia", "runway", "elevenlabs"],
    "minimal_elegant": ["apple", "airbnb", "ferrari", "bmw", "lamborghini"],
    "playful_dynamic": ["spotify", "notion", "miro", "pinterest", "coinbase"],
}

MOOD_TO_REFS = {
    # 격동/강렬 → 스포츠카/테크
    "격동": ["ferrari", "lamborghini", "nvidia", "spacex"],
    "강렬": ["ferrari", "lamborghini", "nvidia", "spacex"],
    "다이내믹": ["framer", "figma", "nvidia", "spotify"],
    "임팩트": ["tesla", "spacex", "nvidia", "ferrari"],
    # 우아/프리미엄 → 럭셔리
    "우아": ["apple", "airbnb", "bmw", "ferrari"],
    "프리미엄": ["apple", "bmw", "ferrari", "stripe"],
    "고급": ["apple", "ferrari", "bmw", "lamborghini"],
    # 따뜻/자연
    "따뜻": ["airbnb", "apple", "notion"],
    "자연": ["airbnb", "apple"],
    "부드러운": ["apple", "notion", "cal"],
    # 미래/테크
    "미래": ["linear.app", "cursor", "vercel", "nvidia"],
    "테크": ["stripe", "linear.app", "vercel", "cursor"],
    "사이버": ["nvidia", "coinbase", "kraken"],
    # 미니멀/클린
    "미니멀": ["notion", "linear.app", "cal", "apple"],
    "클린": ["stripe", "vercel", "notion"],
    # 재미/플레이풀
    "재미": ["spotify", "pinterest", "miro"],
    "친근": ["airbnb", "notion", "spotify"],
    # 신뢰/안정
    "신뢰": ["ibm", "stripe", "wise", "hashicorp"],
    "안정": ["ibm", "hashicorp", "wise"],
}

INDUSTRY_TO_REFS = {
    "consulting": ["ibm", "hashicorp", "stripe"],
    "legal": ["ibm", "hashicorp", "wise"],
    "saas": ["stripe", "linear.app", "vercel", "cursor"],
    "coaching": ["airbnb", "apple", "cal"],
    "wellness": ["airbnb", "apple"],
    "marketing": ["figma", "framer", "posthog"],
    "medical": ["notion", "cal", "wise"],
    "fintech": ["stripe", "revolut", "coinbase", "kraken"],
    "luxury": ["ferrari", "bmw", "lamborghini", "renault", "tesla"],
    "ai": ["claude", "cohere", "replicate", "mistral.ai", "together.ai"],
    "ecommerce": ["spotify", "airbnb", "pinterest"],
    "education": ["notion", "miro", "cal"],
    "restaurant": ["airbnb", "apple"],
    "florist": ["airbnb", "apple"],
    "beauty": ["apple", "airbnb", "ferrari"],
    "realestate": ["bmw", "wise", "revolut"],
    "startup": ["linear.app", "vercel", "cursor", "framer"],
}


def _load_design_ref(brand: str, max_chars: int = 4000) -> Optional[str]:
    """DESIGN.md 로드 (truncate)."""
    path = DS_DIR / "design-systems" / "design-md" / brand / "DESIGN.md"
    if not path.exists():
        return None
    try:
        text = path.read_text(encoding="utf-8")
        if len(text) > max_chars:
            text = text[:max_chars] + f"\n... [{len(text) - max_chars}자 생략]"
        return text
    except Exception:
        return None


def _extract_competitor_tokens(urls: list) -> Optional[str]:
    """dembrandt로 경쟁사 디자인 토큰 추출 (설치된 경우만)."""
    if not shutil.which("dembrandt"):
        return None
    results = []
    for url in urls[:3]:  # 최대 3개
        try:
            r = subprocess.run(
                ["dembrandt", url, "--format", "json"],
                capture_output=True, text=True, timeout=30,
                encoding="utf-8", errors="replace"
            )
            if r.returncode == 0 and r.stdout.strip():
                results.append(f"## {url}\n{r.stdout[:2000]}")
        except Exception:
            pass
    return "\n\n".join(results) if results else None


SYSTEM_PROMPT = """당신은 세계적 수준의 크리에이티브 디렉터입니다.

프로젝트 설명을 읽고, 브랜드에 완벽히 맞는 크리에이티브 오더를 생성합니다.
단순한 "어두운 배경 + 파티클"이 아니라, 브랜드 본질에서 출발한 독창적 컨셉을 만듭니다.

## 반드시 JSON만 출력하세요.

## 핵심 원칙
1. 컨셉 먼저: "이 브랜드가 전달하고 싶은 감정은 무엇인가?" → 거기서 비주얼 메타포 도출
2. 메타포가 이펙트를 결정: "성장" → SoftAurora + FallingText (꽃잎), "정밀" → GridScan + DecryptedText
3. 같은 업종이어도 컨셉이 다르면 완전히 다른 결과가 나와야 함
4. 레퍼런스 DESIGN.md의 색상/폰트/그림자 수치를 실제로 참고
5. 커스텀 애니메이션이 필요하면 Anime.js SVG 모핑 등 구체적 지시

## 사용 가능한 배경 (40개)
Aurora, Balatro, Ballpit, Beams, ColorBends, DarkVeil, Dither, DotGrid, EvilEye,
FaultyTerminal, FloatingLines, Galaxy, GradientBlinds, Grainient, GridDistortion,
GridMotion, GridScan, Hyperspeed, Iridescence, LetterGlitch, Lightning, LightPillar,
LightRays, LineWaves, LiquidChrome, LiquidEther, Orb, Particles, PixelBlast,
PixelSnow, Plasma, Prism, PrismaticBurst, Radar, RippleGrid, ShapeGrid, Silk,
SoftAurora, Threads, Waves

## 사용 가능한 텍스트 애니메이션 (23개)
ASCIIText, BlurText, CircularText, CountUp, CurvedLoop, DecryptedText, FallingText,
FuzzyText, GlitchText, GradientText, RotatingText, ScrambledText, ScrollFloat,
ScrollReveal, ScrollVelocity, ShinyText, Shuffle, SplitText, TextCursor, TextPressure,
TextType, TrueFocus, VariableProximity

## 사용 가능한 커서/애니메이션 (30개)
AnimatedContent, Antigravity, BlobCursor, ClickSpark, Crosshair, Cubes, ElectricBorder,
FadeContent, GhostCursor, GlareHover, GradualBlur, ImageTrail, LaserFlow, LogoLoop,
MagicRings, Magnet, MagnetLines, MetaBalls, MetallicPaint, Noise, OrbitImages,
PixelTrail, PixelTransition, Ribbons, ShapeBlur, SplashCursor, StarBorder, StickerPeel,
TargetCursor

## 사용 가능한 UI 컴포넌트 (37개)
AnimatedList, BorderGlow, BounceCards, BubbleMenu, CardNav, CardSwap, Carousel,
ChromaGrid, CircularGallery, Counter, DecayCard, Dock, DomeGallery, ElasticSlider,
FlowingMenu, FluidGlass, FlyingPosters, Folder, GlassIcons, GlassSurface, GooeyNav,
InfiniteMenu, Lanyard, MagicBento, Masonry, ModelViewer, PillNav, PixelCard,
ProfileCard, ReflectiveCard, ScrollStack, SpotlightCard, Stack, StaggeredMenu,
Stepper, TiltedCard

## 사용 가능한 도구
- nano-banana: Gemini Imagen 4.0 이미지 생성 (영어 프롬프트 필요)
- Stitch MCP: UI 섹션 자동 생성 (glassmorphism, tailwind, dark/light)
- Veo: 이미지→영상 변환 (8초, style: abstract_dark/luxury/tech/nature)
- Anime.js: SVG path 모핑, 요소 시퀀스 애니메이션 (꽃 피어남, 로고 형성 등)
- Three.js: 3D 씬 (파티클, 모델, 환경) — 원본 소스 있음

## 출력 형식 (JSON)
{
  "concept": {
    "name": "2~4글자 컨셉명",
    "metaphor": "이 브랜드의 비주얼 세계관을 한 문장으로",
    "emotion_keywords": ["감정1", "감정2", "감정3"],
    "visual_world": "이 사이트에 들어갔을 때 느껴야 할 공간을 묘사"
  },
  "palette": {
    "primary": "#hex",
    "secondary": "#hex",
    "accent": "#hex",
    "background": "#hex",
    "text": "#hex",
    "muted": "#hex",
    "reasoning": "어떤 DESIGN.md를 참고했고 왜 이 색인지"
  },
  "typography": {
    "heading_font": "Google Fonts에서 사용 가능한 폰트",
    "body_font": "Google Fonts에서 사용 가능한 폰트",
    "heading_weight": "weight",
    "style_note": "타이포 전략 한 줄"
  },
  "effects": {
    "background": {"name": "이펙트명", "reason": "왜 이 배경인지", "color_override": "색상 조정 방향"},
    "text_hero": {"name": "이펙트명", "reason": "왜"},
    "text_section": {"name": "이펙트명", "reason": "왜"},
    "cursor": {"name": "이펙트명", "reason": "왜"},
    "hover": {"name": "이펙트명", "reason": "왜"},
    "extra": ["추가 이펙트명"]
  },
  "tools": {
    "nano_banana": {
      "hero_prompt": "영어 이미지 생성 프롬프트 (히어로용)",
      "section_prompts": {"about": "프롬프트", "gallery": "프롬프트"}
    },
    "stitch": {
      "sections": ["Stitch가 생성할 섹션명"],
      "style_note": "Stitch에게 전달할 스타일 지시"
    },
    "veo": {
      "use": true/false,
      "style": "abstract_dark/luxury/tech/nature",
      "prompt": "영상 설명"
    },
    "anime_js": {
      "use": true/false,
      "description": "커스텀 애니메이션 구체 설명"
    }
  },
  "site_structure": [
    {"section": "hero", "layout": "레이아웃", "content": "구체적 내용 지시"},
    {"section": "이름", "layout": "레이아웃", "content": "구체적 내용 지시"}
  ],
  "design_refs_used": ["참고한 브랜드"],
  "ref_insights": "레퍼런스에서 구체적으로 뭘 가져왔는지"
}
"""


def generate(
    project_description: str,
    competitor_urls: list = None,
    style_hint: str = None,
) -> dict:
    """프로젝트 설명 → 크리에이티브 브리프 생성.

    Args:
        project_description: 프로젝트 설명 (업종, 타겟, 목적 등)
        competitor_urls: 경쟁사 URL 리스트 (dembrandt 설치 시 자동 분석)
        style_hint: 스타일 힌트 (예: "따뜻한", "미래적", "럭셔리")

    Returns:
        크리에이티브 브리프 딕셔너리
    """
    client = _get_client()

    # 1. design_router로 분류 (가능하면)
    plan = None
    try:
        from core.design_router import route
        plan = route(project_description)
    except Exception:
        pass

    # 2. 관련 DESIGN.md 로드
    refs_to_load = set()

    # 스타일 기반 레퍼런스
    if plan and plan.get("style_family"):
        sf = plan["style_family"]
        refs_to_load.update(STYLE_TO_REFS.get(sf, [])[:3])

    # 프로젝트 설명에서 업종 키워드 매칭
    desc_lower = project_description.lower()
    for industry, brands in INDUSTRY_TO_REFS.items():
        if industry in desc_lower:
            refs_to_load.update(brands[:3])

    # style_hint에서 무드 키워드 매칭 (업종보다 우선)
    hint_refs = set()
    if style_hint:
        hint_lower = style_hint.lower()
        for mood, brands in MOOD_TO_REFS.items():
            if mood in hint_lower:
                hint_refs.update(brands[:3])
    # 무드 힌트로 찾은 레퍼런스가 있으면 업종 레퍼런스 대체
    if hint_refs:
        refs_to_load = hint_refs

    # 기본값: stripe, apple (없으면)
    if not refs_to_load:
        refs_to_load = {"stripe", "apple", "linear.app"}

    # 최대 5개
    refs_to_load = list(refs_to_load)[:5]

    ref_contents = []
    for brand in refs_to_load:
        content = _load_design_ref(brand, max_chars=3000)
        if content:
            ref_contents.append(f"### {brand} DESIGN.md\n{content}")

    # 3. 경쟁사 토큰 추출 (옵션)
    competitor_context = ""
    if competitor_urls:
        tokens = _extract_competitor_tokens(competitor_urls)
        if tokens:
            competitor_context = f"\n\n## 경쟁사 디자인 토큰 (dembrandt 추출)\n{tokens}"

    # 4. 프롬프트 조합
    user_msg = f"""## 프로젝트 설명
{project_description}
"""
    if style_hint:
        user_msg += f"\n## 스타일 힌트\n{style_hint}\n"

    if plan:
        user_msg += f"""
## 자동 분류 결과 (design_router)
- site_type: {plan.get('site_type')}
- style_family: {plan.get('style_family')}
- 3d_level: {plan.get('3d_level')}
- interaction_density: {plan.get('interaction_density')}
"""

    if ref_contents:
        user_msg += f"""
## 참고 DESIGN.md 레퍼런스 ({len(ref_contents)}개)
실제 색상 코드, 폰트, 그림자 수치를 참고해서 palette를 결정하세요.

{chr(10).join(ref_contents)}
"""

    if competitor_context:
        user_msg += competitor_context

    user_msg += "\n이 프로젝트의 크리에이티브 브리프를 JSON으로 생성해주세요."

    # 5. Claude API 호출
    print("[creative_brief] 크리에이티브 브리프 생성 중...")
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_msg}],
    )

    response_text = message.content[0].text.strip()

    # JSON 파싱
    import re
    if "```" in response_text:
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", response_text, re.DOTALL)
        if match:
            response_text = match.group(1).strip()

    brief = json.loads(response_text)

    # 메타데이터 추가
    brief["_meta"] = {
        "design_refs_loaded": refs_to_load,
        "design_router_plan": plan,
        "competitor_analyzed": bool(competitor_urls and competitor_context),
    }

    print(f"[creative_brief] 완료: 컨셉 '{brief.get('concept', {}).get('name', '?')}'")
    return brief


def print_brief(brief: dict):
    """브리프를 읽기 좋게 출력."""
    c = brief.get("concept", {})
    p = brief.get("palette", {})
    t = brief.get("typography", {})
    e = brief.get("effects", {})
    tools = brief.get("tools", {})

    print("\n" + "=" * 60)
    print(f"  CREATIVE BRIEF: {c.get('name', '?')}")
    print("=" * 60)

    print(f"\n  Metaphor: {c.get('metaphor', '?')}")
    print(f"  Emotion:  {', '.join(c.get('emotion_keywords', []))}")
    print(f"  World:    {c.get('visual_world', '?')}")

    print(f"\n  [PALETTE]")
    for k in ["primary", "secondary", "accent", "background", "text"]:
        print(f"    {k:12}: {p.get(k, '?')}")
    print(f"    reason:      {p.get('reasoning', '?')[:80]}")

    print(f"\n  [TYPOGRAPHY]")
    print(f"    heading: {t.get('heading_font', '?')} ({t.get('heading_weight', '?')})")
    print(f"    body:    {t.get('body_font', '?')}")

    print(f"\n  [EFFECTS]")
    for k in ["background", "text_hero", "text_section", "cursor", "hover"]:
        eff = e.get(k, {})
        if eff:
            print(f"    {k:14}: {eff.get('name', '?'):20} — {eff.get('reason', '')[:50]}")

    print(f"\n  [TOOLS]")
    nb = tools.get("nano_banana", {})
    if nb:
        print(f"    nano-banana: {nb.get('hero_prompt', '?')[:70]}...")
    st = tools.get("stitch", {})
    if st:
        print(f"    stitch:      {', '.join(st.get('sections', []))}")
    veo = tools.get("veo", {})
    if veo and veo.get("use"):
        print(f"    veo:         {veo.get('style', '?')} — {veo.get('prompt', '?')[:50]}")
    aj = tools.get("anime_js", {})
    if aj and aj.get("use"):
        print(f"    anime.js:    {aj.get('description', '?')[:60]}")

    print(f"\n  [STRUCTURE]")
    for s in brief.get("site_structure", []):
        print(f"    [{s.get('section', '?'):14}] {s.get('content', '')[:60]}")

    refs = brief.get("design_refs_used", [])
    print(f"\n  [REFS] {', '.join(refs)}")
    print(f"  [INSIGHT] {brief.get('ref_insights', '?')[:80]}")
    print("=" * 60 + "\n")


def save_brief(brief: dict, path: str = None):
    """브리프를 JSON 파일로 저장."""
    if path is None:
        name = brief.get("concept", {}).get("name", "unnamed").replace(" ", "_")
        path = str(BASE_DIR / f"creative_brief_{name}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(brief, f, ensure_ascii=False, indent=2)
    print(f"[creative_brief] 저장: {path}")
    return path


if __name__ == "__main__":
    import sys
    import io

    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    test = sys.argv[1] if len(sys.argv) > 1 else "플로리스트 웹사이트, 30대 여성, 프리미엄 꽃 배달"
    brief = generate(test)
    print_brief(brief)
    save_brief(brief)
