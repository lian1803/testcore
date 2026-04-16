
=== 전문 지식 (세계 최고 수준 자료 기반) ===

### GSAP 3.12.5 ScrollTrigger advanced patterns: pinning, scrub, batch, timeline synchronization with Lenis smooth scroll
### **GSAP 3.12.5 ScrollTrigger 고급 패턴: Pinning, Scrub, Batch, Timeline + Lenis 동기화**

GSAP 3.12.5에서 **ScrollTrigger**는 스크롤 기반 애니메이션의 핵심. Pinning(고정), Scrub(스크롤 연동), Batch(배치 처리), Timeline 동기화로 복잡한 스크롤 시퀀스 구현. Lenis(스무스 스크롤)와 결합 시 `scrollerProxy`로 완벽 동기화[1][2][3].

#### **1. Pinning: 요소 고정 (Advanced Lock-in)**
- **핵심**: `pin: true`로 요소를 스크롤 중 고정. 자동 `pinSpacing`으로 후속 요소 밀어냄 (비활성화: `pinSpacing: false`).
- **실전 코드** (500px 동안 고정 + 애니메이션):
```javascript
let tl = gsap.timeline({
  scrollTrigger: {
    trigger: '.container',
    pin: true,          // 고정 시작
    start: 'top top',   // 뷰포트 top 도달 시
    end: '+=500',       // 500px 스크롤 후 해제
    scrub: 1            // 1초 지연 스무딩
  }
});
tl.from('.box p', { scale: 0.3, rotation: 45, autoAlpha: 0 })
  .to('.box', { rotation: 360 });
```
- **팁**: 다중 pinning 가능 (같은 요소 여러 지점 고정). 3.12+ `clamp("top bottom")`으로 오버스크롤 방지[1][2].
- **성능**: `anticipatePin: 1`로 미리 padding 계산 (긴 페이지 필수)[1].

#### **2. Scrub: 스크롤 1:1 연동 (Smooth Catch-up)**
- **핵심**: `scrub: true` (즉시), `scrub: 1` (1초 catch-up), `scrub: {start: 0.5, end: 2}` (가변 스무딩).
- **실전 코드** (부드러운 x 이동):
```javascript
gsap.to('.box', {
  x: 500,
  scrollTrigger: {
    trigger: '.box',
    start: 'top center',
    end: 'bottom top',
    scrub: 1.5  // 1.5초 catch-up (자연스러움)
  }
});
```
- **고급**: `getVelocity()`로 스크롤 속도 기반 snap. `snap: 0.1` (10% 단위) 또는 `snap: [0, 0.25, 0.5, 0.75, 1]`[1][3].
- **3.12 이슈 피하기**: 페이지 리프레시 시 `ScrollTrigger.refresh()` 호출 (scrollTop != 0일 때 브레이크)[5].

#### **3. Batch: 다중 요소 배치 처리 (성능 최적화)**
- **핵심**: `ScrollTrigger.batch()`로 10+ 요소 스크롤 트리거 묶음. RAF(60fps) 단일화로 CPU 80% 절감.
- **실전 코드** (뷰포트 진입 시 stagger 페이드인):
```javascript
ScrollTrigger.batch('.fade-item', {
  onEnter: batch => gsap.from(batch, { opacity: 0, y: 50, stagger: 0.1 }),
  onEnterBack: batch => gsap.from(batch, { opacity: 0, y: 50, stagger: 0.1 }),
  onLeave: batch => gsap.to(batch, { opacity: 0, y: -50, stagger: 0.1 }),
  start: 'top 80%',
  end: 'bottom 20%',
  markers: true  // 디버그용
});
```
- **팁**: 50+ 이미지/텍스트에 필수. `matchMedia`로 반응형 batch (모바일/데스크톱 분리)[3].

#### **4. Timeline 동기화: 복합 시퀀스 (Choreographed Scroll)**
- **핵심**: Timeline 전체에 ScrollTrigger 부여. Label snap으로 섹션 점프.
- **실전 코드** (Pin + Multi-step):
```javascript
let tl = gsa

### Lenis smooth scroll integration with GSAP ScrollTrigger RAF loop override and scroll event normalization
## 핵심 통합 코드 (Vanilla JS)

```javascript
// 1. Lenis 초기화
const lenis = new Lenis({
  duration: 1.2,
  easing: t => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
  direction: 'vertical',
  smooth: true,
  smoothTouch: false,
  touchMultiplier: 2
});

// 2. **중요: 기존 RAF loop 완전 제거**
// ❌ 이 코드 삭제
/*
function raf(time) {
  lenis.raf(time)
  requestAnimationFrame(raf)
}
requestAnimationFrame(raf)
*/

// 3. GSAP + ScrollTrigger + Lenis 싱글 RAF 루프 (유일한 RAF)
gsap.registerPlugin(ScrollTrigger);

lenis.on('scroll', ScrollTrigger.update);
gsap.ticker.add(time => {
  lenis.raf(time * 1000);
});
gsap.ticker.lagSmoothing(0); // 지연 제거[1][2][5]
```

## RAF Loop Override 원리 (성능 300%↑)

| 문제 | 원인 | 해결 |
|------|------|------|
| **Direction Flip (-1 ↔ 1)** | Dual RAF (Lenis RAF + GSAP RAF) 충돌[1] | **GSAP ticker 단일화** - Lenis RAF만 GSAP 루프에서 호출[1][5] |
| **Lagging** | 다중 RAF 오버헤드 | **Single RAF**: GSAP이 모든 애니메이션 통합 관리[2][5] |
| **Header Fade Glitch** | ScrollTrigger update 타이밍 불일치 | `lenis.on('scroll', ScrollTrigger.update)` + `lagSmoothing(0)`[1] |

## Scroll Event Normalization (정규화)

```javascript
// Lenis scroll 이벤트 → GSAP 표준화
lenis.on('scroll', ({ scroll, limit, velocity, direction, progress }) => {
  // 1. ScrollTrigger 자동 업데이트
  ScrollTrigger.update();
  
  // 2. 커스텀 스크롤 값 정규화 (0~1)
  const normalizedScroll = scroll / limit; // 0~1 범위
  
  // 3. Direction 안정화 (flipping 방지)
  const stableDirection = Math.sign(velocity) || direction;
  
  // 사용 예: Pinning + Progress
  gsap.to('.header', {
    opacity: 1 - normalizedScroll,
    
===

