# Frontend Design Skill — 서연 표준

웹 페이지/UI를 만들 때 자동으로 적용되는 디자인 원칙.
리안이 따로 말하지 않아도 이 기준 이상으로 출력한다.

## 1. 레이아웃 & 공간

- 여백은 항상 8px 배수 (8/16/24/32/48/64/80/96px)
- 섹션 간격 최소 80px — 답답하게 붙이지 마라
- 최대 너비: 콘텐츠 1200px, 텍스트 720px
- 그리드: 12컬럼 기준, gap 1px + 배경색으로 구분선 처리
- 모바일 first — clamp() 반응형 필수

## 2. 타이포그래피

- 헤드라인: `clamp(36px, 6vw, 100px)` — 절대 고정 px 쓰지 마라
- letter-spacing: 헤드라인 -2px~-4px / 레이블 +3px~+6px
- line-height: 헤드라인 0.9~1.0 / 본문 1.6~1.7
- font-weight: 900(히어로) / 700(제목) / 400(본문) — 중간값(500/600) 남발 금지
- 그라디언트 텍스트: background-clip: text + animation 필수

## 3. 색상 & 대비

- 배경은 #000 또는 #fff 중 하나로 확실히 — 어중간한 회색 금지
- 다크 테마: 텍스트 계층 #fff / #888 / #444 / #222
- 강조색: 프로젝트 톤에 맞게 — 억지로 퍼플/블루/그린 넣지 마라
- WCAG AA 최소 준수 — 배경 대비 4.5:1 이상

## 4. 애니메이션 & 모션

- 필수 3종: fadeUp(등장) + ScrollTrigger(스크롤) + 카운트업(숫자)
- GSAP 우선 — IntersectionObserver는 폴백용
- easing: `power3.out` / `power4.out` — ease-in-out 금지
- 지연: stagger 0.07~0.12s 순차 등장
- 호버: translateY(-3px) + box-shadow glow 동시

## 5. Three.js 파티클 — 표준 구현

**기본 구조:**
```js
// 파티클 COUNT: 4000~8000
// blending: THREE.AdditiveBlending (글로우 필수)
// depthWrite: false
// ⚠️ 형태는 프로젝트 컨셉에 따라 결정 — 구 하나로 고정하지 마라
```

**컨셉별 파티클 형태 (반드시 이 기준으로):**
| 프로젝트 컨셉 | 파티클 형태 |
|---|---|
| AI / 테크 / 자동화 | DNA 이중나선 + 노드 연결선, 신경망 |
| 에이전시 / 크리에이티브 | Curl Noise 흐름 (오로라), 폭발 후 산개 |
| 금융 / SaaS / 대시보드 | 정밀 격자(Grid), 수직 기둥(Pillar) |
| 패션 / 라이프스타일 | 리본 흐름, 유기적 웨이브 |
| 음식 / 로컬 비즈니스 | 따뜻한 구름형, 별자리 분포 |
| 포트폴리오 / 쇼케이스 | 씬별 전환: 구→토러스→폭발→나선 |
| 텍스트 강조 | 파티클이 텍스트 형태로 모이는 모핑 |
| 기본값 (컨셉 불명확) | 구형 분포 |

**GLSL 버텍스 셰이더 필수 요소:**
- `uTime` uniform — 웨이브 모션 `sin(t + pos.y * 2.0) * 0.08`
- `uMouse` uniform — 마우스 리펄전 (커서 가까이 도망)
- `uScroll` uniform — 스크롤에 반응하는 Y 드리프트
- `aScale` attribute — 파티클마다 다른 크기
- `aOffset` attribute — 각자 다른 위상 (동기화 금지)
- `gl_PointSize = aScale * (380.0 / -mvPos.z)` — 원근감

**모핑 (고급):**
- 3개 위치 배열 (aSpherePos / aTorusPos / aScatterPos)
- `mod(uTime * 0.15, 3.0)`으로 사이클
- `smoothstep` mix로 부드러운 전환

**파티클 색상:**
- 위치 기반 그라디언트 (vColor = mix(purple, blue, nx))
- AdditiveBlending으로 겹치면 자연스럽게 밝아짐
- alpha에 `sin(t + aOffset)` 적용 — 살아있는 느낌

**배경 디테일:**
- `THREE.TorusGeometry` 와이어링 2~3개 배경 배치
- 투명도 0.05~0.1 — 배경 장식만

## 6. 인터랙션

- 커스텀 커서: dot(4~6px) + lagging ring(40px)
  - `gsap.set(dot)` + `gsap.to(ring, {duration:.12})`
  - hover 시 ring 60px + 보라 border
- 마우스 → 카메라 시차: `camera.position.x += (mouseX*0.2 - camera.position.x)*0.04`
- 파티클 마우스 리펄전: `smoothstep(0.8, 0.0, dist) * 0.6`
- 버튼: gradient background + glow box-shadow on hover

## 7. 신뢰/퀄리티 체크

- 노이즈 텍스처: SVG fractalNoise `body::after` — opacity .2~.35
- 마퀴: `animation: marquee 18s linear infinite` — 2배 복제해서 끊김 없이
- 스크롤 인디케이터: scaleY 애니메이션 drip 효과
- 섹션 구분: `border-top: 1px solid #080808` — 컬러 구분선 금지
- 푸터: border-top + 좌우 split

## 8. Bloom 안전 설정 (⚠️ 필수)

**UnrealBloomPass 과노출 방지:**
- `threshold`: 최소 **0.1** 이상 — 0.0~0.05 절대 금지 (전체 화면 하얗게 됨)
- `strength`: 최대 **1.5** — 2.0 이상은 폭발
- `radius`: 0.4~0.6 범위

**파티클 크기:**
- `gl_PointSize = clamp(aScale * (120.0~150.0 / -mvPos.z), 0.5, 10.0)`
- 400.0 분모 금지 — 카메라 가까울 때 파티클이 화면 꽉 채움
- 카메라 z: 최소 5.0 이상 유지 (파티클 구 반지름 1.5~2.0일 때)

## 9. 포트폴리오/쇼케이스 레이아웃 (activetheory 패턴)

씬 기반 쇼케이스 페이지:
- 우상단: `WORK — CONTACT` 알약버튼 (border: 1px solid #333, border-radius: 20px)
- 좌측: 마우스 < 200px 접근 시 카테고리 nav 등장 (`opacity: 0 → 1`)
- 씬 카운터: 우하단 `01 / 05` 형태
- 텍스트 효과: 글리치 스크램블 (랜덤 문자 → 실제 텍스트, 약 1.5초)
- 씬 전환: fade out → camera zoom out → 씬 교체 → camera zoom in → fade in

**씬 설계 원칙:**
- 씬마다 완전히 다른 색상 + 파티클 구조 (구/토러스/폭발/나선/기둥)
- 배경색 `scene.background`를 씬마다 변경
- 블룸 강도도 씬마다 다르게

## 10. 차세대 기술 (다음 목표)

GLB 모델 없이 award-winning 수준 가능한 기술:
1. **파티클 텍스트 모핑** (GPGPU/FBO) — 텍스트↔파티클↔형태 전환
   - 레퍼런스: Codrops Dec 2024 오픈소스
   - Three.js `GPUComputationRenderer` 사용
2. **WebGL 유체 시뮬레이션** — Navier-Stokes, 커서가 잉크처럼 번짐
   - 레퍼런스: paveldogreat.github.io/WebGL-Fluid-Simulation (오픈소스)
3. **Curl Noise 파티클 플로우** — 오로라 같은 빛 궤적
4. **Ray Marching SDF** — 모델 없이 포토리얼 3D 세계 (ShaderToy 스타일)

## SaaS 구조 기본값

- 마케팅/랜딩 페이지 → 위 모든 규칙 풀 적용
- 앱/대시보드 UI → Stitch 설계 + 클린/미니멀 (파티클 없음)
- 쇼케이스/포트폴리오 → activetheory 패턴 (섹션 9)

## 출력 체크리스트

웹 페이지 뽑기 전 이것만 확인:
- [ ] Three.js ShaderMaterial 파티클 (AdditiveBlending) 있나?
- [ ] GLSL에 uTime/uMouse/uScroll uniform 있나?
- [ ] 마우스 리펄전 or 시차 있나?
- [ ] 커스텀 커서 (dot + ring) 있나?
- [ ] clamp() 반응형 타이포 썼나?
- [ ] GSAP ScrollTrigger 스크롤 애니메이션 있나?
- [ ] 노이즈 텍스처 오버레이 있나?
- [ ] 마퀴 배너 있나?
- [ ] 숫자 카운트업 있나?
- [ ] 모바일 반응형 있나?
- [ ] **Bloom threshold ≥ 0.1** 인가? (과노출 방지)
- [ ] **카메라 z ≥ 5.0** 인가? (파티클 크기 안전)

## 디자인 분기 (히어로/랜딩 vs 대시보드)

히어로/랜딩/마케팅 페이지:
→ CDO(나은)한테 넘기지 마라
→ 서연(클코 본체)이 직접 HTML 작성
→ web-quality.md + 이 파일 규칙 자동 적용
→ design_system/ 소스코드 직접 참조
→ Three.js 스킬 (threejs-shaders, threejs-postprocessing 등) 자동 로드

대시보드/로그인/설정:
→ CDO(나은) Stitch로 UI 생성 → FE(민준)이 구현

## 디자인 레시피 (검증된 조합)

새 프로젝트 히어로/랜딩 만들 때:
1. `design_system/templates/` 에서 가장 비슷한 레퍼런스 HTML 선택
2. 그 HTML을 베이스로 복사
3. 프로젝트에 맞게 수정 (텍스트, 색상, 파티클 형태)
4. 새로 만들지 마라. 검증된 것을 변형해라.

절대 금지:
- 빈 파일에서 처음부터 시작하는 것
- 레퍼런스 안 보고 "알아서" 만드는 것

## 레퍼런스 파일 (templates/)

| 파일 | 특징 | 용도 |
|---|---|---|
| `design_system/templates/cafe_hero.html` | GSAP SplitText + 커스텀 커서 + SVG grain + 다크 무드 | 로컬 비즈니스/카페/감성 |
| `design_system/templates/hothaan_hero.html` | clamp() 반응형 + SaaS 스타일 + 비디오 배경 | SaaS/대행사/서비스 |
| `design_system/templates/interactive_particles.html` | WebGL 파티클 + 핸드트래킹 인터랙션 | 테크/AI/인터랙티브 쇼케이스 |
