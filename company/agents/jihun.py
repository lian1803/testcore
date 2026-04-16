import re
import anthropic
from core.models import CLAUDE_SONNET, CLAUDE_HAIKU
from core.context_loader import inject_context
from core.model_loader import get_model

# 모델 설정: config에서 "prd" 역할의 모델 로드
# 기본값 Claude Haiku (PRD는 템플릿 기반이므로 저렴한 모델 사용)
MODEL = get_model("jihun")


def _safe(text: str) -> str:
    return re.sub(r'[\ud800-\udfff]', '', str(text))

# ─────────────────────────────────────────────────────────────
# Pass 1 — PRD 본문 (제품 개요 ~ 리스크)
# ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT_CORE = """너는 지훈이야. 리안 컴퍼니 실행팀의 PRD 담당이야.

이사팀의 판단이 GO로 났어. 이제 개발자가 바로 만들 수 있는 PRD를 작성해.

MetaGPT WritePRD 수준의 구체성이 목표야. 개발자가 이 문서 하나로 바로 코딩 시작할 수 있어야 해.

이번 호출(Pass 1)에서는 **PRD 본문만** 출력해. v4 프레임워크 섹션(Aha Moment / JTBD / Customer Forces / Evidence Appendix)은 별도 호출에서 처리하니 여기선 절대 쓰지 마.

포함해야 할 섹션 (정확히 이 순서로):
1. 제품 개요 (한 줄)
2. 기술 스택 (FE/BE/DB/인프라)
3. 기능 목록 — P0/P1/P2 우선순위 + 의존성
4. Must NOT (범위 제외)
5. User Flow (사용자 시나리오 단계별)
6. 화면 명세 (화면별 컴포넌트 + 동작)
7. API 명세 (엔드포인트 + 요청/응답 구조)
8. 데이터 모델 (핵심 테이블/컬렉션 + 필드)
9. 성공 기준 (측정 가능한 KPI)
10. 리스크

출력 형식:
## 제품 개요
[한 줄]

## 기술 스택
- FE: [프레임워크 + 주요 라이브러리]
- BE: [언어/프레임워크 + 런타임]
- DB: [DB 종류 + 이유]
- 인프라: [배포 환경]

## 기능 목록
> P0 = MVP 필수 / P1 = 1차 출시 후 / P2 = 나중에

| 우선순위 | 기능 | 이유 | 의존 기능 |
|---------|------|------|---------|
| P0 | [기능] | [이유] | 없음 |

## Must NOT (범위 외)
- [제외 기능] — [이유]

## User Flow
[주요 시나리오 이름]
1단계: [사용자 액션] → [시스템 응답]
2단계: ...

## 화면 명세
| 화면명 | URL/Route | 핵심 컴포넌트 | 동작 |
|--------|-----------|-------------|------|

## API 명세
| Method | Endpoint | 요청 Body | 응답 | 인증 |
|--------|---------|-----------|------|------|

## 데이터 모델
### [테이블/컬렉션명]
| 필드 | 타입 | 설명 | 제약 |
|------|------|------|------|

## 성공 기준
- [KPI 1]: [측정 방법]
- [KPI 2]: [측정 방법]

## 리스크
- [하은 반론 기반 리스크]: [대응 방안]

개발자가 바로 코딩 시작할 수 있을 만큼 구체적으로. 모호한 표현 금지.
P0 기능부터 개발 시작 → P1 → P2 순서로 Wave를 나눠야 한다고 명시해.

**중요**: 이번 출력에서는 절대 Aha Moment / JTBD / Customer Forces / Evidence Appendix 를 쓰지 마. 그건 Pass 2 전용이야."""


# ─────────────────────────────────────────────────────────────
# Pass 2 — V4 프레임워크 섹션
# ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT_V4 = """너는 지훈이야. 방금 PRD 본문(제품 개요~리스크)은 Pass 1에서 작성 완료됐어.
이번 호출(Pass 2)에서는 **V4 프레임워크 섹션 4개만** 출력해. 본문은 다시 쓰지 마.

Pass 1에서 작성된 PRD와 민수 전략, 서윤 Phase 1 pain point를 참조해서 아래 4개 섹션을 작성해.

출력 형식 (정확히 이 순서, 정확히 이 섹션들만):

## Aha Moment 정의

**Aha Moment:**
> [사용자가 가치를 처음 깨닫는 정확한 순간 — 1문장]

**측정:**
- 가입부터 아하까지 예상 클릭 수 / 초
- 목표: 60초 이내

**구현 방식:**
1. [온보딩 단축 방법]
2. [핵심 가치 즉시 노출 방법]
3. [시각적 피드백]

## JTBD Statement (민수 전략 → 서윤 Phase 1 기반)

**When I am** [구체적 상황],
**I want to** [원하는 행동/결과],
**so I can** [궁극적 목적].

## Customer Forces Strategy (서윤 Phase 3 Canvas 기반)

### Push 요인 (경쟁사 불만 활용)
- 현재 상태: [엑셀/수작업/외주 등]
- 경쟁사 불만: [서윤 Level 5 quote 2~3개]
- **우리의 Push**: "[한 문장 메시지]"

### Pull 요인 (차별 가치)
1. **[차별점 1]**: [구체적 가치]
2. **[차별점 2]**: [구체적 가치]
3. **[차별점 3]**: [구체적 가치]

### Inertia 감소 (전환 비용 최소화)
- **마이그레이션 도구**: [엑셀/기존 데이터 이전 기능]
- **학습 곡선 최소화**: [온보딩/튜토리얼/템플릿]
- **팀 확산**: [초대/권한/공유 기능]

### Anxiety 해소 (신뢰 신호)
- **무료 체험**: [기간 + 조건]
- **보증**: [환불/SLA/데이터 안전]
- **사회적 증거**: [레퍼런스/후기/케이스 스터디]

## Evidence Appendix (기능 ↔ 페인포인트 trace)

서윤이 수집한 Level 4-5 pain point 중 PRD의 P0 기능 결정에 영향을 준 quote를 전부 나열.
각 P0 기능은 최소 1개의 evidence_quote에 trace 가능해야 함.

형식:
### [P0 기능 1]
> "[인용문 원문]"
— *source_url* (Level X, 페르소나)

**반영 방식**: [해당 quote가 이 기능의 어떤 설계에 반영됐는지]

### [P0 기능 2]
... (모든 P0 기능 반복)

---

**출력 규칙**:
- 4개 섹션만 정확히 출력 (그 이상/이하 금지)
- 본문 섹션(제품 개요/기술 스택/기능 목록 등)은 절대 다시 쓰지 마
- 민수 전략의 가격/단위경제 숫자, 서윤 pain point의 실제 quote를 활용"""


def _build_content_pass1(context: dict) -> str:
    idea = _safe(context.get("clarified", context.get("idea", "")))
    strategy = _safe(context.get("minsu", ""))
    judgment = _safe(context.get("junhyeok_text", ""))
    haeun = _safe(context.get("haeun", ""))
    is_commercial = context.get("is_commercial", False)

    feedback = context.get("lian_feedback", "")
    previous_prd = context.get("previous_prd", "")

    if feedback and previous_prd:
        return f"""[이전 PRD]
{previous_prd}

[리안 피드백]
{feedback}

위 피드백을 반영해서 PRD 본문을 수정해줘. 피드백과 관련 없는 부분은 그대로 유지해."""

    return f"""아이디어: {idea}
유형: {"상용화 서비스" if is_commercial else "개인 툴"}

[민수 - 전략]
{strategy}

[하은 - 검증/반론]
{haeun}

[준혁 - 최종 판단]
{judgment}

PRD 본문(섹션 1~10)을 작성해줘. 하은의 반론을 PRD의 리스크 섹션에 반드시 반영해.
v4 프레임워크 섹션은 쓰지 마 (Pass 2에서 별도 처리)."""


def _build_content_pass2(context: dict, prd_core: str) -> str:
    idea = _safe(context.get("clarified", context.get("idea", "")))
    strategy = _safe(context.get("minsu", ""))
    seoyun = _safe(context.get("seoyun", ""))

    return f"""아이디어: {idea}

[Pass 1 — 작성된 PRD 본문]
{prd_core}

[민수 - 전략]
{strategy}

[서윤 - Phase 1 pain point + evidence]
{seoyun}

위 PRD 본문을 보고, V4 프레임워크 섹션 4개(Aha Moment / JTBD / Customer Forces Strategy / Evidence Appendix)를 작성해.
서윤의 실제 evidence_quote를 Evidence Appendix에 trace해야 해."""


def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("📋 지훈 | PRD 작성 (2-pass)")
    print("="*60)

    # ── Pass 1: PRD 본문 ───────────────────────────────────
    print("\n[Pass 1/2] PRD 본문 (섹션 1~10)...")
    prd_core = ""
    try:
        with client.messages.stream(
            model=MODEL,
            max_tokens=12000,
            system=inject_context(SYSTEM_PROMPT_CORE),
            messages=[{"role": "user", "content": _build_content_pass1(context)}],
            temperature=0.3,
        ) as stream:
            for text in stream.text_stream:
                print(text, end="", flush=True)
                prd_core += text
        print()
    except Exception as e:
        error_msg = f"[지훈 Pass 1 실패: {str(e)[:100]}]"
        print(f"\n⚠️  {error_msg}")
        return error_msg

    # ── Pass 2: V4 섹션 ────────────────────────────────────
    print("\n[Pass 2/2] V4 프레임워크 섹션 (Aha/JTBD/Forces/Evidence)...")
    prd_v4 = ""
    try:
        with client.messages.stream(
            model=MODEL,
            max_tokens=8000,
            system=inject_context(SYSTEM_PROMPT_V4),
            messages=[{"role": "user", "content": _build_content_pass2(context, prd_core)}],
            temperature=0.3,
        ) as stream:
            for text in stream.text_stream:
                print(text, end="", flush=True)
                prd_v4 += text
        print()
    except Exception as e:
        print(f"\n⚠️  지훈 Pass 2 에러: {e} — 본문만 반환")
        return prd_core

    # ── 병합 ────────────────────────────────────────────────
    return prd_core.rstrip() + "\n\n---\n\n" + prd_v4.lstrip()
