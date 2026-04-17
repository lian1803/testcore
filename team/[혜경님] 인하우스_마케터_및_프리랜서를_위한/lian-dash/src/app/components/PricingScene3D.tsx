"use client";

import { Canvas, useFrame } from "@react-three/fiber";
import { Float } from "@react-three/drei";
import { useRef, useMemo } from "react";
import * as THREE from "three";

/* ─── Crystalline shard for each pricing tier ───────────────── */
function PricingShard({
  position,
  color,
  scale,
  rotationSpeed,
  floatSpeed,
}: {
  position: [number, number, number];
  color: string;
  scale: number;
  rotationSpeed: number;
  floatSpeed: number;
}) {
  const ref = useRef<THREE.Mesh>(null);
  useFrame((_, delta) => {
    if (ref.current) {
      ref.current.rotation.y += delta * rotationSpeed;
      ref.current.rotation.x += delta * rotationSpeed * 0.4;
    }
  });
  return (
    <Float speed={floatSpeed} rotationIntensity={0.4} floatIntensity={0.8} floatingRange={[-0.3, 0.3]}>
      <group position={position}>
        <pointLight position={[0, 0, 0]} intensity={2.0} color={color} distance={3} decay={2} />
        <mesh ref={ref} scale={scale}>
          <octahedronGeometry args={[0.8, 2]} />
          <meshStandardMaterial
            color={color}
            emissive={color}
            emissiveIntensity={0.9}
            metalness={0.7}
            roughness={0.1}
            transparent
            opacity={0.85}
          />
        </mesh>
        {/* Inner glow core */}
        <mesh scale={scale * 0.55}>
          <octahedronGeometry args={[0.8, 0]} />
          <meshStandardMaterial
            color="#ffffff"
            emissive={color}
            emissiveIntensity={3}
            transparent
            opacity={0.4}
          />
        </mesh>
      </group>
    </Float>
  );
}

/* ─── Ring connecting the three shards ──────────────────────── */
function ConnectionRing() {
  const ref = useRef<THREE.Mesh>(null);
  useFrame((_, delta) => {
    if (ref.current) {
      ref.current.rotation.z += delta * 0.12;
      ref.current.rotation.x += delta * 0.05;
    }
  });
  return (
    <mesh ref={ref} position={[0, 0, 0]}>
      <torusGeometry args={[3.2, 0.014, 16, 140]} />
      <meshStandardMaterial
        color="#ffffff"
        emissive="#ffffff"
        emissiveIntensity={0.3}
        transparent
        opacity={0.18}
      />
    </mesh>
  );
}

/* ─── Falling particle stream from above ────────────────────── */
function ParticleStream() {
  const ref = useRef<THREE.Points>(null);

  const { positions, speeds } = useMemo(() => {
    const count = 120;
    const pos = new Float32Array(count * 3);
    const spd = new Float32Array(count);
    for (let i = 0; i < count; i++) {
      pos[i * 3]     = (Math.random() - 0.5) * 8;
      pos[i * 3 + 1] = Math.random() * 6 - 3;
      pos[i * 3 + 2] = (Math.random() - 0.5) * 4;
      spd[i] = 0.3 + Math.random() * 0.7;
    }
    return { positions: pos, speeds: spd };
  }, []);

  useFrame((_, delta) => {
    if (!ref.current) return;
    const pos = ref.current.geometry.attributes.position;
    for (let i = 0; i < 120; i++) {
      pos.setY(i, pos.getY(i) - delta * speeds[i] * 0.5);
      if (pos.getY(i) < -3.5) pos.setY(i, 3.5);
    }
    pos.needsUpdate = true;
  });

  return (
    <points ref={ref}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" args={[positions, 3]} />
      </bufferGeometry>
      <pointsMaterial size={0.025} color="#03C75A" transparent opacity={0.4} sizeAttenuation />
    </points>
  );
}

export function PricingScene3D() {
  return (
    <Canvas
      camera={{ position: [0, 0, 8], fov: 54 }}
      dpr={[1, 1.5]}
      gl={{ antialias: true, alpha: true }}
      style={{ width: "100%", height: "100%" }}
    >
      <color attach="background" args={["transparent"]} />
      <ambientLight intensity={0.1} />
      {/* Starter — zinc/white */}
      <PricingShard position={[-3.2, 0, 0]} color="#9ca3af" scale={0.8} rotationSpeed={0.4} floatSpeed={1.5} />
      {/* Pro — gold/white */}
      <PricingShard position={[0, 0.3, 0]} color="#f9fafb" scale={1.15} rotationSpeed={0.55} floatSpeed={2.0} />
      {/* Agency — orange */}
      <PricingShard position={[3.2, 0, 0]} color="#E37400" scale={0.9} rotationSpeed={0.35} floatSpeed={1.3} />
      <ConnectionRing />
      <ParticleStream />
    </Canvas>
  );
}

export default PricingScene3D;
