# Camera Scroll — Implementation Notes

## Source
Extracted from: AndrewPrifer/CodropsCameraFlyThroughTutorial (MIT)
Pattern refined from: JosephASG/codrops-cinematic-scroll-animations (Codrops 2025.11)
Reference: design_system/references/camera-flythrough/

## The Cinematic Easing Curve

```javascript
CustomEase.create("cinematicSilk", "0.45,0.05,0.55,0.95");
```

This single curve is what separates "cinematic" from "demo."
- Slow start: camera hesitates before moving (like a dolly shot pulling away)
- Fast middle: decisive motion through the scene  
- Slow end: camera settles into position (like a tracking shot landing)

Compare to:
- `power2.inOut`: generic. Works, but feels like a UI animation
- `linear`: robotic. Immediately reads as "code demo"
- `cinematicSilk`: feels like a camera operator made a deliberate choice

## ScrollTrigger Scrub Architecture

```
HTML structure:
<div id="scroll-container" style="height: 500vh">  ← scroll room
  <div id="sticky-scene" style="position:sticky; top:0; height:100vh">
    <canvas id="hero-canvas">                       ← Three.js scene
  </div>
</div>

GSAP wiring:
ScrollTrigger.create({
  trigger: "#scroll-container",
  start: "top top",
  end: "bottom bottom",
  scrub: 2,                    ← 2s lag = film-like weight
  onUpdate: (self) => {
    // self.progress: 0 → 1
    updateCamera(self.progress);
  }
});
```

## Keyframe System

Define camera path as keyframes, interpolate between them:

```javascript
const keyframes = [
  { p: 0.0,  pos: [0, 0, 12],  look: [0, 0, 0]  },  // opening: distance
  { p: 0.3,  pos: [0, 2, 6],   look: [0, 0, 0]  },  // approach
  { p: 0.6,  pos: [3, 1, 2],   look: [0, 0, 0]  },  // orbit right
  { p: 1.0,  pos: [0, 0, -4],  look: [0, 0, 0]  },  // through
];

function updateCamera(progress) {
  // find surrounding keyframes
  const i = keyframes.findIndex(k => k.p > progress) - 1;
  const a = keyframes[Math.max(0, i)];
  const b = keyframes[Math.min(keyframes.length-1, i+1)];
  const t = (progress - a.p) / (b.p - a.p);
  const s = cinematicSilkInterpolate(t); // apply curve
  
  camera.position.lerpVectors(
    new THREE.Vector3(...a.pos),
    new THREE.Vector3(...b.pos),
    s
  );
}
```

## Text Sync Pattern

```javascript
// Text appears when camera reaches specific position — NOT on a timer
ScrollTrigger.create({
  trigger: "#scroll-container",
  start: "30% top",   // 30% scroll = camera is at keyframe[1]
  end: "35% top",
  onEnter: () => revealText("headline-1"),
  onLeaveBack: () => hideText("headline-1"),
});
```

## Lenis Setup (Required)

```javascript
const lenis = new Lenis({ duration: 1.4, easing: t => Math.min(1, 1.001 - Math.pow(2, -10*t)) });
lenis.on('scroll', ScrollTrigger.update);
gsap.ticker.add(time => lenis.raf(time * 1000));
gsap.ticker.lagSmoothing(0);
```

## ScrollSmoother Alternative (GSAP Club)

If using GSAP Club (paid):
```javascript
ScrollSmoother.create({ wrapper: "#wrapper", content: "#content", smooth: 4, effects: true });
```
`smooth: 4` = 4s smoothing. Produces the most cinematic scroll feel.
Free alternative: Lenis + `scrub: 2` (95% equivalent).

## Camera Path Presets

| Preset | Keyframe Pattern | Emotional Effect |
|--------|-----------------|------------------|
| Dolly in | z: 12 → 0 | Approach, anticipation |
| Pull back reveal | z: 2 → 12 | Surprise, scale reveal |
| Orbit | x: 0→5→0, z: 8→6→8 | Exploration, confidence |
| Punch through | z: 12 → -8 | Breakthrough, transformation |
| Rising crane | y: -2 → 4, z: 8 → 6 | Aspiration, elevation |
