---
name: crack
version: 1.0
---

# Crack — Fissure Split Effect

## Visual Purpose
Two displaced rock slabs split apart from center, revealing an emissive light vein. Camera can punch through the gap. Works as a hero reveal or section transition.

## When to Use
- Hero openings that need a dramatic "reveal from nothing" moment
- Discovery / exploration / breakthrough concepts
- Dark themes where light source needs to feel earned

## Required Dependencies
- Three.js r128+
- GSAP 3.x (for timeline animation)
- WebGL2 preferred (falls back to WebGL1)

## Performance Cost
- Medium-High
- Two PlaneGeometry meshes: 60×80 segments each (~9,600 vertices each)
- 2 ShaderMaterial instances + 1 fissure glow + 1 interior gradient + Points system
- Manual bloom pipeline: 3 render targets, 2 blur passes
- Target: 60fps on mid-range GPU (GTX 1060 / M1 equivalent)
- Reduce segment count to 30×40 for mobile

## Integration Notes
- Import `implementation.js`, call `CrackEffect(container, options)`
- Returns `{ timeline, dispose }` — use timeline.play() on scroll trigger
- Gap width controlled via `options.maxGap` (default 1.5)
- Camera punch optional: set `options.punchThrough: true` + provide your camera ref
- Colors override: `options.veinColor`, `options.interiorColor`

## Anti-Patterns
- Do NOT use AdditiveBlending on slabs — only on glow strip and particles
- Do NOT set fog density above 0.15 (kills depth)
- Do NOT run bloom at full resolution — always half-res render targets
- Do NOT animate gap and camera simultaneously without easing difference (gap: power2, camera: power3.in)
- Do NOT use this with light themes — vein glow is calibrated for #0a0a0a backgrounds
