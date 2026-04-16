# CTO↔CDO 합의문

## 토론 배경

**CDO 제안 (Wave 1):**
- 진행률 표시: `[3/8] 민수 - 전략 수립 중...`
- 에러 메시지 한국어화 + 해결 방법 제시
- outputs/ 폴더 내 README.md 자동 생성
- CONDITIONAL-GO 시 "진행해 / 조건 수정 / 취소" 선택
- 파일 저장 완료 피드백

**CTO 기술 제약:**
- Windows CMD/PowerShell 환경
- 이모지 출력시 `UnicodeEncodeError` 위험
- 터미널 너비 80자 미만 환경 존재 가능

---

## 채택할 UX 개선사항

| 항목 | 구현 방법 | 우선순위 |
|------|---------|---------|
| 진행률 표시 | `[3/8] 민수 - 전략 수립` ASCII 형식 | P0 |
| 저장 완료 피드백 | `[OK] 저장 완료: 02_전략_민수.md` | P0 |
| 한국어 에러 메시지 | 에러 코드 대신 친절한 설명 + 해결 방법 | P0 |
| README.md 자동 생성 | 파이프라인 완료 후 요약 파일 생성 | P1 |
| CONDITIONAL-GO 선택지 | 3가지 선택지 input 구현 | P1 |
| 단계 구분선 | `===` 60자 (터미널 기본 너비) | P2 |

---

## 기술 제약으로 수정된 제안

### 1. 이모지 처리

**CDO 원안:**
```
[3/8] 💡 민수 - 전략 수립
✓ 저장 완료: 02_전략_민수.md
❌ API 키가 없어
```

**CTO 수정안:**
```
[3/8] 민수 - 전략 수립
[OK] 저장 완료: 02_전략_민수.md
[ERROR] API 키가 없어
```

**합의:**
- 기본값: ASCII 기호 (`[OK]`, `[ERROR]`, `[WARN]`, `[*]`)
- main.py 상단에서 UTF-8 인코딩 시도
- 성공시 이모지 활성화, 실패시 ASCII 폴백

```python
# main.py 상단
import sys
try:
    sys.stdout.reconfigure(encoding='utf-8')
    USE_EMOJI = True
except:
    USE_EMOJI = False
```

---

### 2. 구분선 너비

**CDO 원안:** 60자 고정 (`=` * 60)

**CTO 의견:** 일부 좁은 터미널에서 줄바꿈 발생

**합의:** 60자 유지 (대부분의 터미널 기본 80자 이상)

---

### 3. 파일명 이모지

**CDO 원안:**
```
📊_01_시장조사_서윤.md
💡_02_전략_민수.md
```

**CTO 의견:** Windows 파일 시스템에서 이모지 파일명 문제 가능

**합의:** 파일명에 이모지 사용 안 함. 현재 형식 유지:
```
01_시장조사_서윤.md
02_전략_민수.md
```

---

## Wave 3 구현 스펙 (BE 에이전트 필수 준수)

### 1. 출력 심볼 상수

```python
# core/ui.py (신규 파일)

# 기본값: ASCII 안전
SYMBOLS = {
    "ok": "[OK]",
    "error": "[ERROR]",
    "warn": "[WARN]",
    "progress": "[*]",
    "arrow": "->",
    "check": "[v]",
}

# UTF-8 성공시 이모지로 교체
EMOJI_SYMBOLS = {
    "ok": "✓",
    "error": "❌",
    "warn": "⚠️",
    "progress": "⏳",
    "arrow": "→",
    "check": "✅",
}

def init_symbols():
    """main.py에서 호출. UTF-8 가능하면 이모지 활성화"""
    global SYMBOLS
    import sys
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        # 테스트 출력
        print("✓", end="", flush=True)
        print("\r ", end="", flush=True)  # 지우기
        SYMBOLS = EMOJI_SYMBOLS
    except:
        pass  # ASCII 유지
```

---

### 2. 진행률 헤더 함수

```python
# core/ui.py

def print_header(step: int, total: int, name: str, role: str, note: str = ""):
    """
    출력 예시:
    ============================================================
    [3/8] 민수 - 전략 수립
    ============================================================
    """
    header = f"[{step}/{total}] {name} - {role}"
    if note:
        header += f" ({note})"

    print()
    print("=" * 60)
    print(header)
    print("=" * 60)
```

---

### 3. 저장 완료 피드백 함수

```python
# core/ui.py

def print_save_result(filename: str):
    """
    출력 예시:
    [OK] 저장 완료: 01_시장조사_서윤.md
    """
    print(f"{SYMBOLS['ok']} 저장 완료: {filename}")
```

---

### 4. 에러 메시지 함수

```python
# core/ui.py

def print_error(title: str, causes: list = None, recovery: str = None):
    """
    출력 예시:
    [ERROR] Perplexity API 연결 실패

    가능한 원인:
      1. 인터넷 연결 끊김
      2. API 키 만료

    해결: .env 파일의 PERPLEXITY_API_KEY 확인
    """
    print(f"\n{SYMBOLS['error']} {title}\n")

    if causes:
        print("가능한 원인:")
        for i, cause in enumerate(causes, 1):
            print(f"  {i}. {cause}")
        print()

    if recovery:
        print(f"해결: {recovery}")
        print()
```

---

### 5. 판정 결과 함수

```python
# core/ui.py

def print_verdict(verdict: str, score: int, reason: str = ""):
    """
    출력 예시:
    [판단 결과]
    [OK] GO (종합 점수: 72/100)
    """
    symbol_map = {
        "GO": SYMBOLS["ok"],
        "CONDITIONAL_GO": SYMBOLS["warn"],
        "NO_GO": SYMBOLS["error"],
    }
    symbol = symbol_map.get(verdict, SYMBOLS["progress"])
    label = verdict.replace("_", "-")

    print("\n[판단 결과]")
    print(f"{symbol} {label} (종합 점수: {score}/100)")

    if reason:
        print(f"\n{reason}")
```

---

### 6. CONDITIONAL-GO 선택지

```python
# core/ui.py

def prompt_conditional_go(conditions: str) -> str:
    """
    CONDITIONAL-GO 판정 시 리안에게 선택지 제공

    Returns: "proceed" | "modify" | "cancel"
    """
    print()
    print("=" * 60)
    print(f"{SYMBOLS['warn']} 조건부 진행 (CONDITIONAL-GO)")
    print("=" * 60)
    print()
    print("조건:")
    print(conditions)
    print()
    print("선택지:")
    print("  1. 진행해 - 조건 확인하고 실행팀 진행")
    print("  2. 조건 수정 - 시은과 다시 대화")
    print("  3. 취소 - 여기서 멈춤")
    print()

    while True:
        choice = input("리안 (1/2/3): ").strip()
        if choice in ["1", "진행해", "진행"]:
            return "proceed"
        elif choice in ["2", "조건 수정", "수정"]:
            return "modify"
        elif choice in ["3", "취소"]:
            return "cancel"
        else:
            print("1, 2, 3 중에서 선택해줘.")
```

---

### 7. README.md 자동 생성

```python
# core/output.py에 추가

def generate_readme(output_dir: str, context: dict):
    """
    파이프라인 완료 후 README.md 생성

    context 필수 키:
    - idea: 원본 아이디어
    - verdict: GO/NO_GO/CONDITIONAL_GO
    - score: 종합 점수
    - timestamp: 실행 시각
    """
    verdict_label = {
        "GO": "[OK] GO",
        "NO_GO": "[X] NO-GO",
        "CONDITIONAL_GO": "[!] CONDITIONAL-GO",
    }

    content = f"""# {context.get('idea', '프로젝트')}

실행 일시: {context.get('timestamp', '')}
판정: {verdict_label.get(context.get('verdict', ''), context.get('verdict', ''))} (종합 점수: {context.get('score', 0)}/100)

## 파일 목록

| 파일 | 설명 |
|------|------|
| 01_시장조사_서윤.md | Perplexity 웹 검색 기반 시장 분석 |
| 02_전략_민수.md | 포지셔닝, 수익모델, 가격 전략 |
| 03_검증_하은.md | 차별점 확인, 리스크 분석 |
| 04_최종판단_준혁.json | 종합 점수 및 판정 |
| 05_PRD_지훈.md | Must Have, User Flow, 화면 목록 |
| 06_구현지시서_종범.md | Claude Code용 설계서 |
| 07_마케팅_수아.md | 채널, 카피 A/B, 48시간 검증 |
| 08_트렌드_태호.md | GitHub/HN/ProductHunt 트렌드 참조 |

## 다음 단계

1. `06_구현지시서_종범.md` 열기
2. UltraProduct 폴더에서 Claude Code 실행
3. 구현 지시서 내용 복붙 후 /work 실행
"""

    readme_path = os.path.join(output_dir, "README.md")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(content)

    return readme_path
```

---

### 8. 표준 에러 메시지 (한국어)

| 에러 상황 | 메시지 |
|----------|--------|
| API 키 없음 | `.env 파일에 {KEY}가 없어. .env.example 참고해서 만들어줘.` |
| API 키 만료/무효 | `{SERVICE} API 키가 만료됐거나 잘못됐어. 키를 다시 확인해봐.` |
| 네트워크 오류 | `{SERVICE} 연결 실패. 인터넷 연결 확인하고 다시 시도해봐.` |
| 빈 응답 | `{AGENT}가 빈 응답을 보냈어. 기본값으로 진행할게.` |
| JSON 파싱 실패 | `{AGENT} 응답 형식이 이상해. 기본값으로 진행할게.` |
| 타임아웃 | `{AGENT} 응답이 너무 오래 걸려. 다시 시도할까?` |

---

## 구현 우선순위

### P0 (파이프라인 실행 필수)
1. `core/ui.py` 파일 생성 (심볼, 헤더, 저장 피드백 함수)
2. `pipeline.py`에서 ui 함수 호출
3. 에러 메시지 한국어화

### P1 (사용성 개선)
4. README.md 자동 생성
5. CONDITIONAL-GO 선택지 구현

### P2 (선택)
6. 이모지 폴백 로직 (UTF-8 성공시만)

---

## 합의 서명

- CTO: 기술 제약 내 최선의 UX 구현 가능 확인
- CDO: ASCII 폴백 수용, 핵심 UX 원칙 유지 확인

---

*합의 일시: 2026-03-18*
*Wave 3 BE 에이전트가 이 스펙을 따라 구현할 것*
