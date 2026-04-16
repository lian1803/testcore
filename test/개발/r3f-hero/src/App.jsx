import { Suspense, useRef, useEffect } from 'react'
import { Canvas, useFrame, useThree } from '@react-three/fiber'
import { useGLTF, useAnimations, Environment, Stars } from '@react-three/drei'
import { EffectComposer, Bloom, Vignette } from '@react-three/postprocessing'
import { BlendFunction, KernelSize } from 'postprocessing'
import { ACESFilmicToneMapping, CatmullRomCurve3, Vector3 } from 'three'

// ── CONFIG ──────────────────────────────────────────────────────────────────
const MODEL_URL = 'https://threejs.org/examples/models/gltf/Flamingo.glb'
// 실측 bbox: x:231.60 y:416.10 z:201.40 (2026-04-12 콘솔 확인)
// 공식 three.js GPGPU 비례 역산: sizes[Flamingo]=0.1, cam z=350 → 우리 씬(cam z=9, FOV=45°) 환산
// 거리 8에서 화면 높이 14% = 0.666 world-unit → 0.666/416.10 = 0.0016
const MODEL_SCALE = 0.0016

// 착지 시퀀스 키 포지션
// 카메라 z=9, lookAt(0,0.3,0), FOV=45° → 타이틀 텍스트 위치 추정
const ABOVE_PERCH = new Vector3(0,  1.2,  5.0)   // 텍스트 상공 (진입 스테이징)
const PERCH_POS   = new Vector3(0, -1.5,  4.5)   // FLAMINGO 타이틀 위 착지점
const LEAVE_POS   = new Vector3(-12, 4, -12)      // 이탈 방향 (경로 시작점 근처)

// 시퀀스 타이밍 (초)
const DUR = { fly: 8.0, approach: 2.5, descend: 1.8, sit: 3.2, takeoff: 2.5 }
const CYCLE = DUR.fly + DUR.approach + DUR.descend + DUR.sit + DUR.takeoff  // 18s

// 이징
const easeInOut = t => t < .5 ? 4*t*t*t : 1 - Math.pow(-2*t+2, 3) / 2
const easeOut   = t => 1 - Math.pow(1 - t, 3)
const easeIn    = t => t * t * t

// ── 비행 경로 (자유비행 루프) ─────────────────────────────────────────────────
const PATH = new CatmullRomCurve3([
  new Vector3(-10,  3,  -8),
  new Vector3( -5,  1.5, -4),
  new Vector3( -1,  0.5,  1),
  new Vector3(  0,  0.2,  3),
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

// ── 새 ──────────────────────────────────────────────────────────────────────
function Flamingo() {
  const groupRef  = useRef()
  const tRef      = useRef(Math.random())   // 랜덤 시작 위치
  const actionRef = useRef(null)
  const snapPos   = useRef(new Vector3())   // 페이즈 전환 시 위치 스냅샷
  const prevPhase = useRef('fly')

  const { scene, animations } = useGLTF(MODEL_URL)
  const { actions }           = useAnimations(animations, groupRef)


  useEffect(() => {
    const first = Object.values(actions)[0]
    if (first) { first.play(); actionRef.current = first }
  }, [actions])

  useFrame(({ clock }, dt) => {
    if (!groupRef.current) return
    const cycleT = clock.getElapsedTime() % CYCLE

    // ── 현재 페이즈 계산 ─────────────────────────────────────
    const t0 = DUR.fly
    const t1 = t0 + DUR.approach
    const t2 = t1 + DUR.descend
    const t3 = t2 + DUR.sit

    let phase, phaseT
    if      (cycleT < t0) { phase = 'fly';      phaseT = cycleT / DUR.fly }
    else if (cycleT < t1) { phase = 'approach'; phaseT = (cycleT - t0) / DUR.approach }
    else if (cycleT < t2) { phase = 'descend';  phaseT = (cycleT - t1) / DUR.descend }
    else if (cycleT < t3) { phase = 'sit';       phaseT = (cycleT - t2) / DUR.sit }
    else                  { phase = 'takeoff';   phaseT = (cycleT - t3) / DUR.takeoff }

    // 페이즈 전환 시 현재 위치 스냅샷
    if (prevPhase.current !== phase) {
      snapPos.current.copy(groupRef.current.position)
      prevPhase.current = phase
    }

    const pos        = new Vector3()
    const lookTarget = new Vector3()

    // ── 페이즈별 위치 계산 ────────────────────────────────────
    if (phase === 'fly') {
      tRef.current = (tRef.current + pathSpeed(tRef.current) * dt) % 1
      const pathPos = PATH.getPoint(tRef.current)
      lookTarget.copy(PATH.getPoint((tRef.current + 0.008) % 1))
      if (actionRef.current) actionRef.current.timeScale = 1.0

      // 이탈 후 경로 재진입: 첫 15% 동안 블렌드
      const RECONNECT = 0.15
      if (phaseT < RECONNECT) {
        pos.lerpVectors(snapPos.current, pathPos, easeInOut(phaseT / RECONNECT))
      } else {
        pos.copy(pathPos)
      }

    } else if (phase === 'approach') {
      // 경로 → 텍스트 상공 진입
      const a = easeInOut(phaseT)
      pos.lerpVectors(snapPos.current, ABOVE_PERCH, a)
      lookTarget.lerpVectors(ABOVE_PERCH, PERCH_POS, 0.3 + a * 0.7)
      if (actionRef.current) actionRef.current.timeScale = 1.0 - a * 0.45

    } else if (phase === 'descend') {
      // 상공 → 착지
      const a = easeOut(phaseT)
      pos.lerpVectors(ABOVE_PERCH, PERCH_POS, a)
      lookTarget.set(3, PERCH_POS.y, PERCH_POS.z + 5)   // 착지 후 정면 응시
      if (actionRef.current) actionRef.current.timeScale = 0.55 - a * 0.43  // → 0.12

    } else if (phase === 'sit') {
      // 앉기: 미세 보빙
      pos.copy(PERCH_POS)
      pos.y += Math.sin(phaseT * Math.PI * 5) * 0.025
      lookTarget.set(5, PERCH_POS.y + 0.1, PERCH_POS.z + 3)  // 오른쪽 바라보기
      if (actionRef.current) actionRef.current.timeScale = 0.1

    } else {
      // 이탈: easeIn 가속
      const a = easeIn(phaseT)
      pos.lerpVectors(PERCH_POS, LEAVE_POS, a)
      lookTarget.copy(LEAVE_POS)
      if (actionRef.current) actionRef.current.timeScale = a * 0.9 + 0.1
    }

    groupRef.current.position.copy(pos)
    groupRef.current.lookAt(lookTarget)
    groupRef.current.rotateY(Math.PI)   // Flamingo forward 보정
  })

  return (
    <group ref={groupRef} scale={MODEL_SCALE}>
      <primitive object={scene} />
    </group>
  )
}
useGLTF.preload(MODEL_URL)

// ── 카메라 ───────────────────────────────────────────────────────────────────
function Camera() {
  const { camera } = useThree()
  const mouse  = useRef([0, 0])
  const smooth = useRef([0, 0])

  useEffect(() => {
    const fn = e => {
      mouse.current[0] = (e.clientX / window.innerWidth  - 0.5) * 2
      mouse.current[1] = (e.clientY / window.innerHeight - 0.5) * 2
    }
    window.addEventListener('mousemove', fn)
    return () => window.removeEventListener('mousemove', fn)
  }, [])

  useFrame(({ clock }) => {
    const t = clock.getElapsedTime()
    smooth.current[0] += (mouse.current[0] * 0.6 - smooth.current[0]) * 0.04
    smooth.current[1] += (-mouse.current[1] * 0.3 - smooth.current[1]) * 0.04
    camera.position.set(
      smooth.current[0] + Math.sin(t * 0.05) * 0.4,
      0.8 + smooth.current[1] + Math.sin(t * 0.04) * 0.15,
      9 + Math.cos(t * 0.04) * 0.3
    )
    camera.lookAt(0, 0.3, 0)
  })
  return null
}

// ── 씬 ──────────────────────────────────────────────────────────────────────
function Scene() {
  return (
    <>
      <ambientLight color="#0d1a2e" intensity={1.5} />
      <pointLight color="#ffd4a8" intensity={2.4} position={[5, 6, 4]}   distance={40} />
      <pointLight color="#4488ff" intensity={1.1} position={[-5, 2, -3]} distance={30} />
      <pointLight color="#ff88cc" intensity={0.9} position={[0, -2, -6]} distance={25} />

      <Stars radius={60} depth={40} count={1000} factor={2} saturation={0.3} fade speed={0.2} />
      <Environment preset="night" background={false} />

      <Suspense fallback={null}>
        <Flamingo />
      </Suspense>

      <Camera />

      <EffectComposer>
        <Bloom
          luminanceThreshold={0.82}
          luminanceSmoothing={0.025}
          intensity={0.5}
          kernelSize={KernelSize.LARGE}
          blendFunction={BlendFunction.ADD}
        />
        <Vignette darkness={0.38} offset={0.25} />
      </EffectComposer>
    </>
  )
}

// ── 커서 ────────────────────────────────────────────────────────────────────
function Cursor() {
  const cur = useRef(), ring = useRef()
  const p   = useRef({ cx: 0, cy: 0, rx: 0, ry: 0 })
  useEffect(() => {
    const fn = e => { p.current.cx = e.clientX; p.current.cy = e.clientY }
    window.addEventListener('mousemove', fn)
    let id
    const tick = () => {
      p.current.rx += (p.current.cx - p.current.rx) * 0.11
      p.current.ry += (p.current.cy - p.current.ry) * 0.11
      if (cur.current)  { cur.current.style.left  = p.current.cx + 'px'; cur.current.style.top  = p.current.cy + 'px' }
      if (ring.current) { ring.current.style.left = p.current.rx + 'px'; ring.current.style.top = p.current.ry + 'px' }
      id = requestAnimationFrame(tick)
    }
    id = requestAnimationFrame(tick)
    return () => { window.removeEventListener('mousemove', fn); cancelAnimationFrame(id) }
  }, [])
  return <><div ref={cur} className="cursor" /><div ref={ring} className="cursor-ring" /></>
}

// ── 앱 ──────────────────────────────────────────────────────────────────────
export default function App() {
  return (
    <div style={{ width: '100vw', height: '100vh', position: 'relative' }}>
      <Canvas
        camera={{ fov: 45, position: [0, 0.8, 9], near: 0.05, far: 120 }}
        gl={{ toneMapping: ACESFilmicToneMapping, toneMappingExposure: 0.82, antialias: true }}
        dpr={[1, 2]}
        style={{ position: 'absolute', inset: 0 }}
      >
        <color attach="background" args={['#00000e']} />
        <fog   attach="fog"        args={['#00000e', 25, 60]} />
        <Scene />
      </Canvas>

      <div className="overlay">
        <p className="label">React Three Fiber</p>
        <h1 className="title">FLAMINGO</h1>
        <p className="sub">Wing to wing. Light to light.</p>
        <button className="cta">Enter</button>
      </div>

      <Cursor />
    </div>
  )
}
