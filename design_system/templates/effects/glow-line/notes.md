# Glow Line — Implementation Notes

## Source
Extracted from: test/디자인/2026-04-12_discovery.html Scene 6 (Threshold pillars)
Pattern: energy flow beam on structural geometry

## Shader Design

### Gaussian Falloff
`g = exp(-cx² × 25)` where cx = normalized distance from center (0–1).
The constant 25 controls beam tightness:
- 10: wide, atmospheric beam
- 25: standard pillar (default)
- 80: razor-thin line

### Flow Animation
`mod(vUv.y - uTime × speed, 1.0)` creates a seamless scrolling UV.
The energy "flows" upward at `speed` units per second.
Wrap with `mod()` ensures no seam at UV boundaries.

### Flicker
`0.85 + 0.15 × sin(uTime × freq + vUv.y × spatial_freq)`
- `freq = 12.7`: fast electrical flicker
- `spatial_freq = 8.3`: spatial variation along beam length
Adjust freq for different material types:
- Slow plasma: 2.0
- Electrical: 12–20
- Steady laser: 0 (remove flicker term)

## Common Configurations

```javascript
// Sci-fi door frame
GlowLine(scene, { color: '#6366f1', width: 0.04, height: 10, brightness: 1.2, flowSpeed: 1.5 })

// Energy divider
GlowLine(scene, { color: '#22d3ee', width: 0.01, height: 100, brightness: 0.8, flowSpeed: 3.0 })

// Glowing arch (use PlaneGeometry with displacement instead)
GlowLine(scene, { color: '#a78bfa', width: 0.06, height: 6, brightness: 2.0, flowSpeed: 0.5 })
```
