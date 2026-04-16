# 리안 컴퍼니 AI 비용 최적화 — 빠른 시작 가이드

**5분 안에 확인하는 핵심 내용**

---

## 🎯 이 프로젝트는 뭔가요?

리안 컴퍼니가 매달 $130-200을 쓰는 AI API 비용을 $60-90으로 줄이는 프로젝트입니다.

- **절감율**: 약 55%
- **연간 절감**: $840-1,404
- **성능 영향**: 최소화

---

## 📊 모델 변경 (중요한 5개)

| 에이전트 | 이전 | 새로운 | 효과 |
|----------|------|--------|------|
| 민수 (전략) | GPT-4o | GPT-4o-mini | 85% 저렴 |
| 지훈 (PRD) | Claude Sonnet | Claude Haiku | 73% 저렴 |
| 카피 (콘텐츠) | Claude Sonnet | Claude Haiku | 73% 저렴 |
| 검증자 (검증) | Claude Opus | Claude Sonnet | 80% 저렴 |
| 커리 (교육) | Claude Opus | Claude Sonnet | 80% 저렴 |

---

## 🛠 구현된 것들

1. **config/model_config.json** - 모든 모델을 한 곳에서 관리
2. **core/model_loader.py** - 에이전트가 자동으로 올바른 모델 선택
3. **core/llm_cache.py** - 동일 프롬프트 재호출 방지
4. **core/cost_tracker.py** - 모든 API 호출 자동 기록

---

## ✅ 지금 바로 할 것

### 파일 확인
```bash
cd company
ls -la config/model_config.json
ls -la core/model_loader.py core/llm_cache.py core/cost_tracker.py
```

### 모델 설정 확인
```bash
python -c "from core.model_loader import get_loader; loader = get_loader(); loader.print_config()"
```

### 파이프라인 테스트
```bash
python main.py "AI 비용 최적화 검증"
```

---

## 📈 기대 효과

| 구분 | 현재 | 이후 | 절감 |
|------|------|------|------|
| 월 비용 | $130-207 | $60-90 | 55% |
| 연 비용 | $1,560-2,484 | $720-1,080 | 55% |

---

**작성**: 2026-04-07  
**상태**: 적용 완료 (model_loader 기반 자동 라우팅 동작 중)  
**예상 Go-Live**: 2026-04-15
