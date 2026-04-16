/**
 * DistortionEffect — Image displacement hover transition
 * Adapted from hover-effect by Robin Delaporte (MIT)
 *
 * Usage:
 *   const fx = DistortionEffect(container, {
 *     image1:       '/img/default.jpg',
 *     image2:       '/img/hover.jpg',
 *     displacement: '/img/disp.png',
 *     intensity:    0.3,
 *   });
 *
 *   element.addEventListener('mouseenter', fx.show);
 *   element.addEventListener('mouseleave', fx.hide);
 *   fx.dispose(); // cleanup
 *
 * Options:
 *   image1        {string}  required   Default state image URL
 *   image2        {string}  required   Hover state image URL
 *   displacement  {string}  required   Displacement/noise texture URL
 *   intensity     {number}  0.3        Distortion strength
 *   angle1        {number}  π/4        Rotation for image1 displacement
 *   angle2        {number}  -3π/4      Rotation for image2 displacement
 *   speedIn       {number}  1.2        Transition in duration (s)
 *   speedOut      {number}  0.9        Transition out duration (s)
 *   easing        {string}  'expo.out' GSAP easing
 */
function DistortionEffect(container, opts = {}) {
  if (!opts.image1 || !opts.image2 || !opts.displacement) {
    console.warn('[DistortionEffect] image1, image2, and displacement are required');
    return null;
  }

  const opt = {
    intensity:   opts.intensity   ?? 0.3,
    angle1:      opts.angle1      ?? Math.PI / 4,
    angle2:      opts.angle2      ?? -Math.PI * 3 / 4,
    speedIn:     opts.speedIn     ?? 1.2,
    speedOut:    opts.speedOut    ?? 0.9,
    easing:      opts.easing      || 'expo.out',
  };

  const W = container.offsetWidth;
  const H = container.offsetHeight;

  const renderer = new THREE.WebGLRenderer({ antialias: false, alpha: true });
  renderer.setPixelRatio(1); // intentional — dispFactor animation hides aliasing
  renderer.setClearColor(0xffffff, 0);
  renderer.setSize(W, H);
  container.appendChild(renderer.domElement);

  const scene  = new THREE.Scene();
  const camera = new THREE.OrthographicCamera(W/-2, W/2, H/2, H/-2, 1, 1000);
  camera.position.z = 1;

  const loader = new THREE.TextureLoader();
  loader.crossOrigin = 'anonymous';

  const uniforms = {
    dispFactor:  { value: 0.0 },
    dpr:         { value: 1.0 },
    disp:        { value: null },
    texture1:    { value: null },
    texture2:    { value: null },
    angle1:      { value: opt.angle1 },
    angle2:      { value: opt.angle2 },
    intensity1:  { value: opt.intensity },
    intensity2:  { value: opt.intensity },
    res:         { value: new THREE.Vector4(W, H, W/H > 1 ? W/H : 1, W/H < 1 ? H/W : 1) },
    parent:      { value: new THREE.Vector2(W, H) },
  };

  const mat = new THREE.ShaderMaterial({
    uniforms,
    vertexShader: `
      varying vec2 vUv;
      void main(){ vUv=uv; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.); }`,
    fragmentShader: `
      varying vec2 vUv;
      uniform float dispFactor,dpr; uniform sampler2D disp,texture1,texture2;
      uniform float angle1,angle2,intensity1,intensity2;
      uniform vec4 res; uniform vec2 parent;
      mat2 rot(float a){ float s=sin(a),c=cos(a); return mat2(c,-s,s,c); }
      void main(){
        vec4 d=texture2D(disp,vUv); vec2 dv=vec2(d.r,d.g);
        vec2 uv=.5*gl_FragCoord.xy/res.xy;
        vec2 myUV=(uv-vec2(.5))*res.zw+vec2(.5);
        vec2 p1=myUV+rot(angle1)*dv*intensity1*dispFactor;
        vec2 p2=myUV+rot(angle2)*dv*intensity2*(1.-dispFactor);
        gl_FragColor=mix(texture2D(texture1,p1),texture2D(texture2,p2),dispFactor);
      }`,
    transparent: true, depthTest: false, depthWrite: false
  });

  const geo  = new THREE.PlaneGeometry(W, H, 1, 1);
  const mesh = new THREE.Mesh(geo, mat);
  scene.add(mesh);

  let needsRender = true;
  let rafId;

  function render() {
    rafId = requestAnimationFrame(render);
    if (!needsRender) return;
    renderer.render(scene, camera);
  }

  // Load textures
  loader.load(opts.displacement, tex => {
    tex.magFilter = tex.minFilter = THREE.LinearFilter;
    uniforms.disp.value = tex; needsRender = true;
  });
  loader.load(opts.image1, tex => {
    tex.magFilter = tex.minFilter = THREE.LinearFilter;
    uniforms.texture1.value = tex; needsRender = true;
  });
  loader.load(opts.image2, tex => {
    tex.magFilter = tex.minFilter = THREE.LinearFilter;
    uniforms.texture2.value = tex; needsRender = true;
  });

  render();

  let currentTween = null;

  function animateTo(target, speed) {
    if (currentTween) currentTween.kill();
    currentTween = gsap.to(uniforms.dispFactor, {
      value: target,
      duration: speed,
      ease: opt.easing,
      onUpdate: () => { needsRender = true; },
      onComplete: () => { needsRender = false; }
    });
  }

  function show() { animateTo(1, opt.speedIn); }
  function hide() { animateTo(0, opt.speedOut); }
  function toggle() { uniforms.dispFactor.value < 0.5 ? show() : hide(); }

  function dispose() {
    cancelAnimationFrame(rafId);
    if (currentTween) currentTween.kill();
    renderer.dispose();
    geo.dispose();
    mat.dispose();
    container.removeChild(renderer.domElement);
  }

  return { show, hide, toggle, dispose };
}
