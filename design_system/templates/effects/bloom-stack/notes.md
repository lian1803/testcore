# Bloom Stack — Implementation Notes

## Source
Extracted from: test/디자인/2026-04-12_discovery.html Scene 1 (CrackEffect)
Manual bloom pipeline — no postprocessing dependency

## Architecture: 5-Pass Pipeline

```
Frame N:
1. renderer → rtMain          (full scene, full res)
2. rtMain   → rtBloom1        (brightness extract, half res)
3. rtBloom1 → rtBloom2        (blur horizontal, half res)
4. rtBloom2 → rtBloom1        (blur vertical, half res)
5. rtMain + rtBloom1 → screen (additive composite)
```

## Why Half Resolution for Bloom?
Bloom is a low-frequency effect — halving resolution:
- Cuts GPU memory bandwidth by 75%
- Gaussian blur cost drops by 4x
- Visually indistinguishable at bloom strength < 1.5

## Gaussian Kernel
Uses 3×3 separable kernel = 9 samples per blur pass:
Weights: [1/16, 1/8, 1/16 / 1/8, 1/4, 1/8 / 1/16, 1/8, 1/16]
Two separated passes (H + V) = 18 samples total.
True 3×3 convolution = 9 samples. Small quality loss, large performance gain.

## Threshold Tuning
| Scene Type       | Threshold | Effect |
|------------------|-----------|--------|
| Energy/sci-fi    | 0.10-0.20 | Wide bloom, atmospheric |
| Minimal/editorial| 0.40-0.60 | Only hotspots glow |
| Hero entrance    | 0.15→0.50 | Animate from wide to tight as scene settles |

## BloomStrength Animation
```javascript
// Entrance: bloom surges then settles
gsap.fromTo(bloom, { strength: 0 }, {
  strength: 1.2, duration: 0.5, ease: 'power3.out',
  onUpdate: () => bloomStack.setStrength(bloom.strength)
});
gsap.to(bloom, { strength: 0.5, duration: 1.5, delay: 0.5, ease: 'power2.inOut',
  onUpdate: () => bloomStack.setStrength(bloom.strength)
});
```
