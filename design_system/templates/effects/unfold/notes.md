# Unfold Effect — Implementation Notes

## Source
Extracted from: test/디자인/2026-04-12_discovery.html Scene 2 (Abyss Map)
Pattern: origami panel stagger reveal

## Pivot Point Trick
Three.js mesh rotation pivots around the mesh center. For a panel that flips open like a door, the pivot must be at one edge.

Solution: wrap each panel in a pivot Group.
```
pivotGroup (position at panel edge)
  └── panel mesh (offset by -width/2 from pivot)
```
Rotating `pivotGroup.rotation.x` flips the panel around the edge.

## Why MeshBasicMaterial + Wireframe?
For sci-fi grid aesthetics without lighting setup.
If you want lit panels: switch to MeshStandardMaterial + ambient light.
If you want emissive lines only: keep wireframe + pair with GlowLine on edges.

## Draw-On Contour Lines
After panels unfold, contour lines "draw on" using pathLength animation (CSS SVG trick in 2D), or in Three.js:
```javascript
// Animate geometry via index buffer visibility
// Simple approach: Line object with growing vertex count
const pts = contourPoints.slice(0, Math.floor(progress * contourPoints.length));
contourLine.geometry.setFromPoints(pts);
```

## Stagger Timing
Default: each panel delays by `index × 0.2s`.
For a wave effect: stagger based on row, not flat index.
For random reveal: shuffle indices before staggering.
