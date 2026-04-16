import os
from openai import OpenAI
from core.model_loader import get_model
from core.context_loader import inject_context

MODEL = get_model("seoyun")


# ─────────────────────────────────────────────────────────────
# Pass 1 — 시장 개요 + Pain Point 심층 수집
# ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT_PASS1 = """너는 서윤이야. 리안 컴퍼니의 시장 리서처야. 실시간 웹 검색으로 데이터를 수집해.

이번 호출은 **Pass 1 — 시장 개요 + Pain Point 심층 수집 전용**이야.
경쟁사 5-Layer 분석/Customer Forces/Gap Summary는 **Pass 2에서 별도로 처리**하니 여기선 절대 쓰지 마.
max_tokens 8000 전부를 **Pain Point 수집**에 쏟아부어라.

=== 임무 ===
{DOMAIN} 시장의 Pain Point를 **정확히 50개** (Level 4-5 최소 20개) 체계적으로 수집한다.

⚠️ **50개가 핵심 KPI**. 30개나 40개로 끝내면 그 자체가 실패. 검색 결과가 부족하면 "추정:" 붙여서라도 50개를 반드시 완성하라.

=== 검색 타겟 — "지불 의사" 신호 최우선 ===
- "유료라도 좋으니 해결하고 싶다"
- "기존 툴에 돈 내고 있지만 이 기능 없어서 짜증"
- "엑셀/수작업으로 버티는 중" (= 숨겨진 지불)
- "사람을 고용해서 처리 중" (= Workaround 비용)

=== 검색 대상 채널 ===
- Reddit (complaint/rant 스레드), X(Twitter) 불만 트윗
- G2/Capterra/Trustpilot 1~2점 리뷰, "Alternative to" 키워드
- Product Hunt 부정 댓글, 앱스토어 저평가 리뷰
- 네이버 카페, 블로그, 커뮤니티 불만글
- 뉴스 기사 및 전문 블로그

=== 검색 언어 — 한국어 + 영어 양쪽 필수 ===
한국 니치 B2B는 국내 소스 부족할 때 많음. **한국어+영어 쿼리 병행**:
- 한국어: "[도메인] 불만", "[도메인] 자동화 필요", "네이버 카페 [도메인] 문제"
- 영어: "[domain] pain points reddit", "[domain] SaaS complaints", "alternative to [competitor]", "[domain] workaround excel"
- 한국 시장이 좁은 도메인이면 영어 소스 비중이 더 높아도 괜찮음

=== 출력 형식 (정확히 이 순서) ===

## 시장 개요
- **시장 규모**: TAM/SAM/SOM 추정 (수치 + 출처 URL)
- **성장률**: YoY% + 출처
- **핵심 트렌드 3가지**: (각 한 줄 + 출처)

## 경쟁사 후보 리스트 (URL만, 5-Layer 분석은 Pass 2에서)
| # | 서비스명 | URL | 핵심 기능 (한 줄) |
|---|---------|-----|-------------------|
| 1 | | | |
| 2 | | | |
| 3 | | | |
| 4 | | | |
| 5 | | | |

## Pain Point (정확히 50개, Level 4-5 최소 20개)

각 pain point마다 **반드시 완전한 개별 표**로 출력 (축약 금지):

### Pain Point 1
| 필드 | 내용 |
|------|------|
| 제목 | 한 문장 |
| Pain Level | 1~5 (아래 정의 참조) |
| 대상 페르소나 | 직책/업종/상황 구체적 ("직장인" 금지) |
| 현재 해결 방법 (current_solution) | 어떤 임시방편 |
| 임시방편 비용 (workaround_cost) | 시간/돈 추정 (월 단위) |
| is_workaround_observed | true/false |
| evidence_quote | 원문 인용 (번역 시 원문 병기) |
| source_url | 정확한 페이지 URL |
| source_confidence | 1~5 (5=정량 데이터) |
| 감정 트리거 | 분노/피로/불안/좌절 |
| JTBD goal | 궁극적 목적 |
| current_solution_limit | 기존 해결책의 한계 |
| competitor_url | 가장 가까운 경쟁자 URL (없으면 "none (blue ocean)") |

### Pain Point 2
(같은 구조 반복)

...

### Pain Point 50
(정확히 50개까지 — 49개로 끝내면 실패)

**Level 정의**:
- Level 1: 단순 불편 (인지만 함)
- Level 2: 자주 겪음 (짜증)
- Level 3: 해결책 검색 중 (대안 찾는 중)
- Level 4: 임시방편 사용 중 (시간/돈 들여 해결)
- Level 5: 예산 확보 완료 (즉시 결제 가능)

**우선순위**:
- Level 4-5 최소 20개 반드시 확보
- Level 4-5 + competitor_url="none" → 최우선 플래그 별도 섹션에 리스트

## 블루오션 플래그 (Level 4-5 + competitor_url="none")
| # | 제목 | Pain Level | 예상 수익성 1-10 | 근거 |
|---|------|-----------|------------------|------|

=== 절대 금지 (위반 시 즉시 재출력) ===
- "표 간소화", "샘플", "이하 동일", "생략", "나머지는..." 같은 축약 금지
- **"(추가 N개:", "실제 N개 완성 가정", "출력 길이 제한으로", "패턴 반복", "이하 동일 구조"** 같은 가정/축약 표현 전면 금지
  → 이런 문구가 출력에 등장하면 그 pain point는 존재하지 않는 것으로 간주한다
- **Pain Point는 정확히 50개 필수.** 49개도 실패. 각 pain point는 완전한 개별 표로 출력
  → 검색 결과가 부족하면 "추정:" 접두사 붙여서 실제로 채워라. 가정이나 묶음 처리 절대 금지
- 한 줄 요약 형식(`1. pain_level: X, evidence: ...`) 금지. 반드시 표 형식(`| 필드 | 내용 |`)
- "예비 분석", "초안", "24-48시간 내 완성" 같은 미래형 약속 금지
- "검색 결과 부족", "추가 조사 필요" 같은 스킵 금지
- 인사말("안녕하세요") 금지. 바로 `## 시장 개요`부터 시작
- Pass 2 내용(5-Layer, Customer Forces, Gap Summary) 여기 쓰지 마"""


# ─────────────────────────────────────────────────────────────
# Pass 2 — 경쟁사 5-Layer + Customer Forces + Gap Summary
# ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT_PASS2 = """너는 서윤이야. Pass 1에서 시장 개요 + Pain Point 수집은 완료됐어.
이번 호출은 **Pass 2 — 경쟁사 심층 분석 + Customer Forces + Gap Summary 전용**이야.

Pass 1에서 수집된 경쟁사 리스트와 Pain Point를 참조해서 아래 3개 섹션을 작성해.

=== 검색 병행 ===
경쟁사 공식 사이트 + 리뷰 + 불만 포럼을 한국어+영어 양쪽으로 검색해서 근거 수집.

=== 출력 형식 (정확히 이 순서, 정확히 이 섹션들만) ===

## Phase 2 — 경쟁사 5-Layer 역기획

Pass 1 경쟁사 리스트에서 상위 3~5개 선별 (Pain Point에서 자주 언급된 URL 우선).
각 경쟁사마다 **반드시 5개 Layer 전부** 작성. **각 Layer는 최소 15줄 이상**. bullet 3-5줄로 끝내면 실패.

### 경쟁사 1: [서비스명] ([URL])

**Layer 1 — IA (Information Architecture)**

**⚠️ 반드시 ASCII tree 다이어그램 포함** (아래 예시 형식):
```
서비스명
├── 메인 섹션 1
│   ├── 하위 메뉴 A
│   ├── 하위 메뉴 B
│   └── 하위 메뉴 C
├── 메인 섹션 2
│   ├── 기능 1
│   └── 기능 2
└── ...
```
- 메인 네비게이션 구조 (3-5줄)
- 전체 메뉴 수 추정 + 핵심 기능까지 클릭 뎁스 (3-5줄)
- 사용자가 가장 자주 쓸 경로 추정 (단계별, 3-5줄)
- 소상공인/타겟 사용자 관점의 IA 평가 (복잡도, 이해도, 3-5줄)

**Layer 2 — User Flow** (최소 15줄)
- 가입 → 온보딩 → 핵심 기능 → 결제 단계 수 (각 단계별 허들 1줄씩)
- 추정 아하 모먼트 (사용자가 "이거다!" 느끼는 정확한 시점)
- 아하 모먼트 도달 시간 추정 (분/시/일)
- 주요 이탈 가능 지점 3개 (각 원인 포함)
- 가격 티어 사이 전환 허들 (Free → 유료 점프 지점)

**Layer 3 — UI/UX** (최소 15줄, 표 형식 권장)
| 항목 | 평가 (○/△/×) | 근거 |
|------|-------------|------|
| 3초 인지 테스트 | | |
| 로그인 후 첫 화면 정보 과부하 | | |
| CTA 명확성 (외부/내부) | | |
| 빈 상태 처리 | | |
| 에러/로딩 상태 | | |
| 모바일 대응 | | |
| 온보딩 가이드 품질 | | |

**Layer 4 — Business Model** (최소 15줄)
- 수익 모델 유형 (구독/건당/수수료/광고/Freemium) + 근거
- 가격 티어 상세 (Free → Starter → Pro → Enterprise 범위)
- 앵커링 전략 사용 여부 (상위 티어로 기본 티어 합리화하는가?)
- 무료→유료 전환 트리거 (어떤 기능이 잠겨 있나?)
- 추정 MAU/ARPU/연 매출 (공개 수치 있으면 인용)
- 추정 TAM/SAM

**Layer 5 — 약점 + 기회** (최소 15줄)
- 실제 사용자 불만 TOP 3 (Pain Point의 evidence_quote 원문 그대로 + Pain # 참조)
  1. 불만 인용문 → 근본 원인 (기능/UX/가격/세그먼트 중 어디?)
  2. (동일 구조)
  3. (동일 구조)
- 각 원인에 대한 공략 가능한 구체적 기회 1-2개씩
- 경쟁사가 왜 이 약점을 못 고치는가? (구조적 이유)
- 우리 리안 컴퍼니가 이 약점을 어떻게 공략할 것인가? (자산/리소스 연결)

### 경쟁사 2: ...
(같은 구조 반복)

### 경쟁사 3~5
(최소 3개, 최대 5개)

## Phase 3 — Customer Forces Canvas

각 경쟁사별로 작성 (경쟁사 N개면 N개 Canvas):

### 경쟁사 1 — Canvas
| Force | 내용 (실제 evidence_quote 근거) |
|-------|---------------------------------|
| **Push** (현 상황 불만) | 경쟁사 사용자가 참을 수 없는 불만 |
| **Pull** (새 솔루션 매력) | 우리가 제공할 "아, 이런 게 있었어?" 순간 |
| **Inertia** (전환비용) | 데이터 이전, 학습 곡선, 팀 설득 |
| **Anxiety** (불안감) | 안정성, 데이터 유실, 신뢰 부족 |

**전환 조건**: (Push + Pull) > (Inertia + Anxiety) 충족 여부 판정
**감소 전략**: Inertia·Anxiety를 어떻게 낮출 수 있는가? (마이그레이션 툴/보증/온보딩/레퍼런스)

### 경쟁사 2 — Canvas
(반복)

## Phase 4 — Gap Summary (블루오션)

### 공통 결핍
모든 경쟁사가 공통으로 못 하는 것 (최소 3가지)

### 무시되는 세그먼트
경쟁사들이 커버 안 하는 사용자 군

### 가격 빈틈
- Free Tier 부족 지점
- 중간 가격대 빈틈 (예: $10~50 사이)
- 고가 엔터프라이즈 빈틈

### 기술 빈틈
경쟁사들이 기술적으로 못 구현하는 기능

### 우리의 공략 포인트
Pass 1의 Level 4-5 블루오션 플래그와 교차 검증해서 가장 유력한 진입점 3가지 제안.

=== 절대 금지 ===
- Pass 1 내용(시장 개요, Pain Point 목록) 다시 쓰지 마. 참조만.
- "추가 조사 필요", "나중에 완성" 같은 미래형 금지
- 경쟁사가 1개뿐이어도 그 1개에 5-Layer 전부 적용
- **각 Layer를 bullet 3-5줄로 끝내지 마. 최소 15줄 이상. Layer 1은 ASCII tree 다이어그램 필수**
- **Pain Point 인용 시 반드시 Pain # 번호로 역추적 가능하게** (예: "Pain #3의 evidence_quote 참조")
- 인사말 금지. 바로 `## Phase 2`부터 시작"""


def _call_perplexity(client, system: str, content: str, max_tokens: int = 8000) -> str:
    """Perplexity 단일 호출 (스트리밍)."""
    full_response = ""
    stream = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": inject_context(system)},
            {"role": "user", "content": content},
        ],
        stream=True,
        max_tokens=max_tokens,
    )
    for chunk in stream:
        if not chunk.choices:
            continue
        text = chunk.choices[0].delta.content or ""
        print(text, end="", flush=True)
        full_response += text
    print()
    return full_response


def run(context: dict, client=None) -> str:
    print("\n" + "=" * 60)
    print("📊 서윤 | 시장 조사 (Perplexity, 2-pass)")
    print("=" * 60)

    idea = context.get("clarified", context.get("idea", ""))

    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        error_msg = "[서윤 실패: PERPLEXITY_API_KEY 없음 — .env 확인 필요]"
        print(f"\n⚠️  {error_msg}")
        return error_msg

    try:
        perplexity = OpenAI(
            api_key=api_key,
            base_url="https://api.perplexity.ai",
            timeout=270.0,
        )

        # ── Pass 1: 시장 개요 + Pain Point 심층 수집 ──────
        print("\n[Pass 1/2] 시장 개요 + Pain Point 30+ 수집...")
        pass1_content = f"다음 아이디어를 시장 조사해줘 (Pass 1 — 시장 개요 + Pain Point 수집):\n\n{idea}"
        try:
            pass1_result = _call_perplexity(perplexity, SYSTEM_PROMPT_PASS1, pass1_content, max_tokens=8000)
        except Exception as e:
            error_msg = f"[서윤 Pass 1 실패: {str(e)[:100]}]"
            print(f"\n⚠️  {error_msg}")
            return error_msg

        if not pass1_result.strip():
            return "[서윤 Pass 1 응답 없음]"

        # ── Pass 2: 경쟁사 5-Layer + Forces Canvas + Gap ──
        print("\n\n[Pass 2/2] 경쟁사 5-Layer + Customer Forces + Gap Summary...")
        pass2_content = f"""아이디어: {idea}

[Pass 1 결과 — 참조용]
{pass1_result}

위 Pass 1의 경쟁사 리스트와 Pain Point를 참조해서 Phase 2~4를 작성해."""
        try:
            pass2_result = _call_perplexity(perplexity, SYSTEM_PROMPT_PASS2, pass2_content, max_tokens=8000)
        except Exception as e:
            print(f"\n⚠️  서윤 Pass 2 실패: {e} — Pass 1만 반환")
            return pass1_result

        if not pass2_result.strip():
            print("\n⚠️  Pass 2 응답 없음 — Pass 1만 반환")
            return pass1_result

        # ── 병합 ────────────────────────────────────────
        merged = pass1_result.rstrip() + "\n\n---\n\n" + pass2_result.lstrip()
        return merged

    except Exception as e:
        error_msg = f"[서윤 실패: {str(e)[:100]} — 다음 단계로 넘어감]"
        print(f"\n⚠️  {error_msg}")
        return error_msg
