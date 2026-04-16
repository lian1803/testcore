"""
design_router.py — 프로젝트 설명 → 디자인 결정 JSON

Gemini 2.5 Flash가 프로젝트를 분석해서 시각 컨셉을 결정.
API 실패 시 키워드 기반 fallback.
"""
import os
import json
from typing import Dict, Any

# ─── 유효한 값 목록 (Gemini 출력 검증용) ───
VALID_PATTERNS = ["dark_futuristic", "warm_luxury", "clean_minimal", "creative_bold", "organic_light"]
VALID_THEMES = ["dark", "light"]
VALID_CATEGORIES = ["fluid", "morphing", "typography", "camera_journey", "2d_canvas", "image_reveal", "scroll_video"]

TOOL_MAP = {
    "fluid":          {"lib": "webgl-fluid", "ref": "references/webgl-fluid/", "blend": "normal"},
    "morphing":       {"lib": "three.js", "ref": "templates/nexus_9point.html", "blend": "additive"},
    "typography":     {"lib": "three.js+TextGeometry", "ref": "references/codrops-typo-scroll/", "blend": "normal"},
    "camera_journey": {"lib": "three.js+CatmullRomCurve3", "ref": "references/apple-3d-landing/", "blend": "normal"},
    "2d_canvas":      {"lib": "pixi.js", "ref": "references/ogl/", "blend": "normal"},
    "image_reveal":   {"lib": "hover-effect", "ref": "references/hover-effect/", "blend": "normal"},
    "scroll_video":   {"lib": "gsap+video", "ref": "templates/cafe_hero.html", "blend": "normal"},
}

COLOR_MAP = {
    "dark_futuristic":  ["#6366f1", "#a78bfa", "#22d3ee"],
    "warm_luxury":      ["#C8873A", "#8B5E3C", "#F5F0E8"],
    "clean_minimal":    ["#3b82f6", "#e2e8f0", "#0f172a"],
    "creative_bold":    ["#f43f5e", "#fbbf24", "#0f172a"],
    "organic_light":    ["#16a34a", "#f0fdf4", "#166534"],
}

TEMPLATE_MAP = {
    "dark_futuristic":  "nexus_9point.html",
    "warm_luxury":      "flower_bloom.html",
    "clean_minimal":    "hothaan_hero.html",
    "creative_bold":    "cafe_hero.html",
    "organic_light":    "hothaan_hero.html",
}

# ─── Gemini 프롬프트 ───
GEMINI_PROMPT = """너는 웹 디자인 비주얼 컨셉 라우터야. 프로젝트 설명을 읽고 최적의 시각 전략을 JSON으로 반환해.

프로젝트: "{description}"

아래 옵션에서 선택해서 JSON만 반환해. 설명 없이 JSON만.

pattern (하나 선택):
- dark_futuristic: AI/SaaS/테크/데이터/B2B
- warm_luxury: 카페/호텔/뷰티/패션/인테리어
- clean_minimal: 대시보드/툴/관리 서비스
- creative_bold: 에이전시/포트폴리오/브랜딩
- organic_light: 교육/헬스/이커머스/라이프스타일

theme (하나 선택):
- dark: 어두운 배경, 네온/글로우 효과
- light: 밝은 배경, 그림자/필터 기반

visual_categories (1~2개 선택, 배열):
- fluid: 유체 시뮬레이션, 잉크 번짐
- morphing: 3D 형태 변환 (구→로고→텍스트)
- typography: 텍스트가 3D/파티클/글리치 오브젝트
- camera_journey: 스크롤=3D 공간 여행
- 2d_canvas: PixiJS 2D 필터, 밝은 배경 OK
- image_reveal: 이미지 왜곡/글리치 등장
- scroll_video: 스크롤=비디오 프레임 제어

규칙:
- theme이 "light"이면 "morphing" 선택 금지 (AdditiveBlending 필요해서 밝은 배경에서 안 됨)
- 프로젝트 성격에 가장 창의적이고 적합한 조합을 골라
- 매번 같은 "dark + fluid" 금지 — 다양성 우선

JSON 형식:
{{"pattern":"...","theme":"...","visual_categories":["...","..."]}}"""


def generate_visual_spec(description: str) -> Dict[str, Any] | None:
    """Gemini에게 프로젝트 설명 → 시각 컨셉 JSON 생성 요청."""
    try:
        from google import genai
        from google.genai import types

        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return None

        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=GEMINI_PROMPT.format(description=description),
            config=types.GenerateContentConfig(
                temperature=0.3,
                max_output_tokens=500,
                response_mime_type="application/json",
                thinking_config=types.ThinkingConfig(thinking_budget=0),
            )
        )

        text = response.text.strip()
        # JSON 추출 — 여러 형식 대응
        if "```" in text:
            parts = text.split("```")
            for p in parts:
                p = p.strip()
                if p.startswith("json"):
                    p = p[4:].strip()
                if p.startswith("{"):
                    text = p
                    break
        # { } 만 추출
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            text = text[start:end]
        # 한글 키 대응 — 작은따옴표→큰따옴표
        text = text.replace("'", '"')

        spec = json.loads(text)

        # 검증
        if spec.get("pattern") not in VALID_PATTERNS:
            return None
        if spec.get("theme") not in VALID_THEMES:
            return None
        cats = spec.get("visual_categories", [])
        if not cats or not all(c in VALID_CATEGORIES for c in cats):
            return None

        # light 테마에서 additive 카테고리 필터링
        if spec["theme"] == "light":
            cats = [c for c in cats if TOOL_MAP.get(c, {}).get("blend") != "additive"]
            if not cats:
                cats = ["2d_canvas"]
            spec["visual_categories"] = cats

        return spec

    except Exception as e:
        print(f"  Gemini visual spec 실패 (fallback 사용): {e}")
        return None


def _keyword_fallback(description: str) -> Dict[str, str]:
    """키워드 기반 fallback (Gemini 실패 시)."""
    desc_lower = description.lower()

    PATTERN_KEYWORDS = {
        "dark_futuristic": ["AI", "자동화", "SaaS", "플랫폼", "테크", "데이터", "분석", "시스템", "에이전트", "B2B"],
        "warm_luxury": ["카페", "레스토랑", "호텔", "펜션", "웨딩", "뷰티", "헤어", "인테리어", "패션", "감성", "따뜻한"],
        "clean_minimal": ["대시보드", "툴", "서비스", "앱", "소프트웨어", "관리"],
        "creative_bold": ["에이전시", "포트폴리오", "쇼케이스", "크리에이티브", "디자인", "스튜디오"],
        "organic_light": ["교육", "헬스", "피트니스", "유기농", "키즈", "라이프스타일", "이커머스"],
    }
    VISUAL_MAP = {
        "dark_futuristic": ["fluid", "camera_journey"],
        "warm_luxury": ["image_reveal", "scroll_video"],
        "clean_minimal": ["2d_canvas", "typography"],
        "creative_bold": ["camera_journey", "image_reveal"],
        "organic_light": ["2d_canvas", "scroll_video"],
    }
    THEME_MAP = {
        "dark_futuristic": "dark", "warm_luxury": "dark",
        "clean_minimal": "light", "creative_bold": "dark", "organic_light": "light",
    }

    scores = {}
    for pattern, keywords in PATTERN_KEYWORDS.items():
        scores[pattern] = sum(1 for kw in keywords if kw.lower() in desc_lower or kw in description)

    best = max(scores, key=scores.get) if max(scores.values()) > 0 else "creative_bold"
    theme = THEME_MAP[best]

    # 테마 오버라이드
    if any(kw in desc_lower for kw in ["밝은", "라이트", "화이트", "파스텔", "교육", "키즈"]):
        theme = "light"
    if any(kw in desc_lower for kw in ["다크", "네온", "사이버"]):
        theme = "dark"

    cats = VISUAL_MAP[best]
    if theme == "light":
        cats = [c for c in cats if TOOL_MAP.get(c, {}).get("blend") != "additive"]
        if not cats:
            cats = ["2d_canvas"]

    return {"pattern": best, "theme": theme, "visual_categories": cats}


def route(description: str) -> Dict[str, Any]:
    """프로젝트 설명 → 디자인 결정 JSON. Gemini 우선, 실패 시 키워드 fallback."""
    desc_lower = description.lower()

    # Gemini로 시각 컨셉 생성 시도
    spec = generate_visual_spec(description)

    if not spec:
        spec = _keyword_fallback(description)

    pattern = spec["pattern"]
    theme = spec["theme"]
    categories = spec["visual_categories"]

    # 주요 도구
    primary_tool = TOOL_MAP.get(categories[0], TOOL_MAP["2d_canvas"])

    # 3D 레벨
    has_3d = any(kw in desc_lower for kw in ["3d", "파티클", "셰이더", "인터랙티브"])
    is_dashboard = any(kw in desc_lower for kw in ["대시보드", "로그인", "설정", "admin"])

    if is_dashboard:
        level_3d = "none"
    elif has_3d or categories[0] in ("morphing", "camera_journey"):
        level_3d = "full"
    else:
        level_3d = "hero_only"

    # 사이트 타입
    if is_dashboard:
        site_type = "dashboard"
    elif any(kw in desc_lower for kw in ["포트폴리오", "쇼케이스"]):
        site_type = "portfolio"
    else:
        site_type = "product_landing"

    # 템플릿 결정 (라이트 테마면 nexus_9point 금지)
    template = TEMPLATE_MAP.get(pattern, "hothaan_hero.html")
    if theme == "light" and template == "nexus_9point.html":
        template = "hothaan_hero.html"

    # 히어로 렌더링 방식 자율 판단
    hero_method = _decide_hero_method(desc_lower, pattern, categories)

    return {
        "pattern": pattern,
        "theme": theme,
        "visual_categories": categories,
        "primary_tool": primary_tool,
        "colors": COLOR_MAP.get(pattern, COLOR_MAP["creative_bold"]),
        "template": template,
        "3d_level": level_3d,
        "site_type": site_type,
        "avoid_additive_blending": theme == "light",
        "hero_method": hero_method,
    }


def _decide_hero_method(desc: str, pattern: str, categories: list) -> Dict[str, str]:
    """히어로 렌더링 방식 자율 판단.

    Returns:
        {"method": "glb_model|ai_video|css_motion|three_js_code",
         "reason": "왜 이 방식인지"}
    """
    # 오프라인 비즈니스 → AI 영상 생성 (Veo)
    offline_kw = ["카페", "레스토랑", "호텔", "펜션", "미용실", "헤어", "인테리어",
                  "병원", "클리닉", "피트니스", "웨딩", "부동산"]
    if any(kw in desc for kw in offline_kw):
        return {"method": "ai_video", "reason": "오프라인 비즈니스 — 실물 시네마틱 영상이 임팩트 최고"}

    # 3D 공간/환경이 필요한 컨셉 → Sketchfab GLB 모델
    spatial_kw = ["동굴", "cave", "건축", "도시", "city", "산", "mountain",
                  "숲", "forest", "바다", "ocean", "우주", "space"]
    if any(kw in desc for kw in spatial_kw):
        return {"method": "glb_model", "reason": "공간/환경 컨셉 — Sketchfab GLB + Three.js 로드"}

    # 3D 오브젝트 모핑/캐릭터 → GLB 모델
    if "morphing" in categories:
        return {"method": "glb_model", "reason": "morphing 카테고리 — GLB 모델 기반 형태 변환"}

    # 타이포/모션 중심 → CSS + GSAP (lian_motion 스타일)
    if "typography" in categories or "2d_canvas" in categories:
        return {"method": "css_motion", "reason": "타이포/2D 중심 — CSS+GSAP (lian_motion 패턴)"}

    # 나머지 → Three.js 코드 (파티클 아닌 셰이더/지오메트리)
    return {"method": "three_js_code", "reason": "기본 — Three.js 셰이더/지오메트리 기반"}


def format_design_plan(plan: Dict[str, Any]) -> str:
    """디자인 플랜 → 읽기 좋은 텍스트."""
    if not plan:
        return "디자인 플랜 없음"

    cats = ", ".join(plan.get("visual_categories", []))
    tool = plan.get("primary_tool", {})

    hero = plan.get("hero_method", {})

    return f"""패턴: {plan.get('pattern', '?')}
테마: {plan.get('theme', '?')}
시각 카테고리: {cats}
주요 도구: {tool.get('lib', '?')} (레퍼런스: {tool.get('ref', '?')})
히어로 방식: {hero.get('method', '?')} — {hero.get('reason', '')}
색상: {', '.join(plan.get('colors', []))}
템플릿: {plan.get('template', '?')}
3D 레벨: {plan.get('3d_level', '?')}
사이트 타입: {plan.get('site_type', '?')}
AdditiveBlending 금지: {plan.get('avoid_additive_blending', False)}"""
