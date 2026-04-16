---
name: glow-line
version: 1.0
---

# Glow Line — Energy Beam / Pillar Effect

## Visual Purpose
A vertical or horizontal plane mesh with a GLSL shader that renders a flowing energy beam: bright center core with gaussian falloff, animated noise-driven flicker, and additive blending for natural glow stacking.

## When to Use
- Structural frames (doors, arches, gates, thresholds)
- UI dividers that need energy/tech feel
- Portal or teleportation effects
- Accent lines separating hero from content sections

## Required Dependencies
- Three.js r128+
- No GSAP required (runs standalone)

## Performance Cost
- Very Low
- Single PlaneGeometry (1×1, 1 segment) per beam
- ShaderMaterial with 3 uniforms updated per frame
- AdditiveBlending — no depth test needed
- Multiple beams: linear cost, 10 beams ≈ 0.2ms

## Integration Notes
- Call `GlowLine(scene, options)` → returns `{ mesh, update, dispose }`
- Call `glowLine.update(time)` in your RAF loop (or use auto-update via `autoUpdate: true`)
- Control color via `options.color` (hex string)
- Control flow direction via `options.direction`: 'up' | 'down' | 'horizontal'
- Animate `mesh.scale.x` for width, `mesh.scale.y` for length
- Layer multiple beams with offset positions for complex gate effects

## Anti-Patterns
- Do NOT use MeshBasicMaterial with emissive — no falloff control
- Do NOT use actual PointLight/SpotLight for this — unnecessary scene graph cost
- Do NOT set opacity on the material — control brightness via uBright uniform instead
- Do NOT skip AdditiveBlending — normal blending creates harsh edges
