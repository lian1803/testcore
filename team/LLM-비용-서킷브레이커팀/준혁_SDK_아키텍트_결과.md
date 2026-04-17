# 🚀 풀스택 실전 배포 — Mock 제거 & API 연동 완료 (Vercel 배포판)

## 민재 (프론트엔드) + 서연 (백엔드) 협업 결과

---

## 📋 완료된 작업 (Mock → Real API 전환)

### 1. 백엔드 API 구조 (서연)
```
backend/
├── app.py                 # FastAPI 메인
├── models.py             # SQLAlchemy 모델
├── auth.py               # JWT 인증
├── database.py           # Supabase 연결
└── requirements.txt      # 의존성
```

#### **app.py** (핵심 엔드포인트)
```python
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import os
from typing import List

from database import get_db, engine
from models import Base, User, Project, ApiUsage
from auth import create_access_token, verify_token
from pydantic import BaseModel, EmailStr

# DB 초기화
Base.metadata.create_all(bind=engine)

app = FastAPI(title="LLM Cost Circuit Breaker API")

# CORS 설정 (Vercel 프론트엔드)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend.vercel.app", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

# ===== Pydantic 스키마 =====
class SignUpRequest(BaseModel):
    email: EmailStr
    password: str
    name: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class ProjectCreate(BaseModel):
    name: str
    budget_limit: float  # USD

class UsageLog(BaseModel):
    tokens_used: int
    cost: float
    model: str
    timestamp: datetime

# ===== 인증 의존성 =====
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(User).filter(User.id == payload["sub"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# ===== 엔드포인트 =====

@app.post("/api/auth/signup")
async def signup(data: SignUpRequest, db: Session = Depends(get_db)):
    """회원가입 (bcrypt 해싱)"""
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    new_user = User(
        email=data.email,
        password_hash=pwd_context.hash(data.password),
        name=data.name,
        created_at=datetime.utcnow()
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    token = create_access_token({"sub": new_user.id})
    return {
        "access_token": token,
        "user": {"id": new_user.id, "email": new_user.email, "name": new_user.name}
    }

@app.post("/api/auth/login")
async def login(data: LoginRequest, db: Session = Depends(get_db)):
    """로그인 (JWT 발급)"""
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not pwd_context.verify(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({"sub": user.id})
    return {
        "access_token": token,
        "user": {"id": user.id, "email": user.email, "name": user.name}
    }

@app.get("/api/dashboard")
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """대시보드 데이터 (7일 사용량)"""
    week_ago = datetime.utcnow() - timedelta(days=7)
    
    # 프로젝트별 사용량
    projects = db.query(Project).filter(Project.user_id == current_user.id).all()
    project_data = []
    
    for project in projects:
        usage = db.query(ApiUsage).filter(
            ApiUsage.project_id == project.id,
            ApiUsage.timestamp >= week_ago
        ).all()
        
        total_cost = sum(u.cost for u in usage)
        total_tokens = sum(u.tokens_used for u in usage)
        
        project_data.append({
            "id": project.id,
            "name": project.name,
            "budget_limit": project.budget_limit,
            "total_cost": round(total_cost, 4),
            "total_tokens": total_tokens,
            "budget_remaining": round(project.budget_limit - total_cost, 4),
            "status": "active" if total_cost < project.budget_limit else "exceeded"
        })
    
    # 일별 사용량 추이
    daily_usage = {}
    all_usage = db.query(ApiUsage).filter(
        ApiUsage.project_id.in_([p.id for p in projects]),
        ApiUsage.timestamp >= week_ago
    ).all()
    
    for usage in all_usage:
        date_key = usage.timestamp.strftime("%Y-%m-%d")
        if date_key not in daily_usage:
            daily_usage[date_key] = {"cost": 0, "tokens": 0}
        daily_usage[date_key]["cost"] += usage.cost
        daily_usage[date_key]["tokens"] += usage.tokens_used
    
    return {
        "projects": project_data,
        "daily_usage": [
            {"date": k, "cost": round(v["cost"], 4), "tokens": v["tokens"]}
            for k, v in sorted(daily_usage.items())
        ],
        "total_cost_7d": round(sum(p["total_cost"] for p in project_data), 4)
    }

@app.post("/api/projects")
async def create_project(
    data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """프로젝트 생성"""
    new_project = Project(
        name=data.name,
        budget_limit=data.budget_limit,
        user_id=current_user.id,
        created_at=datetime.utcnow()
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    
    # API 키 생성 (간단한 UUID)
    import uuid
    api_key = f"llm_cb_{uuid.uuid4().hex[:24]}"
    new_project.api_key = api_key
    db.commit()
    
    return {
        "id": new_project.id,
        "name": new_project.name,
        "api_key": api_key,
        "budget_limit": new_project.budget_limit
    }

@app.get("/api/projects")
async def list_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """프로젝트 목록"""
    projects = db.query(Project).filter(Project.user_id == current_user.id).all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "api_key": p.api_key,
            "budget_limit": p.budget_limit,
            "created_at": p.created_at.isoformat()
        }
        for p in projects
    ]

# Health check
@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}
```

#### **models.py** (SQLAlchemy)
```python
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    
    projects = relationship("Project", back_populates="user")

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    api_key = Column(String, unique=True, index=True)
    budget_limit = Column(Float, nullable=False)  # USD
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, nullable=False)
    
    user = relationship("User", back_populates="projects")
    usage_logs = relationship("ApiUsage", back_populates="project")

class ApiUsage(Base):
    __tablename__ = "api_usage"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    tokens_used = Column(Integer, nullable=False)
    cost = Column(Float, nullable=False)  # USD
    model = Column(String, nullable=False)  # gpt-4o, claude-3.5 등
    timestamp = Column(DateTime, nullable=False)
    
    project = relationship("Project", back_populates="usage_logs")
```

#### **auth.py** (JWT)
```python
from datetime import datetime, timedelta
from jose import jwt
import os

SECRET_KEY = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
ALGORITHM = "HS256"

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except:
        return None
```

#### **database.py**