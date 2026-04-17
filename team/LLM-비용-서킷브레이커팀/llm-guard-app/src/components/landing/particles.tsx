'use client';

import { useRef, useMemo, useEffect } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

interface ParticlesProps {
  count?: number;
  animationPhase: number; // 0-1
}

export function Particles({ count = 500, animationPhase }: ParticlesProps) {
  const mesh = useRef<THREE.Points>(null);
  const material = useRef<THREE.PointsMaterial>(null);

  // eslint-disable-next-line react-hooks/exhaustive-deps
  const { positions, colors } = useMemo(() => {
    const pos = new Float32Array(count * 3);
    const col = new Float32Array(count * 3);

    for (let i = 0; i < count; i++) {
      /* eslint-disable no-restricted-globals */
      pos[i * 3] = (Math.random() - 0.5) * 8;
      pos[i * 3 + 1] = Math.random() * 2 + 3;
      pos[i * 3 + 2] = (Math.random() - 0.5) * 2;
      /* eslint-enable no-restricted-globals */
      col[i * 3] = 1;
      col[i * 3 + 1] = 0.26;
      col[i * 3 + 2] = 0.26;
    }

    return { positions: pos, colors: col };
  }, [count]); // intentional: random init per count change

  const velocities = useRef<Array<{ x: number; y: number; z: number }>>(
    Array.from({ length: count }, () => ({
      x: (Math.random() - 0.5) * 0.1,
      y: -Math.random() * 0.15 - 0.05, // downward
      z: (Math.random() - 0.5) * 0.02,
    }))
  );

  useFrame(() => {
    if (!mesh.current) return;

    const posAttr = mesh.current.geometry.getAttribute('position') as THREE.BufferAttribute;
    const colAttr = mesh.current.geometry.getAttribute('color') as THREE.BufferAttribute;
    const posArray = posAttr.array as Float32Array;
    const colArray = colAttr.array as Float32Array;

    // Reset particles beyond bottom
    const gravity = 0.002;

    for (let i = 0; i < count; i++) {
      const idx = i * 3;
      const vel = velocities.current[i] as { x: number; y: number; z: number };

      // Physics
      posArray[idx] += vel.x;
      posArray[idx + 1] += vel.y;
      posArray[idx + 2] += vel.z;
      vel.y -= gravity;

      // Phase transition (0-1: red -> green)
      if (animationPhase < 0.6) {
        // Red phase
        colArray[idx] = 1; // R
        colArray[idx + 1] = 0.26; // G
        colArray[idx + 2] = 0.26; // B
      } else {
        // Transition to green
        const transitionProgress = (animationPhase - 0.6) / 0.4;
        colArray[idx] = Math.max(0, 1 - transitionProgress); // R fades
        colArray[idx + 1] = 0.26 + (1 - 0.26) * transitionProgress; // G grows
        colArray[idx + 2] = 0.26; // B stays
      }

      // Reset if too far down
      if (posArray[idx + 1] < -5) {
        posArray[idx] = (Math.random() - 0.5) * 8;
        posArray[idx + 1] = Math.random() * 2 + 3;
        posArray[idx + 2] = (Math.random() - 0.5) * 2;
        vel.x = (Math.random() - 0.5) * 0.1;
        vel.y = -Math.random() * 0.15 - 0.05;
        vel.z = (Math.random() - 0.5) * 0.02;
      }
    }

    posAttr.needsUpdate = true;
    colAttr.needsUpdate = true;
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
        ref={material}
        size={0.08}
        sizeAttenuation
        vertexColors
        transparent
        opacity={0.8}
      />
    </points>
  );
}
