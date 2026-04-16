# 디자인 자동화 레이어 (Design Automation)

> 3개의 자동화 도구로 프로젝트 설명 → 디자인 전략 → 시각 품질 평가까지 완전 자동화.

**구현 날짜:** 2026-04-09  
**상태:** 프로덕션 준비 완료

---

## 개요

디자인 작업을 3단계 파이프라인으로 자동화합니다:

```
1️⃣  디자인 라우터 (design_router.py)
   프로젝트 텍스트 설명 → 디자인 전략 결정 (3D레벨, 스타일, 상호작용 등)

2️⃣  장면 명세 템플릿 (templates/SCENE.md)
   라우터 결과를 기반으로 3D 장면 상세 스펙 작성

3️⃣  시각 품질 평가 루프 (visual_qa_loop.py)
   웹사이트 스크린샷 + Gemini Vision → 자동 평가 (5가지 기준)
```

---

## 1. 디자인 라우터 (design_router.py)

### 목적
프로젝트 설명만으로 디자인 방향을 자동 결정.
보통 PM이나 CFO가 "우리 제품은 ___"이라고 설명하면 → 라우터가 **스타일, 3D 레벨, 상호작용 밀도** 등을 추천.

### 함수
```python
from core.design_router import route, format_design_plan

# 프로젝트 설명만 제공
description = "우리 B2B SaaS는 분석 대시보드입니다. 타겟은 마케팅 VP..."

# 자동 분석 (Claude Sonnet)
plan = route(description)

# 출력
print(format_design_plan(plan))
```

### 출력 (design_plan dict)
```python
{
    "site_type": "saas_dashboard",     # 또는 product_landing, brand_experience, content_site
    "3d_level": "light",                # 또는 none, hero_only, immersive
    "style_family": "clean_futuristic",  # 또는 bold_expressive, minimal_elegant, playful_dynamic
    "interaction_density": "medium",     # 또는 low, high
    
    "reference_sources": [             # 디자인 시스템에서 참고할 것
        "magicui",
        "uiverse",
        "react-bits"
    ],
    
    "stitch_scope": [                  # Stitch(2D UI)가 담당할 영역
        "dashboard",
        "forms",
        "cards"
    ],
    
    "3d_scope": [                      # 3D가 들어갈 영역
        "hero",
        "background"
    ],
    
    "reasoning": {                     # 왜 이렇게 결정했는가
        "site_type_reason": "데이터 분석 기반 웹앱...",
        "3d_level_reason": "B2B는 신뢰감이 중요하므로...",
        "design_philosophy": "..."
    }
}
```

### 의사 결정 로직 (Claude가 사용)

| 프로젝트 특성 | site_type | 3d_level | style_family |
|-------------|-----------|----------|--------------|
| 데이터 대시보드 / CRM / BI | saas_dashboard | none ∼ light | clean_futuristic |
| 제품 판매 랜딩 (B2C) | product_landing | hero_only | bold_expressive |
| 브랜드 / 포트폴리오 | brand_experience | light ∼ immersive | minimal_elegant |
| 뉴스 / 콘텐츠 | content_site | none ∼ light | varies |

---

## 2. 장면 명세 템플릿 (templates/SCENE.md)

### 목적
라우터의 결정값을 **구현 가능한 상세 스펙**으로 변환.
3D 엔지니어(Three.js) 또는 프론트엔드가 이 문서를 읽고 3D 장면을 만들 수 있어야 함.

### 파일 위치
```
company/templates/SCENE.md
```

### 주요 섹션
1. **기본 정보** — 사이트 타입, 3D 레벨, 스타일, 상호작용 밀도
2. **Hero 장면 명세** — 배경, 오브젝트, 조명, 카메라 위치
3. **스크롤 비트** — 페이지 스크롤(0~100%)에 따른 애니메이션
4. **모션 예산** — Draw Call, 텍스처, 애니메이션 수 제한
5. **성능 예산** — FPS, 로딩 시간, 메모리 제약
6. **2D/3D 분기** — Stitch가 담당할 영역 vs 3D가 담당할 영역
7. **컴포넌트 레퍼런스** — 사용할 UI 컴포넌트 (design_system/)
8. **구현 체크리스트** — Three.js, 반응형, 접근성 등

### 사용 방식
```bash
# 1. 프로젝트 폴더에 템플릿 복사
cp templates/SCENE.md team/{프로젝트명}/SCENE.md

# 2. 기본 정보 채우기 (design_router 결과값 붙여넣기)
vi team/{프로젝트명}/SCENE.md

# 3. 3D 엔지니어가 상세 스펙 추가
# (배경 설명, 오브젝트 명세, 스크롤 비트, 예산 등)
```

### 예시 (B2B SaaS)
```markdown
### 1.1 사이트 타입
- [x] SaaS Dashboard

### 1.2 3D 레벨
- [x] Light (배경 입자만)

### 2.1 배경 환경
유형: 입자 시스템

설명:
- 진한 파란색 그래디언트 (상단: #1a1a2e, 하단: #0f3460)
- 흰색 입자 400개, 천천히 부유
- 드로우콜: 1개
- 성능: 60 FPS 유지

### 2.2 카메라 (스크롤 비트)
- 0%: 위치 (0, 0, 5), 입자 정상 속도
- 25%: 입자 가속, 카메라 약간 상승
- 50%: 입자 피크 속도, 카메라 계속 상승
- 75%: 입자 감속, 다음 섹션 준비
- 100%: 입자 애니메이션 종료, 다음 섹션 표시

### 4. 모션 예산
| 항목 | 제한값 | 현재값 | 상태 |
|------|--------|--------|------|
| 총 Draw Calls | 10 | 1 | 🟢 |
| 활성 오브젝트 | 20 | 1 | 🟢 |
| 애니메이션 개수 | 15 | 2 | 🟢 |
```

---

## 3. 시각 품질 평가 루프 (visual_qa_loop.py)

### 목적
완성된 웹사이트를 스크린샷 → Gemini Vision으로 자동 평가.
5가지 기준으로 0~100점 채점, 기준 미달시 개선 제안 제공.

### 함수
```python
from core.visual_qa_loop import run_qa, format_qa_result

# URL 또는 HTML 파일로 평가
result = run_qa(
    url_or_path="https://example.com",  # 또는 "./dist/index.html"
    scene_md_path="team/프로젝트명/SCENE.md",
    max_iterations=3  # 최대 3번 평가 시도
)

# 결과 출력
print(format_qa_result(result))
```

### 평가 기준 (각 20점)

| 기준 | 정의 | 좋은 예 | 나쁜 예 |
|------|------|--------|--------|
| **레퍼런스 유사도** | SCENE.md 명세가 얼마나 정확히 구현되었는가 | 배경, 3D 오브젝트, 조명이 계획과 일치 | 명세와 전혀 다른 배경, 오브젝트 부재 |
| **여백/밀도** | 공간 활용이 자연스러운가? | 요소들 사이 적절한 호흡 | 너무 붐비거나 텅 빔 |
| **타이포그래피** | 글꼴, 크기, 색상 대비가 일관적인가? | 계층적 폰트 사이즈, 충분한 대비 | 일관성 없는 폰트, 낮은 대비 |
| **모션** | 애니메이션이 과하거나 산만한가? | 부드러운 스크롤, 불필요한 움직임 없음 | 깜박임, 불자연스러운 속도 |
| **3D/2D 경계** | 3D 영역과 2D UI 경계가 자연스러운가? | 조화로운 깊이감 | 어색한 오버레이, 분리된 느낌 |

### 점수 해석

| 점수 | 해석 | 액션 |
|------|------|------|
| 85~100 | 통과 | 배포 가능 |
| 70~84 | 조건부 통과 | 사소한 수정 후 배포 |
| 50~69 | 재검토 | 주요 항목 수정 필요 |
| <50 | 불통과 | 재설계 필요 |

### 출력 (result dict)
```python
{
    "score": 78,                    # 0~100
    "passed": False,                # 85점 이상인가?
    "iterations": 2,                # 몇 번 평가했는가
    
    "issues": [
        "배경 입자 밀도가 과하다",
        "텍스트 색상 대비가 낮다",
        "스크롤 애니메이션이 부자연스럽다"
    ],
    
    "suggestions": [
        "입자 밀도를 300~400개로 줄여라",
        "배경 어두운 톤에서 텍스트 색상 밝기 증가",
        "스크롤 속도를 0.5배로 느리게"
    ],
    
    "summary": "전반적으로 설계는 좋으나 3가지 항목 개선 필요...",
    
    "history": [
        {"iteration": 1, "score": 72, "issues": [...]},
        {"iteration": 2, "score": 78, "issues": [...]}
    ]
}
```

---

## 사용 시나리오

### 시나리오 1: 새 프로젝트 시작

```bash
# 1단계: 디자인 전략 결정
python company/core/design_router.py

# 또는 코드에서
from core.design_router import route

desc = """
우리는 인공지능 기반 마케팅 자동화 플랫폼을 만듭니다.
타겟: CMO, 마케팅 디렉터
핵심: 멀티채널 캠페인 자동 최적화, 예측 모델
경쟁사: HubSpot, Marketo 대비 3배 빠름
"""

plan = route(desc)
# 출력: {"site_type": "saas_dashboard", "3d_level": "light", ...}

# 2단계: SCENE.md 작성
cp templates/SCENE.md team/marketing_ai/SCENE.md
# 개발자가 plan을 기반으로 SCENE.md 상세 스펙 추가

# 3단계: 페이지 개발
# FE 에이전트가 Stitch로 UI 만들고
# 3D 엔지니어가 Three.js로 배경 입자/애니메이션 만듦

# 4단계: 품질 평가
python visual_qa_loop.py https://demo.marketing-ai.com team/marketing_ai/SCENE.md
# 또는 로컬 개발 빌드
python visual_qa_loop.py ./dist/index.html team/marketing_ai/SCENE.md
```

### 시나리오 2: 기존 페이지 재평가

```bash
# 배포 전 마지막 품질 체크
python visual_qa_loop.py https://production.example.com team/project/SCENE.md

# 결과: score 82 (조건부 통과)
# 개선 사항:
# - 텍스트 크기 조정 (접근성)
# - 스크롤 모션 부드럽게

# 수정 후 다시 평가
python visual_qa_loop.py https://production.example.com team/project/SCENE.md

# 결과: score 87 (통과) ✅ → 배포
```

---

## 기술 스택

| 파일 | 용도 | AI 모델 | 라이브러리 |
|------|------|--------|----------|
| **design_router.py** | 전략 결정 | Claude Sonnet | anthropic SDK |
| **SCENE.md** | 명세서 | (템플릿) | (텍스트) |
| **visual_qa_loop.py** | 품질 평가 | Gemini 2.0 Flash | google-generativeai, playwright |

### 환경변수 요구
```
ANTHROPIC_API_KEY=sk-...        # Claude (라우터)
GOOGLE_API_KEY=AIzaSy...        # Gemini (평가)
```

### 선택 의존성
```bash
# 평가 루프를 사용하려면
pip install google-generativeai playwright

# Playwright 첫 사용
playwright install chromium
```

---

## 폴더 구조
```
company/
├── core/
│   ├── design_router.py           ✅ (9.4KB)
│   └── visual_qa_loop.py          ✅ (14KB)
└── templates/
    └── SCENE.md                   ✅ (9.2KB, 템플릿)
```

---

## API 레퍼런스

### design_router.route()

```python
def route(
    project_description: str,
    use_cache: bool = True
) -> dict:
    """
    프로젝트 설명을 분석하고 디자인 전략을 결정합니다.
    
    Args:
        project_description: 프로젝트의 텍스트 설명 (200~500자 권장)
        use_cache: 같은 설명에 대해 캐시 사용 (비용 절감)
    
    Returns:
        {
            "site_type": str,
            "3d_level": str,
            "style_family": str,
            "interaction_density": str,
            "reference_sources": list,
            "stitch_scope": list,
            "3d_scope": list,
            "reasoning": dict
        }
    
    Raises:
        ValueError: API 키 없음
        json.JSONDecodeError: Claude 응답 파싱 실패
    """
```

### visual_qa_loop.run_qa()

```python
def run_qa(
    url_or_path: str,
    scene_md_path: str,
    max_iterations: int = 3,
    headless: bool = True,
    viewport_width: int = 1920,
    viewport_height: int = 1080
) -> dict:
    """
    웹사이트 시각 품질을 자동으로 평가합니다.
    
    Args:
        url_or_path: 평가 대상 URL 또는 로컬 HTML 파일 경로
        scene_md_path: SCENE.md 파일 경로 (평가 기준)
        max_iterations: 최대 평가 반복 횟수 (1~3 권장)
        headless: Playwright 헤드리스 모드
        viewport_width: 스크린샷 가로 (기본 1920)
        viewport_height: 스크린샷 세로 (기본 1080)
    
    Returns:
        {
            "score": int (0~100),
            "passed": bool,
            "issues": list,
            "suggestions": list,
            "iterations": int,
            "history": list
        }
    
    Raises:
        FileNotFoundError: SCENE.md 또는 HTML 파일 없음
        ImportError: playwright/google-generativeai 미설치
    """
```

---

## 비용 추정

| 작업 | 비용 | 횟수 | 월간 비용 |
|------|------|------|----------|
| design_router (1회) | ~$0.02 (Claude Sonnet) | 프로젝트당 1회 | $0.02~0.05 |
| visual_qa_loop (평가 1회) | ~$0.30 (Gemini Vision) | 배포당 2~3회 | $5~10 |
| **월간 합계** | — | 10~20 프로젝트 | ~$50~150 |

---

## 향후 확장

### Phase 2 (예정)
- [ ] 스크롤 애니메이션 자동 생성 (SCENE.md → Three.js 코드)
- [ ] 컬러 팔레트 자동 추천 (이미지 분석)
- [ ] 접근성 자동 검사 (WCAG AA 기준)

### Phase 3 (고급)
- [ ] A/B 테스트 변형 자동 생성
- [ ] 모바일/태블릿 반응형 검증
- [ ] SEO 메타데이터 자동 최적화

---

## 트러블슈팅

### "ANTHROPIC_API_KEY 환경변수가 설정되지 않음"
```bash
# company/.env 확인
ANTHROPIC_API_KEY=sk-ant-...

# 또는 환경 변수 설정
export ANTHROPIC_API_KEY="sk-ant-..."
```

### "playwright 패키지가 설치되지 않음"
```bash
pip install google-generativeai playwright
playwright install chromium
```

### "SCENE.md를 찾을 수 없음"
```bash
# 템플릿 복사
cp templates/SCENE.md team/{프로젝트}/SCENE.md
```

### "Gemini 평가 응답 파싱 실패"
- Gemini API가 JSON이 아닌 텍스트로 응답
- 프롬프트 재시도 (최대 3회)
- 모델을 `gemini-1.5-flash`로 다운그레이드해보기

---

## 참고

- **Claude 모델 선택**: Sonnet (균형), Opus (고정확도, 비용↑)
- **Gemini 모델 선택**: 2.0-flash (빠름, 저비용), 1.5-pro (고정확도)
- **Playwright 성능**: 동기 환경에서도 asyncio로 내부 처리 (블로킹 없음)
- **캐싱**: design_router는 같은 설명에 대해 자동 캐싱하여 비용 절감

---

## 문의 & 개선

- 버그 리포트: core/design_router.py, core/visual_qa_loop.py 이슈 추적
- 기능 요청: CLAUDE.md 또는 리안과 상담
- 성능 최적화: Gemini API 배치 요청 고려

**마지막 업데이트:** 2026-04-09  
**메인테이너:** BE 팀 (정우)
