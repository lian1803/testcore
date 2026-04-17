'use client';

import { useRef, useState, useEffect } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { Particles } from './particles';

function Scene({ animationPhase }: { animationPhase: number }) {
  const cameraRef = useRef<THREE.PerspectiveCamera>(null);
  const lightRef1 = useRef<THREE.PointLight>(null);
  const lightRef2 = useRef<THREE.PointLight>(null);

  useFrame(() => {
    if (cameraRef.current) {
      cameraRef.current.position.z = 5;
    }
  });

  return (
    <>
      <perspectiveCamera
        ref={cameraRef}
        position={[0, 0, 5]}
        fov={60}
        near={0.1}
        far={1000}
      />

      {/* Lighting */}
      <ambientLight intensity={0.2} color="#ffffff" />
      <pointLight
        ref={lightRef1}
        position={[-3, 2, 2]}
        intensity={2}
        color="#ff4444"
      />
      <pointLight
        ref={lightRef2}
        position={[3, -1, 1]}
        intensity={1.5}
        color="#00ff88"
      />

      {/* Particles */}
      <Particles count={500} animationPhase={animationPhase} />

      {/* Grid background plane */}
      <mesh position={[0, 0, -2]}>
        <planeGeometry args={[20, 20, 50, 50]} />
        <meshBasicMaterial
          color="#00ff88"
          opacity={0.06}
          transparent
          wireframe
        />
      </mesh>
    </>
  );
}

export function HeroScene() {
  const [animationPhase, setAnimationPhase] = useState(0);

  useEffect(() => {
    const startTime = Date.now();
    const duration = 5000; // 5 second loop

    const animate = () => {
      const elapsed = (Date.now() - startTime) % duration;
      const progress = elapsed / duration;
      setAnimationPhase(progress);
      requestAnimationFrame(animate);
    };

    animate();
  }, []);

  return (
    <Canvas
      style={{ width: '100%', height: '100%' }}
      dpr={[1, 2]}
      performance={{ min: 0.5 }}
    >
      <Scene animationPhase={animationPhase} />
    </Canvas>
  );
}
