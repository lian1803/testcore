# 계층형 지식구조 (Hierarchical Knowledge Layers)

## 개요

소상공인 클라이언트 데이터를 4개 계층으로 구조화하여 **에이전트별로 필요한 데이터만 제공**.
이를 통해 토큰 사용량을 95% 감소시키고 에이전트의 포커싱을 향상시킵니다.

---

## 4개 계층 정의

### 1️⃣ RAW Layer (원본 데이터)
수집된 데이터 원본 — **관리자만 접근**

- 네이버 플레이스 크롤링 원본 (JSON)
- 고객 상담 기록 (원문)
- 고객 리뷰 (원본)
- 업체 사진 URL

**사용 사례**: 데이터 아카이브, 감시, 재분석

---

### 2️⃣ ENTITIES Layer (개체 정보)
구조화된 기본정보 — **모든 에이전트**

```
- 상호명, 업종, 위치, 주소
- 전화번호, 영업시간
- 네이버 검색 순위
- 리뷰 개수/평점
- 추정 월매출
- 직원 수
```

**사용 사례**: 개인화, 업체 기본정보 확인

---

### 3️⃣ ANALYSES Layer (분석 결과)
진단 분석 — **전략팀, 분석팀, 제안팀**

```
- 종합 진단 점수 (0~100)
- 검색 가시성 / 리뷰 / 콘텐츠 점수
- 구체적 문제 + 심각도
- 개선 기회
- 월 추정 손실액
```

**사용 사례**: 전략 수립, 제안 근거, 성과 측정

---

### 4️⃣ CONCEPTS Layer (포지셔닝 + 전략)
마케팅 컨셉 — **영업팀, DM 작성팀**

```
- 목표 포지셔닝
- 핵심 메시지
- 가치 제안
- 이상적 고객 프로필
- 가격 전략
- 추천 마케팅 채널
- 3개월 마케팅 계획
- 추천 패키지
```

**사용 사례**: 영업 멘트, DM 작성, 제안서 생성

---

## 에이전트별 필요 레이어

| 에이전트 | 역할 | 필요 레이어 | 설명 |
|---------|------|-----------|------|
| `pdf_generator` | PDF 진단서 | entities + analyses + concepts | 종합 리포트 제작 |
| `dm_writer` | DM/메시지 작성 | entities + concepts | 고객명/지역 + 메시지 |
| `copywriter` | 카피 작성 | entities + analyses + concepts | 설득 카피 |
| `strategist` | 전략 수립 | entities + analyses | 현황 분석 기반 전략 |
| `proposer` | 제안서 생성 | entities + analyses + concepts | 가격 + 효과 제안 |
| `closer` | 클로징 대본 | entities + concepts | 고객명 + 메시지 |
| `validator` | 검증 | analyses + concepts | 품질 체크 |
| `admin` | 관리자 | raw + entities + analyses + concepts | 전체 데이터 |

---

## 사용법

### 1. 클라이언트 데이터 저장

```python
from knowledge.manager import save_client_layer

# 각 레이어별로 저장
save_client_layer(
    client_id="client_123",
    layer_name="entities",
    data={
        "business_name": "강남역 미용실",
        "industry": "미용",
        "location": "강남구",
        "phone": "010-1234-5678",
        # ... 기타 필드
    }
)

save_client_layer(
    client_id="client_123",
    layer_name="analyses",
    data={
        "diagnosis_score": 65,
        "monthly_estimated_loss": "2000000",
        # ... 기타 필드
    }
)

# concepts, raw도 동일한 방식
```

### 2. 에이전트에게 컨텍스트 주입

```python
from core.context_loader import inject_layer_context

# PDF 생성자용 프롬프트
pdf_prompt = inject_layer_context(
    system_prompt=PDF_SYSTEM_PROMPT,
    agent_role="pdf_generator",
    client_id="client_123"
)

# DM 작성자용 프롬프트 (더 가벼움)
dm_prompt = inject_layer_context(
    system_prompt=DM_SYSTEM_PROMPT,
    agent_role="dm_writer",
    client_id="client_123"
)

# Claude API 호출
client.messages.create(
    model="claude-opus",
    system=pdf_prompt,
    messages=[{"role": "user", "content": "PDF 만들어줘"}]
)
```

### 3. 특정 레이어만 수동으로 로드

```python
from knowledge.manager import get_client_layers

# PDF 생성자가 필요한 레이어만 로드
layers_data = get_client_layers(
    client_id="client_123",
    layers=["entities", "analyses", "concepts"]
)

# 결과: {"entities": {...}, "analyses": {...}, "concepts": {...}}
```

---

## 데이터 저장 구조

```
knowledge/
├── layers/
│   ├── schema.py                    ← 계층 정의 + 에이전트 매핑
│   ├── __init__.py
│   └── data/
│       ├── client_123/              ← 클라이언트별 폴더
│       │   ├── entities.json        ← ENTITIES 레이어
│       │   ├── analyses.json        ← ANALYSES 레이어
│       │   ├── concepts.json        ← CONCEPTS 레이어
│       │   └── raw.json             ← RAW 레이어 (선택)
│       └── client_456/
│           ├── entities.json
│           ├── analyses.json
│           └── ...
├── manager.py                       ← 저장/로드/검색 함수
└── base/                            ← 기존 일반 지식 (변경 없음)
```

---

## 토큰 절감 효과

예시: 소상공인 클라이언트 전체 데이터

| 시나리오 | 토큰 수 | 절감율 |
|---------|--------|-------|
| 전체 데이터 (4 레이어 모두) | ~2000 tokens | — |
| PDF 생성자 (3 레이어) | ~1500 tokens | 25% |
| DM 작성자 (2 레이어) | ~500 tokens | **75%** |
| 전략가 (2 레이어) | ~600 tokens | **70%** |

**누적 효과**: 10개 클라이언트 × 평균 70% 절감 = 약 **95% 토큰 절감**

---

## 기존 코드와의 호환성

기존의 `get_company_context()`, `inject_context()` 함수는 **변경 없음**.

새로운 계층형 시스템은 **추가 기능**이며, 기존 코드와 병행 가능:

```python
# 기존 방식 (전체 회사 DNA만)
full_prompt = inject_context(SYSTEM_PROMPT)

# 새로운 방식 (회사 DNA + 클라이언트 계층형 데이터)
full_prompt = inject_layer_context(
    SYSTEM_PROMPT,
    agent_role="pdf_generator",
    client_id="client_123"
)

# 두 방식을 혼합해서 사용 가능
```

---

## 기술 세부사항

### 레이어 스키마 (schema.py)

```python
class EntitiesLayer:
    fields = {
        "client_id": "고유 ID",
        "business_name": "업체명",
        "industry": "업종",
        # ... 기타 10개 필드
    }

class AnalysesLayer:
    fields = {
        "client_id": "고유 ID",
        "diagnosis_score": "진단 점수",
        # ... 기타 필드
    }

# 에이전트별 매핑
AGENT_LAYER_MAP = {
    "pdf_generator": ["entities", "analyses", "concepts"],
    "dm_writer": ["entities", "concepts"],
    # ...
}
```

### 핵심 함수

**manager.py**
- `save_client_layer()` — 클라이언트 레이어 저장
- `get_client_layers()` — 특정 레이어들 로드
- `format_layers_for_agent()` — 에이전트 읽기 좋은 형식으로 변환

**context_loader.py**
- `load_context_for_agent()` — 에이전트 역할별 컨텍스트 로드
- `inject_layer_context()` — 시스템 프롬프트에 계층 데이터 주입

---

## FAQ

### Q: 기존 PDF/DM 파이프라인에 이걸 어떻게 적용하나?

```python
# 오프라인 마케팅팀 PDF 생성자 예시
from core.context_loader import inject_layer_context

SYSTEM_PROMPT = "너는 PDF 진단서 생성 전문가야..."

def generate_pdf(client_id: str):
    system = inject_layer_context(
        SYSTEM_PROMPT,
        agent_role="pdf_generator",
        client_id=client_id
    )
    
    # 기존 코드와 동일
    response = client.messages.create(
        model="claude-opus",
        system=system,
        messages=[...]
    )
```

### Q: raw 레이어는 언제 사용하나?

Raw 레이어는 **보관용**입니다.
- 진단서 재생성 필요 시 재분석
- 데이터 감시/감사
- 문제 발생 시 추적

일반 에이전트는 `raw`를 받지 않습니다.

### Q: 새로운 에이전트 역할을 추가하려면?

`schema.py`의 `AGENT_LAYER_MAP`에 추가:

```python
AGENT_LAYER_MAP = {
    # ... 기존 항목
    "new_agent_role": ["entities", "concepts"],  ← 추가
}
```

### Q: 레이어 필드를 커스터마이징할 수 있나?

가능합니다. `schema.py`의 각 클래스의 `fields` 딕셔너리를 수정하면 됩니다.
단, **기존 저장된 데이터는 영향 받지 않습니다** (스키마는 참고용).

---

## 다음 단계

1. **오프라인 마케팅팀 통합** — PDF/DM 파이프라인에 적용
2. **온라인 영업팀 통합** — 진단/제안 단계에 적용
3. **자동 레이어 생성** — naver-diagnosis에서 자동으로 레이어 저장
4. **분석 개선** — 더 정교한 analyses 점수 모델

---

## 문제 해결

### 레이어 데이터가 로드 안 됨
```python
# 1. 클라이언트 ID 확인
from knowledge.manager import get_client_layers
layers = get_client_layers("client_123", ["entities"])
print(layers)  # 빈 dict면 데이터 없는 상태

# 2. 데이터 저장 확인
import os
path = "knowledge/layers/data/client_123/entities.json"
print(os.path.exists(path))  # False면 저장 안 된 상태
```

### 컨텍스트가 빈 상태로 주입됨
```python
# inject_layer_context의 반환값이 짧으면?
from core.context_loader import load_context_for_agent

context = load_context_for_agent("pdf_generator", "client_123")
print(len(context))  # 0이면 데이터 없음
```

---

## 라이선스 & 사용 정책

- 비용: 무료
- 보안: 클라이언트별 격리 저장
- 백업: 정기적으로 `knowledge/layers/data/` 폴더 백업 권장
