# Emissive Core — Implementation Notes

## Source
Extracted from: test/디자인/2026-04-12_discovery.html Scene 3 (Bioluminescence)
Concept: Director brief, Discovery project 2026-04-12

## Key Technical Decisions

### GPU Noise vs Pre-baked Displacement
Core uses GPU noise in vertex shader each frame (simplex-approximation with value noise).
Why not pre-baked: The breathing animation requires continuous deformation — pre-baking would need vertex animation textures (complex). GPU noise at detail=3 (320 vertices) is negligible cost.

### Tentacles: Rotation, Not Curve Rebuild
Tentacles are built as TubeGeometry once, then swayed via mesh.rotation each frame.
Why not rebuild CatmullRomCurve + TubeGeometry: Curve rebuild = ~0.5ms per tentacle per frame. At 12 tentacles = 6ms. That's one whole frame budget.
Trade-off: Rotation sway looks slightly less organic than true curve deformation, but cost is 0.01ms.
When to accept quality hit: Always for interactive/responsive pages. Only rebuild for cinematic pre-renders.

### Breath Period
`scale sin(time * 2π / breathPeriod)` with amplitude 0.04.
Default breathPeriod = 3.0s (20 BPM — slow, like a large marine creature).
For anxiety/urgency: reduce to 1.5s (40 BPM).
For calm/trust: increase to 5s (12 BPM — whale territory).

### Ambient Particle Drift
200 particles drift upward at 0.002 units/frame.
Y reset when > threshold: creates seamless loop without visible pop.
Batch update: only update 25 particles per frame (rolling window), not all 200.

## Tentacle Count Presets
| Context | Count | Notes |
|---------|-------|-------|
| Minimalist | 4–6 | Clean, sculptural |
| Standard | 12 | Organic, balanced |
| Lush | 16–20 | Dense, overwhelming |
| Mobile | 6 | Performance cap |

## Color Presets
| Theme | coreColor | tentacleColor | tipColor |
|-------|-----------|---------------|----------|
| Deep sea (default) | #6366f1 | #6366f1 | #22d3ee |
| Crimson creature | #ef4444 | #b91c1c | #fca5a5 |
| Bioluminescent green | #10b981 | #065f46 | #6ee7b7 |
| Solar flare | #f59e0b | #92400e | #fde68a |
