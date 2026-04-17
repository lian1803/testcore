"use client";

import { Canvas, useFrame } from "@react-three/fiber";
import { Float, Stars, MeshDistortMaterial } from "@react-three/drei";
import { useRef, useMemo } from "react";
import * as THREE from "three";

/* ─── Particle ring orbiting the central sphere ─────────────────── */
function ParticleRing() {
  const pointsRef = useRef<THREE.Points>(null);

  const { positions, count } = useMemo(() => {
    const count = 180;
    const positions = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      const angle = (i / count) * Math.PI * 2;
      const radius = 3.8 + Math.sin(i * 0.7) * 0.25;
      const tilt = Math.sin(i * 0.4) * 0.35;
      positions[i * 3]     = Math.cos(angle) * radius;
      positions[i * 3 + 1] = tilt;
      positions[i * 3 + 2] = Math.sin(angle) * radius;
    }
    return { positions, count };
  }, []);

  useFrame((_, delta) => {
    if (pointsRef.current) {
      pointsRef.current.rotation.y += delta * 0.08;
      pointsRef.current.rotation.x += delta * 0.012;
    }
  });

  return (
    <points ref={pointsRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          args={[positions, 3]}
        />
      </bufferGeometry>
      <pointsMaterial
        size={0.045}
        color="#ffffff"
        transparent
        opacity={0.5}
        sizeAttenuation
      />
    </points>
  );
}

/* ─── Scattered ambient particles ──────────────────────────────── */
function AmbientParticles() {
  const pointsRef = useRef<THREE.Points>(null);

  const positions = useMemo(() => {
    const count = 320;
    const arr = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      arr[i * 3]     = (Math.random() - 0.5) * 14;
      arr[i * 3 + 1] = (Math.random() - 0.5) * 10;
      arr[i * 3 + 2] = (Math.random() - 0.5) * 8;
    }
    return arr;
  }, []);

  useFrame((_, delta) => {
    if (pointsRef.current) {
      pointsRef.current.rotation.y += delta * 0.018;
    }
  });

  return (
    <points ref={pointsRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          args={[positions, 3]}
        />
      </bufferGeometry>
      <pointsMaterial
        size={0.022}
        color="#ffffff"
        transparent
        opacity={0.25}
        sizeAttenuation
      />
    </points>
  );
}

/* ─── GA4 Orange Torus — fast spin + orange glow light ─────────── */
function GA4Torus() {
  const meshRef = useRef<THREE.Mesh>(null);

  useFrame((_, delta) => {
    if (meshRef.current) {
      meshRef.current.rotation.x += delta * 0.9;
      meshRef.current.rotation.z += delta * 0.5;
    }
  });

  return (
    <Float speed={1.8} rotationIntensity={0.6} floatIntensity={1.2} floatingRange={[-0.6, 0.6]}>
      <group position={[2.8, 1.6, -0.8]}>
        {/* glow light near the object */}
        <pointLight position={[0, 0, 0]} intensity={1.8} color="#E37400" distance={4} decay={2} />
        <mesh ref={meshRef}>
          <torusGeometry args={[0.72, 0.26, 32, 48]} />
          <meshStandardMaterial
            color="#E37400"
            emissive="#E37400"
            emissiveIntensity={1.2}
            metalness={0.5}
            roughness={0.2}
          />
        </mesh>
      </group>
    </Float>
  );
}

/* ─── Meta Blue Icosahedron ─────────────────────────────────────── */
function MetaIcosahedron() {
  const meshRef = useRef<THREE.Mesh>(null);

  useFrame((_, delta) => {
    if (meshRef.current) {
      meshRef.current.rotation.y += delta * 0.55;
      meshRef.current.rotation.x += delta * 0.3;
    }
  });

  return (
    <Float speed={2.0} rotationIntensity={0.8} floatIntensity={1.0} floatingRange={[-0.5, 0.5]}>
      <group position={[-2.8, 0.2, -0.4]}>
        <pointLight position={[0, 0, 0]} intensity={2.0} color="#1877F2" distance={4} decay={2} />
        <mesh ref={meshRef}>
          <icosahedronGeometry args={[0.58, 4]} />
          <meshStandardMaterial
            color="#1877F2"
            emissive="#1877F2"
            emissiveIntensity={1.1}
            metalness={0.5}
            roughness={0.2}
          />
        </mesh>
      </group>
    </Float>
  );
}

/* ─── Naver Green Icosahedron ───────────────────────────────────── */
function NaverIcosahedron() {
  const meshRef = useRef<THREE.Mesh>(null);

  useFrame((_, delta) => {
    if (meshRef.current) {
      meshRef.current.rotation.y -= delta * 0.45;
      meshRef.current.rotation.z += delta * 0.25;
    }
  });

  return (
    <Float speed={1.6} rotationIntensity={1.0} floatIntensity={1.3} floatingRange={[-0.7, 0.7]}>
      <group position={[0.4, -2.2, 0.6]}>
        <pointLight position={[0, 0, 0]} intensity={1.6} color="#03C75A" distance={4} decay={2} />
        <mesh ref={meshRef}>
          <icosahedronGeometry args={[0.48, 3]} />
          <meshStandardMaterial
            color="#03C75A"
            emissive="#03C75A"
            emissiveIntensity={1.0}
            metalness={0.5}
            roughness={0.2}
          />
        </mesh>
      </group>
    </Float>
  );
}

/* ─── Central distorted sphere — data convergence node ─────────── */
function CentralSphere() {
  const sphereRef = useRef<THREE.Mesh>(null);

  useFrame((_, delta) => {
    if (sphereRef.current) {
      sphereRef.current.rotation.x += delta * 0.04;
      sphereRef.current.rotation.y += delta * 0.07;
    }
  });

  return (
    <mesh ref={sphereRef} position={[0, 0, 0]}>
      <icosahedronGeometry args={[1.9, 8]} />
      <MeshDistortMaterial
        color="#0a0a12"
        emissive="#ffffff"
        emissiveIntensity={0.08}
        metalness={0.9}
        roughness={0.15}
        distort={0.45}
        speed={1.8}
      />
    </mesh>
  );
}

/* ─── Inner orbit ring — GA4 orange tint ───────────────────────── */
function OrbitRingInner() {
  const ringRef = useRef<THREE.Mesh>(null);

  useFrame((_, delta) => {
    if (ringRef.current) {
      ringRef.current.rotation.z += delta * 0.18;
      ringRef.current.rotation.x += delta * 0.04;
    }
  });

  return (
    <mesh ref={ringRef} position={[0, 0, 0]}>
      <torusGeometry args={[3.0, 0.012, 16, 160]} />
      <meshStandardMaterial
        color="#E37400"
        emissive="#E37400"
        emissiveIntensity={0.7}
        metalness={0.8}
        roughness={0.1}
        transparent
        opacity={0.5}
      />
    </mesh>
  );
}

/* ─── Outer orbit ring — Meta blue tint ────────────────────────── */
function OrbitRingOuter() {
  const ringRef = useRef<THREE.Mesh>(null);

  useFrame((_, delta) => {
    if (ringRef.current) {
      ringRef.current.rotation.z -= delta * 0.10;
      ringRef.current.rotation.y += delta * 0.03;
    }
  });

  return (
    <mesh ref={ringRef} position={[0, 0, 0]} rotation={[0.5, 0, 0]}>
      <torusGeometry args={[4.2, 0.008, 16, 200]} />
      <meshStandardMaterial
        color="#1877F2"
        emissive="#1877F2"
        emissiveIntensity={0.5}
        metalness={0.9}
        roughness={0.1}
        transparent
        opacity={0.3}
      />
    </mesh>
  );
}

/* ─── Scene Lights — channel 3 colors only ──────────────────────── */
function SceneLights() {
  return (
    <>
      {/* Channel key lights — GA4 orange from top-right, Meta blue from left, Naver green from bottom */}
      <pointLight position={[3, 3, 3]}   intensity={2.2}  color="#E37400" decay={2} />
      <pointLight position={[-3, 0, 3]}  intensity={2.0}  color="#1877F2" decay={2} />
      <pointLight position={[0, -3, 2]}  intensity={1.6}  color="#03C75A" decay={2} />
      {/* Soft white fill from front */}
      <pointLight position={[0, 0, 5]}   intensity={0.4}  color="#ffffff" decay={2} />
      {/* Ambient fill */}
      <ambientLight intensity={0.15} />
    </>
  );
}

/* ─── Main Hero Scene ───────────────────────────────────────────── */
export function HeroScene() {
  return (
    <Canvas
      className="absolute inset-0 z-0"
      camera={{ position: [0, 0, 7], fov: 55 }}
      dpr={[1, 2]}
      gl={{ antialias: true, alpha: true }}
      style={{
        position: "absolute",
        top: 0,
        left: 0,
        width: "100%",
        height: "100%",
      }}
    >
      <color attach="background" args={["transparent"]} />

      <Stars
        radius={120}
        depth={60}
        count={3000}
        factor={3.5}
        saturation={0}
        fade
        speed={0.15}
      />

      <SceneLights />
      <CentralSphere />
      <OrbitRingInner />
      <OrbitRingOuter />
      <ParticleRing />
      <AmbientParticles />
      <GA4Torus />
      <MetaIcosahedron />
      <NaverIcosahedron />
    </Canvas>
  );
}

export default HeroScene;
