// glow-line/shader.frag
// Energy beam with gaussian falloff and flow animation

precision highp float;

uniform float uTime;
uniform float uBright;
uniform float uFlowSpeed;   // UV scroll speed (default 1.5)
uniform float uTightness;   // Gaussian k factor (default 25.0)
uniform vec3  uColor;       // RGB 0–1

varying vec2 vUv;

void main() {
  // Distance from horizontal center
  float cx = abs(vUv.x - 0.5) * 2.0;

  // Gaussian core falloff
  float core = exp(-cx * cx * uTightness);

  // Flowing energy: seamless UV scroll
  float flow = mod(vUv.y - uTime * uFlowSpeed, 1.0);
  float line = exp(-pow(flow - 0.5, 2.0) * 80.0);

  // Electrical flicker
  float flicker = 0.85 + 0.15 * sin(uTime * 12.7 + vUv.y * 8.3);

  // Final: additive energy glow
  float intensity = core * flicker * uBright;
  gl_FragColor = vec4(uColor * intensity, intensity);
}
