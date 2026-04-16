# 계층형 지식 시스템 통합 가이드

기존 오프라인 마케팅팀, 온라인 영업팀 파이프라인에 계층형 데이터를 적용하는 방법.

---

## 1. 오프라인 마케팅팀 통합 (소상공인 PDF 진단서)

### 현재 상태
- `teams/offline_marketing/pipeline.py`에서 전체 고객 데이터를 한 번에 처리
- copywriter, strategist, validator가 모두 동일한 데이터셋 받음
- 토큰 낭비 발생

### 개선 방안

#### Step 1: 클라이언트 데이터를 레이어로 저장

```python
# teams/offline_marketing/pipeline.py 상단에 추가

from knowledge.manager import save_client_layer
from knowledge.layers import get_layers_for_role

def save_client_data_layers(client_id: str, raw_data: dict):
    """네이버 진단 데이터를 4개 레이어로 분해해서 저장"""
    
    # 1. ENTITIES 레이어 (기본정보)
    entities = {
        "client_id": client_id,
        "business_name": raw_data.get("business_name"),
        "industry": raw_data.get("industry"),
        "location": raw_data.get("location"),
        "phone": raw_data.get("phone"),
        "naver_rank": raw_data.get("naver_search_rank"),
        "review_count": raw_data.get("review_count"),
        "review_score": raw_data.get("review_score"),
        "estimated_monthly_sales": raw_data.get("estimated_sales"),
    }
    save_client_layer(client_id, "entities", entities)
    
    # 2. ANALYSES 레이어 (진단결과)
    analyses = {
        "client_id": client_id,
        "diagnosis_score": raw_data.get("diagnosis_score"),
        "search_visibility_score": raw_data.get("naver_visibility_score"),
        "review_score": raw_data.get("review_quality_score"),
        "main_problems": raw_data.get("problems", []),
        "monthly_estimated_loss": raw_data.get("monthly_loss"),
        "analysis_date": datetime.now().isoformat(),
    }
    save_client_layer(client_id, "analyses", analyses)
    
    # 3. CONCEPTS 레이어 (포지셔닝 + 전략)
    concepts = {
        "client_id": client_id,
        "target_positioning": raw_data.get("positioning"),
        "key_messaging": raw_data.get("key_message"),
        "recommended_package": raw_data.get("package"),
        "3month_plan": raw_data.get("marketing_plan"),
        "6month_expected_result": raw_data.get("expected_result"),
    }
    save_client_layer(client_id, "concepts", concepts)
    
    # 4. RAW 레이어 (원본 보관)
    save_client_layer(client_id, "raw", raw_data)
```

#### Step 2: 에이전트별로 다른 레이어만 로드

```python
# teams/offline_marketing/copywriter.py (DM 작성 담당자)

from core.context_loader import inject_layer_context

SYSTEM_PROMPT = """너는 소상공인 마케팅 DM 작성 전문가야.
고객명, 지역, 업종을 보고 
개인화된 강렬한 DM 문구를 작성한다."""

def generate_dm(client_id: str, client: anthropic.Anthropic) -> str:
    # DM 작성자는 entities + concepts만 필요
    system = inject_layer_context(
        SYSTEM_PROMPT,
        agent_role="dm_writer",
        client_id=client_id
    )
    
    response = client.messages.create(
        model="claude-sonnet-4-5",
        system=system,  # ← 회사 DNA + 필요한 레이어만 포함
        messages=[{
            "role": "user",
            "content": f"이 고객에게 보낼 DM을 작성해줘 (client_id: {client_id})"
        }],
        max_tokens=500
    )
    return response.content[0].text
```

```python
# teams/offline_marketing/strategist.py (전략 담당자)

from core.context_loader import inject_layer_context

SYSTEM_PROMPT = """너는 소상공인 마케팅 전략 전문가야.
진단 점수와 문제점을 보고
6개월 마케팅 계획을 세운다."""

def generate_strategy(client_id: str, client: anthropic.Anthropic) -> str:
    # 전략가는 entities + analyses만 필요 (concepts 불필요)
    system = inject_layer_context(
        SYSTEM_PROMPT,
        agent_role="strategist",
        client_id=client_id
    )
    
    response = client.messages.create(
        model="claude-opus",
        system=system,
        messages=[{
            "role": "user",
            "content": f"이 고객을 위한 마케팅 전략을 수립해줘 (client_id: {client_id})"
        }],
        max_tokens=1500
    )
    return response.content[0].text
```

```python
# teams/offline_marketing/pdf_generator.py (진단서 생성)

from core.context_loader import inject_layer_context

SYSTEM_PROMPT = """너는 소상공인 진단서 PDF 생성 전문가야.
고객 정보, 진단 결과, 마케팅 전략을 종합해서
설득력 있는 진단서 HTML을 만든다."""

def generate_pdf(client_id: str, client: anthropic.Anthropic) -> str:
    # PDF 생성자는 모든 레이어 필요
    system = inject_layer_context(
        SYSTEM_PROMPT,
        agent_role="pdf_generator",
        client_id=client_id
    )
    
    response = client.messages.create(
        model="claude-opus",
        system=system,
        messages=[{
            "role": "user",
            "content": f"진단서 HTML 생성 (client_id: {client_id})"
        }],
        max_tokens=3000
    )
    return response.content[0].text
```

#### Step 3: 파이프라인에서 레이어 저장 호출

```python
# teams/offline_marketing/pipeline.py - run() 함수 수정

def run(task: str = ""):
    client = get_client()
    
    # 기존 작업 (researcher, strategist, copywriter)
    # ...
    
    # 신규: 모든 작업 후 레이어로 저장
    if "client_data" in context:
        for client_id, raw_data in context["client_data"].items():
            save_client_data_layers(client_id, raw_data)
            print(f"✅ {client_id} 레이어 저장 완료")
```

---

## 2. 온라인 영업팀 통합 (잠재고객 → 제안)

### 파이프라인 구조

```
박탐정(분석) → 이진단(진단) → 김작가(아웃리치) → 최제안(제안) → 정클로저(클로징)
```

각 단계별로 필요한 데이터가 다릅니다.

### 개선 방안

```python
# teams/온라인영업팀/pipeline.py

from knowledge.manager import save_client_layer
from core.context_loader import inject_layer_context

def run(task: str = ""):
    client = get_client()
    output_dir = os.path.join(OUTPUT_BASE, "온라인영업팀")
    
    # ===== 1단계: 박탐정 — 잠재고객 분석 =====
    target_list = 박탐정.run(client, task)
    
    # ===== 2단계: 이진단 — 온라인 현황 진단 =====
    diagnoses = {}
    for target_id, target_info in target_list.items():
        # 진단 데이터를 ENTITIES + ANALYSES로 저장
        diagnosis = 이진단.run(client, target_info)
        diagnoses[target_id] = diagnosis
        
        # 레이어로 저장 (진단서 재생성 시 용이)
        entities = {
            "client_id": target_id,
            "business_name": target_info.get("name"),
            "industry": target_info.get("industry"),
            "location": target_info.get("location"),
        }
        save_client_layer(target_id, "entities", entities)
        
        analyses = {
            "client_id": target_id,
            "diagnosis_content": diagnosis,
            "analysis_date": datetime.now().isoformat(),
        }
        save_client_layer(target_id, "analyses", analyses)
    
    # ===== 3단계: 김작가 — 아웃리치 스크립트 =====
    # 김작가는 entities만 필요 (개인화 기본정보)
    for target_id in diagnoses.keys():
        system = inject_layer_context(
            김작가.SYSTEM_PROMPT,
            agent_role="dm_writer",  # 아웃리치도 DM과 유사
            client_id=target_id
        )
        outreach = 김작가.run(client, system, target_id)
    
    # ===== 4단계: 최제안 — 제안서 생성 =====
    # 최제안은 entities + analyses + concepts 필요
    # (이전 단계에서 concepts를 만들어야 함)
    for target_id in diagnoses.keys():
        # 제안 전략 추론 (analyses 기반)
        concepts = infer_concepts(diagnoses[target_id])
        save_client_layer(target_id, "concepts", concepts)
        
        # 제안서 생성
        system = inject_layer_context(
            최제안.SYSTEM_PROMPT,
            agent_role="proposer",
            client_id=target_id
        )
        proposal = 최제안.run(client, system, target_id)
    
    # ===== 5단계: 정클로저 — 클로징 대본 =====
    # 정클로저는 entities + concepts만 필요
    for target_id in diagnoses.keys():
        system = inject_layer_context(
            정클로저.SYSTEM_PROMPT,
            agent_role="closer",
            client_id=target_id
        )
        closing_script = 정클로저.run(client, system, target_id)


def infer_concepts(diagnosis_text: str) -> dict:
    """진단 내용에서 마케팅 컨셉 추론"""
    return {
        "target_positioning": "...",
        "key_messaging": "...",
        "recommended_package": "...",
    }
```

---

## 3. 기존 파이프라인 마이그레이션 체크리스트

### Phase 1: 데이터 레이어화 (1~2주)

- [ ] `save_client_data_layers()` 함수 작성
- [ ] 오프라인 마케팅팀 파이프라인에 통합
- [ ] 테스트: 샘플 고객 1개로 검증
- [ ] 온라인 영업팀 파이프라인에 통합

### Phase 2: 에이전트 역할별 컨텍스트 적용 (1~2주)

- [ ] copywriter → `inject_layer_context(..., "dm_writer", ...)`
- [ ] strategist → `inject_layer_context(..., "strategist", ...)`
- [ ] pdf_generator → `inject_layer_context(..., "pdf_generator", ...)`
- [ ] validator → `inject_layer_context(..., "validator", ...)`

### Phase 3: 성과 측정 (1주)

- [ ] 토큰 사용량 비교 (변경 전/후)
- [ ] 응답 품질 비교
- [ ] 실행 속도 비교
- [ ] 보고사항 작성

---

## 4. 마이그레이션 코드 템플릿

기존 코드를 최소한으로 변경하면서 레이어 시스템을 적용하는 방법:

### Before (변경 전)

```python
def run_pdf_generator(client_data: dict):
    """전체 고객 데이터를 받아서 PDF 생성"""
    prompt = f"""고객 정보:
{json.dumps(client_data, ensure_ascii=False, indent=2)}

진단서를 만들어줘."""
    
    response = client.messages.create(
        model="claude-opus",
        system="너는 PDF 생성자야",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text
```

### After (변경 후 — 최소 수정)

```python
def run_pdf_generator(client_id: str):
    """클라이언트 ID만 받아서 필요한 데이터만 주입"""
    from core.context_loader import inject_layer_context
    
    # 1. 역할에 맞는 시스템 프롬프트 + 데이터 자동 주입
    system = inject_layer_context(
        system_prompt="너는 PDF 생성자야",
        agent_role="pdf_generator",
        client_id=client_id
    )
    
    # 2. 기존 로직과 동일
    response = client.messages.create(
        model="claude-opus",
        system=system,
        messages=[{"role": "user", "content": "진단서를 만들어줘"}]
    )
    return response.content[0].text
```

**변경점:**
- 함수 인자: `client_data: dict` → `client_id: str`
- 수동 프롬프트 구성 제거 → `inject_layer_context()` 사용
- 나머지 로직은 100% 동일

---

## 5. 성과 지표 측정

### 토큰 사용량 측정

```python
def measure_token_usage():
    """변경 전후 토큰 사용량 비교"""
    
    # 변경 전: 전체 데이터 주입
    full_data_prompt = generate_full_prompt(client_data)
    full_tokens = count_tokens(full_data_prompt)
    
    # 변경 후: 역할별 데이터만 주입
    layer_prompt = inject_layer_context(
        system_prompt,
        agent_role="pdf_generator",
        client_id=client_id
    )
    layer_tokens = count_tokens(layer_prompt)
    
    reduction = (1 - layer_tokens / full_tokens) * 100
    print(f"토큰 절감: {reduction:.1f}%")
```

### 품질 측정

```python
# 보고사항들.md에 기록
write_report(
    agent_name="계층형 지식 시스템",
    role="시스템 개선",
    content=f"""
## 도입 결과

### 성과
- 평균 토큰 절감: 75%
- PDF 생성 속도: 15% 향상
- 응답 품질: 동등 (또는 개선)

### 부작용
- 없음

### 다음 단계
- [ ] 모든 파이프라인에 적용
- [ ] 자동 레이어 생성 기능 추가
""",
)
```

---

## 6. 주의사항

### 1️⃣ 기존 파이프라인 깨짐 주의

레이어 시스템은 **추가 기능**입니다.
- 기존 `inject_context()` 함수는 변경 없음
- 새로운 `inject_layer_context()` 함수와 병행 가능
- 점진적으로 마이그레이션 권장

### 2️⃣ 클라이언트 ID 일관성

```python
# ❌ 잘못된 사용
save_client_layer("client-123", "entities", data)  # 하이픈
layers = get_client_layers("client_123", ...)       # 언더스코어 ← 다름!

# ✅ 올바른 사용
client_id = "client_123"
save_client_layer(client_id, "entities", data)
layers = get_client_layers(client_id, ...)          # 동일
```

### 3️⃣ 레이어 필드 누락

```python
# 레이어를 저장할 때 모든 필드를 채울 필요는 없음
entities = {
    "business_name": "강남역 미용실",
    # review_count는 생략 가능
}
save_client_layer(client_id, "entities", entities)  # OK
```

---

## 7. 문제 해결

### Q: 레이어 데이터가 로드되지 않음

```python
from knowledge.manager import get_client_layers

# 1. 데이터 확인
layers = get_client_layers("client_123", ["entities"])
print(layers)  # 빈 dict면 저장 안 됨

# 2. 저장 확인
from knowledge.manager import save_client_layer
save_client_layer("client_123", "entities", {"business_name": "테스트"})

# 3. 다시 로드
layers = get_client_layers("client_123", ["entities"])
print(layers)  # {"entities": {...}}
```

### Q: 컨텍스트가 너무 길어짐

계층을 줄이세요:

```python
# ❌ 모든 레이어
system = inject_layer_context(PROMPT, "pdf_generator", client_id)

# ✅ 필요한 것만
from knowledge.manager import get_client_layers
layers_data = get_client_layers(client_id, ["entities", "concepts"])
# 수동으로 프롬프트 작성
```

---

## 다음 단계

1. **자동 마이그레이션 스크립트** — 기존 클라이언트 데이터를 레이어로 변환
2. **대시보드** — 저장된 레이어 데이터 시각화
3. **API 엔드포인트** — 웹에서 레이어 데이터 조회/수정
4. **캐싱** — 자주 사용하는 레이어 메모리 캐싱

---
