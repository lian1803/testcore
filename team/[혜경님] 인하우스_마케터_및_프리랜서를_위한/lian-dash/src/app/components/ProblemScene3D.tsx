"use client";

import { Canvas, useFrame } from "@react-three/fiber";
import { useRef, useMemo } from "react";
import * as THREE from "three";

/* ─── DNA-like double helix representing fragmented data ─────── */
function DataHelix() {
  const group1Ref = useRef<THREE.Group>(null);
  const group2Ref = useRef<THREE.Group>(null);

  const { positions1, positions2, count } = useMemo(() => {
    const count = 60;
    const p1 = new Float32Array(count * 3);
    const p2 = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      const t = (i / count) * Math.PI * 4;
      const y = (i / count) * 8 - 4;
      p1[i * 3]     = Math.cos(t) * 1.2;
      p1[i * 3 + 1] = y;
      p1[i * 3 + 2] = Math.sin(t) * 1.2;
      p2[i * 3]     = Math.cos(t + Math.PI) * 1.2;
      p2[i * 3 + 1] = y;
      p2[i * 3 + 2] = Math.sin(t + Math.PI) * 1.2;
    }
    return { positions1: p1, positions2: p2, count };
  }, []);

  useFrame((_, delta) => {
    if (group1Ref.current) group1Ref.current.rotation.y += delta * 0.22;
    if (group2Ref.current) group2Ref.current.rotation.y += delta * 0.22;
  });

  return (
    <>
      <group ref={group1Ref}>
        <points>
          <bufferGeometry>
            <bufferAttribute attach="attributes-position" args={[positions1, 3]} />
          </bufferGeometry>
          <pointsMaterial size={0.12} color="#E37400" transparent opacity={0.8} sizeAttenuation />
        </points>
      </group>
      <group ref={group2Ref}>
        <points>
          <bufferGeometry>
            <bufferAttribute attach="attributes-position" args={[positions2, 3]} />
          </bufferGeometry>
          <pointsMaterial size={0.12} color="#1877F2" transparent opacity={0.8} sizeAttenuation />
        </points>
      </group>
    </>
  );
}

/* ─── Broken connection lines between helix nodes ───────────── */
function BrokenConnections() {
  const linesRef = useRef<THREE.LineSegments>(null);

  const { positions, colors } = useMemo(() => {
    const count = 18;
    const pos = new Float32Array(count * 6);
    const col = new Float32Array(count * 6);
    const channelColors = [
      [0.89, 0.455, 0],   // GA4 orange
      [0.094, 0.463, 0.949], // Meta blue
      [0.012, 0.78, 0.353],  // Naver green
    ];
    for (let i = 0; i < count; i++) {
      const t = (i / count) * Math.PI * 4;
      const y = (i / count) * 8 - 4;
      const x1 = Math.cos(t) * 1.2;
      const z1 = Math.sin(t) * 1.2;
      const x2 = Math.cos(t + Math.PI) * 1.2;
      const z2 = Math.sin(t + Math.PI) * 1.2;
      pos[i * 6]     = x1; pos[i * 6 + 1] = y; pos[i * 6 + 2] = z1;
      pos[i * 6 + 3] = x2; pos[i * 6 + 4] = y; pos[i * 6 + 5] = z2;
      const c = channelColors[i % 3];
      col[i * 6]     = c[0]; col[i * 6 + 1] = c[1]; col[i * 6 + 2] = c[2];
      col[i * 6 + 3] = c[0]; col[i * 6 + 4] = c[1]; col[i * 6 + 5] = c[2];
    }
    return { positions: pos, colors: col };
  }, []);

  useFrame((_, delta) => {
    if (linesRef.current) linesRef.current.rotation.y += delta * 0.22;
  });

  return (
    <lineSegments ref={linesRef}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" args={[positions, 3]} />
        <bufferAttribute attach="attributes-color" args={[colors, 3]} />
      </bufferGeometry>
      <lineBasicMaterial vertexColors transparent opacity={0.35} />
    </lineSegments>
  );
}

/* ─── Floating error cubes ───────────────────────────────────── */
function ErrorCube({ pos, color, speed }: { pos: [number, number, number]; color: string; speed: number }) {
  const ref = useRef<THREE.Mesh>(null);
  useFrame((state) => {
    if (ref.current) {
      ref.current.rotation.x = state.clock.elapsedTime * speed;
      ref.current.rotation.y = state.clock.elapsedTime * speed * 0.7;
      ref.current.position.y = pos[1] + Math.sin(state.clock.elapsedTime * 0.6 + speed) * 0.3;
    }
  });
  return (
    <mesh ref={ref} position={pos}>
      <boxGeometry args={[0.2, 0.2, 0.2]} />
      <meshStandardMaterial color={color} emissive={color} emissiveIntensity={1.2} metalness={0.6} roughness={0.2} />
    </mesh>
  );
}

export function ProblemScene3D() {
  return (
    <Canvas
      camera={{ position: [0, 0, 7], fov: 50 }}
      dpr={[1, 1.5]}
      gl={{ antialias: true, alpha: true }}
      style={{ width: "100%", height: "100%" }}
    >
      <color attach="background" args={["transparent"]} />
      <ambientLight intensity={0.2} />
      <pointLight position={[3, 2, 3]} intensity={1.5} color="#E37400" decay={2} />
      <pointLight position={[-3, -2, 3]} intensity={1.5} color="#1877F2" decay={2} />
      <pointLight position={[0, 0, 3]} intensity={1.0} color="#03C75A" decay={2} />
      <DataHelix />
      <BrokenConnections />
      <ErrorCube pos={[2.5, 1.5, 0]} color="#E37400" speed={0.8} />
      <ErrorCube pos={[-2.5, -0.5, 0.5]} color="#1877F2" speed={0.6} />
      <ErrorCube pos={[2.0, -1.8, -0.5]} color="#03C75A" speed={1.0} />
      <ErrorCube pos={[-2.0, 2.0, -0.3]} color="#E37400" speed={0.5} />
    </Canvas>
  );
}

export default ProblemScene3D;
