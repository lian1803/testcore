---
name: emissive-core
version: 1.0
---

# Emissive Core — Bioluminescent Organism Effect

## Visual Purpose
A pulsing icosahedron core with noise-displaced vertices and 4–16 extending tentacles. Each tentacle tip carries a small emissive sphere. Creates a living, breathing organic focal point.

## When to Use
- Biology, science, deep-sea, or organic discovery concepts
- Scenes needing a "living" focal object (not mechanical/geometric)
- Dark underwater or space environments where point-light sources feel natural
- As a mid-section hero in multi-scroll pages

## Required Dependencies
- Three.js r128+
- GSAP 3.x (for scroll-triggered entrance)
- No GLB files — all procedural geometry

## Performance Cost
- Medium
- Icosahedron: detail level 3–4 = ~500–2000 vertices with noise displacement per frame
- TubeGeometry per tentacle: 12 segments × N tentacles
- Ambient particles: 200 points, drift update per frame (batched)
- Target: 60fps on mid-range GPU
- Reduce icosahedron detail to 2 and tentacles to 8 for mobile

## Integration Notes
- Call `EmissiveCore(container, options)` → returns `{ mesh, entrance, dispose }`
- `entrance` is a GSAP timeline — play on scroll intersection
- Core breathes automatically (scale sin wave, period: options.breathPeriod)
- Tentacles sway via rotation — no curve rebuild per frame
- Colors: `options.coreColor`, `options.tentacleColor`, `options.tipColor`

## Anti-Patterns
- Do NOT rebuild TubeGeometry per frame — sway via rotation only
- Do NOT use SpotLight or PointLight — pure emissive shader
- Do NOT use MeshStandardMaterial — requires lighting setup, kills the emissive look
- Do NOT set icosahedron detail above 5 — vertex count explodes (>5000)
- Do NOT use this on light backgrounds — glow blending requires dark background
