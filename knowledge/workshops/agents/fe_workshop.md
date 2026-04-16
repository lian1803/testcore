## ── 세계 최고 수준 FE 구현 기술 워크샵 (2025) ──

> 이 섹션은 민준을 10년차 시니어 FE로 업그레이드하는 실전 코드 레퍼런스다.
> "설명" 말고 "복붙하면 바로 동작하는 코드"가 핵심.

---

### 🎬 Framer Motion 고급 패턴

> 2025년 이후 패키지명이 `framer-motion` → `motion`으로 변경됨.
> import는 `from 'motion/react'` 사용. 하지만 기존 `framer-motion`도 계속 동작.

#### useScroll + useTransform — 패럴랙스 & 스케일

```tsx
'use client';
import { useScroll, useTransform, motion, useSpring } from 'motion/react';
import { useRef } from 'react';

export function ParallaxSection() {
  const ref = useRef(null);
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ['start end', 'end start'], // 요소가 뷰포트 진입~이탈 구간
  });

  // scrollYProgress 0→1 을 다양한 값으로 변환
  const y = useTransform(scrollYProgress, [0, 1], ['-20%', '20%']); // 배경 패럴랙스
  const opacity = useTransform(scrollYProgress, [0, 0.3, 0.7, 1], [0, 1, 1, 0]);
  const scale = useTransform(scrollYProgress, [0, 0.5], [0.8, 1]);

  // 물리 스프링으로 부드럽게 감쇠
  const smoothY = useSpring(y, { stiffness: 100, damping: 30 });

  return (
    <section ref={ref} className="relative h-[50vh] overflow-hidden">
      {/* 배경 레이어 — 느리게 */}
      <motion.div style={{ y: smoothY }} className="absolute inset-0 bg-cover" />
      {/* 텍스트 레이어 — 페이드+스케일 */}
      <motion.div style={{ opacity, scale }} className="relative z-10 flex items-center justify-center h-full">
        <h2 className="text-5xl font-bold">스크롤 패럴랙스</h2>
      </motion.div>
    </section>
  );
}
```

#### stagger children — 리스트 순차 등장

```tsx
'use client';
import { motion } from 'motion/react';

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,   // 자식마다 0.1초 딜레이
      delayChildren: 0.2,     // 첫 자식 시작 전 대기
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 24 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.5, ease: [0.22, 1, 0.36, 1] }, // cubic bezier
  },
};

export function StaggerList({ items }: { items: string[] }) {
  return (
    <motion.ul
      variants={containerVariants}
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, margin: '-100px' }} // 뷰포트 100px 전에 트리거
    >
      {items.map((item, i) => (
        <motion.li key={i} variants={itemVariants}>
          {item}
        </motion.li>
      ))}
    </motion.ul>
  );
}
```

#### AnimatePresence — 페이지 전환 & 조건부 마운트

```tsx
'use client';
import { AnimatePresence, motion } from 'motion/react';
import { useState } from 'react';

// 규칙: AnimatePresence는 조건부 컴포넌트를 감싸야 함 (안에 있으면 안 됨)
// 규칙: motion 컴포넌트에 반드시 unique key 부여

export function TabContent({ activeTab }: { activeTab: string }) {
  return (
    <AnimatePresence mode="wait"> {/* wait: 이전 exit 완료 후 다음 enter */}
      <motion.div
        key={activeTab}            // key 변경 시 exit→enter 트리거
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        exit={{ opacity: 0, x: -20 }}
        transition={{ duration: 0.25 }}
      >
        {activeTab === 'A' ? <ContentA /> : <ContentB />}
      </motion.div>
    </AnimatePresence>
  );
}

// 모달 예시
export function Modal({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          key="modal"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.9 }}
          transition={{ duration: 0.2, ease: 'easeOut' }}
          className="fixed inset-0 flex items-center justify-center z-50"
        >
          {/* 모달 내용 */}
        </motion.div>
      )}
    </AnimatePresence>
  );
}
```

#### useMotionValue + useSpring — 마우스 추적 카드 틸트

```tsx
'use client';
import { useMotionValue, useSpring, motion } from 'motion/react';

export function TiltCard({ children }: { children: React.ReactNode }) {
  const x = useMotionValue(0);
  const y = useMotionValue(0);

  const rotateX = useSpring(y, { stiffness: 300, damping: 30 });
  const rotateY = useSpring(x, { stiffness: 300, damping: 30 });

  function handleMouseMove(e: React.MouseEvent<HTMLDivElement>) {
    const rect = e.currentTarget.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;
    // 마우스 위치 → -10~10deg 범위로 변환
    x.set(((e.clientX - centerX) / rect.width) * 20);
    y.set(-((e.clientY - centerY) / rect.height) * 20);
  }

  function handleMouseLeave() {
    x.set(0);
    y.set(0);
  }

  return (
    <motion.div
      style={{ rotateX, rotateY, transformStyle: 'preserve-3d' }}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      className="relative rounded-2xl p-6 cursor-pointer"
    >
      {children}
    </motion.div>
  );
}
```

---

### 🌟 Three.js / React Three Fiber (R3F) 고급 패턴

> **버전 기준**: `@react-three/fiber` v8 + `@react-three/drei` v9 + React 18
> **설치**: `npm install three @react-three/fiber @react-three/drei @react-three/postprocessing`
> **타입**: `npm install -D @types/three`

> **SSR 주의**: Three.js는 반드시 `dynamic import + ssr: false`로 감싸야 함 (아래 주의사항 참고)

#### 파티클 시스템 — Points + BufferGeometry

```tsx
'use client';
import { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

export function Particles({ count = 3000 }: { count?: number }) {
  const mesh = useRef<THREE.Points>(null);

  // 파티클 위치 초기화 — useMemo로 렌더링마다 재생성 방지
  const [positions, colors] = useMemo(() => {
    const positions = new Float32Array(count * 3);
    const colors = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      // 구 형태로 분포
      const r = Math.random() * 4;
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      positions[i * 3] = r * Math.sin(phi) * Math.cos(theta);
      positions[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
      positions[i * 3 + 2] = r * Math.cos(phi);
      // 색상 그라디언트 (파란~보라)
      colors[i * 3] = 0.3 + Math.random() * 0.4;
      colors[i * 3 + 1] = 0.1 + Math.random() * 0.3;
      colors[i * 3 + 2] = 0.8 + Math.random() * 0.2;
    }
    return [positions, colors];
  }, [count]);

  // useFrame: delta 기반으로 프레임레이트 독립적 애니메이션
  useFrame((state, delta) => {
    if (!mesh.current) return;
    mesh.current.rotation.y += delta * 0.05;  // delta 사용 필수 (60fps/30fps 동일 속도)
    mesh.current.rotation.x += delta * 0.02;
  });

  return (
    <points ref={mesh}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          args={[positions, 3]}
        />
        <bufferAttribute
          attach="attributes-color"
          args={[colors, 3]}
        />
      </bufferGeometry>
      <pointsMaterial
        size={0.02}
        vertexColors
        transparent
        opacity={0.8}
        sizeAttenuation
      />
    </points>
  );
}
```

#### 커스텀 Shader Material (GLSL)

```tsx
'use client';
import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { shaderMaterial } from '@react-three/drei';
import { extend } from '@react-three/fiber';

// 커스텀 셰이더 머티리얼 정의
const WaveMaterial = shaderMaterial(
  // uniforms
  { uTime: 0, uColor: new THREE.Color(0.3, 0.5, 1.0) },
  // vertex shader
  `
    varying vec2 vUv;
    uniform float uTime;
    void main() {
      vUv = uv;
      vec3 pos = position;
      pos.z += sin(pos.x * 3.0 + uTime) * 0.1;
      pos.z += sin(pos.y * 2.0 + uTime * 1.5) * 0.1;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
    }
  `,
  // fragment shader
  `
    varying vec2 vUv;
    uniform vec3 uColor;
    uniform float uTime;
    void main() {
      float noise = sin(vUv.x * 10.0 + uTime) * sin(vUv.y * 10.0 + uTime) * 0.5 + 0.5;
      gl_FragColor = vec4(uColor * noise, 1.0);
    }
  `
);
extend({ WaveMaterial });

// TypeScript 타입 선언
declare module '@react-three/fiber' {
  interface ThreeElements {
    waveMaterial: { uTime?: number; uColor?: THREE.Color };
  }
}

export function WavePlane() {
  const matRef = useRef<{ uTime: number }>(null);

  useFrame(({ clock }) => {
    if (matRef.current) matRef.current.uTime = clock.elapsedTime;
  });

  return (
    <mesh>
      <planeGeometry args={[4, 4, 64, 64]} />
      <waveMaterial ref={matRef} />
    </mesh>
  );
}
```

#### Next.js에서 R3F 사용 — SSR 처리

```tsx
// page.tsx (서버 컴포넌트)
import dynamic from 'next/dynamic';

const Scene = dynamic(() => import('@/components/Scene'), {
  ssr: false,  // Three.js는 반드시 ssr: false
  loading: () => <div className="h-[500px] bg-black animate-pulse rounded-xl" />,
});

export default function Page() {
  return (
    <main>
      <Scene />
    </main>
  );
}

// components/Scene.tsx
'use client';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Environment } from '@react-three/drei';

export default function Scene() {
  return (
    <Canvas
      camera={{ position: [0, 0, 5], fov: 45 }}
      dpr={[1, 2]}           // 레티나 대응, 최대 2배
      performance={{ min: 0.5 }} // 성능 저하 시 DPR 자동 감소
    >
      <ambientLight intensity={0.5} />
      <Environment preset="city" />
      <OrbitControls enableZoom={false} />
      {/* 씬 내용 */}
    </Canvas>
  );
}
```

---

### 💅 고급 CSS / Tailwind 기법

#### Glassmorphism — 성능 포함 정확한 구현

```css
/* 기본 glassmorphism */
.glass-card {
  /* 핵심 4요소 */
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(12px);           /* GPU 사용 — 8~15px 권장 */
  -webkit-backdrop-filter: blur(12px);   /* Safari 필수 */
  border: 1px solid rgba(255, 255, 255, 0.15);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);

  /* 성능 최적화 */
  transform: translateZ(0);             /* GPU 레이어 강제 생성 */
  will-change: transform;              /* 애니메이션 예정 시만 추가 */
}

/* 다크 배경 위 glassmorphism */
.glass-dark {
  background: rgba(10, 10, 20, 0.5);
  backdrop-filter: blur(10px) saturate(180%);
  -webkit-backdrop-filter: blur(10px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

/* 모바일 성능 주의: blur 줄이기 */
@media (max-width: 768px) {
  .glass-card {
    backdrop-filter: blur(6px);
    -webkit-backdrop-filter: blur(6px);
  }
}

/* 지원 안 되는 브라우저 폴백 */
@supports not (backdrop-filter: blur(1px)) {
  .glass-card {
    background: rgba(15, 15, 25, 0.85);
  }
}
```

```tsx
// Tailwind + glassmorphism (tailwind.config.ts에 추가)
// className="bg-white/[0.08] backdrop-blur-md border border-white/15 shadow-2xl"
```

#### Bento Grid — CSS Grid로 구현

```tsx
// Tailwind Bento Grid
export function BentoGrid() {
  return (
    <div className="grid grid-cols-3 grid-rows-3 gap-4 p-4 max-w-5xl mx-auto">
      {/* 큰 카드 — 2열 2행 차지 */}
      <div className="col-span-2 row-span-2 bg-zinc-900 rounded-2xl p-6">
        <h3 className="text-2xl font-bold">주요 기능</h3>
      </div>
      {/* 오른쪽 작은 카드들 */}
      <div className="col-span-1 row-span-1 bg-violet-900/50 rounded-2xl p-4">카드 A</div>
      <div className="col-span-1 row-span-1 bg-blue-900/50 rounded-2xl p-4">카드 B</div>
      {/* 하단 와이드 카드 */}
      <div className="col-span-3 row-span-1 bg-zinc-800 rounded-2xl p-6">
        <p>풀 너비 카드</p>
      </div>
    </div>
  );
}

// 반응형: 모바일은 1열로
// className="grid grid-cols-1 md:grid-cols-3 ..."
```

#### Gradient Border — 여러 구현법 비교

```css
/* 방법 1: border-image (심플하지만 border-radius 안 됨) */
.gradient-border-1 {
  border: 2px solid transparent;
  border-image: linear-gradient(135deg, #6366f1, #8b5cf6, #06b6d4) 1;
}

/* 방법 2: pseudo-element (border-radius 가능 — 권장) */
.gradient-border-2 {
  position: relative;
  background: #0f0f1a;
  border-radius: 16px;
}
.gradient-border-2::before {
  content: '';
  position: absolute;
  inset: -1px;            /* 1px 테두리 두께 */
  border-radius: 17px;    /* 부모 + 1px */
  background: linear-gradient(135deg, #6366f1, #8b5cf6, #06b6d4);
  z-index: -1;
}

/* 방법 3: background-clip (배경 투명 필요) */
.gradient-border-3 {
  border: 2px solid transparent;
  background:
    linear-gradient(#0f0f1a, #0f0f1a) padding-box,
    linear-gradient(135deg, #6366f1, #8b5cf6, #06b6d4) border-box;
  border-radius: 16px;    /* border-radius 동작함 — 가장 깔끔 */
}
```

#### CSS Scroll-Driven Animations (순수 CSS, JS 불필요)

```css
/* 스크롤하면 progress bar 채워짐 */
@keyframes grow-bar {
  from { transform: scaleX(0); }
  to   { transform: scaleX(1); }
}

.scroll-progress-bar {
  position: fixed;
  top: 0;
  left: 0;
  height: 3px;
  width: 100%;
  background: linear-gradient(to right, #6366f1, #06b6d4);
  transform-origin: left;
  animation: grow-bar linear;
  animation-timeline: scroll(root);   /* 루트 스크롤에 연결 */
}

/* 요소가 뷰포트에 들어올 때 페이드인 */
@keyframes fade-in-up {
  from { opacity: 0; translate: 0 40px; }
  to   { opacity: 1; translate: 0 0; }
}

.reveal-on-scroll {
  animation: fade-in-up linear both;
  animation-timeline: view();         /* 이 요소의 뷰 진행에 연결 */
  animation-range: entry 0% entry 40%; /* 뷰포트 진입 0~40% 구간에서 실행 */
}
```

#### CSS Container Queries — 부모 크기 기반 반응형

```css
/* 컨테이너 정의 */
.card-wrapper {
  container-type: inline-size;
  container-name: card;
}

/* 컨테이너 크기에 따라 스타일 변경 (미디어 쿼리와 독립적) */
@container card (min-width: 400px) {
  .card-inner {
    display: flex;
    flex-direction: row;
    gap: 1rem;
  }
}

@container card (max-width: 399px) {
  .card-inner {
    display: flex;
    flex-direction: column;
  }
}
```

#### clip-path 애니메이션

```css
/* 위에서 아래로 reveal */
.clip-reveal {
  clip-path: polygon(0 0, 100% 0, 100% 0, 0 0);
  transition: clip-path 0.6s cubic-bezier(0.22, 1, 0.36, 1);
}
.clip-reveal.visible {
  clip-path: polygon(0 0, 100% 0, 100% 100%, 0 100%);
}

/* 대각선 wipe */
.clip-diagonal {
  clip-path: polygon(0 0, 0 0, 0 100%, 0 100%);
  transition: clip-path 0.8s ease;
}
.clip-diagonal:hover {
  clip-path: polygon(0 0, 100% 0, 100% 100%, 0 100%);
}
```

---

### ⚡ Next.js 성능 최적화 (2025 기준)

#### Image 컴포넌트 최적화

```tsx
import Image from 'next/image';

// LCP 이미지: priority 필수 + sizes 정확히
<Image
  src="/hero.webp"
  alt="히어로 이미지"
  width={1200}
  height={630}
  priority              // LCP 이미지는 반드시 priority
  sizes="(max-width: 768px) 100vw, (max-width: 1200px) 80vw, 1200px"
  quality={85}          // 기본 75, 90+ 은 용량 과다
  placeholder="blur"    // 블러 플레이스홀더 (blurDataURL 자동 생성)
/>

// lazy 이미지 (LCP 아닌 것들)
<Image
  src="/feature.webp"
  alt="기능 소개"
  width={600}
  height={400}
  // priority 없음 = 자동 lazy loading
  sizes="(max-width: 768px) 100vw, 50vw"
/>
```

#### dynamic import 전략

```tsx
// 무거운 컴포넌트만 dynamic import
import dynamic from 'next/dynamic';

// Three.js: ssr false 필수
const ThreeScene = dynamic(() => import('@/components/ThreeScene'), { ssr: false });

// 차트 라이브러리: 클라이언트 전용
const Chart = dynamic(() => import('@/components/Chart'), {
  loading: () => <div className="h-64 bg-zinc-800 animate-pulse rounded-xl" />,
  ssr: false,
});

// 모달: 보여질 때만 로드 (초기 번들에서 제외)
const Modal = dynamic(() => import('@/components/Modal'));
// → import('...') 는 조건부 렌더링과 함께 쓸 때 효과적
// → 모든 컴포넌트를 dynamic으로 만들면 오히려 느려짐 (워터폴)
```

#### Font 최적화 (next/font)

```tsx
// app/layout.tsx
import { Inter, Pretendard } from 'next/font/google'; // 또는 next/font/local

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',          // FOUT 방지
  variable: '--font-inter', // CSS 변수로 사용
});

// 로컬 폰트 (가장 빠름)
import localFont from 'next/font/local';
const pretendard = localFont({
  src: '../public/fonts/PretendardVariable.woff2',
  display: 'swap',
  variable: '--font-pretendard',
  weight: '100 900',  // variable font
});

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko" className={`${inter.variable} ${pretendard.variable}`}>
      <body className="font-pretendard">{children}</body>
    </html>
  );
}
```

#### React Server Components 전략

```tsx
// 기본 원칙: 서버 컴포넌트 → 클라이언트 컴포넌트 방향으로만 props 전달

// ✅ 서버 컴포넌트 (기본값, 'use client' 없음)
// - DB 쿼리, API 호출, 파일 읽기
// - 초기 HTML에 포함 → LCP 개선
async function ProductList() {
  const products = await fetch('/api/products').then(r => r.json()); // 서버에서 실행
  return <ul>{products.map(p => <ProductCard key={p.id} {...p} />)}</ul>;
}

// ✅ 클라이언트 컴포넌트 ('use client' 필요한 것만)
// - useState, useEffect, event handlers
// - 브라우저 API (window, document)
// - Framer Motion, Three.js
'use client';
import { useState } from 'react';
function Counter() {
  const [count, setCount] = useState(0);
  return <button onClick={() => setCount(c => c + 1)}>{count}</button>;
}
```

---

### 🎨 디자인 시스템 → 코드 변환 마스터클래스

#### 디자인 토큰 → CSS Variables → Tailwind v4 연동

```css
/* app/globals.css (Tailwind v4 방식) */
@import "tailwindcss";

@theme {
  /* 색상 토큰 */
  --color-brand-50: oklch(97% 0.02 270);
  --color-brand-500: oklch(55% 0.2 270);    /* 메인 퍼플 */
  --color-brand-900: oklch(20% 0.15 270);

  /* 시맨틱 토큰 */
  --color-background: var(--color-brand-900);
  --color-surface: oklch(25% 0.08 270);
  --color-text-primary: oklch(95% 0.02 270);
  --color-text-secondary: oklch(70% 0.05 270);
  --color-border: oklch(35% 0.08 270);

  /* 타이포그래피 */
  --font-display: 'Pretendard Variable', sans-serif;
  --font-body: 'Pretendard Variable', sans-serif;

  /* 스페이싱 (4px 기반) */
  --spacing-1: 4px;
  --spacing-2: 8px;
  --spacing-4: 16px;
  --spacing-8: 32px;

  /* 반경 */
  --radius-sm: 6px;
  --radius-md: 12px;
  --radius-lg: 20px;
  --radius-xl: 32px;
}
```

#### CVA (class-variance-authority) — 컴포넌트 variant 시스템

```tsx
// components/ui/button.tsx
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils'; // clsx + tailwind-merge
import { type ButtonHTMLAttributes, forwardRef } from 'react';

const buttonVariants = cva(
  // base: 모든 버튼 공통
  'inline-flex items-center justify-center gap-2 rounded-md font-medium transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500 disabled:pointer-events-none disabled:opacity-50',
  {
    variants: {
      variant: {
        primary:   'bg-brand-500 text-white hover:bg-brand-600 active:bg-brand-700',
        secondary: 'bg-surface text-text-primary border border-border hover:bg-zinc-700',
        ghost:     'text-text-secondary hover:text-text-primary hover:bg-surface',
        danger:    'bg-red-600 text-white hover:bg-red-700',
      },
      size: {
        sm:  'h-8 px-3 text-sm',
        md:  'h-10 px-4 text-sm',
        lg:  'h-12 px-6 text-base',
        xl:  'h-14 px-8 text-lg',
        icon:'h-10 w-10 p-0',
      },
    },
    defaultVariants: {
      variant: 'primary',
      size: 'md',
    },
  }
);

interface ButtonProps
  extends ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  loading?: boolean;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, loading, children, disabled, ...props }, ref) => (
    <button
      ref={ref}
      disabled={disabled || loading}
      className={cn(buttonVariants({ variant, size }), className)}
      {...props}
    >
      {loading && <span className="animate-spin">⏳</span>}
      {children}
    </button>
  )
);
Button.displayName = 'Button';

// 사용법
// <Button variant="primary" size="lg">시작하기</Button>
// <Button variant="ghost" size="icon"><IconX /></Button>
```

#### 반응형 타이포그래피 — clamp() 수식

```css
/* fluid typography: 뷰포트 크기에 따라 자동으로 폰트 크기 변경 */
/* clamp(최솟값, 선호값, 최댓값) */

h1 { font-size: clamp(2rem, 4vw + 1rem, 5rem); }      /* 32px ~ 80px */
h2 { font-size: clamp(1.5rem, 3vw + 0.75rem, 3.5rem); } /* 24px ~ 56px */
h3 { font-size: clamp(1.25rem, 2vw + 0.5rem, 2.5rem); }  /* 20px ~ 40px */
p  { font-size: clamp(1rem, 1vw + 0.75rem, 1.25rem); }    /* 16px ~ 20px */

/* Tailwind 4에서 */
/* className="text-[clamp(2rem,4vw+1rem,5rem)]" */
```

---

### 🏗️ Aceternity UI / Magic UI 실전 활용법

#### Aceternity UI 핵심 컴포넌트 사용법 (200+ 컴포넌트)

```tsx
// 설치: 컴포넌트 소스 직접 복사 방식 (npm 패키지 아님)
// https://ui.aceternity.com/components 에서 소스 복사

// 1. Spotlight — 히어로 섹션 배경 조명 효과
// components/ui/spotlight.tsx 에 소스 붙여넣기 후:
import { Spotlight } from '@/components/ui/spotlight';

<div className="relative min-h-screen bg-black">
  <Spotlight
    className="-top-40 left-0 md:left-60"
    fill="white"        // 조명 색상 (white, purple, blue 등)
  />
  <div className="relative z-10">
    <h1>히어로 텍스트</h1>
  </div>
</div>

// 2. Hero Highlight — 텍스트 하이라이트 배경
import { HeroHighlight, Highlight } from '@/components/ui/hero-highlight';

<HeroHighlight>
  <h1 className="text-4xl font-bold">
    마케터를 위한{' '}
    <Highlight>AI 데이터 분석</Highlight>{' '}
    플랫폼
  </h1>
</HeroHighlight>

// 3. Bento Grid — 기능 섹션
import { BentoGrid, BentoGridItem } from '@/components/ui/bento-grid';

<BentoGrid className="max-w-4xl mx-auto">
  {items.map((item, i) => (
    <BentoGridItem
      key={i}
      title={item.title}
      description={item.description}
      icon={item.icon}
      className={i === 3 || i === 6 ? 'md:col-span-2' : ''} // 큰 카드
    />
  ))}
</BentoGrid>

// 4. Tracing Beam — 스크롤 진행 표시 (블로그/랜딩 긴 페이지)
import { TracingBeam } from '@/components/ui/tracing-beam';

<TracingBeam>
  <div className="max-w-2xl mx-auto">
    {/* 긴 콘텐츠 */}
  </div>
</TracingBeam>

// 5. Card Hover Effect — 카드 그리드에 hover 효과
import { HoverEffect } from '@/components/ui/card-hover-effect';

const projects = [
  { title: '기능1', description: '설명...', link: '/' },
  // ...
];
<HoverEffect items={projects} />
```

#### Magic UI 핵심 컴포넌트

```tsx
// Magic UI도 소스 복사 방식
// https://magicui.design/docs 에서 복사

// 1. Shimmer Button — CTA 버튼에 shimmer 효과
import ShimmerButton from '@/components/magicui/shimmer-button';

<ShimmerButton
  shimmerColor="#9333ea"
  background="rgba(0, 0, 0, 1)"
  className="shadow-2xl"
>
  무료로 시작하기
</ShimmerButton>

// 2. Animated Gradient Text — 그라디언트 흐르는 텍스트
import { AnimatedGradientText } from '@/components/magicui/animated-gradient-text';

<AnimatedGradientText>
  🎉 <span className="font-bold">새로운 기능</span> 출시
</AnimatedGradientText>

// 3. Number Ticker — 숫자 카운트업 애니메이션
import NumberTicker from '@/components/magicui/number-ticker';

<div className="text-5xl font-bold">
  <NumberTicker value={98} />%
</div>

// 4. Border Beam — 카드 테두리에 빛나는 beam 효과
import { BorderBeam } from '@/components/magicui/border-beam';

<div className="relative rounded-xl border bg-zinc-900 p-6">
  카드 내용
  <BorderBeam size={250} duration={12} delay={9} />
</div>

// 5. Shine Border — 반짝이는 테두리
import { ShineBorder } from '@/components/magicui/shine-border';

<ShineBorder
  className="relative flex h-[500px] w-full items-center justify-center rounded-lg"
  color={['#A07CFE', '#FE8FB5', '#FFBE7B']}
>
  카드 내용
</ShineBorder>
```

#### SaaS 랜딩에서 가장 효과적인 컴포넌트 조합

```
히어로 섹션:   Spotlight (배경) + Hero Highlight (텍스트) + Shimmer Button (CTA)
기능 섹션:     Bento Grid + Border Beam (카드 강조)
통계 섹션:     Number Ticker + Animated Gradient Text
가격 섹션:     Shine Border (추천 플랜 강조)
소셜 증명:     Card Hover Effect + Animated Tooltip
스크롤 진행:   Tracing Beam (긴 페이지) 또는 CSS scroll-progress-bar
```

---

### 🐛 흔한 실수 및 주의사항 (10년치 경험)

#### 1. Framer Motion + Next.js App Router 에러

```tsx
// ❌ 에러: 서버 컴포넌트에서 motion 직접 사용
// app/page.tsx (서버 컴포넌트)
import { motion } from 'motion/react'; // 에러!
export default function Page() {
  return <motion.div animate={{ opacity: 1 }}>...</motion.div>;
}

// ✅ 해결: 'use client' 지시어 추가
'use client';
import { motion } from 'motion/react';
export function AnimatedHero() {
  return <motion.div animate={{ opacity: 1 }}>...</motion.div>;
}
// 그리고 서버 컴포넌트에서 이 컴포넌트를 import해서 사용
```

#### 2. Three.js SSR 에러

```tsx
// ❌ 에러: Three.js는 window/document 참조 → SSR에서 폭발
import { Canvas } from '@react-three/fiber'; // 서버에서 에러

// ✅ 해결: dynamic import + ssr: false
const ThreeScene = dynamic(() => import('@/components/ThreeScene'), { ssr: false });
// 반드시 components/ThreeScene.tsx 파일 상단에 'use client' 추가
```

#### 3. Hydration 불일치 에러

```tsx
// ❌ 에러: 서버/클라이언트 렌더링 결과 다를 때
function Component() {
  return <div>{Math.random()}</div>; // 서버값 ≠ 클라이언트값 → hydration error
  return <div>{typeof window !== 'undefined' ? '클라이언트' : '서버'}</div>; // 동일 에러
}

// ✅ 해결 1: useEffect + 클라이언트 전용 상태
'use client';
import { useState, useEffect } from 'react';
function Component() {
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);
  if (!mounted) return null; // 또는 서버 렌더 결과와 동일한 것
  return <div>클라이언트 전용 내용</div>;
}

// ✅ 해결 2: suppressHydrationWarning (날짜/시간처럼 의도적 불일치일 때만)
<time suppressHydrationWarning>{new Date().toLocaleString()}</time>
```

#### 4. AnimatePresence 작동 안 하는 경우

```tsx
// ❌ 작동 안 함
<div>
  <AnimatePresence>
    {isOpen && <motion.div exit={{ opacity: 0 }}>...</motion.div>}
  </AnimatePresence>
</div>

// ❌ 작동 안 함: key 없음
<AnimatePresence>
  {isOpen && <motion.div exit={{ opacity: 0 }}>...</motion.div>}
</AnimatePresence>

// ✅ 작동: key 필수 + AnimatePresence가 직접 감싸야 함
<AnimatePresence>
  {isOpen && (
    <motion.div
      key="my-unique-key"   // 반드시 필요
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      ...
    </motion.div>
  )}
</AnimatePresence>
```

#### 5. z-index 관리

```tsx
// tailwind.config.ts에 z-index 레이어 정의
// z-index 체계: 낮은 숫자 = 뒤, 높은 숫자 = 앞
const zIndex = {
  base: 0,
  above: 10,
  dropdown: 100,
  sticky: 200,
  modal-backdrop: 300,
  modal: 400,
  toast: 500,
  tooltip: 600,
};

// stacking context 주의: transform/opacity/filter 적용 시 새 stacking context 생성
// → 자식 z-index가 부모 밖에서 작동 안 함
// → 해결: isolation: isolate 사용
<div className="isolate"> {/* 새로운 stacking context 명시적 생성 */}
  <div className="z-10">내용</div>
</div>
```

#### 6. Glassmorphism 성능 주의

```tsx
// ❌ 성능 문제: 한 화면에 glass 요소 10개 이상
// ❌ 성능 문제: backdrop-filter 애니메이션
// ❌ 성능 문제: 모바일에서 blur(20px) 이상

// ✅ 규칙:
// - 한 뷰포트에 glass 요소 최대 3~5개
// - blur 값 8~15px (모바일은 6~8px)
// - backdrop-filter 있는 요소에 transition 추가할 때 transform만 animate
// - 저사양 기기 폴백: @supports not (backdrop-filter: blur(1px))
```

#### 7. CSS specificity 충돌 (Tailwind에서 자주 발생)

```tsx
// ❌ 문제: 의도한 클래스가 안 먹힘
<div className="text-red-500 text-blue-500">  // text-blue-500이 이길 수도 있음

// ✅ 해결: tailwind-merge 사용 (cn 유틸리티)
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// cn은 나중에 오는 클래스가 이김 (tailwind-merge가 충돌 해결)
cn('text-red-500', 'text-blue-500')  // → 'text-blue-500'
cn('px-4 py-2', isLarge && 'px-8')  // → 'py-2 px-8' (isLarge=true일 때)
```
## ── UX 구현 원칙 (Part 4 강의) ──

FE(Frontend Engineer) 에이전트가 UI 구현 시 적용할 원칙은 다음과 같습니다.

## FE 개발자가 UI 구현 시 적용할 원칙

### 좋은 디자인 4원칙을 코드 레벨에서 구현하는 법

UI를 코드로 구현할 때 사용성, 일관성, 피드백, 그리고 단순함의 원칙을 적용하여 사용자 경험을 향상시켜야 합니다.

*   **접근성(Accessibility) 확보:**
    *   충분히 큰 글자 크기 (`font-size: 16px` 이상 권장)와 배경-글자 간의 명확한 명도 대비를 CSS로 구현합니다. (예: WCAG 기준 준수)
    *   색맹 사용자도 정보를 구분할 수 있도록 색상 외에 패턴이나 텍스트를 함께 제공하는 방안을 고려합니다.
    *   스크린 리더 사용자를 위해 의미 있는 HTML 태그(Semantic HTML)를 사용하고, 필요시 ARIA(Accessible Rich Internet Applications) 속성을 추가합니다.
*   **일관성(Consistency) 유지:**
    *   애플리케이션 전반에 걸쳐 버튼, 입력 필드 등 공통 UI 컴포넌트의 모양, 크기, 동작 방식을 통일합니다. (예: `Button` 컴포넌트 재사용)
    *   같은 기능을 수행하는 요소(예: 저장 버튼)는 항상 같은 위치에 배치되도록 레이아웃을 설계하고, 동일한 용어를 사용합니다. (예: 디자인 시스템 내 변수 활용)
*   **피드백(Feedback) 제공:**
    *   사용자의 모든 행동(클릭, 입력 등)에 대해 시각적(CSS `:active`, `:hover` 상태) 또는 기능적(로딩 스피너, 에러 메시지) 반응을 즉각적으로 제공합니다.
*   **단순함(Simplicity) 유지:**
    *   꼭 필요한 정보와 기능만 화면에 노출하고, 복잡한 기능은 단계별로 분리하거나 숨깁니다.
    *   컴포넌트 설계 시 재사용성과 단일 책임 원칙을 고려하여 복잡도를 낮춥니다.
    *   정보 밀도가 높은 대시보드와 같은 화면에서는 카드 UI와 충분한 여백(Whitespace)을 활용하여 시각적 혼란을 줄입니다.

### 사용자 피드백(UI 피드백, 로딩, 에러 상태) 구현 원칙

사용자의 현재 상태를 명확히 알리고, 불안감을 최소화하며, 다음 행동을 유도하는 피드백 시스템을 구축해야 합니다.

*   **실시간 유효성 검사 구현:**
    *   회원가입/로그인 등 입력 폼에서 사용자가 입력하는 즉시 유효성을 검사하고 피드백을 제공하여, 전체 제출 후 에러를 발견하는 방식의 불편함을 줄입니다. (예: `onChange` 이벤트 핸들러에서 유효성 검사 로직 실행)
*   **주요 행동(CTA) 시각적 강조:**
    *   가장 중요한 CTA 버튼은 눈에 띄는 색상과 크기로 디자인하고, 취소나 보조적인 버튼은 회색 또는 테두리만 있는 형태로 구현하여 시각적 위계를 명확히 합니다. (예: `primary`, `secondary` 버튼 스타일 구분)
*   **친절하고 구체적인 에러 메시지:**
    *   "Error 500"과 같은 개발자용 메시지 대신 "일시적인 문제입니다. 다시 시도해주세요." 또는 "페이지를 찾을 수 없어요. 주소를 다시 확인해주세요."와 같이 사용자 친화적이고 해결책을 제시하는 메시지를 에러 발생 시 노출합니다. (예: 에러 컴포넌트 내부에서 메시지 맵핑 관리)
*   **로딩 상태 시각화:**
    *   데이터 로딩 중에는 아무 반응 없이 화면이 멈춘 것처럼 보이지 않도록 스켈레톤(Skeleton) UI 또는 스피너(Spinner) 컴포넌트를 사용하여 진행 중임을 명확히 표시합니다.
    *   로딩 상태가 너무 길어질 경우, 사용자에게 진행 상황을 알려주거나 취소 옵션을 제공하는 것을 고려합니다.
*   **알림/토스트 메시지 시스템:**
    *   성공, 경고, 에러, 정보 등 4가지 유형의 알림(토스트 메시지) 시스템을 구현하고, 각 유형별로 색상, 아이콘, 자동 닫힘(auto-dismiss) 시간을 설정하여 일관된 피드백을 제공합니다. (예: `setTimeout`으로 자동 닫힘 구현)

### 단순함 원칙을 컴포넌트 설계에 적용하는 법

컴포넌트 설계를 단순하게 유지하여 유지보수성을 높이고 사용자에게 명확한 경험을 제공합니다.

*   **핵심 기능 우선:**
    *   모바일 환경처럼 제한된 화면에서 가장 중요한 기능과 정보에 집중하여 컴포넌트를 설계하고, 불필요한 요소는 제거하거나 숨깁니다.
    *   (예: 모바일에서는 햄버거 메뉴를 사용하여 네비게이션 복잡도 감소)
*   **정보 밀도 조절:**
    *   대시보드와 같은 정보 집약적인 화면에서는 가장 중요한 핵심 지표(Key Metrics)만 상단에 배치하고, 각 정보 블록을 카드 UI로 구분하여 시각적 혼란을 방지합니다.
    *   컴포넌트 내부에 너무 많은 props나 상태를 두지 않고, 필요한 최소한의 데이터만 전달하도록 설계합니다.
*   **간결한 입력 필드:**
    *   회원가입/로그인 화면의 입력 필드를 최소화하고, 필수 정보만을 요청하여 사용자 이탈률을 낮춥니다.
    *   단순한 컴포넌트는 재사용성이 높아지고, 테스트 및 유지보수가 용이해집니다.

### 일관성 원칙 (디자인 시스템, 컴포넌트 재사용)

일관성 있는 UI는 사용자의 학습 비용을 줄이고 서비스의 신뢰도를 높입니다. 개발자는 디자인 시스템을 활용하여 이를 코드 레벨에서 구현합니다.

*   **디자인 시스템 활용 및 구축:**
    *   색상 팔레트, 타이포그래피, 간격, 그림자 등 디자인 토큰을 CSS 변수(Variables) 또는 JavaScript 객체로 정의하여 중앙에서 관리하고 모든 컴포넌트에서 재사용합니다. (예: `--primary-color`, `theme.palette.primary`)
    *   버튼, 카드, 입력 필드 등 기본적인 UI 요소를 재사용 가능한 컴포넌트로 구현하고, 스토리북(Storybook)과 같은 도구로 문서화하여 개발 일관성을 확보합니다.
*   **컴포넌트 재사용성 극대화:**
    *   Figma와 같은 디자인 툴에서 제공하는 UI Kit나 Design System 템플릿을 코드 레벨의 컴포넌트로 변환하여 활용합니다.
    *   공통 로직이나 UI 패턴을 추상화하여 고차 컴포넌트(HOC)나 훅(Hooks) 등으로 구현, 중복 코드를 줄이고 일관된 동작을 보장합니다.
*   **스타일 가이드 준수:**
    *   디자이너가 정의한 스타일 가이드(Color Palette, Typography, Component Styles)를 CSS variables, Tailwind CSS 설정, 또는 Styled Components ThemeProvider 등을 통해 코드에 반영하여 디자인과 개발 간의 일관성을 유지합니다.

### 모바일 UX 원칙 구현법

모바일 퍼스트 접근 방식을 통해 핵심 사용자 경험에 집중하고, 다양한 화면 크기에 유연하게 대응합니다.

*   **모바일 퍼스트 디자인 및 개발:**
    *   가장 작은 화면(375px 너비)을 기준으로 UI를 먼저 디자인하고 개발하여 핵심 기능에 집중하고, 이후 태블릿 및 데스크탑으로 확장합니다.
    *   콘텐츠 요소를 수직으로 쌓는(stack vertically) 레이아웃을 기본으로 합니다.
*   **터치 영역(Touch Target) 확보:**
    *   버튼이나 인터랙션이 가능한 요소의 터치 영역을 최소 44x44px 이상으로 확보하여 오작동을 방지합니다.
*   **가독성 높은 텍스트:**
    *   본문 텍스트는 최소 16px 이상으로 설정하여 모바일 환경에서도 쉽게 읽을 수 있도록 합니다.
*   **간결한 내비게이션:**
    *   복잡한 메뉴 구조는 햄버거 메뉴(Hamburger Menu) 또는 하단 탭 내비게이션(Bottom Tab Navigation)으로 숨겨 모바일 화면의 효율성을 높입니다.
*   **반응형 레이아웃 구현:**
    *   CSS 미디어 쿼리(Media Queries), Flexbox, CSS Grid 등을 활용하여 모바일, 태블릿, 데스크탑 등 다양한 화면 크기에서 콘텐츠와 레이아웃이 유연하게 변화하도록 구현합니다.
        *   **모바일 (예: 375px):** 모든 카드를 수직으로 쌓고, 사이드바는 햄버거 메뉴 뒤로 숨깁니다.
        *   **태블릿 (예: 768px):** 2열 그리드 레이아웃을 적용하고, 사이드바를 간소화합니다.
        *   **데스크탑 (예: 1440px):** 3~4열 그리드 레이아웃과 전체 사이드바를 표시하여 넓은 화면을 활용합니다.

### User Journey 흐름에 맞는 라우팅/상태 관리

사용자 여정 맵을 이해하고, 각 단계에 맞춰 애플리케이션의 라우팅 및 상태를 효율적으로 관리하여 매끄러운 사용자 경험을 제공합니다.

*   **여정 단계별 라우팅 설계:**
    *   사용자 여정 맵의 각 주요 단계(예: 인지 → 온보딩 → 메인 → 상세 → 결제)를 애플리케이션의 개별 라우트(Route) 또는 하위 라우트(Sub-route)로 매핑하여 설계합니다.
    *   (예: `/onboarding`, `/dashboard`, `/products/:id`, `/checkout`)
*   **단계별 상태 관리:**
    *   다단계 폼(예: 결제/회원가입 플로우)과 같이 사용자 여정 전반에 걸쳐 공유되어야 하는 데이터는 전역 상태 관리(Context API, Redux, Zustand 등)를 활용하여 일관성을 유지합니다.
    *   각 여정 단계에 맞는 특정 상태(예: `isLoading`, `hasError`, `isSubmitted`)를 컴포넌트 또는 페이지 수준에서 관리하여 UI 피드백을 제공합니다.
*   **진행률 표시 및 컨텍스트 전달:**
    *   결제나 신청 등 다단계 여정에서는 상단에 진행률 표시기(Progress Indicator)를 구현하여 사용자에게 현재 위치와 남은 단계를 시각적으로 알려줍니다.
    *   이전 단계에서 다음 단계로 넘어갈 때 필요한 정보(예: 장바구니 품목, 배송지 주소)는 라우트 파라미터, 쿼리 파라미터 또는 전역 상태를 통해 안전하게 전달하여 사용자 경험의 연속성을 확보합니다.
*   **명확한 CTA(Call to Action) 변화:**
    *   여정의 각 단계에 따라 CTA 버튼의 텍스트를 "다음" → "결제하기" → "주문 추적" 등으로 변경하여 사용자에게 명확한 다음 행동을 제시합니다.

