"""
reference_analyzer.py — design_system 폴더에서 프로젝트에 맞는 레퍼런스 자동 검색

design_system/ 폴더의 16개 레포(components, 3d, motion, snippets) + 59개 기업 DESIGN.md에서
프로젝트 설명과 design_router.py 출력 기반으로 관련 컴포넌트/레퍼런스를 찾아준다.

구조:
    design_system/
    ├── components/     (7개: uiverse, magicui, shadcn, react-bits, 21st, shadcn-templates, reactbits-alt)
    ├── 3d/             (5개: threejs-landing, threejs-portfolio, r3f-example, r3f-examples, r3f-portfolio)
    ├── motion/         (2개: anime, shadergradient)
    ├── design-systems/ (59개 기업: stripe, linear, notion, figma, etc.)
    └── snippets/       (코드 조각들: liquid-background.html, codepen-3d, draftly-guide)

사용법 1. 기본 분석:
    from core.reference_analyzer import analyze

    design_plan = {
        "site_type": "saas_dashboard",
        "3d_level": "hero_only",
        "style_family": "clean_futuristic",
        "reference_sources": ["magicui", "uiverse"],
        "stitch_scope": ["dashboard", "cards"],
        "3d_scope": ["hero", "background"]
    }

    result = analyze("프로젝트 설명", design_plan)

사용법 2. 개별 검색:
    from core.reference_analyzer import (
        find_similar_design_md,  # 기업별 DESIGN.md 찾기
        find_components,         # 컴포넌트 라이브러리 찾기
        find_3d_examples,        # 3D 예제 찾기
        find_motion_examples,    # 모션 라이브러리 찾기
        find_snippets            # 코드 스니펫 찾기
    )

캐싱:
    - .cache/ 폴더에 자동 저장
    - 같은 쿼리 재실행 시 파일 시스템 스캔 건너뜀
    - 성능: 캐시 없음 ~2초, 캐시 있음 ~50ms
"""
import os
import sys
import json
from pathlib import Path
from typing import List, Dict, Any
import hashlib
import pickle

# Windows에서 UTF-8 출력 보장
if sys.platform == "win32":
    os.system("chcp 65001 > nul")

# 기본 경로
DESIGN_SYSTEM_ROOT = Path(os.path.dirname(os.path.dirname(__file__))).parent / "design_system"
DESIGN_MD_DIR = DESIGN_SYSTEM_ROOT / "design-systems" / "design-md"
COMPONENTS_DIR = DESIGN_SYSTEM_ROOT / "components"
THREE_D_DIR = DESIGN_SYSTEM_ROOT / "3d"
MOTION_DIR = DESIGN_SYSTEM_ROOT / "motion"
SNIPPETS_DIR = DESIGN_SYSTEM_ROOT / "snippets"

# 캐시 경로
CACHE_DIR = Path(os.path.dirname(__file__)) / ".cache"
CACHE_DIR.mkdir(exist_ok=True)

# 사이트 타입별 관련 기업 매핑 (하드코딩)
SITE_TYPE_TO_COMPANIES = {
    "saas_dashboard": ["stripe", "linear.app", "notion", "figma", "airtable", "supabase", "vercel", "clay"],
    "brand_experience": ["apple", "spotify", "airbnb", "nike", "mercedes", "tesla", "bmw", "ferrari", "lamborghini", "mercedes-benz"],
    "product_landing": ["vercel", "supabase", "openai", "cohere", "replicate", "runwayml", "expo"],
    "ai_tool": ["cohere", "replicate", "minimax", "together.ai", "ollama", "mistral.ai", "elevenlabs"],
    "ecommerce": ["shopify", "alibaba", "amazon", "uber"],
    "portfolio": ["framer", "lovable", "webflow", "behance"],
    "documentation": ["mintlify", "sanity", "hashicorp", "clickhouse", "mongodb"],
    "social_network": ["pinterest", "x.ai", "discord"],
    "devtool": ["cursor", "raycast", "warp", "github", "gitlab"],
    "fintech": ["revolut", "coinbase", "kraken", "stripe", "wise"],
    "crypto": ["coinbase", "kraken", "solana"],
    "mobile_app": ["expo", "framer", "lovable"],
    "analytics": ["posthog", "vercel", "datadog"],
    "community": ["intercom", "discord", "slack"],
    "default": ["stripe", "linear.app", "vercel", "figma", "supabase"],
}

# 스타일별 기업 매핑
STYLE_TO_COMPANIES = {
    "clean_minimal": ["linear.app", "vercel", "figma", "stripe", "supabase"],
    "clean_futuristic": ["vercel", "openai", "cohere", "replicate", "cursor"],
    "bold_gradient": ["spotify", "framer", "lovable", "webflow"],
    "dark_mode": ["warp", "cursor", "raycast", "github"],
    "glass_morphism": ["apple", "framer"],
    "luxury": ["tesla", "ferrari", "lamborghini", "bmw"],
    "playful": ["framer", "lovable", "airbnb", "pinterest"],
    "professional": ["stripe", "notion", "airtable", "intercom"],
    "default": ["stripe", "linear.app", "vercel"],
}

# 컴포넌트 소스별 카테고리 매핑
COMPONENT_CATEGORIES = {
    "uiverse": ["Buttons", "Cards", "Loaders", "Inputs", "Toggles", "Sliders", "Badges", "Menus", "Modals", "Notifications"],
    "magicui": ["hero", "cards", "buttons", "inputs", "animated", "3d", "text-effects", "charts"],
    "shadcn": ["accordion", "alert", "avatar", "badge", "button", "calendar", "card", "checkbox", "dialog", "dropdown-menu"],
    "react-bits": ["components", "patterns", "hooks", "utilities"],
    "21st": ["components", "layouts", "effects"],
    "shadcn-templates": ["templates", "layouts", "examples"],
    "reactbits-alt": ["alternative-components"],
}

# 3D 레퍼런스 메타데이터
THREE_D_REFERENCES = {
    "threejs-landing": {
        "desc": "Three.js landing page - particles, 3D mesh, spatial interaction",
        "techs": ["Three.js", "GSAP", "Shaders"],
        "scope": ["hero", "background", "particle"],
    },
    "threejs-portfolio": {
        "desc": "Three.js portfolio - 3D models and camera animation",
        "techs": ["Three.js", "WebGL"],
        "scope": ["hero", "model", "camera"],
    },
    "r3f-portfolio": {
        "desc": "R3F portfolio - React + Three.js integration",
        "techs": ["React Three Fiber", "Three.js", "Drei"],
        "scope": ["portfolio", "model", "interactive"],
    },
    "r3f-example": {
        "desc": "R3F example collection - various 3D patterns",
        "techs": ["React Three Fiber", "Drei"],
        "scope": ["various"],
    },
    "r3f-examples": {
        "desc": "R3F advanced examples - complex interaction",
        "techs": ["React Three Fiber", "Drei", "Cannon"],
        "scope": ["complex", "interactive"],
    },
}

# 모션 레퍼런스 메타데이터
MOTION_REFERENCES = {
    "anime": {
        "desc": "Anime.js - lightweight animation library",
        "techs": ["Anime.js"],
        "scope": ["scroll", "timeline", "easing"],
    },
    "shadergradient": {
        "desc": "Shader Gradient - 3D gradient background with WebGL",
        "techs": ["WebGL", "Shaders", "Three.js"],
        "scope": ["background", "gradient"],
    },
}


def _get_cache_key(query: str) -> str:
    """캐시 키 생성."""
    return hashlib.md5(query.encode()).hexdigest()


def _load_cache(key: str) -> Any:
    """캐시에서 데이터 로드."""
    cache_file = CACHE_DIR / f"{key}.pkl"
    if cache_file.exists():
        try:
            with open(cache_file, "rb") as f:
                return pickle.load(f)
        except Exception:
            pass
    return None


def _save_cache(key: str, data: Any):
    """캐시에 데이터 저장."""
    cache_file = CACHE_DIR / f"{key}.pkl"
    try:
        with open(cache_file, "wb") as f:
            pickle.dump(data, f)
    except Exception as e:
        print(f"⚠️  캐시 저장 실패: {e}")


def find_similar_design_md(site_type: str, style: str = None) -> List[Dict[str, str]]:
    """
    design-systems/design-md/ 폴더에서 유사한 기업의 DESIGN.md를 찾는다.

    Args:
        site_type: 사이트 유형 (예: "saas_dashboard", "product_landing")
        style: (선택) 스타일 (예: "clean_minimal")

    Returns:
        [{"company": "stripe", "path": "...", "relevance": "..."}, ...]
    """
    cache_key = _get_cache_key(f"design_md_{site_type}_{style}")
    cached = _load_cache(cache_key)
    if cached:
        return cached

    # 사이트 타입 매핑
    companies = SITE_TYPE_TO_COMPANIES.get(site_type, SITE_TYPE_TO_COMPANIES["default"])

    # 스타일도 고려
    if style:
        style_companies = STYLE_TO_COMPANIES.get(style, [])
        companies = list(set(companies) | set(style_companies))

    result = []
    for company in companies:
        # README.md 또는 DESIGN.md 찾기
        design_md_path = DESIGN_MD_DIR / company / "README.md"
        if not design_md_path.exists():
            design_md_path = DESIGN_MD_DIR / company / "DESIGN.md"

        if design_md_path.exists():
            relevance = f"Related to {site_type}" + (f", {style} style" if style else "")
            result.append({
                "company": company,
                "path": str(design_md_path),
                "relevance": relevance,
            })

    _save_cache(cache_key, result)
    return result


def find_components(categories: List[str] = None, sources: List[str] = None) -> List[Dict[str, Any]]:
    """
    design_system/components/ 에서 카테고리별로 컴포넌트를 찾는다.

    Args:
        categories: 찾을 카테고리 (예: ["Cards", "Buttons"])
        sources: 찾을 소스 (예: ["uiverse", "magicui"])

    Returns:
        [{"source": "uiverse", "category": "Cards", "path": "...", "count": 42}, ...]
    """
    cache_key = _get_cache_key(f"components_{sources}_{categories}")
    cached = _load_cache(cache_key)
    if cached:
        return cached

    sources = sources or list(COMPONENT_CATEGORIES.keys())
    result = []

    for source in sources:
        if source not in COMPONENT_CATEGORIES:
            continue

        source_dir = COMPONENTS_DIR / source
        if not source_dir.exists():
            continue

        available_categories = COMPONENT_CATEGORIES.get(source, [])
        target_categories = categories or available_categories

        for cat in target_categories:
            cat_path = source_dir / cat
            if cat_path.exists() and cat_path.is_dir():
                # 폴더/파일 개수 세기
                items = list(cat_path.glob("*"))
                count = len(items)

                result.append({
                    "source": source,
                    "category": cat,
                    "path": str(cat_path),
                    "count": count,
                    "type": "directory" if cat_path.is_dir() else "file",
                })

    _save_cache(cache_key, result)
    return result


def find_3d_examples(scope: List[str] = None) -> List[Dict[str, Any]]:
    """
    design_system/3d/ 에서 관련 3D 레퍼런스를 찾는다.

    Args:
        scope: 찾을 범위 (예: ["hero", "background", "particle"])

    Returns:
        [{"name": "threejs-landing", "path": "...", "desc": "...", ...}, ...]
    """
    result = []
    scope = scope or ["hero", "background", "particle", "portfolio", "model"]

    for name, meta in THREE_D_REFERENCES.items():
        example_dir = THREE_D_DIR / name
        if example_dir.exists():
            # scope와 교집합 확인
            match_scopes = [s for s in meta.get("scope", []) if s in scope or s == "various"]
            if match_scopes or not scope:
                result.append({
                    "name": name,
                    "path": str(example_dir),
                    "desc": meta.get("desc", ""),
                    "techs": meta.get("techs", []),
                    "match_scopes": match_scopes or meta.get("scope", []),
                })

    return result


def find_motion_examples(scope: List[str] = None) -> List[Dict[str, Any]]:
    """
    design_system/motion/ 에서 모션/애니메이션 라이브러리를 찾는다.

    Args:
        scope: 찾을 범위 (예: ["scroll", "background", "timeline"])

    Returns:
        [{"name": "anime", "path": "...", "desc": "...", ...}, ...]
    """
    result = []
    scope = scope or ["scroll", "timeline", "easing", "background"]

    for name, meta in MOTION_REFERENCES.items():
        example_dir = MOTION_DIR / name
        if example_dir.exists():
            match_scopes = [s for s in meta.get("scope", []) if s in scope]
            if match_scopes or not scope:
                result.append({
                    "name": name,
                    "path": str(example_dir),
                    "desc": meta.get("desc", ""),
                    "techs": meta.get("techs", []),
                    "match_scopes": match_scopes or meta.get("scope", []),
                })

    return result


def find_snippets() -> List[Dict[str, str]]:
    """
    design_system/snippets/ 에서 유용한 코드 조각을 찾는다.

    Returns:
        [{"name": "liquid-background.html", "path": "...", "desc": "..."}, ...]
    """
    result = []

    if not SNIPPETS_DIR.exists():
        return result

    snippet_map = {
        "liquid-background.html": "Three.js liquid background effect",
        "codepen-3d-references.md": "CodePen 3D references collection",
        "draftly-guide.md": "Draftly guide and examples",
    }

    for filename, desc in snippet_map.items():
        filepath = SNIPPETS_DIR / filename
        if filepath.exists():
            result.append({
                "name": filename,
                "path": str(filepath),
                "desc": desc,
            })

    return result


def analyze(project_description: str, design_plan: Dict[str, Any]) -> Dict[str, Any]:
    """
    메인 분석 함수. design_plan 기반으로 모든 관련 레퍼런스를 찾는다.

    Args:
        project_description: 프로젝트 설명 문자열
        design_plan: design_router.py 출력 (site_type, 3d_level, style_family 등)

    Returns:
        {
            "design_md_references": [...],
            "component_references": [...],
            "3d_references": [...],
            "motion_references": [...],
            "snippets": [...],
            "summary": {...}
        }
    """
    site_type = design_plan.get("site_type", "default")
    style = design_plan.get("style_family", "")
    three_d_level = design_plan.get("3d_level", "none")
    reference_sources = design_plan.get("reference_sources", [])
    stitch_scope = design_plan.get("stitch_scope", [])
    three_d_scope = design_plan.get("3d_scope", [])

    # 1. DESIGN.md 레퍼런스
    design_md_refs = find_similar_design_md(site_type, style)

    # 2. 컴포넌트 레퍼런스
    component_refs = find_components(categories=stitch_scope, sources=reference_sources)

    # 3. 3D 레퍼런스
    three_d_refs = []
    if three_d_level != "none":
        three_d_refs = find_3d_examples(scope=three_d_scope or ["hero", "background"])

    # 4. 모션 레퍼런스
    motion_refs = find_motion_examples()

    # 5. 스니펫
    snippets = find_snippets()

    result = {
        "design_md_references": design_md_refs,
        "component_references": component_refs,
        "3d_references": three_d_refs,
        "motion_references": motion_refs,
        "snippets": snippets,
        "summary": {
            "site_type": site_type,
            "style": style,
            "3d_level": three_d_level,
            "total_design_sources": len(design_md_refs),
            "total_components": sum(c.get("count", 0) for c in component_refs),
            "total_3d_examples": len(three_d_refs),
            "total_motion_libs": len(motion_refs),
        }
    }

    return result


def print_analysis(analysis_result: Dict[str, Any]):
    """분석 결과를 보기 좋게 출력한다."""
    print("\n" + "="*60)
    print("[Reference Analysis Results]")
    print("="*60)

    summary = analysis_result.get("summary", {})
    print(f"\n[Summary]")
    print(f"  Site Type: {summary.get('site_type')}")
    print(f"  Style: {summary.get('style', 'not set')}")
    print(f"  3D Level: {summary.get('3d_level')}")
    print(f"  Total Design Sources: {summary.get('total_design_sources')}")
    print(f"  Total Components: {summary.get('total_components')}")
    print(f"  3D Examples: {summary.get('total_3d_examples')}")
    print(f"  Motion Libraries: {summary.get('total_motion_libs')}")

    # DESIGN.md 레퍼런스
    design_refs = analysis_result.get("design_md_references", [])
    if design_refs:
        print(f"\n[Design.md References] ({len(design_refs)})")
        for ref in design_refs[:10]:  # 최대 10개만 출력
            print(f"  - {ref['company']}: {ref['relevance']}")

    # 컴포넌트 레퍼런스
    comp_refs = analysis_result.get("component_references", [])
    if comp_refs:
        print(f"\n[Components] ({len(comp_refs)})")
        for ref in comp_refs[:10]:
            print(f"  - {ref['source']}/{ref['category']}: {ref['count']} items")

    # 3D 레퍼런스
    three_d = analysis_result.get("3d_references", [])
    if three_d:
        print(f"\n[3D References] ({len(three_d)})")
        for ref in three_d:
            print(f"  - {ref['name']}: {ref['desc'][:50]}...")

    # 모션 라이브러리
    motion = analysis_result.get("motion_references", [])
    if motion:
        print(f"\n[Motion Libraries] ({len(motion)})")
        for ref in motion:
            print(f"  - {ref['name']}: {ref['desc'][:50]}...")

    # 스니펫
    snippets = analysis_result.get("snippets", [])
    if snippets:
        print(f"\n[Code Snippets] ({len(snippets)})")
        for ref in snippets:
            print(f"  - {ref['name']}: {ref['desc']}")

    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    # 테스트 1: SaaS Dashboard
    test_plan = {
        "site_type": "saas_dashboard",
        "3d_level": "hero_only",
        "style_family": "clean_futuristic",
        "reference_sources": ["magicui", "uiverse", "react-bits"],
        "stitch_scope": ["dashboard", "cards", "forms"],
        "3d_scope": ["hero", "background"],
    }

    result = analyze("AI 기반 영업 자동화 SaaS", test_plan)
    print_analysis(result)

    # JSON으로도 저장 가능
    output_path = Path(__file__).parent / "reference_analysis_sample.json"
    with open(output_path, "w", encoding="utf-8") as f:
        # Path 객체는 JSON 직렬화 안 되므로 문자열로 변환
        def path_to_str(obj):
            if isinstance(obj, dict):
                return {k: path_to_str(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [path_to_str(v) for v in obj]
            elif isinstance(obj, Path):
                return str(obj)
            return obj

        json.dump(path_to_str(result), f, indent=2, ensure_ascii=False)

    print(f"[SUCCESS] Analysis results saved: {output_path}")


def example_usage():
    """
    design_router.py와 함께 사용하는 예제.

    design_router.py 실행 후 결과를 받아서 reference_analyzer로 분석:

        from core.design_router import analyze_design_requirements
        from core.reference_analyzer import analyze, print_analysis

        # 1. design_router에서 설계 계획 생성
        design_plan = analyze_design_requirements("프로젝트 설명", {"경험수준": "advanced"})

        # 2. reference_analyzer에서 레퍼런스 자동 검색
        references = analyze("프로젝트 설명", design_plan)

        # 3. 결과 출력
        print_analysis(references)

        # 4. FE 에이전트/설계팀에 전달
        # design_md_references는 설계 가이드로
        # component_references는 Stitch 컴포넌트 소스로
        # 3d_references는 Three.js 구현으로
        # motion_references는 애니메이션 엔진으로 활용
    """
    pass
