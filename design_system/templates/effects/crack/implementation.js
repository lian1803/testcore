/**
 * CrackEffect — Fissure split hero effect
 *
 * Usage:
 *   const crack = CrackEffect(container, { veinColor: '#6366f1' });
 *   crack.timeline.play();              // starts 5s animation
 *   crack.setGap(2.0);                  // manual gap override
 *   crack.dispose();                    // cleanup WebGL resources
 *
 * Options:
 *   veinColor       {string}  '#6366f1'   Hex color for emissive vein
 *   interiorColor   {string}  '#22d3ee'   Hex color for interior glow
 *   maxGap          {number}  1.5         Final crack half-width
 *   noiseAmp        {number}  0.4         Surface vertex displacement
 *   particleCount   {number}  900         Crack particle count
 *   punchThrough    {boolean} false       Animate camera Z through crack
 *   camera          {Camera}  null        Required if punchThrough: true
 *   onComplete      {fn}      null        Called after animation finishes
 */
function CrackEffect(container, opts = {}) {
  const opt = {
    veinColor:     opts.veinColor     || '#6366f1',
    interiorColor: opts.interiorColor || '#22d3ee',
    maxGap:        opts.maxGap        ?? 1.5,
    noiseAmp:      opts.noiseAmp      ?? 0.4,
    particleCount: opts.particleCount ?? 900,
    punchThrough:  opts.punchThrough  ?? false,
    camera:        opts.camera        || null,
    onComplete:    opts.onComplete    || null,
  };

  // ── Renderer setup ────────────────────────────────────────────
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(container.clientWidth, container.clientHeight);
  renderer.setClearColor(0x000000, 1);
  container.appendChild(renderer.domElement);

  const scene = new THREE.Scene();
  scene.fog = new THREE.FogExp2(0x000000, 0.10);

  const camera = new THREE.PerspectiveCamera(
    60, container.clientWidth / container.clientHeight, 0.1, 100
  );
  camera.position.set(0, 0, 12);

  // ── Render targets (manual bloom) ─────────────────────────────
  function makeRT(w, h) {
    return new THREE.WebGLRenderTarget(w, h, {
      minFilter: THREE.LinearFilter,
      magFilter: THREE.LinearFilter,
      format: THREE.RGBAFormat,
      type: THREE.HalfFloatType,
    });
  }
  const W = container.clientWidth, H = container.clientHeight;
  const rtMain   = makeRT(W, H);
  const rtBloom1 = makeRT(W >> 1, H >> 1);
  const rtBloom2 = makeRT(W >> 1, H >> 1);

  const quadGeo = new THREE.PlaneGeometry(2, 2);
  const orthoC  = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
  const orthoS  = new THREE.Scene();
  const qMesh   = new THREE.Mesh(quadGeo);
  orthoS.add(qMesh);

  const extractMat = new THREE.ShaderMaterial({
    uniforms: { tDiffuse: { value: null }, threshold: { value: 0.15 } },
    vertexShader:   'varying vec2 vUv; void main(){ vUv=uv; gl_Position=vec4(position,1.); }',
    fragmentShader: `uniform sampler2D tDiffuse; uniform float threshold; varying vec2 vUv;
      void main(){ vec4 c=texture2D(tDiffuse,vUv);
        float l=dot(c.rgb,vec3(.299,.587,.114));
        float e=smoothstep(threshold,threshold+.2,l);
        gl_FragColor=vec4(c.rgb*e,1.); }`,
    depthTest: false, depthWrite: false
  });

  function makeBlurMat(dir) {
    return new THREE.ShaderMaterial({
      uniforms: {
        tDiffuse:   { value: null },
        resolution: { value: new THREE.Vector2(W >> 1, H >> 1) },
        direction:  { value: new THREE.Vector2(dir === 'h' ? 1 : 0, dir === 'h' ? 0 : 1) },
        radius:     { value: 2.0 }
      },
      vertexShader: 'varying vec2 vUv; void main(){ vUv=uv; gl_Position=vec4(position,1.); }',
      fragmentShader: `uniform sampler2D tDiffuse; uniform vec2 resolution,direction; uniform float radius; varying vec2 vUv;
        void main(){ vec2 ts=radius/resolution; vec4 col=vec4(0.);
          float w[9]; w[0]=.0625;w[1]=.125;w[2]=.0625;w[3]=.125;w[4]=.25;w[5]=.125;w[6]=.0625;w[7]=.125;w[8]=.0625;
          int idx=0; for(int i=-1;i<=1;i++){ for(int j=-1;j<=1;j++){
            col+=texture2D(tDiffuse,vUv+vec2(float(i),float(j))*ts*direction)*w[idx]; idx++;
          }} gl_FragColor=col; }`,
      depthTest: false, depthWrite: false
    });
  }
  const blurH = makeBlurMat('h');
  const blurV = makeBlurMat('v');

  const compMat = new THREE.ShaderMaterial({
    uniforms: { tBase: { value: null }, tBloom: { value: null }, bloomStrength: { value: 0.2 } },
    vertexShader: 'varying vec2 vUv; void main(){ vUv=uv; gl_Position=vec4(position,1.); }',
    fragmentShader: `uniform sampler2D tBase,tBloom; uniform float bloomStrength; varying vec2 vUv;
      void main(){ vec4 b=texture2D(tBase,vUv); vec4 bl=texture2D(tBloom,vUv);
        gl_FragColor=vec4(b.rgb+bl.rgb*bloomStrength,1.); }`,
    depthTest: false, depthWrite: false
  });

  // ── CPU value noise (for vertex displacement) ──────────────────
  function h(n) { return ((Math.sin(n) * 43758.5453) % 1 + 1) % 1; }
  function noise3(x, y, z) {
    const ix=Math.floor(x),iy=Math.floor(y),iz=Math.floor(z);
    const fx=x-ix,fy=y-iy,fz=z-iz;
    const ux=fx*fx*(3-2*fx),uy=fy*fy*(3-2*fy),uz=fz*fz*(3-2*fz);
    const a=h(ix+iy*57+iz*113),  b=h(ix+1+iy*57+iz*113),
          c=h(ix+(iy+1)*57+iz*113), d=h(ix+1+(iy+1)*57+iz*113),
          e=h(ix+iy*57+(iz+1)*113), f=h(ix+1+iy*57+(iz+1)*113),
          g=h(ix+(iy+1)*57+(iz+1)*113), k=h(ix+1+(iy+1)*57+(iz+1)*113);
    return a*(1-ux)*(1-uy)*(1-uz)+b*ux*(1-uy)*(1-uz)
          +c*(1-ux)*uy*(1-uz)   +d*ux*uy*(1-uz)
          +e*(1-ux)*(1-uy)*uz   +f*ux*(1-uy)*uz
          +g*(1-ux)*uy*uz       +k*ux*uy*uz;
  }

  // ── Slab geometry ──────────────────────────────────────────────
  const veinRGB = hexToVec3(opt.veinColor);

  function buildSlab(sign) {
    const geo = new THREE.PlaneGeometry(14, 22, 60, 80);
    const pos = geo.attributes.position;
    for (let i = 0; i < pos.count; i++) {
      const x = pos.getX(i), y = pos.getY(i);
      const n = noise3(x * 0.4 + 3.7, y * 0.3 + 1.2, 0.8) * 2 - 1;
      pos.setZ(i, n * opt.noiseAmp);
      const ep = 1 - Math.min(Math.abs(x) / 7, 1);
      pos.setX(i, x + (noise3(y * 1.5 + 10, x * 2, 5) * 0.3) * ep * sign * -0.3);
    }
    geo.computeVertexNormals();
    return geo;
  }

  function makeSlab(sign) {
    const mat = new THREE.ShaderMaterial({
      uniforms: {
        uTime:       { value: 0 },
        uVeinBright: { value: 0.3 },
        uSide:       { value: sign },
      },
      vertexShader: `
        varying vec2 vUv; varying vec3 vNormal;
        void main(){ vUv=uv; vNormal=normalize(normalMatrix*normal);
          gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.); }`,
      fragmentShader: `
        precision highp float;
        uniform float uTime,uVeinBright,uSide; varying vec2 vUv; varying vec3 vNormal;
        float hh(float n){ return fract(sin(n)*43758.5453); }
        float ns(vec2 p){ vec2 i=floor(p),f=fract(p); f=f*f*(3.-2.*f);
          return mix(mix(hh(i.x+i.y*57.),hh(i.x+1.+i.y*57.),f.x),
                     mix(hh(i.x+(i.y+1.)*57.),hh(i.x+1.+(i.y+1.)*57.),f.x),f.y); }
        float fbm(vec2 p){ return .5*ns(p)+.25*ns(p*2.)+.125*ns(p*4.)+.0625*ns(p*8.); }
        void main(){
          float rock=fbm(vUv*6.+1.3);
          vec3 base=mix(vec3(.03,.03,.04),vec3(.12,.10,.13),rock);
          float edgeU=uSide>0.?vUv.x:1.-vUv.x;
          float vm=pow(edgeU,3.);
          float vein=pow(fbm(vUv*vec2(2.,8.)+vec2(uTime*.05,0.)),2.5)*vm;
          float pulse=.65+.35*sin(uTime*(6.2832/.8));
          vec3 vc=vec3(${veinRGB})*vein*uVeinBright*pulse*3.;
          float fres=1.-abs(dot(vNormal,vec3(0.,0.,1.)));
          vec3 fc=vec3(${veinRGB})*pow(fres,4.)*uVeinBright*.5;
          gl_FragColor=vec4(base+vc+fc,1.); }`
    });
    return new THREE.Mesh(buildSlab(sign), mat);
  }

  const HALF = 7;
  const slabL = makeSlab(-1);
  const slabR = makeSlab(+1);
  slabL.position.set(-HALF - 0.01, 0, 0);
  slabR.position.set( HALF + 0.01, 0, 0);
  scene.add(slabL, slabR);

  // ── Fissure glow ───────────────────────────────────────────────
  const fissureMat = new THREE.ShaderMaterial({
    uniforms: { uTime: { value: 0 }, uBright: { value: 1 }, uScale: { value: 0.01 } },
    vertexShader: 'varying vec2 vUv; void main(){ vUv=uv; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.); }',
    fragmentShader: `precision highp float; uniform float uTime,uBright,uScale; varying vec2 vUv;
      void main(){ float cx=abs(vUv.x-.5)*2.; float g=exp(-cx*cx*25./max(uScale,.005));
        float fl=.85+.15*sin(uTime*12.7+vUv.y*8.3);
        gl_FragColor=vec4(vec3(${veinRGB})*g*fl*uBright, g*uBright); }`,
    transparent: true, blending: THREE.AdditiveBlending, depthWrite: false
  });
  const fissureStrip = new THREE.Mesh(new THREE.PlaneGeometry(0.02, 22), fissureMat);
  fissureStrip.position.z = 0.05;
  scene.add(fissureStrip);

  // ── Interior gradient ──────────────────────────────────────────
  const intRGB = hexToVec3(opt.interiorColor);
  const intMat = new THREE.ShaderMaterial({
    uniforms: { uTime: { value: 0 }, uAlpha: { value: 0 } },
    vertexShader: 'varying vec2 vUv; void main(){ vUv=uv; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.); }',
    fragmentShader: `precision highp float; uniform float uTime,uAlpha; varying vec2 vUv;
      void main(){ float cx=abs(vUv.x-.5)*2.; float g=pow(1.-cx,1.5); float pls=.7+.3*sin(uTime*7.9);
        vec3 col=mix(vec3(${veinRGB}),vec3(${intRGB}),cx);
        gl_FragColor=vec4(col*g*pls*2.,g*uAlpha); }`,
    transparent: true, blending: THREE.AdditiveBlending, depthWrite: false
  });
  const intMesh = new THREE.Mesh(new THREE.PlaneGeometry(0.04, 22), intMat);
  intMesh.position.z = 0.03;
  scene.add(intMesh);

  // ── Particles ─────────────────────────────────────────────────
  const PC = opt.particleCount;
  const pPos  = new Float32Array(PC * 3);
  const pSeed = new Float32Array(PC);
  for (let i = 0; i < PC; i++) {
    pPos[i*3]   = (Math.random() - 0.5) * 0.08;
    pPos[i*3+1] = (Math.random() - 0.5) * 20;
    pPos[i*3+2] = (Math.random() - 0.5) * 2 + 0.1;
    pSeed[i]    = Math.random() * 6.28;
  }
  const pGeo = new THREE.BufferGeometry();
  pGeo.setAttribute('position', new THREE.BufferAttribute(pPos, 3));
  pGeo.setAttribute('seed',     new THREE.BufferAttribute(pSeed, 1));
  const pMat = new THREE.ShaderMaterial({
    uniforms: {
      uTime:    { value: 0 },
      uAlpha:   { value: 0 },
      uGapHalf: { value: 0.01 },
      uSize:    { value: window.devicePixelRatio * 2.5 }
    },
    vertexShader: `attribute float seed; uniform float uTime,uGapHalf,uSize; varying float vA;
      void main(){ vec3 p=position; float t=mod(uTime*.4+seed,1.);
        p.y=mix(-10.,10.,t); float dr=sin(uTime*2.3+seed*7.1)*.015;
        p.x=clamp(p.x+dr,-uGapHalf*.8,uGapHalf*.8);
        vA=1.-abs(t*2.-1.); gl_PointSize=uSize*vA;
        gl_Position=projectionMatrix*modelViewMatrix*vec4(p,1.); }`,
    fragmentShader: `varying float vA; void main(){
      float d=length(gl_PointCoord-vec2(.5)); if(d>.5) discard;
      gl_FragColor=vec4(${intRGB},(1.-d*2.)*vA); }`,
    transparent: true, blending: THREE.AdditiveBlending, depthWrite: false
  });
  const particles = new THREE.Points(pGeo, pMat);
  scene.add(particles);

  // ── Animation state ────────────────────────────────────────────
  const state = { gapHalf: 0.01, bloom: 0.2, vein: 0.3, pA: 0, intA: 0 };

  const timeline = gsap.timeline({ paused: true, onComplete: opt.onComplete });

  // Phase 1: crack opens (0→2s)
  timeline.to(state, { duration: 2.0, gapHalf: opt.maxGap, bloom: 0.9, vein: 1.0, pA: 1.0, intA: 1.0, ease: 'power2.inOut' }, 0);

  if (opt.punchThrough && opt.camera) {
    // Phase 2: camera punches through (2→4s)
    timeline.to(opt.camera.position, { duration: 2.0, z: -8, ease: 'power3.in' }, 2.0);
    // Phase 3: gap expands to fill screen
    timeline.to(state, { duration: 0.5, gapHalf: 9.0, ease: 'power4.in' }, 3.5);
  }

  // ── Resize ─────────────────────────────────────────────────────
  const resizeObs = new ResizeObserver(() => {
    const W = container.clientWidth, H = container.clientHeight;
    camera.aspect = W / H; camera.updateProjectionMatrix();
    renderer.setSize(W, H);
    rtMain.setSize(W, H);
    rtBloom1.setSize(W >> 1, H >> 1);
    rtBloom2.setSize(W >> 1, H >> 1);
    blurH.uniforms.resolution.value.set(W >> 1, H >> 1);
    blurV.uniforms.resolution.value.set(W >> 1, H >> 1);
  });
  resizeObs.observe(container);

  // ── Render loop ────────────────────────────────────────────────
  const clock = new THREE.Clock();
  let rafId;

  function renderBloom() {
    renderer.setRenderTarget(rtMain); renderer.render(scene, camera);
    qMesh.material = extractMat; extractMat.uniforms.tDiffuse.value = rtMain.texture;
    renderer.setRenderTarget(rtBloom1); renderer.render(orthoS, orthoC);
    qMesh.material = blurH; blurH.uniforms.tDiffuse.value = rtBloom1.texture;
    renderer.setRenderTarget(rtBloom2); renderer.render(orthoS, orthoC);
    qMesh.material = blurV; blurV.uniforms.tDiffuse.value = rtBloom2.texture;
    renderer.setRenderTarget(rtBloom1); renderer.render(orthoS, orthoC);
    qMesh.material = compMat;
    compMat.uniforms.tBase.value = rtMain.texture;
    compMat.uniforms.tBloom.value = rtBloom1.texture;
    compMat.uniforms.bloomStrength.value = state.bloom;
    renderer.setRenderTarget(null); renderer.render(orthoS, orthoC);
  }

  function loop() {
    rafId = requestAnimationFrame(loop);
    const t = clock.getElapsedTime();

    camera.position.z = opt.punchThrough && opt.camera ? opt.camera.position.z : camera.position.z;

    slabL.position.x = -HALF - state.gapHalf;
    slabR.position.x =  HALF + state.gapHalf;

    [slabL.material, slabR.material].forEach(m => {
      m.uniforms.uTime.value      = t;
      m.uniforms.uVeinBright.value = state.vein;
    });

    fissureStrip.scale.x         = Math.max(state.gapHalf / 0.01, 1);
    fissureMat.uniforms.uTime.value  = t;
    fissureMat.uniforms.uBright.value = Math.min(state.vein * 1.5, 3.0);
    fissureMat.uniforms.uScale.value  = state.gapHalf;

    intMesh.scale.x             = Math.max(state.gapHalf * 4, 1);
    intMat.uniforms.uTime.value  = t;
    intMat.uniforms.uAlpha.value = state.intA;

    pMat.uniforms.uTime.value    = t;
    pMat.uniforms.uAlpha.value   = state.pA * Math.min(state.gapHalf * 0.7, 1.0);
    pMat.uniforms.uGapHalf.value = state.gapHalf * 0.6;

    const batch = 25, start = Math.floor((t * 120) % (PC / batch)) * batch;
    for (let i = start; i < Math.min(start + batch, PC); i++) {
      pPos[i*3] = (Math.random() - 0.5) * state.gapHalf * 1.4;
    }
    pGeo.attributes.position.needsUpdate = true;

    renderBloom();
  }

  loop();

  // ── Helpers ────────────────────────────────────────────────────
  function hexToVec3(hex) {
    const r = parseInt(hex.slice(1,3),16)/255;
    const g = parseInt(hex.slice(3,5),16)/255;
    const b = parseInt(hex.slice(5,7),16)/255;
    return `${r.toFixed(3)},${g.toFixed(3)},${b.toFixed(3)}`;
  }

  function setGap(value) { state.gapHalf = value; }

  function dispose() {
    cancelAnimationFrame(rafId);
    timeline.kill();
    resizeObs.disconnect();
    renderer.dispose();
    [rtMain, rtBloom1, rtBloom2].forEach(rt => rt.dispose());
    container.removeChild(renderer.domElement);
  }

  return { timeline, setGap, dispose, camera, scene, renderer };
}
