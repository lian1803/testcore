# /kling-hero — fal.ai Kling 영상 히어로 페이지 자동 생성

리안이 "디자인 하나 돌려줘" / "히어로 하나 뽑아줘" / "키링으로 만들어" 등으로 말하면 이 플로우 실행.

---

## Step 1: 컨셉 확인

리안이 컨셉을 말했으면 그대로 사용.  
말 안 했으면 **한 줄만** 물어봐:
> "어떤 컨셉이야? (예: 화원, 도시야경, 설원, 바다)" 

컨셉이 확정되면 바로 Step 2로.

---

## Step 2: 스토리 4컷 프롬프트 설계

컨셉을 기반으로 **시간 흐름 스토리** 4챕터를 설계:

| 챕터 | 시간대 | 촬영 기법 | 분위기 |
|------|--------|-----------|--------|
| 0 | 골든아워/전경 | 카메라 드리프트 와이드 | 웅장, 시작 |
| 1 | 새벽/클로즈업 | 매크로, 이슬/디테일 | 섬세, 감성 |
| 2 | 낮/이동 | 워킹샷, 길/공간 | 여유, 탐색 |
| 3 | 황혼/마법 | 실루엣, 반딧불/별빛 | 마무리, 여운 |

각 프롬프트 끝에 반드시 추가:
```
Cinematic 16:9, ultra HD, dreamy atmosphere, no people, no text.
```

Negative prompt (공통): `people, text, logos, dark, horror, blur, distortion`

---

## Step 3: fal.ai Kling 영상 생성

**도구**: `mcp__fal-ai__generate_video`  
**모델**: `fal-ai/kling-video/v2.5-turbo/pro/text-to-video`  
**설정**: `aspect_ratio: "16:9"`, `duration: 5`

> ⚠️ 병렬 생성 시 타임아웃 발생 가능. 순서대로 하나씩 생성하고 URL 수집.  
> 타임아웃 나면 재시도 1회. 재시도도 실패하면 해당 챕터 건너뛰고 3챕터로 진행.

생성된 URL 4개(또는 3개) 메모.

---

## Step 4: 챕터 텍스트 생성

컨셉에 맞는 한국어 카피 4세트:
- `hero__eyebrow`: 영문 브랜드 무드 태그라인 (예: `Spring Collection 2026`)
- `hero__title`: 2줄 시적 한국어 제목 (마지막 줄 `<em>`으로 이탤릭)
- `chapter__sub`: 2줄 감성 설명 문구
- CTA 버튼: 첫 챕터에만 2개 (주요 액션 / 보조 액션)

---

## Step 5: HTML 히어로 페이지 생성

아래 구조를 반드시 지켜서 HTML 작성:

### 핵심 구조
```
hero (position: relative, 100vw/100vh, overflow: hidden)
├── video-layer × N (position: absolute, inset 0, object-fit cover)
│   └── .active → opacity: 1 (transition: opacity 1.6s ease-in-out)
├── hero__overlay (그라데이션: 상단 0.3→중앙 0.05→하단 0.88)
├── petals (꽃잎/컨셉 파티클, z-index 1)
├── logo (position: absolute, top 36px, 가운데)
├── nav (position: absolute, top 32px, 우측)
├── hero__content (position: absolute, inset 0, flex column, center)
│   ├── hero__eyebrow (골드, 작은 대문자, 상단 fade-up)
│   └── chapters-wrapper (position: relative, height: 360px)
│       └── chapter × N (position: absolute, inset 0, flex center)
│           ├── hero__title (clamp 44px~96px, serif, 이탤릭 em)
│           ├── chapter__sub (sans-serif, 0.7 opacity)
│           └── hero__cta (챕터 0만, 버튼 2개)
└── chapters-nav (position: absolute, bottom 40px, 가운데)
    └── dots (진행바 dot × N, 골드 fill 애니메이션)
```

### 크로스페이드 JS 로직
```js
// 영상 끝나기 1.8초 전 다음 영상 미리 play()
// ended 이벤트에서 next 비디오 .active 추가 → 1.6s 후 prev .active 제거
// 챕터 텍스트: prev .active 제거 → 400ms 후 next .active 추가
// dot 진행바: CSS var(--dot-duration) + reflow 강제로 재시작
```

### 색상 기본값 (컨셉에 맞게 조정)
```css
--cream: #fdf6ee  /* 메인 텍스트 */
--gold:  #c9a96e  /* 포인트, 도트, eyebrow */
--blush: #e8b4a0  /* 이탤릭 em */
--dark:  #1a1a18  /* 배경, 오버레이 */
```

---

## Step 6: 저장 & 열기

저장 경로: `test/디자인/YYYY-MM-DD_{컨셉}_hero.html`  
생성 후 바로: `start "{경로}"` 로 브라우저 오픈.

---

## 완료 보고 형식

```
영상 N개 생성 완료.
→ test/디자인/YYYY-MM-DD_{컨셉}_hero.html 저장
챕터: [챕터0 제목] / [챕터1] / [챕터2] / [챕터3]
```
