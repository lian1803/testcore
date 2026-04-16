# Distortion Effect — Implementation Notes

## Source
Extracted from: design_system/references/hover-effect/src/hover-effect.js
Author: Robin Delaporte — https://github.com/robin-dela/hover-effect
License: MIT — attribution preserved

## How the Displacement Works

```glsl
vec4 disp = texture2D(dispMap, vUv);         // sample noise texture
vec2 dispVec = vec2(disp.r, disp.g);          // use R,G channels as XY offset

// Apply opposite rotations to each image for cross-distort
vec2 pos1 = myUV + rotate(angle1) * dispVec * intensity * dispFactor;
vec2 pos2 = myUV + rotate(angle2) * dispVec * intensity * (1.0 - dispFactor);

vec4 t1 = texture2D(texture1, pos1);
vec4 t2 = texture2D(texture2, pos2);
gl_FragColor = mix(t1, t2, dispFactor);
```

Key insight: both images are displaced simultaneously in opposite directions.
At dispFactor=0: image1 undisplaced, image2 fully displaced (invisible)
At dispFactor=0.5: both images equally displaced — peak distortion
At dispFactor=1: image1 fully displaced (invisible), image2 undisplaced

## Displacement Texture Selection
| Texture | Effect |
|---------|--------|
| Diagonal noise (default) | Organic liquid transition |
| Horizontal stripes | Venetian blind wipe |
| Radial gradient | Ripple from center |
| Perlin noise | Fog/smoke transition |
| Hard edges (comic halftone) | Graphic burst |

Good free sources: transitionImages from gl-transition library, or generate with GIMP filter.

## Angle Configuration
- `angle1 = Math.PI/4` (45°): default, good for organic feel
- `angle2 = -angle1 * 3` (-135°): creates cross-tension
- Same angle: directional wipe
- 90° apart: circular distortion

## Performance Optimization
- Set `renderer.setPixelRatio(1)` for this effect — dispFactor animation hides aliasing
- Run `renderer.render()` only on frame where dispFactor changes (not every frame)
- For static state: render once, then pause RAF
