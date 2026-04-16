/**
 * GlowLine — Energy beam / pillar effect
 *
 * Usage:
 *   const beam = GlowLine(scene, {
 *     color: '#6366f1',
 *     width: 0.06,
 *     height: 12,
 *     position: new THREE.Vector3(-3.5, 0, 0),
 *   });
 *
 *   // In RAF loop:
 *   beam.update(clock.getElapsedTime());
 *
 *   // Or use autoUpdate for standalone use:
 *   const beam = GlowLine(scene, { ..., autoUpdate: true });
 *
 * Options:
 *   color       {string}  '#6366f1'           Hex color
 *   width       {number}  0.06                Beam width (world units)
 *   height      {number}  12                  Beam height (world units)
 *   brightness  {number}  1.0                 Peak brightness multiplier
 *   tightness   {number}  25.0                Gaussian falloff (higher = tighter)
 *   flowSpeed   {number}  1.5                 UV scroll speed
 *   position    {Vector3} new Vector3(0,0,0)  World position
 *   rotation    {number}  0                   Z rotation in radians
 *   autoUpdate  {boolean} false               Run own RAF loop
 */
function GlowLine(scene, opts = {}) {
  const opt = {
    color:      opts.color      || '#6366f1',
    width:      opts.width      ?? 0.06,
    height:     opts.height     ?? 12,
    brightness: opts.brightness ?? 1.0,
    tightness:  opts.tightness  ?? 25.0,
    flowSpeed:  opts.flowSpeed  ?? 1.5,
    position:   opts.position   || new THREE.Vector3(0, 0, 0),
    rotation:   opts.rotation   ?? 0,
    autoUpdate: opts.autoUpdate ?? false,
  };

  function hexToVec3(hex) {
    return new THREE.Vector3(
      parseInt(hex.slice(1,3),16)/255,
      parseInt(hex.slice(3,5),16)/255,
      parseInt(hex.slice(5,7),16)/255
    );
  }

  const mat = new THREE.ShaderMaterial({
    uniforms: {
      uTime:      { value: 0 },
      uBright:    { value: opt.brightness },
      uFlowSpeed: { value: opt.flowSpeed },
      uTightness: { value: opt.tightness },
      uColor:     { value: hexToVec3(opt.color) },
    },
    vertexShader: `
      varying vec2 vUv;
      void main(){ vUv=uv; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.); }`,
    fragmentShader: `
      precision highp float;
      uniform float uTime,uBright,uFlowSpeed,uTightness; uniform vec3 uColor; varying vec2 vUv;
      void main(){
        float cx=abs(vUv.x-.5)*2.;
        float core=exp(-cx*cx*uTightness);
        float flow=mod(vUv.y-uTime*uFlowSpeed,1.);
        float line=exp(-pow(flow-.5,2.)*80.);
        float flicker=.85+.15*sin(uTime*12.7+vUv.y*8.3);
        float intensity=core*flicker*uBright;
        gl_FragColor=vec4(uColor*intensity,intensity);
      }`,
    transparent: true,
    blending: THREE.AdditiveBlending,
    depthWrite: false,
    side: THREE.DoubleSide,
  });

  const geo  = new THREE.PlaneGeometry(opt.width, opt.height);
  const mesh = new THREE.Mesh(geo, mat);
  mesh.position.copy(opt.position);
  mesh.rotation.z = opt.rotation;
  scene.add(mesh);

  function update(time) {
    mat.uniforms.uTime.value  = time;
  }

  function setColor(hex)    { mat.uniforms.uColor.value = hexToVec3(hex); }
  function setBrightness(v) { mat.uniforms.uBright.value = v; }

  function dispose() {
    scene.remove(mesh);
    geo.dispose();
    mat.dispose();
  }

  // Optional standalone loop
  if (opt.autoUpdate) {
    const clk = new THREE.Clock();
    (function loop(){ requestAnimationFrame(loop); update(clk.getElapsedTime()); })();
  }

  return { mesh, update, setColor, setBrightness, dispose };
}
