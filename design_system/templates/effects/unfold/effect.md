---
name: unfold
version: 1.0
---

# Unfold — Origami Panel Reveal

## Visual Purpose
A set of flat panels that unfold sequentially from a folded/closed state. Each panel flips open on a hinge axis with staggered timing, revealing content or textures underneath. Creates a sense of uncovering something hidden.

## When to Use
- Map, document, or knowledge reveal concepts
- Dashboard or data visualization entrances
- Navigation menus that need physical metaphor
- Portfolio grid reveals where each item "unfolds" into view

## Required Dependencies
- Three.js r128+
- GSAP 3.x (for staggered flip animation)

## Performance Cost
- Very Low
- N PlaneGeometry meshes (1 per panel) — static geometry after build
- No per-frame shader computation
- MeshBasicMaterial or emissive wireframe
- 20 panels ≈ 0.1ms render cost

## Integration Notes
- Call `UnfoldEffect(scene, options)` → returns `{ entrance, panels, dispose }`
- `entrance` is a GSAP timeline — play on intersection
- Each panel has a `.userData.index` for stagger reference
- Override panel appearance by accessing `panels[i].material`
- Works well with `GlowLine` on panel edges for sci-fi feel

## Anti-Patterns
- Do NOT animate geometry vertices per frame — rotate the whole mesh on hinge axis
- Do NOT use pivot point at mesh center — set pivot to edge using group wrapper
- Do NOT use more than 6 columns × 4 rows on mobile (24 panels max)
- Do NOT apply physics simulation — deterministic rotation is sufficient and much faster
