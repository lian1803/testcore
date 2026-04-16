/**
 * EmissiveCore — Bioluminescent pulsing organism
 *
 * Usage:
 *   const core = EmissiveCore(container, {
 *     coreColor: '#6366f1',
 *     tentacleCount: 12,
 *     tipColor: '#22d3ee'
 *   });
 *   core.entrance.play();   // scroll-triggered entrance
 *   core.dispose();
 *
 * Options:
 *   coreColor       {string}  '#6366f1'  Icosahedron emissive color
 *   tentacleColor   {string}  '#6366f1'  Tube color
 *   tipColor        {string}  '#22d3ee'  Tip sphere color
 *   tentacleCount   {number}  12         Number of tentacles
 *   tentacleLength  {number}  2.0        Reach of each tentacle
 *   breathPeriod    {number}  3.0        Core breathing period in seconds
 *   particleCount   {number}  200        Ambient particle count
 *   cameraDistance  {number}  6          Initial camera Z
 */
function EmissiveCore(container, opts = {}) {
  const opt = {
    coreColor:      opts.coreColor      || '#6366f1',
    tentacleColor:  opts.tentacleColor  || '#6366f1',
    tipColor:       opts.tipColor       || '#22d3ee',
    tentacleCount:  opts.tentacleCount  ?? 12,
    tentacleLength: opts.tentacleLength ?? 2.0,
    breathPeriod:   opts.breathPeriod   ?? 3.0,
    particleCount:  opts.particleCount  ?? 200,
    cameraDistance: opts.cameraDistance ?? 6,
  };

  function hexToRGB01(hex) {
    return [
      parseInt(hex.slice(1,3),16)/255,
      parseInt(hex.slice(3,5),16)/255,
      parseInt(hex.slice(5,7),16)/255,
    ];
  }

  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(container.clientWidth, container.clientHeight);
  renderer.setClearColor(0x000000, 0);
  container.appendChild(renderer.domElement);

  const scene  = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(55, container.clientWidth / container.clientHeight, 0.1, 100);
  camera.position.set(0, -4, opt.cameraDistance + 2);
  camera.lookAt(0, -1, 0);

  // ── Icosahedron core ─────────────────────────────────────────
  const [cr, cg, cb] = hexToRGB01(opt.coreColor);
  const coreGeo = new THREE.IcosahedronGeometry(1.2, 4);
  const coreMat = new THREE.ShaderMaterial({
    uniforms: { uTime: { value: 0 } },
    vertexShader: `
      uniform float uTime;
      varying vec3 vNormal;
      float hh(float n){ return fract(sin(n)*43758.5453); }
      float ns(vec3 p){
        vec3 i=floor(p),f=fract(p); f=f*f*(3.-2.*f);
        return mix(
          mix(mix(hh(i.x+i.y*57.+i.z*113.),hh(i.x+1.+i.y*57.+i.z*113.),f.x),
              mix(hh(i.x+(i.y+1.)*57.+i.z*113.),hh(i.x+1.+(i.y+1.)*57.+i.z*113.),f.x),f.y),
          mix(mix(hh(i.x+i.y*57.+(i.z+1.)*113.),hh(i.x+1.+i.y*57.+(i.z+1.)*113.),f.x),
              mix(hh(i.x+(i.y+1.)*57.+(i.z+1.)*113.),hh(i.x+1.+(i.y+1.)*57.+(i.z+1.)*113.),f.x),f.y),f.z);
      }
      void main(){
        vNormal = normalize(normal);
        float d   = ns(position * 2.0 + uTime * 0.3) * 0.25;
        vec3  pos = position + normal * d;
        float breathe = 1.0 + 0.04 * sin(uTime * (6.2832 / ${opt.breathPeriod.toFixed(2)}));
        pos *= breathe;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
      }`,
    fragmentShader: `
      varying vec3 vNormal;
      void main(){
        float f   = pow(1.0 - abs(dot(vNormal, vec3(0., 0., 1.))), 2.0);
        vec3  col = mix(vec3(${cr.toFixed(3)},${cg.toFixed(3)},${cb.toFixed(3)}),
                        vec3(${cr.toFixed(3)+0.2},${(cg*1.3).toFixed(3)},${cb.toFixed(3)}), f);
        gl_FragColor = vec4(col, 0.85);
      }`,
    transparent: true, side: THREE.DoubleSide
  });
  const coreMesh = new THREE.Mesh(coreGeo, coreMat);
  coreMesh.position.y = -1;
  scene.add(coreMesh);

  // ── Tentacles ────────────────────────────────────────────────
  const [tr, tg, tb] = hexToRGB01(opt.tentacleColor);
  const [pr, pg, pb] = hexToRGB01(opt.tipColor);
  const tentacles = [];
  const tips      = [];

  for (let i = 0; i < opt.tentacleCount; i++) {
    const angle = (i / opt.tentacleCount) * Math.PI * 2;
    const L = opt.tentacleLength;

    // Build curve
    const pts = [];
    for (let s = 0; s <= 8; s++) {
      const t = s / 8;
      pts.push(new THREE.Vector3(
        Math.cos(angle) * t * L,
        Math.sin(angle * 0.5) * t * L - t * t * 0.5,
        Math.sin(angle) * t * L
      ));
    }
    const curve   = new THREE.CatmullRomCurve3(pts);
    const tubGeo  = new THREE.TubeGeometry(curve, 12, 0.04, 6, false);
    const tubMat  = new THREE.MeshBasicMaterial({
      color: new THREE.Color(tr, tg, tb), transparent: true, opacity: 0.6
    });
    const tube = new THREE.Mesh(tubGeo, tubMat);
    tube.position.y = -1;
    tube.userData   = { phase: i * 0.52 };
    tentacles.push(tube);
    scene.add(tube);

    // Tip glow
    const tipMesh = new THREE.Mesh(
      new THREE.SphereGeometry(0.08, 6, 6),
      new THREE.MeshBasicMaterial({ color: new THREE.Color(pr, pg, pb) })
    );
    const endPt = pts[pts.length - 1];
    tipMesh.position.set(endPt.x, endPt.y - 1, endPt.z);
    tips.push(tipMesh);
    scene.add(tipMesh);
  }

  // ── Ambient particles ────────────────────────────────────────
  const PC = opt.particleCount;
  const apPos = new Float32Array(PC * 3);
  for (let i = 0; i < PC; i++) {
    apPos[i*3]   = (Math.random() - 0.5) * 12;
    apPos[i*3+1] = (Math.random() - 0.5) * 10 - 2;
    apPos[i*3+2] = (Math.random() - 0.5) * 8;
  }
  const apGeo = new THREE.BufferGeometry();
  apGeo.setAttribute('position', new THREE.BufferAttribute(apPos, 3));
  const [ar, ag, ab] = hexToRGB01(opt.coreColor);
  const apMat = new THREE.PointsMaterial({
    color: new THREE.Color(ar + 0.15, ag + 0.15, ab),
    size: 0.04, transparent: true, opacity: 0.25,
    blending: THREE.AdditiveBlending, depthWrite: false
  });
  scene.add(new THREE.Points(apGeo, apMat));

  // ── Entrance timeline ────────────────────────────────────────
  const entrance = gsap.timeline({ paused: true });
  entrance.to(camera.position, {
    y: -1, z: opt.cameraDistance,
    duration: 2.0, ease: 'power2.out',
    onUpdate: () => camera.lookAt(0, -1, 0)
  }, 0);
  entrance.from(coreMesh.scale, { x: 0, y: 0, z: 0, duration: 0.8, ease: 'back.out(1.3)' }, 0.3);

  // ── Resize ───────────────────────────────────────────────────
  const ro = new ResizeObserver(() => {
    const W = container.clientWidth, H = container.clientHeight;
    camera.aspect = W / H; camera.updateProjectionMatrix();
    renderer.setSize(W, H);
  });
  ro.observe(container);

  // ── Render loop ──────────────────────────────────────────────
  const clock = new THREE.Clock();
  let rafId;

  function loop() {
    rafId = requestAnimationFrame(loop);
    const t = clock.getElapsedTime();

    coreMat.uniforms.uTime.value = t;

    tentacles.forEach((tb_mesh, i) => {
      tb_mesh.rotation.z = Math.sin(t + tb_mesh.userData.phase) * 0.3;
      tb_mesh.rotation.x = Math.cos(t * 0.7 + tb_mesh.userData.phase) * 0.2;
    });

    // Particle drift
    const batch = 10, start = Math.floor(t * 30) % (PC / batch) * batch;
    for (let i = start; i < Math.min(start + batch, PC); i++) {
      apPos[i*3+1] += 0.002;
      if (apPos[i*3+1] > 3) apPos[i*3+1] = -8;
    }
    apGeo.attributes.position.needsUpdate = true;

    renderer.render(scene, camera);
  }

  loop();

  function dispose() {
    cancelAnimationFrame(rafId);
    entrance.kill();
    ro.disconnect();
    renderer.dispose();
    container.removeChild(renderer.domElement);
  }

  return { mesh: coreMesh, entrance, camera, scene, renderer, dispose };
}
