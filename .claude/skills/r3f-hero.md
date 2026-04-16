# /r3f-hero — R3F 3D 인터랙티브 히어로

리안이 "3D 히어로" / "R3F" / "살아있는 3D" / "날아다니는 캐릭터" → 이 플로우 실행.

---

## 프로젝트 세팅

```bash
# test/개발/ 아래에 생성
mkdir test/개발/{프로젝트명} && cd test/개발/{프로젝트명}
npm create vite@latest . -- --template react
npm install three @react-three/fiber @react-three/drei @react-three/postprocessing postprocessing --legacy-peer-deps
```

`vite.config.js`:
```js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
export default defineConfig({ plugins: [react()], server: { port: 5174 } })
```

---

## 검증된 CONFIG 값 (Flamingo.glb 기준)

```js
const MODEL_URL   = 'https://threejs.org/examples/models/gltf/Flamingo.glb'
// bbox 실측 (2026-04-12): x:231.60 y:416.10 z:201.40
// 공식 three.js GPGPU 비례 역산 → 우리 씬(cam z=9, FOV=45°) 기준
const MODEL_SCALE = 0.0016   // 거리 8에서 화면 높이 14%

const CAMERA = { fov: 45, pos: [0, 0.8, 9], near: 0.05, far: 120 }
const TONE   = { mapping: ACESFilmicToneMapping, exposure: 0.82 }
const FOG    = ['#00000e', 25, 60]
const BG     = '#00000e'
```

**다른 모델 쓸 때**: 첫 렌더 콘솔에 bbox 찍어서 max_dim 확인 → `MODEL_SCALE = 0.666 / max_dim`

⚠️ **절대 금지**: `Box3.setFromObject(scene)` 결과를 scale에 쓰는 것 → 컴포넌트 리마운트 시 이미 스케일 적용된 bbox를 다시 계산해서 폭주함. **반드시 하드코딩**.

---

## 비행 경로 패턴 (검증됨)

```js
// 카메라 z=9, 새가 항상 시야 안에 있도록 설계
const PATH = new CatmullRomCurve3([
  new Vector3(-10,  3,  -8),
  new Vector3( -5,  1.5, -4),
  new Vector3( -1,  0.5,  1),
  new Vector3(  0,  0.2,  3),   // ★ 최근접 (카메라 바로 앞)
  new Vector3(  1,  0.5,  1),
  new Vector3(  5,  1.5, -4),
  new Vector3( 10,  3,  -8),
  new Vector3(  5,  6, -18),
  new Vector3(  0,  8, -22),
  new Vector3( -5,  6, -18),
], true)

function pathSpeed(t) {
  const CLOSE = 0.24
  const d = Math.min(Math.abs(t - CLOSE), 1 - Math.abs(t - CLOSE))
  return d < 0.08 ? 0.003 + (d / 0.08) * 0.02 : 0.042
}
```

---

## 착지 시퀀스 (텍스트 위에 앉기)

18초 주기 반복: fly(8s) → approach(2.5s) → descend(1.8s) → sit(3.2s) → takeoff(2.5s)

```js
const ABOVE_PERCH = new Vector3(0,  1.2, 5.0)   // 텍스트 상공
const PERCH_POS   = new Vector3(0, -1.5, 4.5)   // 착지점 (타이틀 텍스트 위)
const LEAVE_POS   = new Vector3(-12, 4, -12)     // 이탈 방향
```

- **fly**: PATH 따라 루프, actionRef.timeScale = 1.0
- **approach**: snapPos → ABOVE_PERCH lerp, timeScale 1.0 → 0.55
- **descend**: ABOVE_PERCH → PERCH_POS easeOut, timeScale → 0.12
- **sit**: 미세 보빙(sin*0.025), timeScale = 0.1
- **takeoff**: PERCH_POS → LEAVE_POS easeIn, timeScale 0.1 → 1.0
- fly 재진입: 첫 15% 동안 snapPos → pathPos 블렌드 (경로 재진입 부드럽게)

---

## 모델 방향 보정

```js
groupRef.current.lookAt(ahead)
groupRef.current.rotateY(Math.PI)   // Flamingo.glb forward 보정 — 빼면 뒤통수 보임
```

---

## 포스트프로세싱 (검증된 조합)

```jsx
<EffectComposer>
  <Bloom luminanceThreshold={0.82} luminanceSmoothing={0.025}
         intensity={0.5} kernelSize={KernelSize.LARGE} blendFunction={BlendFunction.ADD} />
  <Vignette darkness={0.38} offset={0.25} />
</EffectComposer>
```

⚠️ **DoF(DepthOfField) 절대 금지** — 전체 씬이 흐려짐  
⚠️ **transmission 재질 금지** — 모델이 투명/검정으로 사라짐

---

## 조명 (검증됨)

```js
<ambientLight color="#0d1a2e" intensity={1.5} />
<pointLight color="#ffd4a8" intensity={2.4} position={[5, 6, 4]}   distance={40} />  // 키
<pointLight color="#4488ff" intensity={1.1} position={[-5, 2, -3]} distance={30} />  // 필
<pointLight color="#ff88cc" intensity={0.9} position={[0, -2, -6]} distance={25} />  // 림
```

---

## 레퍼런스 템플릿

현재 작동 중인 완성 코드: `test/개발/r3f-hero/src/App.jsx`
