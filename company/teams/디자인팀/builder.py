#!/usr/bin/env python3
"""
Builder v5 — 3 Pass 방식 (HTML → CSS → JS)

핵심 개선:
- Pass 2 CSS: HTML 구조를 받아서 실제 class명에 맞는 CSS 작성
- Pass 3 JS: IntersectionObserver 초기 뷰포트 즉시 처리 명시
- fonts_url: italic 변형도 로드
"""
import os, re
import anthropic

DESIGN_TEAM_ROOT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
    "team", "디자인팀"
)
REACT_BITS_BG   = os.path.join(DESIGN_TEAM_ROOT, "components", "react-bits", "src", "content", "Backgrounds")
REACT_BITS_TEXT = os.path.join(DESIGN_TEAM_ROOT, "components", "react-bits", "src", "content", "TextAnimations")
REACT_BITS_ANIM = os.path.join(DESIGN_TEAM_ROOT, "components", "react-bits", "src", "content", "Animations")

CURSOR_CAT = {
    "BlobCursor": "Animations", "GhostCursor": "Animations",
    "ImageTrail": "Animations", "PixelTrail": "Animations",
    "SplashCursor": "Animations", "TargetCursor": "Animations",
    "Crosshair": "Animations", "MouseFollower": None,
}


def read_src(name, cat):
    roots = {"Backgrounds": REACT_BITS_BG, "TextAnimations": REACT_BITS_TEXT, "Animations": REACT_BITS_ANIM}
    path = os.path.join(roots.get(cat, ""), name, f"{name}.jsx")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f: src = f.read()
        print(f"  📄 {name}.jsx ({len(src):,}자)"); return src
    return ""


def extract_glsl(src):
    r = {}
    for key, patterns in [
        ("vertex",   [r'vertexShader\s*[:=]\s*`([^`]+)`', r'vertexShader\s*=\s*`([^`]+)`']),
        ("fragment", [r'fragmentShader\s*[:=]\s*`([^`]+)`', r'fragmentShader\s*=\s*`([^`]+)`']),
    ]:
        for p in patterns:
            m = re.search(p, src, re.DOTALL)
            if m: r[key] = m.group(1)[:2000]; break
    if "fragment" not in r:
        m = re.search(r'`([^`]*gl_FragColor[^`]*)`', src, re.DOTALL)
        if m: r["fragment"] = m.group(1)[:2000]
    return r


# ──────────────────────────────────────────────────────────────────────
# PASS 1: HTML 구조
# ──────────────────────────────────────────────────────────────────────
PASS1_SYS = """시니어 HTML 작성자. 역할: body 안에 들어가는 HTML 구조만 작성.
규칙:
- <style>, <script> 태그 절대 포함 금지
- 실제 콘텐츠 텍스트 포함 (placeholder 금지)
- 한국어 텍스트는 최소화 (섹션당 1-2줄)
- 각 섹션 제목의 단어는 <span class="word">단어</span>로 감싸기
- canvas#shader-canvas 맨 위에 (body 첫 번째)
- #cursor-dot, #cursor-ring 포함

nav 구조 필수 (이 구조 그대로):
<nav id="main-nav">
  <div class="nav-inner">
    <a href="#" class="nav-logo">브랜드명</a>
    <ul class="nav-links">
      <li><a href="#section">메뉴</a></li>
    </ul>
    <a href="#contact" class="nav-cta">CTA텍스트</a>
  </div>
</nav>

- 섹션: hero, collection, services, contact (각 <section id="..."> 형태)
- hero 섹션: <section id="hero"><div class="hero-content">...</div></section>
출력: HTML 태그들만 (DOCTYPE/html/head 없이, body 태그도 없이, 순수 콘텐츠만)"""


def gen_html(concept, project_desc, client):
    sections = concept.get("sections", ["hero", "collection", "services", "contact"])
    p = f"""프로젝트: {project_desc}
컨셉: {concept['name']} — {concept['big_idea']}
섹션: {', '.join(sections)}
브랜드 이름: 영문 브랜드명 창작 (컨셉에 맞게)
서비스: 웨딩 플라워, 부케, 구독
HTML 구조만 출력 (style/script 없이)."""
    r = client.messages.create(model="claude-sonnet-4-6", max_tokens=3000, system=PASS1_SYS,
                                messages=[{"role": "user", "content": p}])
    html = r.content[0].text.strip()
    html = re.sub(r'<style[\s\S]*?</style>', '', html, flags=re.IGNORECASE)
    html = re.sub(r'<script[\s\S]*?</script>', '', html, flags=re.IGNORECASE)
    html = re.sub(r'<!DOCTYPE[^>]+>', '', html, flags=re.IGNORECASE)
    html = re.sub(r'</?html[^>]*>', '', html, flags=re.IGNORECASE)
    html = re.sub(r'</?head[^>]*>', '', html, flags=re.IGNORECASE)
    html = re.sub(r'</?body[^>]*>', '', html, flags=re.IGNORECASE)
    print(f"  ✅ HTML ({len(html):,}자)")
    return html.strip()


# ──────────────────────────────────────────────────────────────────────
# PASS 2: CSS (HTML 구조를 알고 작성)
# ──────────────────────────────────────────────────────────────────────
PASS2_SYS = """CSS 전문가. 역할: Visual DNA 법칙을 따르면서, HTML 구조에 맞는 CSS를 작성. 최대 150줄.

⚠️ Visual DNA가 주어지면 반드시 따른다:
- 색상법칙 → :root 변수 + 모든 색상 선택
- 모션법칙 → transition 속도, transform 방향
- 형태법칙 → border-radius, 라인 스타일

필수 포함:
- :root { CSS 변수들 }
- body { cursor:none; background:var(--bg); color:var(--primary); font-family:var(--font-body); }
- #shader-canvas { position:fixed; top:0; left:0; width:100%; height:100%; z-index:-1; pointer-events:none; }
- #cursor-dot { position:fixed; width:8px; height:8px; background:var(--primary); border-radius:50%; pointer-events:none; z-index:9999; transform:translate(-50%,-50%); }
- #cursor-ring { position:fixed; width:40px; height:40px; border:1px solid var(--primary); border-radius:50%; pointer-events:none; z-index:9998; transform:translate(-50%,-50%); transition:width .3s,height .3s; }
- .word { display:inline-block; opacity:0; transform:translateY(25px); transition:opacity .8s,transform .8s; }
- .word.visible { opacity:1; transform:translateY(0); }
- #main-nav { position:fixed; top:0; left:0; right:0; z-index:900; padding:1.4rem clamp(1.5rem,6vw,8rem); background:linear-gradient(to bottom,rgba(0,0,0,.8),transparent); backdrop-filter:blur(8px); }
- .nav-inner { display:flex; align-items:center; justify-content:space-between; width:100%; }
- .nav-logo { font-family:var(--font-heading); font-size:clamp(1.1rem,2vw,1.5rem); color:var(--primary); text-decoration:none; }
- .nav-links { list-style:none; display:flex; align-items:center; gap:2rem; }
- .nav-links a { font-size:.8rem; letter-spacing:.15em; text-transform:uppercase; color:rgba(255,255,255,.65); text-decoration:none; transition:color .3s; }
- .nav-cta { padding:.5em 1.5em; border:1px solid var(--accent); color:var(--primary); font-size:.8rem; letter-spacing:.12em; text-transform:uppercase; text-decoration:none; transition:background .3s,color .3s; }
- section { padding:clamp(5rem,10vw,12rem) clamp(1.5rem,6vw,8rem); }
- #hero { min-height:100vh; display:flex; align-items:center; }
- h1 { font-family:var(--font-heading); font-size:clamp(2.8rem,7vw,6.5rem); font-weight:300; line-height:1.1; }
- clamp() 타이포그래피 필수
- HTML에 있는 모든 클래스 스타일링 필수
- 백틱(`) 절대 사용 금지
출력: CSS 규칙만 (style 태그 없이)"""


def gen_css(concept, html_body, client):
    colors = concept["colors"]
    typo = concept["typography"]

    # HTML에서 실제 class 이름 추출 (CSS가 알아야 할 정보)
    raw_classes = re.findall(r'class="([^"]+)"', html_body)
    unique_cls = list(dict.fromkeys(c for s in raw_classes for c in s.split()))
    cls_hint = "  ".join(f".{c}" for c in unique_cls[:60])

    # Visual DNA가 있으면 법칙 추출
    dna = concept.get("visual_dna", {})
    dna_rules = ""
    if dna:
        dna_rules = f"""
Visual DNA 법칙 (반드시 따를 것):
- 색상법칙: {dna.get('color_rule','없음')}
- 모션법칙: {dna.get('motion_rule','없음')}
- 형태법칙: {dna.get('shape_rule','없음')}
- 금지: {', '.join(dna.get('forbidden',[]))}
"""

    p = f"""색상: bg={colors.get('bg','#0a0a0a')} primary={colors.get('primary','#fff')} accent={colors.get('accent','#888')} secondary={colors.get('secondary','#ccc')}
폰트: --font-heading='{typo['heading_font']}', --font-body='{typo['body_font']}'
스타일 방향: {concept['name']} — {concept.get('special','')}
{dna_rules}

HTML 클래스 목록 (전부 스타일링 필수):
{cls_hint}

HTML 구조 앞부분 (참고):
{html_body[:1500]}

150줄 이내로."""
    r = client.messages.create(model="claude-sonnet-4-6", max_tokens=2500, system=PASS2_SYS,
                                messages=[{"role": "user", "content": p}])
    css = r.content[0].text.strip()
    css = re.sub(r'</?style[^>]*>', '', css, flags=re.IGNORECASE).strip()
    css = re.sub(r"```\w*\n?", '', css)
    css = re.sub(r"'''\w*\n?", '', css)
    css = css.strip()
    print(f"  ✅ CSS ({len(css):,}자)")
    return css


# ──────────────────────────────────────────────────────────────────────
# PASS 3: JavaScript
# ──────────────────────────────────────────────────────────────────────
PASS3_SYS = """WebGL + 인터랙션 엔지니어. 역할: JavaScript만 작성.
규칙:
- HTML/CSS 주입 없음 — DOM은 이미 있음
- querySelector로 기존 DOM 요소 찾아서 사용
- 반드시 포함: WebGL 셰이더(#shader-canvas), Lenis, 커스텀 커서(#cursor-dot/#cursor-ring), SplitText
- Lenis: const lenis = new Lenis(); raf 루프
- 커서: mousemove에서 dot 즉시 이동, ring에 CSS transition으로 lag
- SplitText + IntersectionObserver:
  1. h1,h2,h3,[data-split] 요소의 텍스트를 단어 단위로 <span class="word">로 감싸기
  2. IntersectionObserver (threshold:0.1)로 .visible 토글
  3. ⚠️ 필수: observer.observe(el) 전에 이미 뷰포트 안 요소 즉시 처리:
     targets.forEach(el => {
       if (el.getBoundingClientRect().top < window.innerHeight * 0.95) {
         el.querySelectorAll('.word').forEach((w,i) => setTimeout(()=>w.classList.add('visible'), i*70));
       }
       observer.observe(el);
     });
- WebGL: 주어진 GLSL로 fullscreen quad. uniform uTime(float), uMouse(vec2 0~1), uResolution(vec2)
- GLSL 없으면: canvas 2D로 animated gradient 대체 (requestAnimationFrame 루프)
- window.addEventListener('DOMContentLoaded', init) 로 감싸기
- 백틱(template literal) 써도 됨 — JS 안에서만
출력: 순수 JavaScript만 (script 태그 없이)"""


def gen_js(concept, bg_src, cur_src, client):
    glsl = extract_glsl(bg_src)
    has_glsl = bool(glsl.get("vertex") or glsl.get("fragment"))
    print(f"  {'✅' if has_glsl else '⚠️'} GLSL {'추출' if has_glsl else '없음'}")

    dna = concept.get("visual_dna", {})
    motion_rule = dna.get("motion_rule", "")
    cursor_name = concept.get('cursor', 'BlobCursor')
    if isinstance(cursor_name, dict):
        cursor_name = cursor_name.get('component', 'BlobCursor')

    p = f"""컨셉: {concept['name']} | 커서: {cursor_name}
{f'모션법칙: {motion_rule}' if motion_rule else ''}

GLSL — {concept['background']['component']}:
Vertex:
{glsl.get('vertex', '없음 — canvas 2D gradient 대체')[:800]}

Fragment:
{glsl.get('fragment', '없음 — canvas 2D gradient 대체')[:1500]}

커서 참고:
{cur_src[:400] if cur_src else '#cursor-dot 8px, #cursor-ring 40px border ring — mousemove로 위치 업데이트'}

배경 accent color: {concept['colors'].get('accent','#888')}
JS만 출력."""
    r = client.messages.create(model="claude-sonnet-4-6", max_tokens=5000, system=PASS3_SYS,
                                messages=[{"role": "user", "content": p}])
    js = r.content[0].text.strip()
    js = re.sub(r'</?script[^>]*>', '', js, flags=re.IGNORECASE).strip()
    js = re.sub(r'```\w*\n?', '', js).strip()
    print(f"  ✅ JS ({len(js):,}자)")
    return js


# ──────────────────────────────────────────────────────────────────────
# 조립
# ──────────────────────────────────────────────────────────────────────
def build_html(concept, project_desc, client):
    print(f"\n🔨 Builder v5 — {concept['id']}: {concept['name']}")

    bg     = concept["background"]["component"]
    bg_src = read_src(bg, "Backgrounds")
    cur    = concept.get("cursor", "BlobCursor")
    if isinstance(cur, dict):
        cur = cur.get("component", "BlobCursor")
    cur_src = read_src(cur, CURSOR_CAT.get(cur, "Animations")) if CURSOR_CAT.get(cur) else ""

    typo = concept["typography"]
    hf = typo["heading_font"].replace(" ", "+")
    hw = typo["heading_weight"]
    bf = typo["body_font"].replace(" ", "+")
    bw = typo["body_weight"]
    # italic 변형도 포함 (serif heading에 font-style:italic 작동하도록)
    fonts_url = (
        f"https://fonts.googleapis.com/css2"
        f"?family={hf}:ital,wght@0,{hw};1,{hw}"
        f"&family={bf}:wght@{bw}"
        f"&display=swap"
    )

    print("  [1/3] HTML 구조...")
    html_body = gen_html(concept, project_desc, client)

    print("  [2/3] CSS (HTML 구조 참고)...")
    css = gen_css(concept, html_body, client)

    print("  [3/3] JavaScript...")
    js = gen_js(concept, bg_src, cur_src, client)

    # ── 강제 패치: LLM이 빠뜨리는 코드 주입 ──────────────────────────
    # 1) .word 초기 뷰포트 패치 — IntersectionObserver 타이밍 이슈 방어
    word_patch = """
// [PATCH] .word 초기 뷰포트 표시 — IntersectionObserver 타이밍 fallback
(function() {
  function revealInViewport() {
    var words = document.querySelectorAll('.word');
    words.forEach(function(w) {
      var parent = w.closest('h1,h2,h3,section,nav,.hero-content,[data-split]') || w.parentElement;
      if (!parent) return;
      var r = parent.getBoundingClientRect();
      if (r.bottom > 0 && r.top < window.innerHeight * 1.05) {
        w.classList.add('visible');
      }
    });
  }
  // DOMContentLoaded + 300ms 후 한 번, load 후 한 번 더
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() { setTimeout(revealInViewport, 300); });
  } else {
    setTimeout(revealInViewport, 100);
  }
  window.addEventListener('load', function() { setTimeout(revealInViewport, 200); });
})();"""

    # 2) Lenis 안전 fallback — CDN 로드 실패 시 no-op
    lenis_fallback = """<!-- Lenis CDN -->\n  <script src="https://cdn.jsdelivr.net/npm/@studio-freight/lenis@1.0.45/bundled/lenis.min.js"></script>
  <script>if(typeof Lenis==='undefined'){window.Lenis=function(){this.on=function(){return this};this.raf=function(){};this.scrollTo=function(){};};console.warn('Lenis CDN failed, using no-op fallback');}</script>"""

    final = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{concept['name']}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="{fonts_url}" rel="stylesheet">
  {lenis_fallback}
  <style>
{css}
  </style>
</head>
<body>
{html_body}
<script>
{js}
{word_patch}
</script>
</body>
</html>"""

    print(f"  ✅ 최종 HTML ({len(final):,}자)")
    return final


def validate_html(html, concept):
    issues = []
    if "<body" not in html:        issues.append("CRITICAL: <body> 없음")
    if "</html>" not in html:      issues.append("CRITICAL: </html> 없음")
    if "```" in html or "'''" in html: issues.append("CRITICAL: markdown 아티팩트")
    if "<script>" not in html:     issues.append("CRITICAL: <script> 없음")
    if "<nav" not in html and "<section" not in html:
        issues.append("CRITICAL: HTML 구조 없음")
    if "nav-inner" not in html:    issues.append("CRITICAL: nav-inner 없음 (nav 레이아웃 깨짐)")
    if "lenis" not in html.lower(): issues.append("Lenis 미포함")
    hf = concept["typography"]["heading_font"]
    if hf.lower() not in html.lower() and hf.replace(" ","+").lower() not in html.lower():
        issues.append(f"폰트 미로드: {hf}")
    if "canvas" not in html.lower(): issues.append("canvas 없음")
    if "getBoundingClientRect" not in html:
        issues.append("SplitText 초기 뷰포트 처리 없음")
    return len(issues) == 0, issues


def validate_html_browser(html_path):
    """Playwright로 실제 브라우저 렌더링 검증"""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("  ⚠️ Playwright 없음 — 브라우저 검증 스킵")
        return True, []

    errors = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1280, "height": 720})

            console_errors = []
            page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
            page.on("pageerror", lambda err: console_errors.append(str(err)))

            file_url = "file:///" + html_path.replace("\\", "/")
            page.goto(file_url, wait_until="domcontentloaded", timeout=10000)
            page.wait_for_timeout(2000)

            fatal_kw = ["webgl", "shader", "uncaught", "referenceerror",
                        "typeerror", "syntaxerror", "cannot read", "is not defined",
                        "is not a function", "failed to compile"]
            for err in console_errors:
                if any(kw in err.lower() for kw in fatal_kw):
                    errors.append(f"JS오류: {err[:200]}")

            has_content = page.evaluate("""() => {
                const els = document.querySelectorAll('h1,h2,nav,section');
                let visible = 0;
                els.forEach(el => { const r = el.getBoundingClientRect(); if (r.width > 0 && r.height > 0) visible++; });
                return visible >= 3;
            }""")
            if not has_content:
                errors.append("CRITICAL: 보이는 콘텐츠 없음 (빈 화면)")

            # h1 텍스트가 실제로 보이는지 (opacity > 0)
            h1_visible = page.evaluate("""() => {
                const words = document.querySelectorAll('h1 .word');
                if (!words.length) return true;  // word 없으면 패스
                let visible = 0;
                words.forEach(w => {
                    const style = window.getComputedStyle(w);
                    if (parseFloat(style.opacity) > 0.5) visible++;
                });
                return visible > 0;
            }""")
            if not h1_visible:
                errors.append("CRITICAL: h1 텍스트 안 보임 (.word opacity=0)")

            screenshot_path = html_path.replace(".html", "_preview.png")
            page.screenshot(path=screenshot_path)
            print(f"  📸 프리뷰: {screenshot_path}")

            browser.close()
    except Exception as e:
        errors.append(f"브라우저 검증 실패: {str(e)[:200]}")

    return len(errors) == 0, errors
