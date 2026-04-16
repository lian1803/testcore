// crack/shader.frag — Slab surface fragment shader
// Used by: CrackEffect slab meshes

precision highp float;

uniform float uTime;
uniform float uVeinBright;
uniform float uSide;   // -1.0 = left slab, +1.0 = right slab

varying vec2 vUv;
varying vec3 vNormal;

// Value noise helpers
float hh(float n) { return fract(sin(n) * 43758.5453); }

float ns(vec2 p) {
  vec2 i = floor(p);
  vec2 f = fract(p);
  f = f * f * (3.0 - 2.0 * f);
  float a = hh(i.x + i.y * 57.0);
  float b = hh(i.x + 1.0 + i.y * 57.0);
  float c = hh(i.x + (i.y + 1.0) * 57.0);
  float d = hh(i.x + 1.0 + (i.y + 1.0) * 57.0);
  return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
}

// Fractal Brownian Motion — 4 octaves
float fbm(vec2 p) {
  return 0.5  * ns(p)
       + 0.25 * ns(p * 2.0)
       + 0.125 * ns(p * 4.0)
       + 0.0625 * ns(p * 8.0);
}

void main() {
  // Rock base color — dark stone with subtle variation
  float rock = fbm(vUv * 6.0 + 1.3);
  vec3 base = mix(vec3(0.03, 0.03, 0.04), vec3(0.12, 0.10, 0.13), rock);

  // Emissive vein — concentrated at inner edge (crack face)
  float edgeU = uSide > 0.0 ? vUv.x : 1.0 - vUv.x;
  float vm    = pow(edgeU, 3.0);

  // Vein pattern: fbm streaks along Y axis with slow drift
  float vein  = pow(fbm(vUv * vec2(2.0, 8.0) + vec2(uTime * 0.05, 0.0)), 2.5) * vm;

  // Heartbeat pulse: 0.8s period
  float pulse = 0.65 + 0.35 * sin(uTime * (6.2832 / 0.8));

  vec3 vc = vec3(0.388, 0.400, 0.945) * vein * uVeinBright * pulse * 3.0;

  // Fresnel rim — bleed of vein color onto facing edge
  float fres = 1.0 - abs(dot(vNormal, vec3(0.0, 0.0, 1.0)));
  vec3 fc    = vec3(0.388, 0.400, 0.945) * pow(fres, 4.0) * uVeinBright * 0.5;

  gl_FragColor = vec4(base + vc + fc, 1.0);
}
