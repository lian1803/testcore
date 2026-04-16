---
paths:
  - "**/*.html"
  - "design_system/**"
  - "team/**/dist/**"
---
# 웹 페이지 출력 기준

## Step 0: design_system/INDEX.md 먼저 읽어라 (필수)
1. 프로젝트에 맞는 배경 셰이더 선택 (LiquidChrome, Silk, Aurora 등)
2. 텍스트 애니메이션 선택 (SplitText, BlurText, DecryptedText 등)
3. 커서 스타일 선택
4. 해당 소스 코드(.jsx) 읽고 vanilla JS/WebGL로 포팅해서 써라

## Step 1: design_router 실행 (자동)
```python
from core.design_router import route
from core.reference_analyzer import analyze
plan = route("[프로젝트 설명]")
refs = analyze("[프로젝트 설명]", plan)
```

## Step 2: 소스 코드 기반 구현
- 배경: `components/react-bits/src/content/Backgrounds/` 셰이더 포팅
- 텍스트: `components/react-bits/src/content/TextAnimations/` 로직 포팅
- 카드/UI: `components/uiverse/Cards/`, `components/uiverse/Buttons/` 참고
- DESIGN.md: `design-systems/design-md/{기업}/` 유사 기업 토큰 참고

## 필수 체크리스트
- GLSL 셰이더 배경 (기본 파티클 금지)
- Lenis smooth scroll (기본 스크롤 금지)
- 커스텀 커서 (dot + lagging ring 또는 BlobCursor)
- Split text reveal (글자/라인 단위 등장)
- clamp() 반응형 타이포그래피 (고정 px 금지)
- SVG grain overlay
- Horizontal scroll 또는 parallax (수직만은 금지)
- 카운트업 숫자 애니메이션 (숫자 섹션 있으면)
- 검증된 조합: `design_system/demo/showcase.html`

## SaaS 구조 기본값
- 마케팅/랜딩/히어로/가격 → Claude 직접 HTML (셰이더 + 풀 모션)
- 대시보드/로그인/설정 → Stitch → FE 에이전트

## 절대 금지
- design_system/ 안 보고 시작하는 것
- Three.js 파티클 + 와이어프레임 구 + 퍼플 그라데이션 (기본값이라 매번 같음)

## 상세 디자인 규칙
`.claude/skills/frontend-design.md` 참고 (파티클, GLSL, 색상, 애니메이션 상세)
