"use client";

import { Canvas, useFrame } from "@react-three/fiber";
import { useRef, useMemo } from "react";
import * as THREE from "three";

/* ─── Converging particle burst — all channels merging to one ─ */
function ConvergingParticles() {
  const ref = useRef<THREE.Points>(null);

  const { positions, targets, speeds, colors } = useMemo(() => {
    const count = 300;
    const pos = new Float32Array(count * 3);
    const tgt = new Float32Array(count * 3);
    const spd = new Float32Array(count);
    const col = new Float32Array(count * 3);

    const channelColors: [number, number, number][] = [
      [0.89, 0.455, 0],     // GA4 orange
      [0.094, 0.463, 0.949], // Meta blue
      [0.012, 0.78, 0.353],  // Naver green
    ];

    for (let i = 0; i < count; i++) {
      // Start scattered
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      const r = 3.5 + Math.random() * 1.5;
      pos[i * 3]     = r * Math.sin(phi) * Math.cos(theta);
      pos[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
      pos[i * 3 + 2] = r * Math.cos(phi);
      // Target: near center
      tgt[i * 3]     = (Math.random() - 0.5) * 0.4;
      tgt[i * 3 + 1] = (Math.random() - 0.5) * 0.4;
      tgt[i * 3 + 2] = (Math.random() - 0.5) * 0.4;
      spd[i] = 0.3 + Math.random() * 0.5;
      // Color by channel
      const c = channelColors[i % 3];
      col[i * 3] = c[0]; col[i * 3 + 1] = c[1]; col[i * 3 + 2] = c[2];
    }
    return { positions: pos, targets: tgt, speeds: spd, colors: col };
  }, []);

  useFrame((state) => {
    if (!ref.current) return;
    const pos = ref.current.geometry.attributes.position;
    // Oscillate between scattered and converged state
    const phase = (Math.sin(state.clock.elapsedTime * 0.4) + 1) * 0.5; // 0 to 1
    for (let i = 0; i < 300; i++) {
      const ox = positions[i * 3], oy = positions[i * 3 + 1], oz = positions[i * 3 + 2];
      const tx = targets[i * 3], ty = targets[i * 3 + 1], tz = targets[i * 3 + 2];
      pos.setXYZ(i, ox + (tx - ox) * phase, oy + (ty - oy) * phase, oz + (tz - oz) * phase);
    }
    pos.needsUpdate = true;
    ref.current.rotation.y = state.clock.elapsedTime * 0.08;
  });

  return (
    <points ref={ref}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" args={[positions, 3]} />
        <bufferAttribute attach="attributes-color" args={[colors, 3]} />
      </bufferGeometry>
      <pointsMaterial size={0.055} vertexColors transparent opacity={0.9} sizeAttenuation />
    </points>
  );
}

/* ─── Central convergence core — pulses with the animation ──── */
function CorePulse() {
  const ref = useRef<THREE.Mesh>(null);
  useFrame((state) => {
    if (ref.current) {
      const s = 0.7 + Math.sin(state.clock.elapsedTime * 0.8) * 0.25;
      ref.current.scale.setScalar(s);
    }
  });
  return (
    <mesh ref={ref}>
      <icosahedronGeometry args={[0.45, 4]} />
      <meshStandardMaterial
        color="#ffffff"
        emissive="#ffffff"
        emissiveIntensity={3}
        transparent
        opacity={0.6}
      />
    </mesh>
  );
}

/* ─── Three channel lines converging ────────────────────────── */
function ChannelLines() {
  const ref = useRef<THREE.LineSegments>(null);

  const { positions, colors } = useMemo(() => {
    const lines = [
      { from: [-3, 1, 0], to: [0, 0, 0], color: [0.89, 0.455, 0] as [number, number, number] },
      { from: [3, 1, 0], to: [0, 0, 0], color: [0.094, 0.463, 0.949] as [number, number, number] },
      { from: [0, -2.5, 0], to: [0, 0, 0], color: [0.012, 0.78, 0.353] as [number, number, number] },
    ];
    const pos = new Float32Array(lines.length * 6);
    const col = new Float32Array(lines.length * 6);
    lines.forEach(({ from, to, color }, i) => {
      pos[i * 6]     = from[0]; pos[i * 6 + 1] = from[1]; pos[i * 6 + 2] = from[2];
      pos[i * 6 + 3] = to[0];  pos[i * 6 + 4] = to[1];  pos[i * 6 + 5] = to[2];
      col[i * 6]     = color[0]; col[i * 6 + 1] = color[1]; col[i * 6 + 2] = color[2];
      col[i * 6 + 3] = 1; col[i * 6 + 4] = 1; col[i * 6 + 5] = 1;
    });
    return { positions: pos, colors: col };
  }, []);

  useFrame((state) => {
    if (ref.current) {
      (ref.current.material as THREE.LineBasicMaterial).opacity =
        0.3 + Math.sin(state.clock.elapsedTime * 0.8) * 0.2;
    }
  });

  return (
    <lineSegments ref={ref}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" args={[positions, 3]} />
        <bufferAttribute attach="attributes-color" args={[colors, 3]} />
      </bufferGeometry>
      <lineBasicMaterial vertexColors transparent opacity={0.5} linewidth={2} />
    </lineSegments>
  );
}

export function CTAScene3D() {
  return (
    <Canvas
      camera={{ position: [0, 0, 7], fov: 58 }}
      dpr={[1, 1.5]}
      gl={{ antialias: true, alpha: true }}
      style={{ width: "100%", height: "100%" }}
    >
      <color attach="background" args={["transparent"]} />
      <ambientLight intensity={0.1} />
      <pointLight position={[0, 0, 3]} intensity={2} color="#ffffff" decay={2} />
      <pointLight position={[3, 2, 2]} intensity={1.5} color="#E37400" decay={2} />
      <pointLight position={[-3, 2, 2]} intensity={1.5} color="#1877F2" decay={2} />
      <pointLight position={[0, -2, 2]} intensity={1.2} color="#03C75A" decay={2} />
      <ConvergingParticles />
      <CorePulse />
      <ChannelLines />
    </Canvas>
  );
}

export default CTAScene3D;
