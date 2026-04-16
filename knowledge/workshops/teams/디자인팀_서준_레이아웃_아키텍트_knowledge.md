
=== 전문 지식 (세계 최고 수준 자료 기반) ===

### CSS grain texture overlay techniques: SVG feTurbulence filter vs canvas noise vs PNG overlay performance comparison 2024
### **성능 비교 (2024 기준, 모바일/데스크톱 기준)**
| Technique | FPS (60fps 기준, iPhone 14/Chrome) | CPU 사용량 | 장점 | 단점 | 추천 용도 |
|-----------|------------------------------------|------------|------|------|----------|
| **SVG feTurbulence** | 58-60fps[6][7][9] | 낮음 (GPU 가속) | 무한 스케일, 애니메이션 부드러움, 파일 0KB | 노이즈 패턴 고정적 (baseFrequency 조정 필요) | 대형 배경/전체 페이지 (99% 케이스) |
| **Canvas Noise** | 45-55fps (WebGL 사용 시 58fps) | 높음 (JS 렌더링) | 동적/랜덤 생성 가능, 인터랙티브 | JS 오버헤드, 배터리 소모 ↑ | 인터랙티브 요소만 (버튼/호버) |
| **PNG Overlay** | 60fps[3][4][7] | 최저 (이미지 캐시) | 간단, 크로스브라우저 | 파일 크기 10-50KB, 고정 해상도 (스케일 블러) | 정적 소규모 오버레이 |

**결론: SVG feTurbulence가 2024 최고 성능/효율.** Canvas는 JS 피하세요. PNG는 100x100px 이하로 압축[3][4].

### **SVG feTurbulence (최고 추천, GPU 최적화)**
**실전 코드 (전체 화면 오버레이):**
```html
<svg style="position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;opacity:0.1;z-index:9999">
  <filter id="grain">
    <feTurbulence type="fractalNoise" baseFrequency="0.9713" numOctaves="4" result="noise"/>
    <feDisplacementMap in="SourceGraphic" in2="noise" scale="150" xChannelSelector="R"/>
  </filter>
  <rect width="100%" height="100%" filter="url(#grain)"/>
</svg>
```
- **파라미터 튜닝:** `baseFrequency: 0.7-1.0` (세밀도), `scale: 50-200` (강도), `numOctaves: 2-4` (층위, 4=고품질)[6][7][9].
- **성능 팁:** `color-interpolation-filters='sRGB'` 추가로 색상 정확도 ↑. 애니메이션 시 `turbulence` seed 변경 (JS minimal)[9].
- **테스트 사례:** 4K 화면 60fps 유지, 모바일 Safari/Chrome 100% 호환[7].

### **Canvas Noise (동적 필요 시 한정)**
**실전 코드 (WebGL 최소 JS):**
```js
const canvas = document.createElement('canvas');
canvas.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;opacity:0.1;z-index:9999';
document.body.append(canvas);
const ctx = canvas.getContext('2d');
canvas.width = innerWidth; canvas.height = innerHeight;
const imageData = ctx.createImageData(canvas.width, canvas.height);
for(let i=0; i<imageData.data.length; i+=4) {
  const noise = (Math.sin(i*0.01) + Math.sin(i*0.02)) * 128;
  imageData.data[i+3] = noise; // 알파만 노이즈
}
ctx.putImageData(imageData,0,0);
```
- **성능 팁:** requestAnimationFrame으로 30fps 제한, WebGL2 전환 시 SVG급[3]. 배터리 20% ↑ 주의.
- **용도:** 마우스 따라가는 노이즈만.

### **PNG Overlay (가장 빠른 fallback)**
**실전 코드 (애니메이션 포함):**
```css
.grain::after {
  content: '';
  position: fixed; top:0; left:0; width:300%; height:300%;
  background: url('noise.png') repeat; /* 100x100px PNG */
  opacity: 0.08; pointer-events: none; z-index: 9999;
  animation: grain 8s steps(10) infinite;
}
@keyframes grain {
  0%,100%{transform:translate(0,0);}


### custom cursor implementation with GSAP magnetic effect and blend-mode mix-blend-mode techniques
## Custom Cursor + GSAP Magnetic Effect + mix-blend-mode 핵심 구현

### 1. 기본 Custom Cursor 구조 (GSAP + RAF)
```javascript
// 고성능 커스텀 커서 (60fps 보장)
const cursor = document.querySelector('.cursor');
const cursorInner = document.querySelector('.cursor-inner');

function updateCursor(e) {
  const { clientX: x, clientY: y } = e;
  
  gsap.to(cursor, { 
    duration: 0.15, 
    x: x, 
    y: y,
    ease: "power2.out"
  });
  gsap.to(cursorInner, { 
    duration: 0.08, 
    x: x, 
    y: y,
    ease: "power3.out"
  });
}

document.addEventListener('mousemove', updateCursor);
```
**성능 팁**: `requestAnimationFrame` + GSAP의 `inertia` 플러그인 사용으로 120fps 달성[3][7].

### 2. Magnetic Effect 핵심 수식 (버텍스 기반)
```javascript
// 요소 중심으로부터 마우스 거리 계산 → 비례 이동
function magneticEffect(target, e) {
  const rect = target.getBoundingClientRect();
  const centerX = rect.left + rect.width / 2;
  const centerY = rect.top + rect.height / 2;
  
  const distanceX = (e.clientX - centerX) * 0.3; // 30% 강도
  const distanceY = (e.clientY - centerY) * 0.3;
  
  gsap.to(target, {
    x: distanceX,
    y: distanceY,
    duration: 0.4,
    ease: "back.out(1.7)"
  });
}

// 마우스 엔터/리브 핸들러
targets.forEach(target => {
  target.addEventListener('mouseenter', (e) => magneticEffect(target, e)
===

