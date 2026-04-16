---
name: landing
description: design_system/ 레포 기반 최고 퀄 랜딩페이지 자동 생성
---

# /landing — 최고 퀄 랜딩페이지 자동 생성

## ⚡ Step -1: 사이트 타입 자동 감지 (가장 먼저)

프로젝트 설명을 보고 즉시 판단:

**Track A — 실물 비즈니스** (아래 키워드 포함 시):
레스토랑, 카페, 인테리어, 뷰티, 헤어, 부동산, 호텔, 펜션, 패션, 음식점, 병원, 클리닉, 피트니스, 웨딩, 쇼핑, 브랜드, 제품

→ **Imagen+Veo 영상 히어로 파이프라인** 실행:
```python
import sys, os
_ROOT = os.popen("git rev-parse --show-toplevel").read().strip()
sys.path.insert(0, os.path.join(_ROOT, "company"))
os.chdir(os.path.join(_ROOT, "company"))
from dotenv import load_dotenv; load_dotenv()
from core.gen_hero import generate_hero

result = generate_hero(
    business_type="[레스토랑/카페/인테리어/뷰티/호텔/패션]",
    description="[프로젝트 설명]",
    output_dir="[출력 폴더 절대경로]"
)
print(result)
```

생성된 hero.mp4를 `<video autoplay muted loop playsinline>` 히어로 배경으로 사용.
supanova 규칙 적용: Pretendard + Cormorant Garamond, 골드/웜 컬러, Double-Bezel 카드, Floating glass nav.

**Track B — SaaS/Tech/AI/플랫폼** (아래 키워드 포함 시):
SaaS, AI, 플랫폼, 대시보드, 앱, 서비스, 소프트웨어, 자동화, 데이터, 분석, B2B, 툴, 시스템

→ 기존 GLSL 셰이더 파이프라인 실행 (Step 0부터 진행)

---

리안이 "랜딩 만들어줘" / "사이트 만들어" / `/landing` 하면 아래를 즉시 실행해라.

---

## Step -0.5: 최근 7일 디자인 트렌드 자동 로드

design_context_picker 전에 트렌드 읽기. 효과/색상 방향 결정에 반영.

```python
import os
from pathlib import Path
from datetime import datetime, timedelta

_ROOT = os.popen("git rev-parse --show-toplevel").read().strip()
TRENDS_DIR = Path(_ROOT) / "company" / "knowledge" / "base" / "design" / "trends"
today = datetime.now()
recent_trends = []

for i in range(7):
    f = TRENDS_DIR / f"{(today - timedelta(days=i)).strftime('%Y-%m-%d')}.md"
    if f.exists():
        recent_trends.append(f.read_text(encoding="utf-8"))

if recent_trends:
    trends_context = "\n\n---\n\n".join(recent_trends[:3])
    print(f"[TRENDS] {len(recent_trends)}일치 트렌드 로드")
else:
    trends_context = ""
    print("[TRENDS] 없음")
```

`trends_context`에서 추출 → 이후 단계에 반영:
- **반복 효과** (2일+ 등장) → Step 6 HTML에 우선 적용
- **색상 힌트** → design_context_picker 선택 가이드
- **훔칠 것** → 구체적 인터랙션으로 구현

---

## Step 0: design_context_picker 실행 (⚠️ 필수)

이 단계를 **반드시 먼저 실행해야 한다.**

```python
import sys, os
_ROOT = os.popen("git rev-parse --show-toplevel").read().strip()
sys.path.insert(0, os.path.join(_ROOT, "company"))
os.chdir(os.path.join(_ROOT, "company"))
from dotenv import load_dotenv
load_dotenv()

from core.design_context_picker import pick

# 프로젝트 설명을 받으면 즉시 pick() 실행
design_context = pick("[프로젝트명 + 설명]")

print(f"\n✅ {design_context['total_chars']:,} 글자 로드됨")
print(f"📋 선택된 파일:")
for file in design_context['selected']:
    print(f"  - {file}")
```

**이 step의 역할:**
- design_system/ 폴더에서 **태스크에 맞는 파일만** 선택적으로 로드
- 항상 같은 2개(LiquidChrome, Silk)만 읽는 게 아니라, **프로젝트마다 다른 이펙트 조합** 읽힘
- 로드된 context에서 effects[].content를 Step 5에서 직접 포팅

**skip 금지**: 건너뛰면 결과가 제한됨. 반드시 실행.

---

## Step 1: 프로젝트 파악

현재 폴더에 있는 파일 확인:
- `PRD.md` 있으면 읽기 (기획서)
- `CLAUDE.md` 있으면 읽기 (프로젝트 배경)
- 둘 다 없으면 → 리안에게 한 줄 질문: **"어떤 사이트 만들까? 한 줄만 알려줘"**

파악할 것:
- **프로젝트 이름 + 목적**
- **타겟 고객**
- **핵심 메시지 3개**

---

## Step 2: 디자인 방향 자동 결정 (design_router)

```python
import sys, os
_ROOT = os.popen("git rev-parse --show-toplevel").read().strip()
sys.path.insert(0, os.path.join(_ROOT, "company"))
os.chdir(os.path.join(_ROOT, "company"))
from dotenv import load_dotenv
load_dotenv()

from core.design_router import route
# Step 1에서 읽은 프로젝트 설명 (또는 리안의 한 줄) 입력
design_plan = route("[프로젝트명 + 목적 + 타겟]")
```

**출력 예시 (JSON):**
```json
{
  "pattern": "dark_futuristic",
  "shader": "noise",
  "particle": "DNA",
  "colors": ["#6366f1", "#a78bfa", "#22d3ee"],
  "template": "interactive_particles.html",
  "3d_level": "hero_only",
  "site_type": "product_landing"
}
```

**이 JSON의 `template` 값 → Step -1.5에서 복사할 파일.
`shader` → 복사한 HTML의 셰이더 코드를 그대로 쓰고 `colors`만 교체.
`particle` → 복사한 HTML의 파티클 형태를 그대로 쓰거나 이 값으로 변형.**

---

## Step 3: 레퍼런스 자동 분석 (reference_analyzer)

```python
from core.reference_analyzer import analyze
refs = analyze("[프로젝트 설명]", design_plan)
```

**출력 결과를 리안에게 보여주기:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎨 디자인 전략 (자동 분석)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

사이트 타입: [design_plan.site_type]
3D 레벨: [design_plan.3d_level]
스타일: [design_plan.style_family]

참고 배경: [3D 스타일에 맞는 배경]
참고 컴포넌트: [2-3개 추천]
참고 DESIGN.md: [1-2개 기업 레퍼런스]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
수정할 거 있으면 말해. 없으면 "진행해" 입력.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

리안 응답:
- **"진행해"** → Step 4로
- **수정 요청** (예: "더 크리에이티브하게") → design_plan 값 수정 후 Step 4로

---

## Step 3.5: 도구 분기 (design_plan 기반 자동 결정)

design_plan.3d_level과 site_type 보고 아래 도구 조합 자동 결정:

| 요소 | 도구 | 조건 |
|---|---|---|
| **3D 히어로/셰이더/파티클** | 서연(클코 본체) 직접 HTML + Three.js 스킬 | 3d_level ≠ "none" |
| **2D UI 컴포넌트** | Stitch MCP | 대시보드/로그인/설정 페이지 |
| **마케팅 이미지/소재** | Nano Banana MCP | 제품 사진/배너 필요 시 |
| **시네마틱 배경 영상** | Veo (tools/veo_generator.py) | Track A (실물 비즈니스) |
| **디자인 토큰 참고** | design_system/design-md/ | 항상 |
| **검증된 템플릿** | design_system/templates/ | 항상 (베이스로 사용) |

**핵심 분기:**
- 히어로/랜딩/마케팅 → **CDO(나은)한테 넘기지 마라.** 서연이 직접 HTML.
- 대시보드/설정 UI → CDO Stitch → FE 구현.

---

## Step 3.7: ⛔ Director — 은유 선택 + 시네마틱 스토리. 스킵 금지.

**기술 스펙 금지. 은유와 스토리가 먼저. 코드는 나중.**

`Agent(model="opus")` 스폰:
```
너는 크리에이티브 디렉터야.

프로젝트: [프로젝트명]
브랜드 핵심 메시지: [3개]
타겟: [타겟 고객]

## 할 일 (순서대로):

### 1. 은유 후보 3~7개 나열
주제에서 나올 수 있는 은유들. 예시:
- "디스커버리" → 탐험, 동굴, 여행, 지도, 신호, 발굴, 등대, 균열에서 나오는 빛
- "핀테크" → 동전이 쌓이는 탑, 금고 문이 열림, 디지털 강줄기
각 은유를 한 줄로. 나열만, 선택 아직 금지.

### 2. 하나 선택
브랜드 스토리에 가장 맞는 은유 1개. 선택 이유 한 줄.

### 3. 시네마틱 스토리 작성 (5~10문장)
영화 오프닝처럼 써라:
- 우리가 어디에 있는가
- 무엇이 먼저 등장하는가
- 무엇이 움직이거나 변화하는가
- 브랜드가 어떻게 드러나는가 (마지막에)
산문체. 기술 용어 금지. "ShaderMaterial" "Three.js" 같은 단어 절대 금지.

## 출력: HERO_CONCEPT.md 파일로 저장
경로: [현재 프로젝트 폴더]/HERO_CONCEPT.md
형식:
---
metaphor: [선택한 은유]
brand_message: [브랜드가 전달하는 핵심 감정/메시지]
---
[시네마틱 스토리 산문]
```

**이 파일이 이후 모든 Step의 원천이다. 기술이 아니라 스토리에서 시작.**

---

## Step 3.8: ⛔ Visual Director — 스토리보드. 스킵 금지.

**HERO_CONCEPT.md를 받아서 구체적인 비주얼 플랜으로 변환.**

`Agent(model="opus")` 스폰:
```
너는 비주얼 디렉터야. 시네마틱 스토리를 구현 가능한 비주얼 플랜으로 변환해.

HERO_CONCEPT.md 읽어라: [경로]
design_plan: [Step 2 결과 JSON]

## 할 일:

### 비주얼 플랜 작성
아래 항목을 순서대로, 구체적으로:

1. **Opening Shot** — 사용자가 페이지를 열었을 때 첫 0.5초에 보이는 것
2. **Motion Sequence** — 처음 3~5초 동안 무슨 일이 일어나는가 (단계별)
3. **Text Reveal** — 브랜드 타이틀/서브카피가 언제, 어떻게 등장하는가
   - 시간 기반 금지. 반드시 **카메라 위치 또는 스크롤 진행도**에 동기화
4. **Camera Path** — 카메라가 이동하는 경로
   - 형식: progress 0.0~1.0 기준 keyframe 3~5개
   - 각 keyframe: progress값, 카메라 위치(x,y,z), 바라보는 방향
5. **Effects** — 사용할 이펙트 (effect 라이브러리에서 선택):
   - crack / emissive-core / glow-line / distortion / unfold / bloom-stack / camera-scroll
   - 이유와 함께
6. **Technology** — three_js_code / css_motion / video_scroll 중 선택. 이유 한 줄.
7. **Brand Reveal Moment** — 스크롤 progress 몇 %에서 브랜드가 완전히 드러나는가

## 금지:
- 이 단계에서 코드 작성 금지
- effect 라이브러리에 없는 걸 발명하지 마라 — 있는 걸 조합해라
- "예쁘게" "화려하게" 같은 추상적 표현 금지 — 전부 구체적 수치/동작으로

## 출력: HERO_PLAN.md 파일로 저장
경로: [현재 프로젝트 폴더]/HERO_PLAN.md
```

**HERO_PLAN.md가 hero_builder의 유일한 입력이다.**

---

## Step 3.9: ⛔ hero_builder — 히어로 전담 구현. 스킵 금지.

**역할: Step 3.8의 HERO_PLAN.md를 받아 히어로 섹션만 구현. 시네마틱 임팩트 규칙 강제.**

**실행 전: `design_system/templates/effects/INDEX.md` 읽고 HERO_PLAN.md에 맞는 이펙트 선택.**
선택한 이펙트의 `effect.md` → `notes.md` → `implementation.js` 순서로 읽어라.

서연 서브에이전트로 스폰:
```
Agent(prompt="""
너는 히어로 섹션 전담 구현자야.
HERO_PLAN.md를 그대로 받아서 히어로 HTML+JS만 작성해.

HERO_PLAN.md 읽어라:
[현재 프로젝트 폴더]/HERO_PLAN.md

## 이펙트 라이브러리 (반드시 여기서 조립):
경로: design_system/templates/effects/

사용 가능한 이펙트:
- crack/           균열 벌어짐 + 카메라 관통
- emissive-core/   발광 유기체 코어 + 촉수
- glow-line/       에너지 빔 / 기둥 / 문 프레임
- distortion/      이미지 디스플레이스먼트 호버
- unfold/          오리가미 패널 순차 열림
- bloom-stack/     수동 블룸 파이프라인 (다른 이펙트에 추가)
- camera-scroll/   스크롤 연동 카메라 플라이스루 (cinematicSilk easing + Lenis)

HERO_PLAN.md에서 핵심 오브젝트와 카메라 경로를 파악하고:
1. INDEX.md 읽어서 어떤 이펙트가 맞는지 결정
2. 선택한 이펙트의 effect.md → Anti-Patterns 확인
3. implementation.js 읽어서 그대로 사용하거나 커스터마이즈
HERO_PLAN.md가 묘사한 컨셉과 다르면 implementation.js를 변형해라.
라이브러리에 없는 건 새로 짜되, 있는 거 다시 짜지 마라.

## 강제 규칙 (어기면 실패):
- 첫 1.5초 안에 화면 전체를 뒤집는 모션 1개 이상
- MeshBasicMaterial flat 색상으로 히어로 구현 금지
- SphereGeometry / BoxGeometry 그대로 히어로 오브젝트로 쓰기 금지
- 타이포는 fade만 금지 — scale/position/clip-path 중 최소 2개 조합
- 화면을 가로지르는 메인 모션 경로 1개 (수평/대각/나선)
- 배경+텍스트가 "잔잔한 이미지 + 타이틀"로 보이면 실패

## 출력 형식:
히어로 섹션 HTML (section.hero + 관련 CSS + JS)만 출력.
전체 페이지 아님. 나머지 섹션 구현 금지.
""")
```

**hero_builder 결과 → Step 4~6에서 그대로 삽입. 히어로 수정 금지.**

---

## Step 4: INDEX.md 필수 읽기

이 단계를 **절대 스킵하면 안 된다.**

`design_system/INDEX.md` 파일을 Read 도구로 읽어라.

읽고 확인할 것:
- **design_plan.3d_level**과 matching되는 배경 셰이더 찾기
  - 예: `3d_level: "hero_only"` → LiquidChrome, Silk, Aurora 중 선택
- **design_plan.style_family**에 맞는 텍스트 애니메이션
  - 예: `style_family: "clean_minimal"` → SplitText, BlurText
- **커서 스타일** (기본: dot + lagging ring)

---

## Step 5: 배경 셰이더 소스 코드 준비 (⚠️ 핵심)

**Step 0에서 로드한 design_context의 effects[]를 직접 사용하면 된다.**

design_context['effects']에 이미 다음이 포함되어 있다:
- 이펙트 이름 (예: "LiquidChrome", "Silk", "Aurora" 등)
- 실제 소스 코드 (이미 로드됨, 최대 8000자)
- 파일 경로

**이 코드에서 추출해야 할 것:**
- GLSL 셰이더 코드 (fragmentShader, vertexShader)
- Three.js/Babylon.js 초기화 패턴
- 유니폼 변수 (시간, 마우스 위치 등)

**예시:**
```python
for effect in design_context['effects']:
    print(f"효과: {effect['name']}")
    print(f"경로: {effect['path']}")
    shader_code = effect['content']  # 여기서 GLSL 셰이더 추출
    # Step 6에서 이 코드를 HTML에 직접 포팅
```

**⚠️ 이 Step을 건너뛰면 퀄이 떨어집니다. Step 0에서 이미 로드되었으니 활용하세요.**

---

## Step 6: HTML 생성 (최종 코드 작성)

### 6-1. 보일러플레이트 구조

```html
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>[프로젝트명]</title>
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', sans-serif;
            background: #0a0a0a;
            color: #fff;
            overflow-x: hidden;
        }
        
        h1, h2, h3 { font-family: 'Space Grotesk', sans-serif; }
        
        /* 커스텀 커서 */
        * { cursor: none; }
        
        #cursor {
            position: fixed;
            width: 8px;
            height: 8px;
            background: #fff;
            border-radius: 50%;
            pointer-events: none;
            z-index: 9999;
        }
        
        #cursor-ring {
            position: fixed;
            width: 30px;
            height: 30px;
            border: 1px solid rgba(255, 255, 255, 0.5);
            border-radius: 50%;
            pointer-events: none;
            z-index: 9998;
        }
        
        /* clamp() 반응형 타이포 */
        h1 { font-size: clamp(2rem, 8vw, 4rem); }
        h2 { font-size: clamp(1.5rem, 5vw, 2.5rem); }
        p { font-size: clamp(1rem, 2.5vw, 1.125rem); }
        
        /* SVG Grain Overlay */
        #grain {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            opacity: 0.03;
            z-index: 1;
        }
        
        /* WebGL Canvas */
        #gl {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 0;
        }
        
        main {
            position: relative;
            z-index: 2;
        }
        
        section {
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 2rem;
        }
    </style>
</head>
<body>
    <!-- WebGL 배경 -->
    <div id="gl"></div>
    
    <!-- SVG Grain Overlay -->
    <svg id="grain" width="100%" height="100%">
        <filter id="noise">
            <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="4" result="noise" seed="2"/>
            <feDisplacementMap in="SourceGraphic" in2="noise" scale="1"/>
        </filter>
        <rect width="100%" height="100%" filter="url(#noise)" opacity="0.03"/>
    </svg>
    
    <!-- 커스텀 커서 -->
    <div id="cursor"></div>
    <div id="cursor-ring"></div>
    
    <!-- 콘텐츠 -->
    <main>
        <section class="hero">
            <div style="text-align: center; max-width: 800px;">
                <h1 class="split-text">[프로젝트명]</h1>
                <p class="split-text" style="margin-top: 1rem; color: rgba(255, 255, 255, 0.7);">
                    [핵심 메시지]
                </p>
                <button style="margin-top: 2rem; padding: 1rem 2rem; background: #fff; color: #000; border: none; border-radius: 0.5rem; font-weight: 600; cursor: pointer;">
                    시작하기
                </button>
            </div>
        </section>
        
        <!-- 추가 섹션 (리안 요청에 따라 작성) -->
    </main>
    
    <!-- CDN 라이브러리 -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js"></script>
    <script src="https://unpkg.com/lenis@1.1.18/dist/lenis.min.js"></script>
    
    <script>
        // ===== Lenis Smooth Scroll =====
        const lenis = new Lenis({
            duration: 1.2,
            easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
            direction: 'vertical',
            gestureOrientation: 'vertical',
            smoothWheel: true,
        });
        
        function raf(time) {
            lenis.raf(time);
            requestAnimationFrame(raf);
        }
        requestAnimationFrame(raf);
        
        // ===== 커스텀 커서 =====
        const cursor = document.getElementById('cursor');
        const cursorRing = document.getElementById('cursor-ring');
        let mouseX = 0, mouseY = 0;
        let ringX = 0, ringY = 0;
        
        document.addEventListener('mousemove', (e) => {
            mouseX = e.clientX;
            mouseY = e.clientY;
            cursor.style.left = (mouseX - 4) + 'px';
            cursor.style.top = (mouseY - 4) + 'px';
        });
        
        // Ring lagging 애니메이션
        setInterval(() => {
            ringX += (mouseX - ringX - 15) * 0.15;
            ringY += (mouseY - ringY - 15) * 0.15;
            cursorRing.style.left = ringX + 'px';
            cursorRing.style.top = ringY + 'px';
        }, 16);
        
        // ===== WebGL 배경 셰이더 =====
        // Step 5에서 읽은 GLSL fragmentShader와 vertexShader를 여기에 삽입
        const container = document.getElementById('gl');
        const cvs = document.createElement('canvas');
        container.appendChild(cvs);
        const gl = cvs.getContext('webgl2') || cvs.getContext('webgl');
        
        function resize() {
            cvs.width = window.innerWidth;
            cvs.height = window.innerHeight;
            gl.viewport(0, 0, cvs.width, cvs.height);
        }
        resize();
        window.addEventListener('resize', resize);
        
        // Vertex Shader (기본)
        const vs = `
            attribute vec2 p;
            varying vec2 vUv;
            void main() {
                vUv = p * 0.5 + 0.5;
                gl_Position = vec4(p, 0, 1);
            }
        `;
        
        // Fragment Shader (Step 5에서 읽은 코드 삽입 — 아래는 기본 예시)
        const fs = `
            precision highp float;
            uniform float u_time;
            uniform vec2 u_mouse;
            varying vec2 vUv;
            
            void main() {
                vec2 uv = vUv;
                vec3 col = mix(
                    vec3(0.05, 0.05, 0.1),
                    vec3(0.2, 0.15, 0.3),
                    sin(uv.y * 3.0 + u_time * 0.5) * 0.5 + 0.5
                );
                gl_FragColor = vec4(col, 1.0);
            }
        `;
        
        // Shader 컴파일 헬퍼
        function compileShader(src, type) {
            const s = gl.createShader(type);
            gl.shaderSource(s, src);
            gl.compileShader(s);
            if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) {
                console.error(gl.getShaderInfoLog(s));
            }
            return s;
        }
        
        // Program 링크
        const prog = gl.createProgram();
        gl.attachShader(prog, compileShader(vs, gl.VERTEX_SHADER));
        gl.attachShader(prog, compileShader(fs, gl.FRAGMENT_SHADER));
        gl.linkProgram(prog);
        
        if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) {
            console.error(gl.getProgramInfoLog(prog));
        }
        
        gl.useProgram(prog);
        
        // VBO 설정
        const buf = gl.createBuffer();
        gl.bindBuffer(gl.ARRAY_BUFFER, buf);
        gl.bufferData(
            gl.ARRAY_BUFFER,
            new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]),
            gl.STATIC_DRAW
        );
        
        const pLoc = gl.getAttribLocation(prog, 'p');
        gl.enableVertexAttribArray(pLoc);
        gl.vertexAttribPointer(pLoc, 2, gl.FLOAT, false, 0, 0);
        
        // Uniform 설정
        const uTimeLoc = gl.getUniformLocation(prog, 'u_time');
        const uMouseLoc = gl.getUniformLocation(prog, 'u_mouse');
        
        // 렌더 루프
        let startTime = Date.now();
        function render() {
            const elapsed = (Date.now() - startTime) / 1000;
            gl.uniform1f(uTimeLoc, elapsed);
            gl.uniform2f(uMouseLoc, mouseX / cvs.width, 1 - mouseY / cvs.height);
            gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
            requestAnimationFrame(render);
        }
        render();
        
        // ===== SplitText 애니메이션 =====
        gsap.registerPlugin(ScrollTrigger);
        
        document.querySelectorAll('.split-text').forEach((el) => {
            const text = el.innerText;
            el.innerHTML = text.split('').map(char => 
                char === ' ' ? '&nbsp;' : `<span style="display:inline-block">${char}</span>`
            ).join('');
            
            gsap.from(el.querySelectorAll('span'), {
                duration: 0.8,
                opacity: 0,
                y: 10,
                stagger: 0.02,
                ease: 'power2.out'
            });
        });
    </script>
</body>
</html>
```

### 6-2. 실제 코드 작성 규칙

**필수 포함 요소:**
- ✅ WebGL 셰이더 배경 (Step 0의 design_context['effects']에서 추출한 GLSL)
- ✅ Lenis smooth scroll
- ✅ 커스텀 커서 (dot + lagging ring)
- ✅ SVG grain overlay
- ✅ SplitText 또는 BlurText reveal (GSAP) — design_context['effects']에 해당 이펙트 있으면 사용
- ✅ clamp() 반응형 타이포
- ✅ Space Grotesk + Inter 폰트
- ✅ 어두운 배경 (dark mode)
- ✅ design_context['design_refs']에서 참고한 DESIGN.md의 색감 팔레트 적용

**design_context 활용법:**
```javascript
// Step 0의 design_context 구조를 HTML에 주입
const effectsUsed = design_context['effects'];  // [{"name": "LiquidChrome", "content": "..."}]
const designRefs = design_context['design_refs'];  // [{"brand": "stripe", "content": "..."}]

// 각 effect의 content에서 GLSL/JS 코드 추출해서 직접 포팅
// 각 design_ref의 content에서 색감 토큰, 폰트 스케일, 간격 규칙 추출
```

**절대 금지:**
- ❌ 내 기본 패턴 (Three.js 파티클/와이어프레임 구)
- ❌ design_context 무시하고 새로 만든 배경
- ❌ 기본 브라우저 스크롤
- ❌ opacity 0→1 단순 페이드
- ❌ 고정 px 폰트 사이즈
- ❌ 기본 검은 배경만

---

## Step 7: 파일 생성 + 브라우저 열기

현재 폴더에 `index.html` (또는 `landing.html`) 생성 후 브라우저로 열기:

```bash
start "" "[파일경로]"
```

**Windows:**
```bash
start "" "$(git rev-parse --show-toplevel)/team/[프로젝트명]/index.html"
```

---

## Step 7.5: Visual QA 자동 평가 (Gemini Vision)

HTML 생성 후 **브라우저 열기 전에** 자동 평가 실행:

```python
import sys, os
_ROOT = os.popen("git rev-parse --show-toplevel").read().strip()
sys.path.insert(0, os.path.join(_ROOT, "company"))
os.chdir(os.path.join(_ROOT, "company"))
from dotenv import load_dotenv; load_dotenv()

from core.visual_qa_loop import run_qa
result = run_qa("[HTML 파일 경로 또는 localhost URL]", "SCENE.md", max_iterations=2)
```

**결과 판단:**
- **85점 이상** → Step 8로 (리안에게 보여주기)
- **85점 미만** → QA 피드백 기반으로 HTML 자동 수정 1회 → 재평가
- **재평가 후에도 85점 미만** → 그대로 리안에게 보여주되 점수 + 이슈 함께 보고

---

## Step 7.8: ⛔ Polish Pass (마감 품질 보정)

**HTML 생성 후, 리안에게 보여주기 전에 반드시 실행.**

`polish` 스킬을 로드하고 아래 7개 항목 순서대로 체크+수정:

1. **Typography Scale** — clamp() 범위, weight 계층, letter-spacing
2. **Spacing System** — 8px 배수, 섹션 padding, max-width
3. **Color Contrast** — WCAG AA, opacity 최소값
4. **Visual Hierarchy** — 섹션당 초점 1개, CTA 돋보임
5. **Motion Restraint** — 동시 움직임 ≤3, Bloom ≤0.8, stagger 0.05~0.15s
6. **Mobile** — grid 1열, 터치 44px, 커서 숨김, 파티클 50% 감소
7. **Performance** — rAF, lazy loading, pixelRatio 제한

**규칙: 새 기능 추가 금지. 컨셉 변경 금지. 마감만.**

---

## Step 8: 리안 확인 + 반복

리안이 사이트를 본 후:
- **"좋아"** → 완료, Git 커밋
- **"더 ~해줘"** (예: "더 크리에이티브하게" / "배경 바꿔줘") → Step 2로 돌아가서 design_plan 수정 → Step 6 재작성

---

## 참고: 검증된 조합

### 다크 퓨처리스틱 (추천)
```
배경: LiquidChrome shader (showcase.html 참고)
텍스트: SplitText reveal (line by line)
커서: dot + lagging ring
색감: 웜 블랙 + 골드 accent
```

### 클린 미니멀
```
배경: Silk shader
텍스트: BlurText reveal
커서: Crosshair (옵션)
색감: 화이트 + 단일 accent
```

### 브랜드/크리에이티브
```
배경: Aurora 또는 Iridescence
텍스트: GlitchText
커서: BlobCursor (옵션)
색감: 비비드 그라데이션
```

---

## 레퍼런스

- **실제 작동 예시**: `design_system/demo/showcase.html`
- **INDEX.md**: `design_system/INDEX.md`
- **GLSL 셰이더 예제**: `design_system/snippets/liquid-background.html`
