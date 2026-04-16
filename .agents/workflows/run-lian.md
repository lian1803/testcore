---
description: 혜경 컴퍼니 실행 방법
---

# 혜경 컴퍼니 실행

## 사전 준비
1. `.env` 파일에 API 키 입력 (위치: `hkyoun_company/.env`)
   - 최소 1개 이상의 API 키 필요

## 실행
// turbo-all

1. 가상환경 활성화
```
cd hkyoun_company
.\venv\Scripts\activate
```

2. 대화형 실행
```
python main.py
```

3. 또는 아이디어를 직접 입력
```
python main.py "소상공인 AI 상세페이지 자동 생성 서비스"
```

## 결과 확인
- `outputs/` 폴더에 날짜별 결과 저장
- `01_리서치_서윤.md` → `02_전략_민수.md` → `03_검증_하은.md` → `04_최종결론_준혁.json`
