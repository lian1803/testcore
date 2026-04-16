# Crack Effect — Implementation Notes

## Source
Extracted from: test/디자인/2026-04-12_discovery.html Scene 1
Original concept: director brief, Discovery project 2026-04-12

## Key Technical Decisions

### Vertex Displacement (CPU, not GPU)
Slab geometry is displaced on the CPU at build time using a hand-rolled value noise function.
Why: Predictable, cacheable, no uniform overhead per frame.
GPU noise would add ~0.3ms per frame per slab — not worth it for static rock geometry.

### Manual Bloom vs EffectComposer
We avoid three.js EffectComposer because:
1. Requires postprocessing package (extra bundle weight)
2. Less control over bloom threshold per-object
3. Manual pipeline: render → extract bright → blur H → blur V → composite
   Total cost: 5 draw calls, 3 render targets (half-res)

### Gap Animation Curve
- Opening phase: `power2.inOut` — feels like physical resistance
- Camera punch phase: `power3.in` — acceleration through the breach
- NEVER use linear — removes the physicality

### Vein Pulse
Vein brightness oscillates: `0.65 + 0.35 * sin(time * (2π / 0.8))`
Period = 0.8s matches human heartbeat range (75 BPM) — creates subconscious tension.

## Tuning Parameters
| Parameter | Default | Range | Effect |
|-----------|---------|-------|--------|
| maxGap | 1.5 | 0.5–9.0 | Final crack width |
| veinBrightness | 1.0 | 0.3–2.0 | Peak emissive intensity |
| bloomStrength | 0.9 | 0.2–1.5 | Bloom composite weight |
| noiseAmp | 0.4 | 0.1–0.8 | Surface roughness |
| particleCount | 900 | 200–1500 | Crack particles |

## Known Issues
- On Safari/WebKit: HalfFloatType render targets may fallback to FloatType — performance hit ~15%
- Fix: detect `renderer.capabilities.isWebGL2` and use `THREE.UnsignedByteType` fallback

## Color Presets
| Theme | veinColor | interiorColor | bgColor |
|-------|-----------|---------------|---------|
| Indigo (default) | #6366f1 | #22d3ee | #000000 |
| Crimson | #ef4444 | #f97316 | #0a0000 |
| Emerald | #10b981 | #06b6d4 | #000a05 |
| Gold | #f59e0b | #fde68a | #0a0800 |
