/**
 * CameraScroll — Scroll-driven camera flythrough
 *
 * Requires: Three.js r128+, GSAP + ScrollTrigger, Lenis
 * Reference: design_system/references/camera-flythrough/
 *
 * Usage:
 *   // 1. Setup Lenis (required for smooth feel)
 *   const lenis = setupLenis();
 *
 *   // 2. Create scroll container in HTML:
 *   //   <div id="scroll-wrap" style="height:500vh">
 *   //     <div id="sticky" style="position:sticky;top:0;height:100vh">
 *   //       <canvas id="canvas"></canvas>
 *   //     </div>
 *   //   </div>
 *
 *   // 3. Define camera path
 *   const path = CameraScroll(camera, [
 *     { p: 0.0, pos: [0, 0, 12], look: [0, 0, 0] },
 *     { p: 0.5, pos: [3, 2,  4], look: [0, 0, 0] },
 *     { p: 1.0, pos: [0, 0, -4], look: [0, 0, 0] },
 *   ], {
 *     trigger:  '#scroll-wrap',
 *     scrub:    2,
 *   });
 *
 *   // 4. Sync text reveals to scroll progress
 *   path.onProgress(0.3, () => revealText('#headline'));
 *
 *   // 5. Cleanup
 *   path.kill();
 */

// cinematicSilk easing — must call after GSAP loads
function registerCinematicEase() {
  if (typeof CustomEase !== 'undefined') {
    CustomEase.create('cinematicSilk', '0.45,0.05,0.55,0.95');
    CustomEase.create('cinematicFlow',  '0.25,0.46,0.45,0.94');
    CustomEase.create('cinematicSlam',  '0.77,0,0.175,1');
  }
}

// Lenis setup (call once, globally)
function setupLenis() {
  const lenis = new Lenis({
    duration:    1.4,
    easing:      t => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
    smoothWheel: true,
  });
  lenis.on('scroll', ScrollTrigger.update);
  gsap.ticker.add(time => lenis.raf(time * 1000));
  gsap.ticker.lagSmoothing(0);
  return lenis;
}

/**
 * CameraScroll
 * @param {THREE.Camera} camera
 * @param {Array} keyframes  [{p: 0-1, pos: [x,y,z], look?: [x,y,z]}]
 * @param {Object} opts
 *   trigger  {string}  CSS selector for scroll container (height: N*100vh)
 *   scrub    {number}  GSAP scrub value (default: 2 — cinematic lag)
 *   start    {string}  ScrollTrigger start (default: 'top top')
 *   end      {string}  ScrollTrigger end   (default: 'bottom bottom')
 */
function CameraScroll(camera, keyframes, opts = {}) {
  const trigger = opts.trigger || '#scroll-wrap';
  const scrub   = opts.scrub   ?? 2;
  const start   = opts.start   || 'top top';
  const end     = opts.end     || 'bottom bottom';

  // Sort keyframes by progress
  const kf = [...keyframes].sort((a, b) => a.p - b.p);

  // Ensure 0 and 1 are covered
  if (kf[0].p > 0) kf.unshift({ ...kf[0], p: 0 });
  if (kf[kf.length-1].p < 1) kf.push({ ...kf[kf.length-1], p: 1 });

  const tmpA = new THREE.Vector3();
  const tmpB = new THREE.Vector3();
  const tmpL = new THREE.Vector3();

  // Smooth step (cinematicSilk approximation for internal use)
  function smoothstep(t) {
    // Approximates "0.45,0.05,0.55,0.95" cubic bezier
    t = Math.max(0, Math.min(1, t));
    return t < 0.5
      ? 4 * t * t * t
      : 1 - Math.pow(-2 * t + 2, 3) / 2;
  }

  function updateCamera(progress) {
    progress = Math.max(0, Math.min(1, progress));

    // Find surrounding keyframes
    let lo = 0;
    for (let i = 0; i < kf.length - 1; i++) {
      if (kf[i].p <= progress) lo = i;
    }
    const hi  = Math.min(lo + 1, kf.length - 1);
    const a   = kf[lo];
    const b   = kf[hi];
    const seg = b.p - a.p;
    const t   = seg > 0 ? (progress - a.p) / seg : 0;
    const s   = smoothstep(t);

    // Position
    tmpA.set(...a.pos);
    tmpB.set(...b.pos);
    camera.position.lerpVectors(tmpA, tmpB, s);

    // LookAt (if provided)
    const la = a.look || b.look;
    const lb = b.look || a.look;
    if (la && lb) {
      tmpA.set(...la);
      tmpB.set(...lb);
      tmpL.lerpVectors(tmpA, tmpB, s);
      camera.lookAt(tmpL);
    }
  }

  // Callbacks per progress threshold
  const callbacks = [];
  let lastProgress = 0;

  const st = ScrollTrigger.create({
    trigger, start, end, scrub,
    onUpdate(self) {
      updateCamera(self.progress);
      // Fire progress callbacks
      callbacks.forEach(cb => {
        if (lastProgress < cb.p && self.progress >= cb.p) cb.fn();
        if (cb.back && lastProgress >= cb.p && self.progress < cb.p) cb.back();
      });
      lastProgress = self.progress;
    },
  });

  function onProgress(p, fn, back) {
    callbacks.push({ p, fn, back });
  }

  function kill() {
    st.kill();
  }

  // Set initial position
  updateCamera(0);

  return { onProgress, kill, trigger: st };
}
