---
name: bloom-stack
version: 1.0
---

# Bloom Stack — Manual Two-Pass Bloom Pipeline

## Visual Purpose
Adds selective additive bloom to a Three.js scene without requiring EffectComposer or the postprocessing package. Extracts bright areas, blurs them in two passes (H+V), then composites back over the base render.

## When to Use
- Any scene with emissive materials, glow strips, or energy effects
- When you want per-object bloom control via brightness threshold
- When bundle size matters (no postprocessing package needed)
- When you need bloom strength to animate (e.g., pulse with heartbeat)

## Required Dependencies
- Three.js r128+
- No additional packages required

## Performance Cost
- Low-Medium
- 5 draw calls per frame (main render + extract + blur H + blur V + composite)
- 3 render targets at half resolution
- Total overhead: ~1.5ms on mid-range GPU
- Can reduce to 1 blur pass for ultra-low-end devices

## Integration Notes
- Call `BloomStack(renderer, scene, camera)` — returns `{ render, setStrength, resize, dispose }`
- Call `bloom.render()` each frame instead of `renderer.render(scene, camera)`
- Animate `bloom.setStrength(0→1.5)` via GSAP for entrance effects
- Threshold uniform (default 0.15) controls which pixels get bloomed — lower = more bloom, higher = only bright hotspots

## Anti-Patterns
- Do NOT run at full resolution — always use half-res render targets
- Do NOT use more than 2 blur passes without performance testing
- Do NOT combine with EffectComposer — pick one pipeline
- Do NOT set threshold to 0 — entire scene blooms, performance tanks
- Do NOT set bloomStrength above 2.0 — creates unreadable white haze
