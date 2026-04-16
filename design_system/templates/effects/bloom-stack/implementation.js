/**
 * BloomStack — Manual two-pass bloom pipeline
 *
 * Usage:
 *   const bloom = BloomStack(renderer, scene, camera, { threshold: 0.15 });
 *
 *   // In your RAF loop, replace renderer.render(scene, camera) with:
 *   bloom.render();
 *
 *   // Animate bloom strength:
 *   bloom.setStrength(0.9);
 *
 *   // On resize:
 *   bloom.resize(newWidth, newHeight);
 *
 *   // Cleanup:
 *   bloom.dispose();
 */
function BloomStack(renderer, scene, camera, opts = {}) {
  const threshold = opts.threshold ?? 0.15;
  let   strength  = opts.strength  ?? 0.5;

  function makeRT(w, h) {
    return new THREE.WebGLRenderTarget(w, h, {
      minFilter: THREE.LinearFilter,
      magFilter: THREE.LinearFilter,
      format:    THREE.RGBAFormat,
      type:      THREE.HalfFloatType,
    });
  }

  let W = renderer.domElement.width;
  let H = renderer.domElement.height;

  let rtMain   = makeRT(W, H);
  let rtBloom1 = makeRT(W >> 1, H >> 1);
  let rtBloom2 = makeRT(W >> 1, H >> 1);

  const quadGeo = new THREE.PlaneGeometry(2, 2);
  const orthoC  = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
  const orthoS  = new THREE.Scene();
  const quad    = new THREE.Mesh(quadGeo);
  orthoS.add(quad);

  const extractMat = new THREE.ShaderMaterial({
    uniforms: { tDiffuse: { value: null }, threshold: { value: threshold } },
    vertexShader:   'varying vec2 vUv; void main(){ vUv=uv; gl_Position=vec4(position,1.); }',
    fragmentShader: `uniform sampler2D tDiffuse; uniform float threshold; varying vec2 vUv;
      void main(){ vec4 c=texture2D(tDiffuse,vUv);
        float l=dot(c.rgb,vec3(.299,.587,.114));
        float e=smoothstep(threshold,threshold+.2,l);
        gl_FragColor=vec4(c.rgb*e,1.); }`,
    depthTest: false, depthWrite: false
  });

  function makeBlur(dx, dy) {
    return new THREE.ShaderMaterial({
      uniforms: {
        tDiffuse:   { value: null },
        resolution: { value: new THREE.Vector2(W >> 1, H >> 1) },
        direction:  { value: new THREE.Vector2(dx, dy) },
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
  const blurH = makeBlur(1, 0);
  const blurV = makeBlur(0, 1);

  const compMat = new THREE.ShaderMaterial({
    uniforms: { tBase: { value: null }, tBloom: { value: null }, bloomStrength: { value: strength } },
    vertexShader: 'varying vec2 vUv; void main(){ vUv=uv; gl_Position=vec4(position,1.); }',
    fragmentShader: `uniform sampler2D tBase,tBloom; uniform float bloomStrength; varying vec2 vUv;
      void main(){ vec4 b=texture2D(tBase,vUv); vec4 bl=texture2D(tBloom,vUv);
        gl_FragColor=vec4(b.rgb+bl.rgb*bloomStrength,1.); }`,
    depthTest: false, depthWrite: false
  });

  function render() {
    // 1. Full scene → rtMain
    renderer.setRenderTarget(rtMain);
    renderer.render(scene, camera);

    // 2. Extract bright → rtBloom1 (half res)
    quad.material = extractMat;
    extractMat.uniforms.tDiffuse.value = rtMain.texture;
    renderer.setRenderTarget(rtBloom1);
    renderer.render(orthoS, orthoC);

    // 3. Blur horizontal → rtBloom2
    quad.material = blurH;
    blurH.uniforms.tDiffuse.value = rtBloom1.texture;
    renderer.setRenderTarget(rtBloom2);
    renderer.render(orthoS, orthoC);

    // 4. Blur vertical → rtBloom1
    quad.material = blurV;
    blurV.uniforms.tDiffuse.value = rtBloom2.texture;
    renderer.setRenderTarget(rtBloom1);
    renderer.render(orthoS, orthoC);

    // 5. Composite → screen
    quad.material = compMat;
    compMat.uniforms.tBase.value  = rtMain.texture;
    compMat.uniforms.tBloom.value = rtBloom1.texture;
    compMat.uniforms.bloomStrength.value = strength;
    renderer.setRenderTarget(null);
    renderer.render(orthoS, orthoC);
  }

  function setStrength(v) {
    strength = v;
    compMat.uniforms.bloomStrength.value = v;
  }

  function resize(w, h) {
    W = w; H = h;
    rtMain.setSize(W, H);
    rtBloom1.setSize(W >> 1, H >> 1);
    rtBloom2.setSize(W >> 1, H >> 1);
    blurH.uniforms.resolution.value.set(W >> 1, H >> 1);
    blurV.uniforms.resolution.value.set(W >> 1, H >> 1);
  }

  function dispose() {
    [rtMain, rtBloom1, rtBloom2].forEach(rt => rt.dispose());
    [extractMat, blurH, blurV, compMat].forEach(m => m.dispose());
    quadGeo.dispose();
  }

  return { render, setStrength, resize, dispose };
}
