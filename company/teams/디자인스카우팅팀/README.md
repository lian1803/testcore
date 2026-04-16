# 디자인스카우팅팀 (Design Scouting Team)

한국 B2B 기업을 위한 **주간 웹 디자인 트렌드 및 레퍼런스 스카우팅 팀**.

매주 Awwwards, Dribbble, Lapa.ninja 등에서 최신 디자인 트렌드를 자동 수집하고,
현재 design_system에서 안 쓴 효과들을 추천하는 팀입니다.

---

## 팀 구성 (4명)

| 이름 | 파일 | 역할 | AI/도구 |
|------|------|------|---------|
| **박어워즈** | `박어워즈.py` | 어워드 사이트 스크래핑 (Awwwards, Dribbble, Lapa.ninja, Land-book 캡처) | Playwright / BeautifulSoup |
| **서트렌드** | `서트렌드.py` | 웹 디자인 트렌드 리서치 (Perplexity API로 최신 정보 수집) | Perplexity API |
| **김레포** | `김레포.py` | design_system 효과 스캔 (배경/텍스트 애니메이션, 사용 이력 추적) | Python 파일 스캔 |
| **디자인정보** | `디자인정보.py` | 팀 리더 / 브리핑 생성 (3명의 결과를 Claude로 정리, 보고서 작성) | Claude Haiku API |

---

## 실행 방법

### 1. 단독 실행 (권장)
```bash
cd company
python run_디자인스카우팅팀.py
```

### 2. 직접 파이프라인 실행
```bash
python teams/디자인스카우팅팀/pipeline.py
```

### 3. 개별 스카우트 실행
```bash
python teams/디자인스카우팅팀/박어워즈.py        # 사이트 스크랩
python teams/디자인스카우팅팀/서트렌드.py        # 트렌드 리서치
python teams/디자인스카우팅팀/김레포.py          # 효과 스캔
python teams/디자인스카우팅팀/디자인정보.py      # 브리핑 생성
```

---

## 산출물

### 1. 스크린샷 (screenshots/)
- `awwwards_*.png`, `dribbble_*.png`, `lapa.ninja_*.png`, `land-book_*.png`
- 각 사이트의 홈페이지/주요 페이지 캡처

### 2. 결과 JSON
- `awwwards_results.json` — 4개 어워드 사이트 정보 + 스크린샷 경로
- `trends_results.json` — 3개 트렌드 쿼리 결과
- `repo_results.json` — design_system 효과 목록 + 추천 사항

### 3. 브리핑 문서
- `briefing_YYYY-MM-DD.md` — Claude가 생성한 주간 브리핑 (로컬 저장)
- **보고사항들.md에 자동 추가** — 팀 전체가 확인

---

## 자동화 설정 (Windows Task Scheduler)

매일 아침 9:00에 자동 실행하도록 설정:

### 1. Windows Task Scheduler 열기
```
Win + R → taskschd.msc → Enter
```

### 2. 기본 작업 만들기
- **이름**: "Design Scouting Team Daily"
- **트리거**: "매일 09:00"
- **작업**:
  - **프로그램/스크립트**: `C:\Users\lian1\Documents\Work\core\company\venv\Scripts\python.exe`
  - **인수 추가**: `teams/디자인스카우팅팀/pipeline.py`
  - **시작 위치**: `C:\Users\lian1\Documents\Work\core\company`

### 3. 저장 및 확인
설정 완료 후, 매일 자동으로 돌아갑니다.

---

## 의존성 (venv 이미 포함)

- `anthropic` — Claude API (브리핑 생성)
- `requests` — HTTP 요청 (트렌드 리서치)
- `playwright` — 웹 캡처 (Awwwards, Dribbble 등)
- `beautifulsoup4` — HTML 파싱 (playwright 실패 시 폴백)
- `python-dotenv` — 환경변수 로딩

---

## 팀 개선 사항

### 🔧 추후 확장 가능성
1. **Figma 커뮤니티 스캔** — 최신 디자인 컴포넌트 추가
2. **설계 품질 점수** — Claude Vision으로 캡처 이미지 분석 + 점수화
3. **경쟁사 추적** — 특정 기업들의 사이트 변경사항 자동 감지
4. **색상 팔레트 추출** — 각 레퍼런스 사이트에서 주요 색상 추출
5. **트렌드 분류** — 자동으로 "B2B vs SaaS vs 엔터테인먼트" 분류

---

## 주의사항

### 스크린샷 경로
- `repo_results.json`의 추천 효과들이 비어있을 수 있습니다.
- 이유: design_system 경로 (`C:/Users/lian1/Documents/Work/core/design_system/components/react-bits/src/content/`)가 사용자 환경에서 다를 수 있음
- **수정 방법**: `김레포.py` 34-35줄의 경로를 실제 디렉토리로 변경

### Playwright 설치
Playwright가 설치되지 않으면 자동으로 BeautifulSoup 폴백:
```bash
pip install playwright
playwright install chromium
```

### API 키
`.env` 파일에서 확인:
- `ANTHROPIC_API_KEY` — Claude API
- `PERPLEXITY_API_KEY` — Perplexity API

---

## 팀 성과 추적

매주 `briefing_YYYY-MM-DD.md` 생성 횟수와 내용 품질로 팀 성과 평가:
- **정량 지표**: 트렌드 3개, 사이트 3개 이상 수집
- **정성 지표**: Claude 브리핑의 B2B 적용 가능성

---

**팀 리더**: 디자인정보 (Design Info Manager)  
**설립일**: 2026-04-10  
**목표**: 리안 컴퍼니의 모든 프로젝트가 최신 디자인 트렌드를 따르도록 지원
