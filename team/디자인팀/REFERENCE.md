# 디자인팀 — 툴 & 리소스 레퍼런스

---

## MCP 툴 (Claude에서 직접 호출)

### 연결됨

| MCP | 용도 | 핵심 툴 |
|-----|------|---------|
| **Stitch** | 텍스트→UI 스크린 생성 | `mcp__stitch__generate_screen_from_text`, `edit_screens`, `fetch_screen_code`, `generate_variants` |
| **나노바나나** | 텍스트→이미지 (Gemini Imagen 4.0) | `mcp__nano-banana__generate_image`, `edit_image` |

### 설치 필요 (서칭팀 발견)

| MCP | GitHub | 용도 |
|-----|--------|------|
| **Lighthouse MCP** | `@danielsogl/lighthouse-mcp` | 생성된 사이트 자동 퀄리티 점수 (성능/접근성/SEO 0-100) |
| **21st Magic MCP** | `21st-dev/magic-mcp` | IDE에서 UI 컴포넌트 변형 자동 생성 |
| **SuperDesign MCP** | `superdesigndev/superdesign` | 자연어→UI 목업. API 키 불필요 |
| **Blender MCP** | `ahujasid/blender-mcp` | Claude로 Blender 3D 모델링 직접 제어 |
| **Figma Context MCP** | `GLips/Figma-Context-MCP` | Figma 레이아웃→AI 코딩 에이전트 연동 |
| **Design Token Bridge MCP** | `kenneives/design-token-bridge-mcp` | 디자인 토큰 플랫폼 간 자동 변환 |
| **Replicate Flux MCP** | `awkoy/replicate-flux-mcp` | Flux 이미지 + Recraft SVG 생성 |

---

## 로컬 툴

### Veo Generator (`tools/veo_generator.py`)
Google Imagen 4.0 + Veo 2.0으로 배경 영상 자동 생성 (8초 mp4).
```bash
python tools/veo_generator.py "abstract flowing energy" --style abstract_dark|luxury|tech|nature
```

### 영상 클로너 (`company/utils/video_cloner.py`)
인스타/유튜브 URL → 영상 다운로드 → Gemini 디자인 스펙 추출 → Claude HTML 클론 생성.
```bash
cd company && ./venv/Scripts/python.exe utils/video_cloner.py "URL"
```

---

## 컴포넌트 라이브러리 (components/)

### 기존

| 레포 | 내용 | 경로 |
|------|------|------|
| **react-bits** | 배경 셰이더 40개 + 텍스트 애니메이션 24개 + 커서 30개 (React JSX) | `components/react-bits/` |
| **reactbits-alt** | react-bits 대체 버전 | `components/reactbits-alt/` |
| **uiverse** | 버튼/카드/인풋/로더 HTML+CSS 726개+ | `components/uiverse/` |
| **magicui** | Magic UI React 컴포넌트 | `components/magicui/` |
| **shadcn** | shadcn/ui 컴포넌트 | `components/shadcn/` |
| **shadcn-templates** | shadcn 기반 완성 템플릿 | `components/shadcn-templates/` |
| **21st** | 21st.dev 컴포넌트 | `components/21st/` |

### 신규 (2026-04-10 추가)

| 레포 | GitHub | 내용 | 경로 |
|------|--------|------|------|
| **mouse-follower** | Cuberto/mouse-follower | GSAP 기반 프로덕션급 커서 효과 | `components/mouse-follower/` |
| **shader-web-background** | xemantic/shader-web-background | GLSL 셰이더→웹 배경. Shadertoy 호환 | `components/shader-web-background/` |
| **vfx-js** | fand/vfx-js | HTML 요소에 WebGL 효과 한 줄로 적용 | `components/vfx-js/` |
| **theatre** | theatre-js/theatre | 웹용 모션 디자인 에디터. Three.js/HTML/SVG | `components/theatre/` |
| **tsparticles** | tsparticles/tsparticles | particles.js 후속. 모든 프레임워크 지원 | `components/tsparticles/` |
| **cursor-effects** | tholman/cursor-effects | fairy dust, snowflake 등 커서 이펙트 | `components/cursor-effects/` |
| **blobity** | gmrchk/blobity | 블롭 커서 효과. React 지원 | `components/blobity/` |
| **motion** | motiondivision/motion | Framer Motion 후속. JS/React/Vue 범용 | `components/motion/` |
| **aos** | michalsnik/aos | 8KB 스크롤 애니메이션 (가장 가벼움) | `components/aos/` |

### 미설치 (npm/CDN으로 사용)

| 라이브러리 | npm | 내용 |
|-----------|-----|------|
| **@mesh-gradient/core** | npm | SwiftUI 영감 메시 그라디언트. WebGL 가속 |
| **gradient-stripe** | npm | Stripe 스타일 WebGL 메시 그라디언트 |
| **OGL** | npm `ogl` | Three.js보다 가벼운 WebGL 라이브러리 |
| **TWGL.js** | npm `twgl.js` | WebGL 헬퍼. Three.js 오버헤드 없이 직접 |
| **gl-react** | npm | React 컴포넌트로 셰이더 조합 |
| **quad-shader** | npm | 제로 의존성 GLSL→2D 애니메이션 |
| **Rive** | npm `@rive-app/canvas` | 스테이트 머신 기반 인터랙티브 애니메이션 |
| **Trig.js** | npm `trig.js` | 8KB CSS 네이티브 애니메이션 |

---

## 3D (3d/)

| 레포 | 스택 | 내용 |
|------|------|------|
| **threejs-landing** | Three.js + GSAP | 랜딩용 패턴 |
| **threejs-portfolio** | Three.js + 카메라 | 카메라 움직임, 모델 로딩 |
| **r3f-portfolio** | R3F + Framer | R3F 씬 구성 |
| **r3f-example** | R3F | 기본 패턴 |
| **r3f-examples** | R3F | 다양한 패턴 |

### 3D 도구 (미설치, 필요 시 사용)

| 도구 | 내용 |
|------|------|
| **Spline** (`@splinetool/runtime`) | 비주얼 3D 에디터→React 임베드 |
| **model-viewer** (`@google/model-viewer`) | glTF/GLB 모델 웹 컴포넌트+AR |
| **Babylon.js** | MS 엔터프라이즈 3D 엔진 |
| **A-Frame** | HTML 태그로 3D/VR 씬 |
| **Needle Engine** | Three.js 기반 3D 런타임. Unity/Blender 익스포트 |

---

## 디자인 레퍼런스 (design-md/)

59개 기업 디자인 시스템 분석 문서.

| 카테고리 | 기업 |
|----------|------|
| 결제/금융 | stripe, coinbase, revolut, wise, kraken |
| SaaS/생산성 | notion, linear.app, airtable, figma, miro, cal, framer |
| AI/Tech | openai, claude, cohere, replicate, elevenlabs, mistral.ai, x.ai, minimax, ollama, together.ai, voltagent |
| 개발 도구 | vercel, supabase, expo, hashicorp, raycast, warp, semrush, sentry, posthog, resend, sanity, mintlify, webflow, opencode.ai, composio, clickhouse, mongodb |
| 브랜드/럭셔리 | apple, bmw, ferrari, lamborghini, tesla, renault, spacex, spotify, airbnb, pinterest, uber |
| 기타 | nvidia, ibm, intercom, zapier, superhuman, runwayml, lovable, clay |

---

## 퀄리티 체크 도구 (미설치)

| 도구 | 용도 |
|------|------|
| **BackstopJS** | 생성 전후 스크린샷 비교 비주얼 QA |
| **Argos** | PR별 비주얼 diff |
| **Lighthouse** (CLI) | 성능/접근성/SEO 0-100 자동 점수 |
| **Style Dictionary** | W3C 디자인 토큰→CSS/SCSS/JS 빌드 |

---

## 완성 레퍼런스 (demo/)

| 파일 | 내용 |
|------|------|
| `showcase.html` | 다크 퓨처리스틱 SaaS 랜딩 완성본 (515줄) |
| `hand-shader.html` | 손추적 + 셰이더 데모 |

---

## 인스타 디자인 스펙 (video_cloner_output/)

| 스펙 파일 | 원본 | 핵심 |
|----------|------|------|
| `video_1775767130_spec.json` | 릴스 1 | 3D 컴포넌트 + 인터랙티브 캔버스 + 셰이더 라인 |
| `video_1775767277_spec.json` | 릴스 2 | 3D car/book + wave prism + animated gradient |
| `video_1775767402_spec.json` | 릴스 3 | scroll-driven 3D + glassmorphism + parallax |
| `video_1775767510_spec.json` | 릴스 4 | 화이트+파스텔 그라데이션 + 3D page fold |
| `video_1775767626_spec.json` | 릴스 5 | tubes cursor + liquid text + particle orb |
| `insta_DWRPyEMGBIT_spec.json` | 포스트 6 | 3D bee + 스크롤 스토리텔링 + 퍼플+골드 |

경로: `company/utils/video_cloner_output/`

---

## 모션/인터랙티브

| 경로 | 내용 |
|------|------|
| `motion/anime/` | Anime.js — SVG 모핑, path 애니메이션 |
| `motion/shadergradient/` | ShaderGradient — 실시간 그라데이션 셰이더 |
| `interactive/hand-particles/` | 카메라 손→파티클 (MediaPipe) |
| `interactive/gesture-particles/` | 제스처 인식 파티클 |
| `interactive/handtracking-101/` | 기본 손 추적 |
| `interactive/handwave-xr/` | XR 핸드웨이브 |

---

## 기타

| 경로 | 내용 |
|------|------|
| `snippets/` | codepen 3D 레퍼런스, liquid 배경 html |
| `mcp/` | Magic UI MCP 서버 |
| `mcp-magic-ui/` | Magic UI MCP (빌드 포함) |

---

## 외부 레퍼런스 사이트

| 사이트 | URL | 내용 |
|--------|-----|------|
| **Codrops** | tympanus.net/codrops/ | 1000+ WebGL+GSAP+Three.js 데모/튜토리얼 |
| **samcodes.ai** | samcodes.ai | 트렌디한 인터랙션 디자인 패턴+코드 1000개+ |
| **CodeMyUI** | codemyui.com | 208+ 웹 애니메이션 HTML/CSS 스니펫 |
| **scroll-driven-animations.style** | scroll-driven-animations.style | CSS 스크롤 애니메이션 데모 모음 |
