/**
 * UnfoldEffect — Origami panel stagger reveal
 *
 * Usage:
 *   const unfold = UnfoldEffect(scene, {
 *     cols: 3, rows: 2,
 *     panelW: 2.5, panelH: 2.5,
 *     gap: 0.1,
 *     color: 0x0a081e,
 *     wireColor: 0x6366f1,
 *   });
 *   unfold.entrance.play();
 *   unfold.dispose();
 *
 * Options:
 *   cols      {number}  3         Grid columns
 *   rows      {number}  2         Grid rows
 *   panelW    {number}  2.5       Panel width (world units)
 *   panelH    {number}  2.5       Panel height (world units)
 *   gap       {number}  0.1       Gap between panels
 *   color     {hex}     0x0a081e  Panel face color
 *   wireColor {hex}     0x6366f1  Wireframe edge color
 *   stagger   {number}  0.2       Seconds between panel reveals
 *   duration  {number}  0.6       Individual panel flip duration
 *   easing    {string}  'power2.out' GSAP easing
 *   startFold {string}  'top'     Initial fold axis: 'top'|'bottom'|'left'|'right'
 */
function UnfoldEffect(scene, opts = {}) {
  const opt = {
    cols:      opts.cols      ?? 3,
    rows:      opts.rows      ?? 2,
    panelW:    opts.panelW    ?? 2.5,
    panelH:    opts.panelH    ?? 2.5,
    gap:       opts.gap       ?? 0.1,
    color:     opts.color     ?? 0x0a081e,
    wireColor: opts.wireColor ?? 0x6366f1,
    stagger:   opts.stagger   ?? 0.2,
    duration:  opts.duration  ?? 0.6,
    easing:    opts.easing    || 'power2.out',
    startFold: opts.startFold || 'top',
  };

  const totalW = opt.cols * (opt.panelW + opt.gap) - opt.gap;
  const totalH = opt.rows * (opt.panelH + opt.gap) - opt.gap;

  const panelGroup = new THREE.Group();
  scene.add(panelGroup);

  const panels    = [];
  const pivots    = [];
  const wirePanels = [];

  for (let row = 0; row < opt.rows; row++) {
    for (let col = 0; col < opt.cols; col++) {
      const idx = row * opt.cols + col;

      // World position of panel center
      const px = col * (opt.panelW + opt.gap) - totalW / 2 + opt.panelW / 2;
      const py = -(row * (opt.panelH + opt.gap) - totalH / 2 + opt.panelH / 2);

      // Pivot group — positioned at panel top edge
      const pivot = new THREE.Group();
      pivot.position.set(px, py + opt.panelH / 2, 0);
      panelGroup.add(pivot);
      pivots.push(pivot);

      // Panel face (offset down from pivot)
      const geo  = new THREE.PlaneGeometry(opt.panelW, opt.panelH);
      const mat  = new THREE.MeshBasicMaterial({
        color: opt.color, side: THREE.DoubleSide, transparent: true, opacity: 0.9
      });
      const panel = new THREE.Mesh(geo, mat);
      panel.position.y = -opt.panelH / 2; // offset: pivot is at top edge
      panel.userData   = { index: idx, col, row };
      pivot.add(panel);
      panels.push(panel);

      // Wireframe edges
      const wireGeo = new THREE.EdgesGeometry(geo);
      const wireMat = new THREE.LineBasicMaterial({ color: opt.wireColor, transparent: true, opacity: 0.4 });
      const wire    = new THREE.LineSegments(wireGeo, wireMat);
      wire.position.y = -opt.panelH / 2;
      pivot.add(wire);
      wirePanels.push(wire);

      // Start folded (90° = flat against parent, invisible)
      pivot.rotation.x = -Math.PI / 2;
    }
  }

  // ── Entrance timeline ────────────────────────────────────────
  const entrance = gsap.timeline({ paused: true });

  pivots.forEach((pivot, i) => {
    entrance.to(pivot.rotation, {
      x: 0,
      duration: opt.duration,
      ease:     opt.easing,
    }, i * opt.stagger);
  });

  function dispose() {
    entrance.kill();
    scene.remove(panelGroup);
    panels.forEach(p => { p.geometry.dispose(); p.material.dispose(); });
    wirePanels.forEach(w => { w.geometry.dispose(); w.material.dispose(); });
  }

  return { entrance, panels, pivots, group: panelGroup, dispose };
}
