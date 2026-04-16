"""
design_context_picker.py — 태스크에 맞게 design_system 파일들을 선택적으로 로드

프로젝트 설명을 받아서 관련 효과/레퍼런스만 선택해서 로드.
LLM 없이 순수 Python 키워드 매칭으로 동작.

사용법:
    from core.design_context_picker import pick

    context = pick("우리는 B2B SaaS 분석 대시보드를 만들고 있습니다...")

    # context 구조:
    # {
    #     "index_md": str,               # INDEX.md 전체
    #     "effects": [                   # 선택된 이펙트 소스들
    #         {"name": str, "path": str, "content": str}
    #     ],
    #     "design_refs": [               # 관련 DESIGN.md
    #         {"brand": str, "content": str}
    #     ],
    #     "showcase_benchmark": str,     # showcase.html 앞부분
    #     "total_chars": int,            # 총 주입 글자수
    #     "selected": list,              # 선택된 파일 목록 (로깅용)
    # }
"""

import os
import re
import random
from typing import Optional, Dict, List, Any
from pathlib import Path


# ===== 컨셉 레시피 정의 (매번 다른 스타일 생성용) =====

CONCEPT_RECIPES = [
    {
        "name": "dark_hacker",
        "vibe": "해커 터미널, 네온 그린, 차가운 다크",
        "bg": "FaultyTerminal",
        "text": "ASCIIText",
        "cursor": "Crosshair",
        "palette_brand": "linear.app",
        "colors": {"bg": "#0a0a0a", "text": "#00ff88", "accent": "#00cc66"},
    },
    {
        "name": "luxury_brand",
        "vibe": "럭셔리 브랜드, 골드/레드, 고급감",
        "bg": "Iridescence",
        "text": "ShinyText",
        "cursor": "GhostCursor",
        "palette_brand": "ferrari",
        "colors": {"bg": "#0d0d0d", "text": "#f5f0e8", "accent": "#c41e3a"},
    },
    {
        "name": "clean_ai",
        "vibe": "클린 AI SaaS, 흰배경, 차가운 블루",
        "bg": "Aurora",
        "text": "BlurText",
        "cursor": "BlobCursor",
        "palette_brand": "openai",
        "colors": {"bg": "#fafafa", "text": "#0a0a0a", "accent": "#2563eb"},
    },
    {
        "name": "cyber_rave",
        "vibe": "사이버펑크, 전기 퍼플, 하이퍼스피드",
        "bg": "Hyperspeed",
        "text": "GlitchText",
        "cursor": "LaserFlow",
        "palette_brand": "nvidia",
        "colors": {"bg": "#050510", "text": "#e0e0ff", "accent": "#76b900"},
    },
    {
        "name": "minimal_nordic",
        "vibe": "미니멀, 크림/오프화이트, 스칸디나비안",
        "bg": "DotGrid",
        "text": "FuzzyText",
        "cursor": "Crosshair",
        "palette_brand": "notion",
        "colors": {"bg": "#f8f6f0", "text": "#1a1a1a", "accent": "#8b6f47"},
    },
    {
        "name": "galaxy_scifi",
        "vibe": "우주, 딥블루, SF 미래",
        "bg": "Galaxy",
        "text": "ScrambledText",
        "cursor": "MagicRings",
        "palette_brand": "mistral.ai",
        "colors": {"bg": "#020617", "text": "#e2e8f0", "accent": "#6366f1"},
    },
    {
        "name": "warm_liquid",
        "vibe": "유기적, 웜 골드, 프리미엄 다크",
        "bg": "LiquidChrome",
        "text": "DecryptedText",
        "cursor": "BlobCursor",
        "palette_brand": "framer",
        "colors": {"bg": "#030303", "text": "#f0ede6", "accent": "#c4a35a"},
    },
    {
        "name": "grid_futurist",
        "vibe": "그리드, 라인아트, 테크 블루",
        "bg": "GridScan",
        "text": "TextPressure",
        "cursor": "Crosshair",
        "palette_brand": "raycast",
        "colors": {"bg": "#0f0f1a", "text": "#c8c8e8", "accent": "#ff6363"},
    },
    {
        "name": "dark_velvet",
        "vibe": "딥 다크, 벨벳, 핀테크",
        "bg": "DarkVeil",
        "text": "SplitText",
        "cursor": "GlareHover",
        "palette_brand": "revolut",
        "colors": {"bg": "#080810", "text": "#f0f0ff", "accent": "#7c3aed"},
    },
    {
        "name": "neon_lightning",
        "vibe": "번개, 에너지, 일렉트릭 화이트",
        "bg": "Lightning",
        "text": "RotatingText",
        "cursor": "GhostCursor",
        "palette_brand": "coinbase",
        "colors": {"bg": "#020914", "text": "#ffffff", "accent": "#0052ff"},
    },
    {
        "name": "silk_organic",
        "vibe": "부드러운 실크, 웜톤, 프리미엄",
        "bg": "Silk",
        "text": "ScrollReveal",
        "cursor": "GhostCursor",
        "palette_brand": "apple",
        "colors": {"bg": "#fefdfb", "text": "#1d1d1f", "accent": "#a2845d"},
    },
    {
        "name": "plasma_energy",
        "vibe": "에너지, 플라즈마, 전기적",
        "bg": "Plasma",
        "text": "CountUp",
        "cursor": "ClickSpark",
        "palette_brand": "stripe",
        "colors": {"bg": "#0a0a1a", "text": "#e8e8ff", "accent": "#625bff"},
    },
    {
        "name": "orb_elegant",
        "vibe": "우아한 구, 중력감, 미니멀 다크",
        "bg": "Orb",
        "text": "BlurText",
        "cursor": "MetaBalls",
        "palette_brand": "figma",
        "colors": {"bg": "#0f0f0f", "text": "#f5f5f5", "accent": "#a259ff"},
    },
    {
        "name": "glitch_digital",
        "vibe": "디지털 글리치, 사이버, 고르지 않은",
        "bg": "LetterGlitch",
        "text": "GlitchText",
        "cursor": "PixelTrail",
        "palette_brand": "coinbase",
        "colors": {"bg": "#000000", "text": "#00ffff", "accent": "#ff00ff"},
    },
    {
        "name": "light_rays",
        "vibe": "빛의 광선, 신비로운, 우아함",
        "bg": "LightRays",
        "text": "DecryptedText",
        "cursor": "GhostCursor",
        "palette_brand": "claude",
        "colors": {"bg": "#fafaf9", "text": "#0c0c0c", "accent": "#8b5cf6"},
    },
    {
        "name": "pixels_retro",
        "vibe": "픽셀, 레트로 아케이드, 80년대",
        "bg": "PixelBlast",
        "text": "TextType",
        "cursor": "PixelTrail",
        "palette_brand": "composio",
        "colors": {"bg": "#0a0a14", "text": "#ff00ff", "accent": "#00ff00"},
    },
    {
        "name": "gradient_modern",
        "vibe": "그라데이션, 모던 SaaS, 부드러운",
        "bg": "GradientBlinds",
        "text": "ShinyText",
        "cursor": "BlobCursor",
        "palette_brand": "vercel",
        "colors": {"bg": "#fbfbfb", "text": "#0a0a0a", "accent": "#000000"},
    },
    {
        "name": "particles_cosmic",
        "vibe": "우주 입자, 신비로움, 깊이감",
        "bg": "Particles",
        "text": "ScrollVelocity",
        "cursor": "MagicRings",
        "palette_brand": "mistral.ai",
        "colors": {"bg": "#0a0a14", "text": "#e8e8ff", "accent": "#6366f1"},
    },
    {
        "name": "beams_focus",
        "vibe": "집중된 빔, 강조, 테크",
        "bg": "Beams",
        "text": "CountUp",
        "cursor": "Crosshair",
        "palette_brand": "hashicorp",
        "colors": {"bg": "#1a1a2e", "text": "#fafafa", "accent": "#f0883e"},
    },
    {
        "name": "threads_woven",
        "vibe": "직조된 스레드, 기술적, 연결됨",
        "bg": "Threads",
        "text": "VariableProximity",
        "cursor": "MagnetLines",
        "palette_brand": "intercom",
        "colors": {"bg": "#0f0f0f", "text": "#e8e8e8", "accent": "#3b82f6"},
    },
]

# ===== 키워드 매칭 맵 =====

EFFECT_KEYWORDS = {
    # 배경 셰이더
    "liquid": ["LiquidChrome", "LiquidEther"],
    "chrome": ["LiquidChrome"],
    "silk": ["Silk"],
    "aurora": ["Aurora"],
    "wave": ["Waves"],
    "mesh": ["MeshMatrix"],
    "grid": ["GridDistortion"],
    "plasma": ["Plasma"],
    "orb": ["Orb"],
    "hyperspeed": ["Hyperspeed"],
    "galaxy": ["Galaxy"],
    "iridescence": ["Iridescence"],
    "thread": ["Threads"],

    # 3D/interactive
    "3d": ["threejs-landing", "r3f-portfolio"],
    "three": ["threejs-landing"],
    "threejs": ["threejs-landing"],
    "r3f": ["r3f-portfolio"],
    "hand": ["hand-particles", "handwave-xr", "handtracking-101"],
    "gesture": ["gesture-particles"],
    "particle": ["gesture-particles", "hand-particles"],
    "camera": ["handtracking-101", "handwave-xr"],
    "mediapipe": ["handtracking-101"],
    "interactive": ["hand-particles", "gesture-particles"],

    # 모션/애니메이션
    "motion": ["anime"],
    "gsap": ["anime"],
    "animation": ["anime"],
    "gradient": ["shadergradient"],
    "shader": ["shadergradient", "LiquidChrome", "Silk"],

    # 텍스트 이펙트
    "glitch": ["GlitchText"],
    "decrypt": ["DecryptedText"],
    "blur": ["BlurText"],
    "split": ["SplitText"],
    "typewriter": ["TypewriterEffect"],
    "shiny": ["ShinyText"],
    "scroll": ["ScrollFloat", "ScrollVelocity"],
    "pressure": ["TextPressure"],
    "scramble": ["ScrambledText"],
    "fuzzy": ["FuzzyText"],
    "text": ["SplitText", "BlurText"],

    # 커서
    "cursor": ["BlobCursor"],
    "blob": ["BlobCursor"],
    "splash": ["SplashCursor"],
    "ghost": ["GhostCursor"],
    "crosshair": ["Crosshair"],
    "pixel": ["PixelTrail"],

    # 스타일/브랜드 (DESIGN.md 매칭)
    "saas": ["linear.app", "stripe", "vercel", "notion"],
    "linear": ["linear.app"],
    "stripe": ["stripe"],
    "vercel": ["vercel"],
    "notion": ["notion"],
    "figma": ["figma"],
    "airtable": ["airtable"],
    "cursor_editor": ["cursor"],
    "supabase": ["supabase"],
    "expo": ["expo"],
    "hashicorp": ["hashicorp"],
    "openai": ["openai"],
    "claude": ["claude"],
    "cohere": ["cohere"],
    "replicate": ["replicate"],
    "elevenlabs": ["elevenlabs"],
    "luxury": ["apple", "bmw", "ferrari"],
    "apple": ["apple"],
    "bmw": ["bmw"],
    "ferrari": ["ferrari"],
    "brand": ["spotify", "airbnb"],
    "spotify": ["spotify"],
    "airbnb": ["airbnb"],
    "fintech": ["stripe"],
    "ai": ["openai", "claude", "cohere", "replicate"],
    "dark": ["linear.app", "stripe"],
    "minimal": ["notion", "linear.app"],
}

EFFECT_PATHS = {
    # 배경 셰이더 (40개)
    "Aurora": "components/react-bits/src/content/Backgrounds/Aurora/Aurora.jsx",
    "Balatro": "components/react-bits/src/content/Backgrounds/Balatro/Balatro.jsx",
    "Ballpit": "components/react-bits/src/content/Backgrounds/Ballpit/Ballpit.jsx",
    "Beams": "components/react-bits/src/content/Backgrounds/Beams/Beams.jsx",
    "ColorBends": "components/react-bits/src/content/Backgrounds/ColorBends/ColorBends.jsx",
    "DarkVeil": "components/react-bits/src/content/Backgrounds/DarkVeil/DarkVeil.jsx",
    "Dither": "components/react-bits/src/content/Backgrounds/Dither/Dither.jsx",
    "DotGrid": "components/react-bits/src/content/Backgrounds/DotGrid/DotGrid.jsx",
    "EvilEye": "components/react-bits/src/content/Backgrounds/EvilEye/EvilEye.jsx",
    "FaultyTerminal": "components/react-bits/src/content/Backgrounds/FaultyTerminal/FaultyTerminal.jsx",
    "FloatingLines": "components/react-bits/src/content/Backgrounds/FloatingLines/FloatingLines.jsx",
    "Galaxy": "components/react-bits/src/content/Backgrounds/Galaxy/Galaxy.jsx",
    "GradientBlinds": "components/react-bits/src/content/Backgrounds/GradientBlinds/GradientBlinds.jsx",
    "Grainient": "components/react-bits/src/content/Backgrounds/Grainient/Grainient.jsx",
    "GridDistortion": "components/react-bits/src/content/Backgrounds/GridDistortion/GridDistortion.jsx",
    "GridMotion": "components/react-bits/src/content/Backgrounds/GridMotion/GridMotion.jsx",
    "GridScan": "components/react-bits/src/content/Backgrounds/GridScan/GridScan.jsx",
    "Hyperspeed": "components/react-bits/src/content/Backgrounds/Hyperspeed/Hyperspeed.jsx",
    "Iridescence": "components/react-bits/src/content/Backgrounds/Iridescence/Iridescence.jsx",
    "LetterGlitch": "components/react-bits/src/content/Backgrounds/LetterGlitch/LetterGlitch.jsx",
    "Lightning": "components/react-bits/src/content/Backgrounds/Lightning/Lightning.jsx",
    "LightPillar": "components/react-bits/src/content/Backgrounds/LightPillar/LightPillar.jsx",
    "LightRays": "components/react-bits/src/content/Backgrounds/LightRays/LightRays.jsx",
    "LineWaves": "components/react-bits/src/content/Backgrounds/LineWaves/LineWaves.jsx",
    "LiquidChrome": "components/react-bits/src/content/Backgrounds/LiquidChrome/LiquidChrome.jsx",
    "LiquidEther": "components/react-bits/src/content/Backgrounds/LiquidEther/LiquidEther.jsx",
    "Orb": "components/react-bits/src/content/Backgrounds/Orb/Orb.jsx",
    "Particles": "components/react-bits/src/content/Backgrounds/Particles/Particles.jsx",
    "PixelBlast": "components/react-bits/src/content/Backgrounds/PixelBlast/PixelBlast.jsx",
    "PixelSnow": "components/react-bits/src/content/Backgrounds/PixelSnow/PixelSnow.jsx",
    "Plasma": "components/react-bits/src/content/Backgrounds/Plasma/Plasma.jsx",
    "Prism": "components/react-bits/src/content/Backgrounds/Prism/Prism.jsx",
    "PrismaticBurst": "components/react-bits/src/content/Backgrounds/PrismaticBurst/PrismaticBurst.jsx",
    "Radar": "components/react-bits/src/content/Backgrounds/Radar/Radar.jsx",
    "RippleGrid": "components/react-bits/src/content/Backgrounds/RippleGrid/RippleGrid.jsx",
    "ShapeGrid": "components/react-bits/src/content/Backgrounds/ShapeGrid/ShapeGrid.jsx",
    "Silk": "components/react-bits/src/content/Backgrounds/Silk/Silk.jsx",
    "SoftAurora": "components/react-bits/src/content/Backgrounds/SoftAurora/SoftAurora.jsx",
    "Threads": "components/react-bits/src/content/Backgrounds/Threads/Threads.jsx",
    "Waves": "components/react-bits/src/content/Backgrounds/Waves/Waves.jsx",

    # 텍스트 이펙트 (24개)
    "ASCIIText": "components/react-bits/src/content/TextAnimations/ASCIIText/ASCIIText.jsx",
    "BlurText": "components/react-bits/src/content/TextAnimations/BlurText/BlurText.jsx",
    "CircularText": "components/react-bits/src/content/TextAnimations/CircularText/CircularText.jsx",
    "CountUp": "components/react-bits/src/content/TextAnimations/CountUp/CountUp.jsx",
    "CurvedLoop": "components/react-bits/src/content/TextAnimations/CurvedLoop/CurvedLoop.jsx",
    "DecryptedText": "components/react-bits/src/content/TextAnimations/DecryptedText/DecryptedText.jsx",
    "FallingText": "components/react-bits/src/content/TextAnimations/FallingText/FallingText.jsx",
    "FuzzyText": "components/react-bits/src/content/TextAnimations/FuzzyText/FuzzyText.jsx",
    "GlitchText": "components/react-bits/src/content/TextAnimations/GlitchText/GlitchText.jsx",
    "GradientText": "components/react-bits/src/content/TextAnimations/GradientText/GradientText.jsx",
    "RotatingText": "components/react-bits/src/content/TextAnimations/RotatingText/RotatingText.jsx",
    "ScrambledText": "components/react-bits/src/content/TextAnimations/ScrambledText/ScrambledText.jsx",
    "ScrollFloat": "components/react-bits/src/content/TextAnimations/ScrollFloat/ScrollFloat.jsx",
    "ScrollReveal": "components/react-bits/src/content/TextAnimations/ScrollReveal/ScrollReveal.jsx",
    "ScrollVelocity": "components/react-bits/src/content/TextAnimations/ScrollVelocity/ScrollVelocity.jsx",
    "ShinyText": "components/react-bits/src/content/TextAnimations/ShinyText/ShinyText.jsx",
    "Shuffle": "components/react-bits/src/content/TextAnimations/Shuffle/Shuffle.jsx",
    "SplitText": "components/react-bits/src/content/TextAnimations/SplitText/SplitText.jsx",
    "TextCursor": "components/react-bits/src/content/TextAnimations/TextCursor/TextCursor.jsx",
    "TextPressure": "components/react-bits/src/content/TextAnimations/TextPressure/TextPressure.jsx",
    "TextType": "components/react-bits/src/content/TextAnimations/TextType/TextType.jsx",
    "TrueFocus": "components/react-bits/src/content/TextAnimations/TrueFocus/TrueFocus.jsx",
    "VariableProximity": "components/react-bits/src/content/TextAnimations/VariableProximity/VariableProximity.jsx",

    # 커서/애니메이션 (30개)
    "AnimatedContent": "components/react-bits/src/content/Animations/AnimatedContent/AnimatedContent.jsx",
    "Antigravity": "components/react-bits/src/content/Animations/Antigravity/Antigravity.jsx",
    "BlobCursor": "components/react-bits/src/content/Animations/BlobCursor/BlobCursor.jsx",
    "ClickSpark": "components/react-bits/src/content/Animations/ClickSpark/ClickSpark.jsx",
    "Crosshair": "components/react-bits/src/content/Animations/Crosshair/Crosshair.jsx",
    "Cubes": "components/react-bits/src/content/Animations/Cubes/Cubes.jsx",
    "ElectricBorder": "components/react-bits/src/content/Animations/ElectricBorder/ElectricBorder.jsx",
    "FadeContent": "components/react-bits/src/content/Animations/FadeContent/FadeContent.jsx",
    "GhostCursor": "components/react-bits/src/content/Animations/GhostCursor/GhostCursor.jsx",
    "GlareHover": "components/react-bits/src/content/Animations/GlareHover/GlareHover.jsx",
    "GradualBlur": "components/react-bits/src/content/Animations/GradualBlur/GradualBlur.jsx",
    "ImageTrail": "components/react-bits/src/content/Animations/ImageTrail/ImageTrail.jsx",
    "LaserFlow": "components/react-bits/src/content/Animations/LaserFlow/LaserFlow.jsx",
    "LogoLoop": "components/react-bits/src/content/Animations/LogoLoop/LogoLoop.jsx",
    "MagicRings": "components/react-bits/src/content/Animations/MagicRings/MagicRings.jsx",
    "Magnet": "components/react-bits/src/content/Animations/Magnet/Magnet.jsx",
    "MagnetLines": "components/react-bits/src/content/Animations/MagnetLines/MagnetLines.jsx",
    "MetaBalls": "components/react-bits/src/content/Animations/MetaBalls/MetaBalls.jsx",
    "MetallicPaint": "components/react-bits/src/content/Animations/MetallicPaint/MetallicPaint.jsx",
    "Noise": "components/react-bits/src/content/Animations/Noise/Noise.jsx",
    "OrbitImages": "components/react-bits/src/content/Animations/OrbitImages/OrbitImages.jsx",
    "PixelTrail": "components/react-bits/src/content/Animations/PixelTrail/PixelTrail.jsx",
    "PixelTransition": "components/react-bits/src/content/Animations/PixelTransition/PixelTransition.jsx",
    "Ribbons": "components/react-bits/src/content/Animations/Ribbons/Ribbons.jsx",
    "ShapeBlur": "components/react-bits/src/content/Animations/ShapeBlur/ShapeBlur.jsx",
    "SplashCursor": "components/react-bits/src/content/Animations/SplashCursor/SplashCursor.jsx",
    "StarBorder": "components/react-bits/src/content/Animations/StarBorder/StarBorder.jsx",
    "StickerPeel": "components/react-bits/src/content/Animations/StickerPeel/StickerPeel.jsx",
    "TargetCursor": "components/react-bits/src/content/Animations/TargetCursor/TargetCursor.jsx",
}

INTERACTIVE_PATHS = {
    "hand-particles": "interactive/hand-particles",
    "handwave-xr": "interactive/handwave-xr",
    "handtracking-101": "interactive/handtracking-101",
    "gesture-particles": "interactive/gesture-particles",
}

DESIGN_MD_BRANDS = [
    "linear.app", "stripe", "vercel", "notion", "figma", "airtable", "cursor",
    "supabase", "expo", "hashicorp", "openai", "claude", "cohere", "replicate",
    "elevenlabs", "apple", "bmw", "ferrari", "spotify", "airbnb", "cal", "clay",
    "clickhouse", "codesandbox", "datadog", "discord", "docker", "github", "gitlab",
    "google", "heroku", "jira", "mailchimp", "monday", "okta", "postgres", "sendgrid",
    "slack", "twilio", "zapier",
]


def _get_ds_base() -> str:
    """design_system 루트 경로 계산."""
    # company/core/design_context_picker.py -> design_system/
    current = os.path.dirname(os.path.abspath(__file__))  # company/core
    parent = os.path.dirname(current)  # company
    grandparent = os.path.dirname(parent)  # core
    ds_base = os.path.join(grandparent, "design_system")
    return ds_base


def _truncate(text: str, max_chars: int) -> str:
    """텍스트를 최대 글자수로 트런케이트."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + f"\n... [트런케이트됨: {len(text) - max_chars}자 생략]"


def _load_file(path: str, ds_base: str, max_chars: Optional[int] = None) -> Optional[str]:
    """파일을 읽어서 반환 (없으면 None)."""
    full_path = os.path.join(ds_base, path)
    if not os.path.exists(full_path):
        return None
    try:
        with open(full_path, encoding="utf-8") as f:
            content = f.read()
        if max_chars:
            content = _truncate(content, max_chars)
        return content
    except Exception as e:
        return None


def _find_interactive_html(interactive_dir: str) -> Optional[str]:
    """interactive 폴더에서 첫 번째 .html 파일 찾기."""
    if not os.path.exists(interactive_dir):
        return None
    try:
        for file in os.listdir(interactive_dir):
            if file.endswith(".html"):
                return os.path.join(interactive_dir, file)
    except Exception:
        pass
    return None


def _find_design_md(design_md_path: str, brand: str) -> Optional[str]:
    """design-md/{brand}/ 아래 DESIGN.md 찾기."""
    brand_dir = os.path.join(design_md_path, brand)
    if not os.path.exists(brand_dir):
        return None

    # DESIGN.md 또는 README.md 찾기
    for filename in ["DESIGN.md", "README.md", "index.md"]:
        candidate = os.path.join(brand_dir, filename)
        if os.path.exists(candidate):
            return candidate

    return None


def pick_concept(seed: Optional[int] = None) -> Dict[str, Any]:
    """
    CONCEPT_RECIPES에서 랜덤으로 컨셉 레시피 1개 선택해서 소스 파일 로드.

    매번 다른 디자인 조합이 나오도록 설계됨.
    seed 지정하면 재현 가능.

    Args:
        seed: 선택적 난수 시드 (기본 None = 매번 다름)

    Returns:
        {
            "recipe": dict,             # 선택된 레시피 전체 (name, vibe, bg, text, cursor, palette_brand, colors)
            "bg_source": str,           # 배경 셰이더 소스 코드 (최대 10000자)
            "text_source": str,         # 텍스트 이펙트 소스 코드 (최대 6000자)
            "cursor_source": str,       # 커서 소스 코드 (최대 4000자)
            "design_ref": str,          # DESIGN.md 내용 (최대 3000자)
            "showcase_benchmark": str,  # showcase.html 앞 2000자
            "total_chars": int,         # 총 주입 글자수
            "selected": list,           # 선택된 파일 목록 (로깅용)
        }
    """
    if seed is not None:
        random.seed(seed)

    ds_base = _get_ds_base()
    result = {
        "recipe": {},
        "bg_source": "",
        "text_source": "",
        "cursor_source": "",
        "design_ref": "",
        "showcase_benchmark": "",
        "total_chars": 0,
        "selected": [],
    }

    total_chars = 0

    # 1. 레시피 랜덤 선택
    recipe = random.choice(CONCEPT_RECIPES)
    result["recipe"] = recipe.copy()
    result["selected"].append(f"concept:{recipe['name']}")

    # 2. 배경 셰이더 로드 (최대 10000자)
    bg_name = recipe["bg"]
    if bg_name in EFFECT_PATHS:
        bg_content = _load_file(EFFECT_PATHS[bg_name], ds_base, max_chars=10000)
        if bg_content:
            result["bg_source"] = bg_content
            total_chars += len(bg_content)
            result["selected"].append(f"bg:{bg_name}")
        else:
            # fallback: 배경을 Warm Liquid (가장 안정적)로 교체
            fallback_content = _load_file(EFFECT_PATHS["LiquidChrome"], ds_base, max_chars=10000)
            if fallback_content:
                result["bg_source"] = fallback_content
                total_chars += len(fallback_content)
                result["selected"].append(f"bg:LiquidChrome(fallback)")

    # 3. 텍스트 이펙트 로드 (최대 6000자)
    text_name = recipe["text"]
    if text_name in EFFECT_PATHS:
        text_content = _load_file(EFFECT_PATHS[text_name], ds_base, max_chars=6000)
        if text_content:
            result["text_source"] = text_content
            total_chars += len(text_content)
            result["selected"].append(f"text:{text_name}")
        else:
            # fallback: BlurText
            fallback_content = _load_file(EFFECT_PATHS["BlurText"], ds_base, max_chars=6000)
            if fallback_content:
                result["text_source"] = fallback_content
                total_chars += len(fallback_content)
                result["selected"].append(f"text:BlurText(fallback)")

    # 4. 커서/애니메이션 로드 (최대 4000자)
    cursor_name = recipe["cursor"]
    if cursor_name in EFFECT_PATHS:
        cursor_content = _load_file(EFFECT_PATHS[cursor_name], ds_base, max_chars=4000)
        if cursor_content:
            result["cursor_source"] = cursor_content
            total_chars += len(cursor_content)
            result["selected"].append(f"cursor:{cursor_name}")
        else:
            # fallback: BlobCursor
            fallback_content = _load_file(EFFECT_PATHS["BlobCursor"], ds_base, max_chars=4000)
            if fallback_content:
                result["cursor_source"] = fallback_content
                total_chars += len(fallback_content)
                result["selected"].append(f"cursor:BlobCursor(fallback)")

    # 5. DESIGN.md 로드 (최대 3000자)
    palette_brand = recipe.get("palette_brand")
    if palette_brand:
        design_md_path = os.path.join(ds_base, "design-systems", "design-md")
        design_file = _find_design_md(design_md_path, palette_brand)
        if design_file:
            try:
                with open(design_file, encoding="utf-8") as f:
                    design_content = f.read()
                design_content = _truncate(design_content, 3000)
                result["design_ref"] = design_content
                total_chars += len(design_content)
                result["selected"].append(f"design:{palette_brand}")
            except Exception:
                pass

    # 6. showcase.html 벤치마크 (앞 2000자)
    showcase_content = _load_file("demo/showcase.html", ds_base, max_chars=2000)
    if showcase_content:
        result["showcase_benchmark"] = showcase_content
        total_chars += len(showcase_content)
        result["selected"].append("demo/showcase.html")

    result["total_chars"] = total_chars

    return result


def pick(task_description: str, max_total_chars: int = 15000) -> Dict[str, Any]:
    """
    태스크 설명 기반 design_system 파일 선택적 로드.

    Args:
        task_description: 프로젝트/태스크 설명
        max_total_chars: 최대 반환 글자수 (기본 ~15,000 = 약 60,000토큰)

    Returns:
        {
            "index_md": str,               # INDEX.md 전체
            "effects": [                   # 선택된 이펙트 (최대 3개, 각 8000자 트런케이트)
                {"name": str, "path": str, "content": str}
            ],
            "design_refs": [               # 관련 DESIGN.md (최대 2개, 각 3000자 트런케이트)
                {"brand": str, "content": str}
            ],
            "showcase_benchmark": str,     # showcase.html 앞 2000자
            "total_chars": int,            # 총 주입 글자수
            "selected": list,              # 선택된 파일 목록 (로깅용)
        }
    """
    ds_base = _get_ds_base()
    result = {
        "index_md": "",
        "effects": [],
        "design_refs": [],
        "showcase_benchmark": "",
        "total_chars": 0,
        "selected": [],
    }

    total_chars = 0

    # 1. INDEX.md (항상 로드)
    index_content = _load_file("INDEX.md", ds_base)
    if index_content:
        result["index_md"] = index_content
        total_chars += len(index_content)
        result["selected"].append("INDEX.md")

    # 2. 키워드 매칭으로 관련 이펙트 선택
    task_lower = task_description.lower()
    selected_effects = set()

    for keyword, effects in EFFECT_KEYWORDS.items():
        # 단순 부분 매칭 (한글/영문 혼합 처리)
        if keyword in task_lower:
            for effect in effects:
                selected_effects.add(effect)

    # 선택된 이펙트를 3개로 제한
    selected_effects = list(selected_effects)[:3]

    # 3. 선택된 이펙트의 소스 로드 (최대 8000자 각)
    for effect_name in selected_effects:
        if effect_name in EFFECT_PATHS:
            content = _load_file(EFFECT_PATHS[effect_name], ds_base, max_chars=8000)
            if content:
                result["effects"].append({
                    "name": effect_name,
                    "path": EFFECT_PATHS[effect_name],
                    "content": content,
                })
                total_chars += len(content)
                result["selected"].append(f"effect:{effect_name}")
        elif effect_name in INTERACTIVE_PATHS:
            interactive_dir = os.path.join(ds_base, INTERACTIVE_PATHS[effect_name])
            html_file = _find_interactive_html(interactive_dir)
            if html_file:
                with open(html_file, encoding="utf-8") as f:
                    content = f.read()
                content = _truncate(content, 8000)
                result["effects"].append({
                    "name": effect_name,
                    "path": INTERACTIVE_PATHS[effect_name],
                    "content": content,
                })
                total_chars += len(content)
                result["selected"].append(f"interactive:{effect_name}")

    # 4. 관련 DESIGN.md 선택 (최대 2개, 각 3000자)
    selected_brands = set()
    for keyword, brands in EFFECT_KEYWORDS.items():
        if keyword in task_lower:
            for brand in brands:
                if brand in DESIGN_MD_BRANDS:
                    selected_brands.add(brand)

    selected_brands = list(selected_brands)[:2]
    design_md_path = os.path.join(ds_base, "design-systems", "design-md")

    for brand in selected_brands:
        design_file = _find_design_md(design_md_path, brand)
        if design_file:
            try:
                with open(design_file, encoding="utf-8") as f:
                    content = f.read()
                content = _truncate(content, 3000)
                result["design_refs"].append({
                    "brand": brand,
                    "content": content,
                })
                total_chars += len(content)
                result["selected"].append(f"design:{brand}")
            except Exception:
                pass

    # 5. showcase.html 벤치마크 (앞 2000자)
    showcase_content = _load_file("demo/showcase.html", ds_base, max_chars=2000)
    if showcase_content:
        result["showcase_benchmark"] = showcase_content
        total_chars += len(showcase_content)
        result["selected"].append("demo/showcase.html")

    result["total_chars"] = total_chars

    return result


if __name__ == "__main__":
    # Windows 콘솔 인코딩 수정
    import sys
    import io
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    print("=" * 70)
    print("CONCEPT PICKER 테스트 — 5번 연속 호출해서 매번 다른 레시피 나오는지 확인")
    print("=" * 70)

    for i in range(5):
        result = pick_concept()
        recipe = result["recipe"]
        print(f"\n[{i+1}] 컨셉: {recipe['name']}")
        print(f"    Vibe: {recipe['vibe']}")
        print(f"    BG: {recipe['bg']} | Text: {recipe['text']} | Cursor: {recipe['cursor']}")
        print(f"    Brand: {recipe['palette_brand']}")
        print(f"    총 {result['total_chars']:,}자 로드")
        print(f"    선택된 파일: {len(result['selected'])}개")
        for item in result["selected"]:
            print(f"      - {item}")

    print("\n" + "=" * 70)
    print("기존 KEYWORD-BASED PICKER 테스트")
    print("=" * 70)

    # 테스트
    test_task = """
    우리는 B2B SaaS 분석 대시보드를 만들고 있습니다.
    크리에이티브하고 현대적인 느낌. 액체 같은 배경, 글리치 텍스트.
    """

    context = pick(test_task)

    print(f"\n[OK] 총 {context['total_chars']:,} 글자 로드됨")
    print(f"[FILES] 선택된 파일:")
    for item in context["selected"]:
        print(f"  - {item}")
    print(f"\n[EFFECTS] 이펙트 ({len(context['effects'])}개):")
    for effect in context["effects"]:
        print(f"  - {effect['name']}: {len(effect['content'])} 글자")
    print(f"\n[DESIGN_REFS] DESIGN.md ({len(context['design_refs'])}개):")
    for ref in context["design_refs"]:
        print(f"  - {ref['brand']}: {len(ref['content'])} 글자")
    print(f"\n[SHOWCASE] 벤치마크: {len(context['showcase_benchmark'])} 글자")
