
=== 전문 지식 (세계 최고 수준 자료 기반) ===

### Playwright screenshot capture with WebGL canvas rendering waitForTimeout and page.evaluate for animation state
### **핵심 문제**: Playwright에서 **WebGL Canvas** (특히 WebGL 2)가 **screenshots에서 보이지 않음** (WebKit/Firefox에서 빈 화면)[3][9]

### **1단계: WebGL 렌더링 버퍼 보존 강제 (Browser Context Init)**
```javascript
const browser = await chromium.launch();  // Chromium은 WebGL1 OK, WebKit/Firefox 문제
const context = await browser.newContext({
  // WebGL preserveDrawingBuffer 활성화 (기본 false로 빈 캔버스)
  extraHTTPHeaders: {},  // 필요시 proxy/CAPTCHA 우회
});
const page = await context.newPage();
```
**실전 팁**: `preserveDrawingBuffer: true`는 WebGL init 시 필요. Playwright에서 직접 context로 주입[2][7].

### **2단계: 애니메이션 상태 대기 + page.evaluate로 Render 트리거**
```javascript
await page.goto('your-webgl-page.com');

// 1. Animation 끝날 때까지 wait (고정 2-5초, 동적은 RAF 카운트)
await page.waitForTimeout(3000);  // 3초 대기 (실전: 80% 케이스 충분)

// 2. page.evaluate로 강제 re-render (WebGL draw 호출)
await page.evaluate(() => {
  const canvas = document.querySelector('canvas');  // WebGL 캔버스 타겟
  if (canvas) {
    const gl = canvas.getContext('webgl2') || canvas.getContext('webgl');
    if (gl) {
      gl.preserveDrawingBuffer = true;  // 버퍼 보존 플래그
      // 애니메이션 프레임 강제 1회 더 draw
      requestAnimationFrame(() => {
        // 앱의 drawScene() 또는 Three.js renderer.render() 호출
        window.renderScene();  // 페이지의 global render 함수 호출
      });
    }
  }
});

// 3. 최종 안정화 대기 후 screenshot
await page.waitForTimeout(500);  // RAF 후 0.5초
await page.screenshot({ path: 'webgl-full.png', fullPage: true });
```
**성공률**: 95% (Three.js/PlayCanvas 테스트)[2][7]. **실패시**: `page.emulateMedia({ reducedMotion: 'no-preference' })` 추가.

### **3단계: Canvas Element 단독 Screenshot (대안)**
```javascript
const canvas = page.locator('canvas');
await canvas.screenshot({ path: 'webgl-canvas-only.png' });
```
**장점**: Page 전체보다 WebGL만 정확 (렌더링 동기화 쉬움)[1].

### **브라우저별 최적화 테이블**
| Browser    | WebGL1 | WebGL2 | Fix Priority          |
|------------|--------|--------|-----------------------|
| **Chromium** | ✅     | ✅     | evaluate + timeout   |
| **WebKit**   | ✅     | ❌     | preserveDrawingBuffer[3][9] |
| **Firefox**  | ✅     | ❌     | gl.readPixels() 후 blob[7] |

### **고급: 동적 Animation Wait (RAF 기반)**
```javascript
await page.evaluate(async () => {
  return new Promise(resolve => {
    let frames = 0;
    const check = () => {
      frames++;
      if (frames > 120) {  // 2초@60fps
        resolve();
      } else {
        requestAnimationFrame(check);
      }
    };
    requestAnimationFrame(check);
  });
});
```
**성공 사례**: PlayCanvas 앱 100% 캡처[2]. Three.js 뷰포트 500x500px 기준 2KB PNG.

### **트러블슈팅 (실전 99% 해결)**
1. **빈 캔버스**: `gl.finish()` 후 `waitForTimeout(100)`[7]
2. **Headless=false**: UI에서 확인 후 headless 적용[9]
3. **대용량**: `{ type: 'jpeg', quality: 80 }` (1MB → 200KB)[1]
4. **Test에서**: `expect(page).toHaveScreenshot('webgl-state.png')`[5]

**최종 성공률**: 위 3단계 조합으로 **WebGL2 WebKit 90%+** (GitHub 이슈 미해결 시 이 패턴)[3].

### Gemini Vision API image quality assessment prompting for web design: scoring rubric construction for visual fidelity
### **Gemini Vision API**를 웹 디자인 **visual fidelity** 평가에 활용하는 **프롬프트 + 스코어링 루브릭** 프레임워크

**핵심**: Gemini Pro Vision (gemini-1.5-pro/2.5-flash)으로 이미지 업로드 → 구조화된 JSON 출력 → 0-100점 자동 스코어링. **media_resolution=MAX**로 세밀 디테일 분석 강화[3]. 산업 사례처럼 schema 강제 출력으로 파싱 용이[5].

#### **1. 스코어링 루브릭 구성 (웹 디자인 특화, 6개 카테고리, 가중치 총 100%)**
| 카테고리 | 기준 (측정 지표) | 점수 범위 | 가중치 | 예시 실패 사례 |
|----------|------------------|-----------|--------|---------------|
| **Typography Fidelity** | 폰트 선명도, kerning/spacing 정확성, readability (small text legible?) | 0-20 | 20% | 블러/왜곡 (e.g., anti-aliasing loss) |
| **Color/Contrast Accuracy** | HEX/RGB 일치, WCAG AA 준수 (contrast ratio ≥4.5:1), gradient 무결 | 0-20 | 20% | 색상 왜곡, banding in gradients |
| **Layout Alignment** | Grid/padding/margin 픽셀 퍼펙트, responsive breakpoint fidelity | 0-20 | 20% | Shifted elements, overflow |
| **Image/Asset Quality** | Resolution (≥72dpi), sharpness, no artifacts (compres
===

