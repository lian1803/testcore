---
name: glsl-expert
description: Advanced GLSL shader writing — noise functions, ray marching, SDF, fluid simulation, light refraction. Use when creating custom WebGL shaders, fixing shader compilation errors, or implementing advanced visual effects.
---

# GLSL Expert Skill

## Noise Functions (copy-paste ready)

### Simplex 2D
```glsl
vec3 mod289(vec3 x){return x-floor(x*(1./289.))*289.;}
vec2 mod289(vec2 x){return x-floor(x*(1./289.))*289.;}
vec3 permute(vec3 x){return mod289(((x*34.)+1.)*x);}
float snoise(vec2 v){
  const vec4 C=vec4(.211324865405187,.366025403784439,-.577350269189626,.024390243902439);
  vec2 i=floor(v+dot(v,C.yy));vec2 x0=v-i+dot(i,C.xx);
  vec2 i1;i1=(x0.x>x0.y)?vec2(1,0):vec2(0,1);
  vec4 x12=x0.xyxy+C.xxzz;x12.xy-=i1;
  i=mod289(i);vec3 p=permute(permute(i.y+vec3(0,i1.y,1))+i.x+vec3(0,i1.x,1));
  vec3 m=max(.5-vec3(dot(x0,x0),dot(x12.xy,x12.xy),dot(x12.zw,x12.zw)),0.);
  m=m*m;m=m*m;
  vec3 x=2.*fract(p*C.www)-1.;vec3 h=abs(x)-.5;vec3 ox=floor(x+.5);vec3 a0=x-ox;
  m*=1.79284291400159-.85373472095314*(a0*a0+h*h);
  vec3 g;g.x=a0.x*x0.x+h.x*x0.y;g.yz=a0.yz*x12.xz+h.yz*x12.yw;
  return 130.*dot(m,g);
}
```

### FBM (Fractal Brownian Motion)
```glsl
float fbm(vec2 p){
  float v=0.,a=.5;
  mat2 rot=mat2(cos(.5),sin(.5),-sin(.5),cos(.5));
  for(int i=0;i<6;i++){v+=a*snoise(p);p=rot*p*2.;a*=.5;}
  return v;
}
```

### Curl Noise (3D)
```glsl
vec3 curl(vec3 p){
  float e=.1;
  vec3 dx=vec3(e,0,0),dy=vec3(0,e,0),dz=vec3(0,0,e);
  float x=fbm((p+dy).xz)-fbm((p-dy).xz)-fbm((p+dz).xy)+fbm((p-dz).xy);
  float y=fbm((p+dz).xy)-fbm((p-dz).xy)-fbm((p+dx).yz)+fbm((p-dx).yz);
  float z=fbm((p+dx).yz)-fbm((p-dx).yz)-fbm((p+dy).xz)+fbm((p-dy).xz);
  return normalize(vec3(x,y,z)/(2.*e));
}
```

## SDF (Signed Distance Functions)
```glsl
float sdSphere(vec3 p,float r){return length(p)-r;}
float sdBox(vec3 p,vec3 b){vec3 q=abs(p)-b;return length(max(q,0.))+min(max(q.x,max(q.y,q.z)),0.);}
float sdTorus(vec3 p,vec2 t){vec2 q=vec2(length(p.xz)-t.x,p.y);return length(q)-t.y;}
float opSmoothUnion(float d1,float d2,float k){float h=clamp(.5+.5*(d2-d1)/k,0.,1.);return mix(d2,d1,h)-k*h*(1.-h);}
```

## Ray Marching Template
```glsl
float map(vec3 p){
  float d=sdSphere(p,1.);
  d=opSmoothUnion(d,sdBox(p-vec3(1.5,0,0),vec3(.5)),.3);
  return d;
}
vec3 getNormal(vec3 p){
  vec2 e=vec2(.001,0);
  return normalize(vec3(map(p+e.xyy)-map(p-e.xyy),map(p+e.yxy)-map(p-e.yxy),map(p+e.yyx)-map(p-e.yyx)));
}
void mainImage(out vec4 O,vec2 U){
  vec2 uv=(U-.5*iResolution.xy)/iResolution.y;
  vec3 ro=vec3(0,0,-3),rd=normalize(vec3(uv,1));
  float t=0.;
  for(int i=0;i<80;i++){
    vec3 p=ro+rd*t;float d=map(p);
    if(d<.001||t>20.)break;t+=d;
  }
  vec3 col=vec3(0);
  if(t<20.){vec3 p=ro+rd*t;vec3 n=getNormal(p);col=vec3(dot(n,normalize(vec3(1,1,-1))))*.5+.5;}
  O=vec4(col,1);
}
```

## Fluid Simulation (Navier-Stokes basics)
```glsl
// Advection step
vec2 advect(sampler2D vel,vec2 uv,float dt){
  vec2 pos=uv-texture2D(vel,uv).xy*dt;
  return texture2D(vel,pos).xy;
}
// Divergence
float divergence(sampler2D vel,vec2 uv,vec2 texel){
  return .5*(texture2D(vel,uv+vec2(texel.x,0)).x-texture2D(vel,uv-vec2(texel.x,0)).x
            +texture2D(vel,uv+vec2(0,texel.y)).y-texture2D(vel,uv-vec2(0,texel.y)).y);
}
```

## Common Patterns

### Chromatic Aberration
```glsl
vec3 chromaticAberration(sampler2D tex,vec2 uv,float amount){
  return vec3(
    texture2D(tex,uv+vec2(amount,0)).r,
    texture2D(tex,uv).g,
    texture2D(tex,uv-vec2(amount,0)).b
  );
}
```

### Screen-space Distortion (barrel)
```glsl
vec2 barrelDistort(vec2 uv,float k){
  vec2 d=uv-.5;
  float r2=dot(d,d);
  return .5+d*(1.+k*r2);
}
```

## Debugging Tips
- Black screen? Check `gl_FragColor` alpha (must be 1.0)
- Pink/magenta? Shader compilation error — check console
- Flickering? Use `highp float` precision
- Performance? Reduce loop iterations, use `step()` instead of `if()`
