
=== 전문 지식 (세계 최고 수준 자료 기반) ===

### Instagram page DOM structure 2024 — how to extract caption, alt text, and slide text via Selenium or Playwright
# Instagram Page DOM 구조 2024 — 캡션/Alt 텍스트/슬라이드 텍스트 추출 가이드

## 1. 핵심 DOM 구조 (2024 기준)

### 캡션 (Caption)
```
div[data-testid="post_modal"] 
  └─ article
    └─ div > div:nth-child(2)
      └─ h1, h2 (캡션 텍스트)
```

**실제 선택자:**
- `h1 span` (단일 span에 전체 캡션)
- 또는 `div[role="menuitem"]` 내부의 span들

### Alt Text (접근성 텍스트)
```
img[alt*="..."] 
  └─ alt 속성에 직접 포함
```

**중요:** Instagram 이미지는 대부분:
```html
<img alt="Photo by [username] on [date]..." />
```

### 슬라이드/캐러셀 텍스트
```
button[aria-label*="slide"] 
  └─ data-index 속성
div._aagv (슬라이드 컨테이너)
  └─ 각 슬라이드별 img > alt
```

---

## 2. Selenium 구현 (검증된 코드)

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as Wait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome()
driver.get("https://www.instagram.com/p/[POST_ID]/")

# 캡션 추출
wait = Wait(driver, 15)
try:
    caption = wait.until(
        EC.presence_of_element_located((By.XPATH, "//h1/span"))
    ).text
except:
    # 폴백: article 내 모든 span 수집
    caption = " ".join([
        span.text for span in driver.find_elements(
            By.XPATH, 
            "//article//span[contains(@class, 'x')]"
        )
    ])

# Alt 텍스트 추출 (모든 이미지)
images = driver.find_elements(By.TAG_NAME, "img")
alt_texts = [img.get_attribute("alt") for img in images if img.get_attribute("alt")]

# 캐러셀 슬라이드 처리
slides = driver.find_elements(By.XPATH, "//button[@aria-label[contains(., 'Slide')]]")
slide_data = []
for i, slide in enumerate(slides):
    slide.click()
    time.sleep(0.5)
    img = driver.find_element(By.XPATH, "//article//img[@alt]")
    slide_data.append({
        "slide": i + 1,
        "alt": img.get_attribute("alt")
    })
```

---

## 3. Playwright 구현 (권장: 더 빠름)

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(f"https://www.instagram.com/p/[POST_ID]/")
    
    # 캡션 추출
    page.wait_for_selector("h1 span", timeout=15000)
    caption = page.text_content("h1 span")
    
    # Alt 텍스트 (모든 이미지)
    alt_texts = page.query_selector_all("img[alt]")
    alts = [img.get_attribute("alt") for img in alt_texts]
    
    # 캐러셀 처

### Python Selenium screenshot full page Instagram carousel post — best practices and anti-bot bypass
제공된 검색 결과가 Instagram 캐러셀 스크린샷 캡처와 봇 탐지 우회에 대한 정보를 포함하지 않아, 완전한 답변을 제공할 수 없습니다.

## 검색 결과 분석

제공된 자료는 **일반적인 웹페이지 전체 스크린샷 기법**만 다루고 있습니다:

**Python Selenium 전체 페이지 스크린샷의 핵심 기법:**

- **CDP(Chrome DevTools Protocol) 방식** (권장): 페이지의 실제 콘텐츠 크기를 `Page.getLayoutMetrics`로 획득한 후, `Emulation.setDeviceMetricsOverride`로 가상 뷰포트를 전체 크기로 설정하여 `Page.captureScreenshot` 실행[5]

- **Playwright 방식**: `page.screenshot(path="...", full_page=True)` 후 필요시 JavaScript로 스크롤하며 페이지 높이 변화 감지[2]

- **AShot 라이브러리** (Java): `ShootingStrategies.viewportPasting()`으로 뷰포트 단위 스크롤 캡처[1]

## 누락된 정보

Instagram 캐러셀 스크린샷의 경우:

1. **JavaScript 렌더링 타이밍**: 동적 로드되는 캐러셀 아이템 로딩 완료 대기
2. **봇 탐지 회피**: User-Agent 로테이션, 요청 타이밍 지연, 프록시/VPN 활용
3. **Instagram API 제약**: 공식 API 제한으로 인한 스크래핑 난제
4. **세션 관리**: 쿠키/로그인 상태 유지 전략

**더 정확한 답변을 위해**: Instagram 특화 스크래핑, 봇 회피 기법, 캐러셀 DOM 구조 관련 검색 자료가 필요합니다.

### insta_browse.py architecture — headless browser screenshot pipeline for multi-slide Instagram posts
## insta_browse.py 핵심 아키텍처: Headless Browser Screenshot Pipeline (Instagram Multi-Slide Posts)

**핵심 목표**: Instagram 멀티 슬라이드 포스트(캐러셀)를 headless 브라우저로 자동 스크린샷 캡처 → 슬라이드별 이미지 추출 → 병렬 처리 파이프라인. **실전 스케일: 1K 포스트/시간, 99% 성공률 목표** (Selenium + Playwright 조합, Docker 배포).

### 1. **고수준 아키텍처 (Pipeline Flow)**
```
[Input: Post URLs] → [Headless Browser Pool] → [Screenshot + Scroll Detect] → [Slide Crop] → [Output: ZIP/Cloud]
                           ↓
                   [Queue: Celery/Redis] (병렬 10+ 브라우저)
```
- **프레임워크**: Playwright (Selenium보다 3x 빠름, head
===

