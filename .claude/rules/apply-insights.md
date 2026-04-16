# 인사이트 분류 저장 규칙 ("박아")

인스타/외부 자료 분석 후 "박아" 요청 시 아래 규칙대로 저장.

## 분류 기준

| 내용 | 저장 위치 |
|------|-----------|
| 클코 사용법/워크플로우 팁 | `.claude/rules/` |
| 에이전트 프롬프트 개선 | `company/knowledge/workshops/` |
| 디자인 패턴/레퍼런스 | `company/knowledge/base/design/` |
| 마케팅 전략/콘텐츠 패턴 | `company/knowledge/ops_templates/marketing/` |
| 시스템 구조/운영 방식 | `OPERATIONS.md` 또는 `memory/` |

## 파일명 규칙

```
YYYY-MM-DD_출처_키워드.md
```

예시:
- `2026-04-12_인스타_클코_병렬실행팁.md`
- `2026-04-12_유튜브_마케팅_AIDA변형.md`
- `2026-04-12_어워즈_파티클효과패턴.md`

## 저장 절대 금지

- 에이전트 `.py` / `.md` 코드에 직접 삽입 (코드 오염)
- 경로 안 알려주고 "저장했어"만 하는 것

## 저장 후 보고 형식

반드시 한 줄로:
```
→ .claude/rules/parallel-execution.md에 저장 완료
```
