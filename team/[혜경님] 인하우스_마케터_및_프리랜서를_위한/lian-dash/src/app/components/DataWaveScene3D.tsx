"use client";

import { Canvas, useFrame } from "@react-three/fiber";
import { useRef, useMemo } from "react";
import * as THREE from "three";

/* ─── Animated wave terrain — represents data flowing in ──────── */
function WaveTerrain() {
  const meshRef = useRef<THREE.Mesh>(null);
  const geoRef = useRef<THREE.PlaneGeometry>(null);

  const { grid, widthSegments, heightSegments } = useMemo(() => ({
    widthSegments: 40,
    heightSegments: 40,
    grid: 40 * 40,
  }), []);

  useFrame((state) => {
    const geo = geoRef.current;
    if (!geo) return;
    const pos = geo.attributes.position;
    const t = state.clock.elapsedTime;
    for (let i = 0; i <= widthSegments; i++) {
      for (let j = 0; j <= heightSegments; j++) {
        const idx = j * (widthSegments + 1) + i;
        const x = (i / widthSegments) * 8 - 4;
        const y = (j / heightSegments) * 8 - 4;
        // Multi-frequency wave mixing GA4/Meta/Naver rhythms
        const z = Math.sin(x * 0.8 + t * 0.9) * 0.35
                + Math.sin(y * 0.6 + t * 0.7) * 0.25
                + Math.sin((x + y) * 0.4 + t * 0.5) * 0.2
                + Math.cos(x * 1.2 - t * 0.8) * 0.15;
        pos.setZ(idx, z);
      }
    }
    pos.needsUpdate = true;
    geo.computeVertexNormals();
  });

  return (
    <mesh ref={meshRef} rotation={[-Math.PI / 2.8, 0, 0]} position={[0, -1.5, 0]}>
      <planeGeometry ref={geoRef} args={[12, 12, widthSegments, heightSegments]} />
      <meshStandardMaterial
        color="#050a14"
        emissive="#1877F2"
        emissiveIntensity={0.3}
        wireframe={false}
        metalness={0.8}
        roughness={0.3}
        side={THREE.DoubleSide}
      />
    </mesh>
  );
}

/* ─── Wireframe overlay — shows the grid structure ──────────── */
function WireframeTerrain() {
  const meshRef = useRef<THREE.Mesh>(null);
  const geoRef = useRef<THREE.PlaneGeometry>(null);

  const widthSegments = 20;
  const heightSegments = 20;

  useFrame((state) => {
    const geo = geoRef.current;
    if (!geo) return;
    const pos = geo.attributes.position;
    const t = state.clock.elapsedTime;
    for (let i = 0; i <= widthSegments; i++) {
      for (let j = 0; j <= heightSegments; j++) {
        const idx = j * (widthSegments + 1) + i;
        const x = (i / widthSegments) * 8 - 4;
        const y = (j / heightSegments) * 8 - 4;
        const z = Math.sin(x * 0.8 + t * 0.9) * 0.35
                + Math.sin(y * 0.6 + t * 0.7) * 0.25
                + Math.sin((x + y) * 0.4 + t * 0.5) * 0.2
                + Math.cos(x * 1.2 - t * 0.8) * 0.15;
        pos.setZ(idx, z);
      }
    }
    pos.needsUpdate = true;
  });

  return (
    <mesh ref={meshRef} rotation={[-Math.PI / 2.8, 0, 0]} position={[0, -1.48, 0]}>
      <planeGeometry ref={geoRef} args={[12, 12, widthSegments, heightSegments]} />
      <meshStandardMaterial
        color="#1877F2"
        emissive="#03C75A"
        emissiveIntensity={0.2}
        wireframe
        transparent
        opacity={0.18}
      />
    </mesh>
  );
}

/* ─── Floating channel orbs above the wave ──────────────────── */
function ChannelOrb({ pos, color, phaseOffset }: { pos: [number, number, number]; color: string; phaseOffset: number }) {
  const ref = useRef<THREE.Mesh>(null);
  useFrame((state) => {
    if (ref.current) {
      ref.current.position.y = pos[1] + Math.sin(state.clock.elapsedTime * 0.8 + phaseOffset) * 0.25;
    }
  });
  return (
    <mesh ref={ref} position={pos}>
      <sphereGeometry args={[0.18, 16, 16]} />
      <meshStandardMaterial color={color} emissive={color} emissiveIntensity={2.5} metalness={0.2} roughness={0.1} />
    </mesh>
  );
}

export function DataWaveScene3D() {
  return (
    <Canvas
      camera={{ position: [0, 2, 7], fov: 52 }}
      dpr={[1, 1.5]}
      gl={{ antialias: true, alpha: true }}
      style={{ width: "100%", height: "100%" }}
    >
      <color attach="background" args={["transparent"]} />
      <ambientLight intensity={0.1} />
      <pointLight position={[4, 4, 4]} intensity={2.0} color="#E37400" decay={2} />
      <pointLight position={[-4, 3, 4]} intensity={2.0} color="#1877F2" decay={2} />
      <pointLight position={[0, 4, 3]} intensity={1.5} color="#03C75A" decay={2} />
      <WaveTerrain />
      <WireframeTerrain />
      <ChannelOrb pos={[-3, 1.5, 0]} color="#E37400" phaseOffset={0} />
      <ChannelOrb pos={[0, 2.0, -1]} color="#1877F2" phaseOffset={2.1} />
      <ChannelOrb pos={[3, 1.5, 0]} color="#03C75A" phaseOffset={4.2} />
    </Canvas>
  );
}

export default DataWaveScene3D;
