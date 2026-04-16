---
name: distortion
version: 1.0
---

# Distortion — Image Displacement Hover Effect

## Visual Purpose
Two images blended via a displacement map texture. On hover, `dispFactor` animates 0→1 transitioning from image1 to image2 with a warped, liquid distortion. The displacement direction is controllable via rotation angle.

## When to Use
- Portfolio / case study image reveals
- Before/After comparisons with visual drama
- Product hover states (default → hover variant)
- Section transitions where two visual states need to merge

## Required Dependencies
- Three.js r128+
- GSAP 3.x (for dispFactor animation)
- A displacement/noise texture (PNG, grayscale)
- Two source images (same aspect ratio)

## Performance Cost
- Low
- Single PlaneGeometry (orthographic) per instance
- 4 texture samples per fragment (2 displaced + 2 originals — actually just 3)
- Runs at element size, not fullscreen
- Multiple instances: linear cost

## Integration Notes
- Call `DistortionEffect(container, { image1, image2, displacement })` → returns `{ show, hide, toggle, dispose }`
- `container` is the DOM element that holds the canvas
- `show()` animates dispFactor 0→1 (transition to image2)
- `hide()` animates dispFactor 1→0 (back to image1)
- Add event listeners manually: `el.addEventListener('mouseenter', effect.show)`
- `intensity` controls distortion amount (default 0.3)

## Anti-Patterns
- Do NOT use this without a displacement texture — flat mix is just crossfade
- Do NOT use images with different aspect ratios — UV mapping will distort
- Do NOT run at full viewport size — design for element size
- Do NOT skip the GSAP tween — jumping dispFactor 0→1 looks broken
- Credit: displacement shader concept by Robin Delaporte (hover-effect library)
  Extracted and simplified from: design_system/references/hover-effect/
