---
name: creative-coding
description: Creative coding patterns for award-winning web design — generative art, spatial UX, non-particle 3D, organic motion, light themes. Use when designing unique visual concepts, breaking out of particle/dark patterns, or creating Awwwards-level diversity.
---

# Creative Coding / Awwwards UI Skill

## 10점 사이트의 시각 카테고리 (파티클 외)

### Category 1: Fluid / Liquid
- WebGL Navier-Stokes 시뮬레이션
- 마우스가 잉크/물감처럼 번짐
- 레퍼런스: `design_system/references/webgl-fluid/`
```javascript
// CDN으로 사용 가능한 fluid 배경
// PavelDoGreat/WebGL-Fluid-Simulation 참조
// 핵심: framebuffer ping-pong + advection + pressure solve
```

### Category 2: Morphing Geometry
- 하나의 3D 형태가 다른 형태로 변환
- 예: 구 → 얼굴 → 로고 → 텍스트
- Three.js MorphTargets 또는 GPGPU(FBO) 사용
```javascript
// BufferGeometry morph
const geo = new THREE.BufferGeometry();
geo.morphAttributes.position = [target1Positions, target2Positions];
mesh.morphTargetInfluences[0] = scrollProgress;
```

### Category 3: Typography as Hero
- 텍스트 자체가 3D 오브젝트
- TextGeometry + 셰이더로 글자가 깨지거나 흘러내리거나 터짐
- 파티클이 모여서 글자 형태를 만듦 (GPGPU)
```javascript
import { TextGeometry } from 'three/addons/geometries/TextGeometry.js';
import { FontLoader } from 'three/addons/loaders/FontLoader.js';
// 글자 위에 파티클을 배치 → 스크롤 시 산발
```

### Category 4: Camera Journey
- 스크롤 = 카메라가 3D 공간을 여행
- 파티클 없이 기하학 공간만으로 임팩트
- Three.js CatmullRomCurve3로 카메라 경로 정의
```javascript
const curve = new THREE.CatmullRomCurve3([
  new THREE.Vector3(0,0,10),
  new THREE.Vector3(5,2,5),
  new THREE.Vector3(-3,0,0),
  new THREE.Vector3(0,-2,-5),
]);
// scroll → curve.getPointAt(progress)
camera.position.copy(curve.getPointAt(scrollProgress));
camera.lookAt(curve.getPointAt(scrollProgress + 0.01));
```

### Category 5: 2D Canvas / SVG Animation
- WebGL 없이 Canvas 2D or SVG로 고퀄 달성
- PixiJS 필터, SVG morphing, Lottie
- **밝은 배경에서 작동** (AdditiveBlending 불필요)
```javascript
// PixiJS 2D 파티클 (밝은 배경 OK)
const app = new PIXI.Application({ background: '#ffffff' });
const emitter = new PIXI.ParticleContainer(1000);
// DisplacementFilter로 물결 효과
const displace = new PIXI.DisplacementFilter(sprite);
app.stage.filters = [displace];
```

### Category 6: Image Reveal / Distortion
- 이미지가 글리치/왜곡/모자이크로 등장
- hover-effect 라이브러리 또는 커스텀 셰이더
- 레퍼런스: `design_system/references/hover-effect/`
```javascript
// hover-effect (distortion transition)
new hoverEffect({
  parent: document.querySelector('.img-container'),
  image1: 'img1.jpg',
  image2: 'img2.jpg',
  displacementImage: 'displacement.png',
  intensity: 0.6,
});
```

### Category 7: Scroll-driven Video
- 스크롤 = 비디오 프레임 제어
- Apple 제품 페이지 스타일
- `video.currentTime = scrollProgress * video.duration`

## 밝은 테마 전략

어두운 배경 + AdditiveBlending 없이 9점 내는 방법:

1. **그림자 기반**: MeshStandardMaterial + DirectionalLight + 부드러운 그림자
2. **와이어프레임 라인**: LineBasicMaterial + EdgesGeometry (밝은 배경에 선만)
3. **PixiJS 2D 필터**: DisplacementFilter, BlurFilter (밝은 배경 네이티브)
4. **SVG 모션**: GSAP MorphSVGPlugin으로 형태 변환
5. **CSS 3D**: perspective + rotateY/Z + clip-path (WebGL 없이)

## Director 다양성 강제 규칙 + 도구 우선순위

감독한테 컨셉을 짤 때 이 카테고리 중에서 선택하게 해:

```
프로젝트 컨셉별 권장 카테고리 + 우선 도구:
- 금융/핀테크 → Camera Journey + 기하학               → three.js CatmullRomCurve3
- 뷰티/패션   → Image Reveal + Fluid                  → hover-effect (우선) + webgl-fluid
- 교육/HR    → Typography Hero + 밝은 테마             → PixiJS + CSS 3D
- 부동산/건축 → Camera Journey + Scroll Video           → three.js + GSAP video
- AI/SaaS   → Fluid + Camera Journey                  → webgl-fluid (우선) + three.js
- 포트폴리오  → Image Reveal + Camera Journey           → hover-effect (우선)
- 이커머스   → 2D Canvas + 밝은 테마                    → PixiJS
- 카페/레스토랑 → Scroll Video + Image Reveal           → GSAP video + hover-effect
```

**핵심 우선순위:**
- SaaS/AI/테크 → `webgl-fluid` 우선 (파티클 뿌리기 대신 유체 시뮬)
- 뷰티/패션/포트폴리오 → `hover-effect` 우선 (이미지 디스토션)
- 밝은 테마 → `PixiJS` (AdditiveBlending 없이 2D WebGL)
## OGL (경량 WebGL 대안)

Three.js 대신 OGL 사용하면:
- 번들 70KB (Three.js 600KB+)
- 스크롤 마이크로 인터랙션에 적합
- 레퍼런스: `design_system/references/ogl/`

```javascript
import { Renderer, Camera, Program, Mesh, Triangle } from 'ogl';
const renderer = new Renderer();
const gl = renderer.gl;
document.body.appendChild(gl.canvas);
// 풀스크린 셰이더는 Triangle + Program으로 충분
```
