---
name: camera-scroll
version: 1.0
---

# Camera Scroll — Scroll-Driven Camera Flythrough

## Visual Purpose
Binds Three.js camera position/rotation directly to scroll progress via GSAP ScrollTrigger scrub.
The user scrolls → camera moves through 3D space → feels like watching a film.
This is the single most impactful pattern for "cinematic" web experiences.

## When to Use
- ANY hero section that needs to feel like a movie opening
- Brand story told through camera journey (approach, reveal, pass-through)
- Product reveals where camera orbits around the subject
- "Director's cut" sequences where the camera path IS the narrative

## Required Dependencies
- Three.js r128+
- GSAP 3.x + ScrollTrigger plugin
- CustomEase plugin (for cinematicSilk curve)
- Lenis (scroll smoothing, essential for non-choppy camera)

## Performance Cost
- Low overhead on top of existing Three.js scene
- ScrollTrigger scrub: 0 extra draw calls
- Camera position lerp: negligible CPU
- The scene complexity drives cost, not this pattern

## Integration Notes
- Call `CameraScroll(camera, keyframes, scrollContainer)` → returns `{ timeline, kill }`
- `keyframes` array: `[{ progress: 0-1, x, y, z, lookAt? }]`
- Set `scrub: true` for 1:1 scroll, `scrub: 2` for 2s lag (cinematic feel)
- **Always use CustomEase("cinematicSilk")** — linear camera = amateur feel
- Text sync: trigger text reveals at specific scroll progress values, not time values
- Pair with `ScrollSmoother({ smooth: 4 })` for the fluid film-like scroll
- Reference implementation: design_system/references/camera-flythrough/

## Anti-Patterns
- Do NOT animate camera with `setInterval` or `requestAnimationFrame` manually — use scrub
- Do NOT use linear easing for camera — always cinematicSilk or custom curve
- Do NOT trigger text by time — trigger by scroll progress (`onEnter` at specific scrub position)
- Do NOT set scrub < 1 for hero sections — too snappy, loses cinematic weight
- Do NOT forget Lenis — without smooth scroll, camera stutters on trackpad
