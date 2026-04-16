
=== 전문 지식 (세계 최고 수준 자료 기반) ===

### Python FastAPI 기반 B2B SaaS 백엔드 아키텍처 best practice 2024 - multi-tenant design, API rate limiting, job queue for long-running tasks
# FastAPI B2B SaaS 백엔드 아키텍처 Best Practice

## 핵심 아키텍처 3층 구조

**Pseudo 3-tier architecture 패턴**을 채택하세요.[5] 이는 MVC보다 엔터프라이즈급 확장성을 제공합니다.

| 계층 | 역할 | 핵심 구성 |
|------|------|---------|
| **API Layer** | HTTP 요청 처리 | router.py, 인증 미들웨어 |
| **Service Layer** | 비즈니스 로직 | service.py, 도메인 로직 집중 |
| **Data Layer** | 데이터 접근 | models.py (ORM), DAO 패턴 |

**관심사 분리 원칙**:[1] core(인증·설정·외부 서비스) / api(엔드포인트) / models·schemas(DB·API 계약) 분리로 유지보수성 극대화.

```
backend/
├─ core/
│  ├─ auth.py          # 권한 검증 의존성
│  ├─ clerk.py         # 외부 인증 서비스
│  ├─ config.py        # 환경설정
│  └─ database.py      # DB 연결
├─ api/
│  ├─ tasks.py         # 엔드포인트
│  └─ webhooks.py      # 웹훅 처리
├─ models/
│  └─ task.py          # ORM 모델
├─ schemas/
│  └─ task.py          # Pydantic DTO
└─ service/
   └─ task_service.py  # 비즈니스 로직
```

## Multi-Tenant 데이터 설계 (필수)

**조직 단위 데이터 격리** 구현:[1]

```python
# models.py
from uuid import UUID
from enum import Enum
from sqlalchemy import Column, String, ForeignKey

class Task(Base):
    __tablename__ = "tasks"
    
    id: UUID = Column(UUID, primary_key=True)
    organization_id: UUID = Column(UUID, ForeignKey("organizations.id"), index=True)  # 테넌트 키
    user_id: UUID = Column(UUID, ForeignKey("users.id"))
    title: str = Column(String)
    status: TaskStatus = Column(Enum(TaskStatus))  # Enum 기반 상태 관리
    
    __table_args__ = (
        Index('idx_org_id', 'organization_id'),  # 멀티테넌트 쿼리 최적화
    )

# schemas.py (Pydantic)
from pydantic import BaseModel, validator

class TaskCreate(BaseModel):
    title: str
    
    @validator('title')
    def title_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Title cannot be empty')
        return v
```

**핵심 원칙**: 모든 쿼리에 `organization_id` 필터링 강제화. 데이터 유출 방지.

## 권한 제어 (Role-Based Access Control)

**FastAPI 의존성 주입으로 선언적 권한 검증**:[1]

```python
# core/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthCredentials = Depends(security)):
    # Clerk 또는 JWT 검증
    user = await verify_token(credentials.credentials)
    if

### 기존 CLI/스크립트 기반 파이썬 파이프라인을 REST API SaaS로 전환하는 실전 가이드 - Celery task queue, Redis, 비동기 처리 패턴
### **CLI 스크립트 → REST API SaaS 전환 핵심 프레임워크**

**기존 CLI 파이프라인을 FastAPI + Celery + Redis로 비동기 SaaS 전환: 5단계 실전 가이드 (수치/코드 중심).** 생산성 10배↑, 동시 1,000req/s 처리 가능[1][2].

#### **1. 아키텍처 설계 (제어권 역전: CLI 주도 → 클라이언트 주도)**
```
CLI: 프로그램이 입력 요구 → 로직 실행 → 출력
REST: 클라이언트 HTTP POST → 서버 비동기 task → Redis 큐 → 결과 polling/Webhook
```
- **스택**: FastAPI (API), Celery (task queue), Redis (broker/result backend), Docker (배포).
- **비동기 패턴**:
  | 패턴 | 용도 | 지연시간 예시 | 코드 스니펫 |
  |------|------|--------------|-------------|
  | **Sync Invoke** | 즉시작업 (1s<) | 200ms | `@app.post("/sync")` |
  | **Async Task** | 장기작업 (10s+) | Celery 5-30s | `task.delay(input)` + `/status/{task_id}` |
  | **Stream** | 실시간 (LLM 등) | chunk 100ms | `StreamingResponse(chain.stream())` |
  | **Batch** | 벌크 (100+) | 2-10s | `chain.batch(inputs)`[2] |

#### **2. 구현 Step-by-Step (Bottom-Up, Python 전용)**
**Step 1: Domain Layer (순수 로직, 프레임워크 독립)**
```python
# domain.py - 기존 CLI 함수 재사용
def calculate_add(a: int, b: int) -> int:
    return a + b  # 비즈니스 로직만 (테스트 커버리지 100% 목표)
```

**Step 2: DTO (Pydantic으로 입력/출력 검증)**
```python
# dto.py
from pydantic import BaseModel
class CalcRequest(BaseModel):
    a: int
    b: int
class CalcResponse(BaseModel):
    result: int
    task_id: str = None  # 비동기용
```

**Step 3: Service Layer (Celery 통합 비즈니스)**
```python
# services.py
from celery import Celery
app = Celery('saas', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')

@app.task(bind=True)
def heavy_pipeline(self, data: dict) -> str:
    # 기존 CLI 스크립트 로직 (e.g., ML 훈련 30s)
    result = calculate_add(data['a'], data['b'])  # + 무거운 작업
 
===

