# 5분 안에 시작하기 (Quick Start)

계층형 지식 시스템을 바로 사용하려면 이 가이드를 따르세요.

---

## Step 1: 클라이언트 데이터 저장 (1분)

```python
from knowledge.manager import save_client_layer

client_id = "client_001"

# 1단계: ENTITIES 저장 (고객 기본정보)
save_client_layer(
    client_id,
    "entities",
    {
        "business_name": "강남역 미용실",
        "industry": "미용",
        "location": "강남구",
        "phone": "010-1234-5678",
    }
)

# 2단계: ANALYSES 저장 (진단결과)
save_client_layer(
    client_id,
    "analyses",
    {
        "diagnosis_score": 65,
        "monthly_estimated_loss": "2000000",
        "main_problems": [
            {
                "problem": "네이버 검색 순위 낮음",
                "severity": "high",
            }
        ],
    }
)

# 3단계: CONCEPTS 저장 (마케팅 전략)
save_client_layer(
    client_id,
    "concepts",
    {
        "key_messaging": "개인화 맞춤 시술",
        "recommended_package": "집중 (49만원)",
    }
)
```

---

## Step 2: 에이전트에게 데이터 주입 (2분)

### 방법 A: 자동 주입 (추천)

```python
from core.context_loader import inject_layer_context

# 역할에 필요한 레이어만 자동 주입
pdf_prompt = inject_layer_context(
    system_prompt="너는 PDF 생성자야",
    agent_role="pdf_generator",
    client_id="client_001"
)

# Claude 호출
response = client.messages.create(
    model="claude-opus",
    system=pdf_prompt,  # ← 회사 DNA + 필요 레이어만 포함
    messages=[{
        "role": "user",
        "content": "진단서를 만들어줘"
    }],
    max_tokens=3000
)
```

### 방법 B: 수동 로드 (커스터마이징 필요 시)

```python
from knowledge.manager import get_client_layers, format_layers_for_agent

# 특정 레이어만 로드
layers = get_client_layers(
    client_id="client_001",
    layers=["entities", "concepts"]  # DM 작성자용
)

# 마크다운 형식으로 변환
formatted = format_layers_for_agent(layers)

# 프롬프트에 수동 삽입
prompt = f"""
## 클라이언트 정보

{formatted}

---

고객에게 보낼 DM을 작성해줘.
"""
```

---

## Step 3: 역할별로 다르게 사용 (2분)

### 예시 1: PDF 생성자

```python
# PDF는 전체 정보 필요 (entities + analyses + concepts)
pdf_prompt = inject_layer_context(
    "너는 PDF 진단서 생성 전문가야",
    agent_role="pdf_generator",
    client_id="client_001"
)
```

### 예시 2: DM 작성자

```python
# DM은 기본정보 + 메시지만 필요 (entities + concepts)
dm_prompt = inject_layer_context(
    "너는 영업 DM 작성 전문가야",
    agent_role="dm_writer",
    client_id="client_001"
)
```

### 예시 3: 전략가

```python
# 전략은 현황 + 기본정보만 필요 (entities + analyses)
strategy_prompt = inject_layer_context(
    "너는 마케팅 전략 수립가야",
    agent_role="strategist",
    client_id="client_001"
)
```

---

## 4가지 역할 매핑표

| 역할 | 시스템 | 필요 레이어 | 토큰 |
|------|--------|-----------|------|
| `pdf_generator` | PDF 진단서 생성 | entities + analyses + concepts | 1500 |
| `dm_writer` | DM/메시지 작성 | entities + concepts | 500 |
| `strategist` | 마케팅 전략 | entities + analyses | 600 |
| `proposer` | 제안서 작성 | entities + analyses + concepts | 1500 |
| `validator` | 품질 검증 | analyses + concepts | 700 |

---

## 다른 역할들

```python
# 카피 작성자
inject_layer_context(PROMPT, "copywriter", "client_001")

# 제안자
inject_layer_context(PROMPT, "proposer", "client_001")

# 클로저
inject_layer_context(PROMPT, "closer", "client_001")

# 검증자
inject_layer_context(PROMPT, "validator", "client_001")

# 관리자 (모든 레이어)
inject_layer_context(PROMPT, "admin", "client_001")

# 기본값 (entities + concepts)
inject_layer_context(PROMPT, "default", "client_001")
```

---

## 전체 흐름 (실제 파이프라인)

```python
import anthropic
from datetime import datetime
from knowledge.manager import save_client_layer
from core.context_loader import inject_layer_context

client = anthropic.Anthropic()

# 1️⃣ 클라이언트 데이터 수집 (예: 네이버 플레이스 크롤링)
raw_data = {
    "business_name": "강남역 미용실",
    "industry": "미용",
    "location": "강남구",
    "phone": "010-1234-5678",
    "review_count": 145,
    "review_score": 4.7,
}

client_id = "client_001"

# 2️⃣ 데이터를 레이어로 저장
save_client_layer(client_id, "entities", {
    "business_name": raw_data["business_name"],
    "industry": raw_data["industry"],
    "location": raw_data["location"],
})

save_client_layer(client_id, "analyses", {
    "diagnosis_score": 65,
    "monthly_estimated_loss": "2000000",
})

save_client_layer(client_id, "concepts", {
    "key_messaging": "맞춤형 스타일링",
    "recommended_package": "집중",
})

# 3️⃣ 각 에이전트에게 필요한 데이터만 주입해서 호출

# PDF 생성자
pdf_system = inject_layer_context(
    "너는 PDF 생성자야",
    "pdf_generator",
    client_id
)
pdf = client.messages.create(
    model="claude-opus",
    system=pdf_system,
    messages=[{"role": "user", "content": "진단서"}],
    max_tokens=3000
).content[0].text

# DM 작성자
dm_system = inject_layer_context(
    "너는 DM 작성자야",
    "dm_writer",
    client_id
)
dm = client.messages.create(
    model="claude-sonnet-4-5",
    system=dm_system,
    messages=[{"role": "user", "content": "DM"}],
    max_tokens=500
).content[0].text

# 전략가
strategy_system = inject_layer_context(
    "너는 전략가야",
    "strategist",
    client_id
)
strategy = client.messages.create(
    model="claude-opus",
    system=strategy_system,
    messages=[{"role": "user", "content": "전략"}],
    max_tokens=1500
).content[0].text

# 4️⃣ 결과 저장
print(f"PDF:\n{pdf}\n")
print(f"DM:\n{dm}\n")
print(f"전략:\n{strategy}\n")
```

---

## 자주 묻는 질문

### Q: 에이전트 역할은 어디서 정의되나?

`knowledge/layers/schema.py`의 `AGENT_LAYER_MAP` 딕셔너리:

```python
AGENT_LAYER_MAP = {
    "pdf_generator": ["entities", "analyses", "concepts"],
    "dm_writer": ["entities", "concepts"],
    # ... 기타 역할
}
```

### Q: 새로운 역할을 추가하려면?

```python
# schema.py 수정
AGENT_LAYER_MAP["my_new_role"] = ["entities", "concepts"]

# 사용
inject_layer_context(PROMPT, "my_new_role", client_id)
```

### Q: 데이터가 없으면 어떻게 되나?

```python
# 저장 전에 로드하면 빈 dict 반환
layers = get_client_layers("no_data", ["entities"])
print(layers)  # {"entities": {}}

# inject_layer_context도 정상 작동 (빈 섹션만 추가)
system = inject_layer_context(PROMPT, "pdf_generator", "no_data")
# → 회사 DNA + 빈 클라이언트 데이터 + 프롬프트
```

### Q: 토큰 사용량이 감소했는지 어떻게 확인하나?

```python
import anthropic

# 변경 전
full_data_prompt = generate_full_prompt(client_data)
response1 = client.messages.create(
    system=full_data_prompt,
    messages=[...],
)
print(f"토큰: {response1.usage.input_tokens}")

# 변경 후
layer_prompt = inject_layer_context(PROMPT, "pdf_generator", client_id)
response2 = client.messages.create(
    system=layer_prompt,
    messages=[...],
)
print(f"토큰: {response2.usage.input_tokens}")

# 비교
reduction = (1 - response2.usage.input_tokens / response1.usage.input_tokens) * 100
print(f"절감율: {reduction:.1f}%")
```

---

## 다음 단계

1. **기존 파이프라인 적용** — INTEGRATION_GUIDE.md 참고
2. **성과 측정** — 토큰 및 응답 품질 비교
3. **자동화** — 레이어 저장 프로세스 자동화
4. **확장** — 다른 팀으로 확대

---

## 도움말

- 📖 **전체 가이드**: README.md
- 🔗 **통합 가이드**: INTEGRATION_GUIDE.md
- 🧪 **테스트**: `python test_layer_system.py`
- 💬 **의문사항**: 리안(CEO)에게 문의

---
