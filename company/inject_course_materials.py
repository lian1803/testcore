#!/usr/bin/env python3
"""
강의 자료 → 에이전트 전체 주입 스크립트
Gemini 2.5 Flash로 HTML 파일 글자 하나하나 전부 읽고
각 에이전트/파일에 박음. 완료 후 원본 삭제.

실행:
  cd company
  ./venv/Scripts/python.exe inject_course_materials.py
"""
import os, re, sys, io
from pathlib import Path
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

load_dotenv()

from google import genai

MODEL = "gemini-2.5-flash"
LIANCP_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIAN_CO     = os.path.dirname(os.path.abspath(__file__))
COURSE_DIR  = os.path.join(LIANCP_ROOT, "자료들", "12")
AGENTS_PY   = os.path.join(LIAN_CO, "agents")
TEAMS       = os.path.join(LIAN_CO, "teams")
CLAUDE_AGT  = os.path.join(LIANCP_ROOT, ".claude", "agents")
KB          = os.path.join(LIAN_CO, "knowledge", "base")

# ── HTML 파일 목록 ─────────────────────────────────────────
HTML = {
    "part1": "Part 1. 생성형 AI 기초 및 비즈니스 활용.html",
    "part2": "Part2. 실무를 위한 AI 툴 심화 기초 (2월 4일 업데이트).html",
    "part3": "Part3. 서비스 기획의 기초(2월 11일 업데이트).html",
    "part4": "Part4. 사용자 중심 설계와 UX의 이해(ver.0212).html",
    "part5": "Part5. AI를 활용한 아이디어 구체화와 프로토타이핑(ver. 2월 25일).html",
    "part6": "Part6. 린 스타트업 방법론(2월 27일 버전).html",
    "mkt":   "마케팅 설계자.html",
}


# ── 유틸 ──────────────────────────────────────────────────
def strip_html(path: str) -> str:
    with open(path, encoding="utf-8", errors="replace") as f:
        html = f.read()
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    text = re.sub(r'<[^>]+>', ' ', html)
    text = re.sub(r'&nbsp;', ' ', text)
    text = re.sub(r'&[a-zA-Z0-9#]+;', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def call_gemini(client, content: str, instruction: str) -> str:
    prompt = f"{instruction}\n\n{'='*60}\n원본 전문:\n{'='*60}\n{content}"
    resp = client.models.generate_content(model=MODEL, contents=prompt)
    return (resp.text or "").strip()


def append_section(filepath: str, section: str, marker: str):
    """파일에 섹션 추가. marker가 이미 있으면 교체."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    existing = ""
    if os.path.exists(filepath):
        with open(filepath, encoding="utf-8") as f:
            existing = f.read()

    if marker in existing:
        # 기존 섹션 교체: marker부터 다음 ## 전까지
        pattern = re.escape(marker) + r'.*?(?=\n## |\Z)'
        new = re.sub(pattern, section.rstrip(), existing, flags=re.DOTALL)
    else:
        new = existing.rstrip() + "\n\n" + section

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new)
    print(f"  ✅ 저장: {os.path.relpath(filepath, LIANCP_ROOT)}")


def inject_into_py_prompt(filepath: str, knowledge: str, label: str):
    """Python 파일 SYSTEM_PROMPT / system 변수 끝에 지식 섹션 주입."""
    with open(filepath, encoding="utf-8") as f:
        code = f.read()

    marker = f"\n\n## ── {label} ──"
    if marker in code:
        # 기존 제거 후 재삽입
        pattern = re.escape(marker) + r'.*?(?=""")'
        code = re.sub(pattern, "", code, flags=re.DOTALL)

    # SYSTEM_PROMPT = """..."""  또는  system = """..."""  둘 다 처리
    for var in ("SYSTEM_PROMPT", "system"):
        pat = rf'({var}\s*=\s*""")(.*?)(""")'
        m = re.search(pat, code, re.DOTALL)
        if m:
            new_body = m.group(2).rstrip() + f"{marker}\n{knowledge}\n"
            code = code[:m.start(2)] + new_body + code[m.end(2):]
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(code)
            print(f"  ✅ 주입: {os.path.relpath(filepath, LIANCP_ROOT)} [{label}]")
            return
    print(f"  ⚠️  SYSTEM_PROMPT 못 찾음: {filepath}")


# ── 추출 지시문 ───────────────────────────────────────────
INSTRUCTIONS = {

    # ── knowledge/base 저장용 ─────────────────────────────

    "kb_part1": (
        os.path.join(KB, "AI기초_비즈니스활용.md"),
        "## ── AI 기초 & 비즈니스 활용 ──",
        """이 문서는 'AI 리터러시 & 비즈니스 활용' 강의 전문이야.
글자 하나도 빠짐없이 읽고, 마크다운 형식으로 완전한 지식 베이스를 만들어.

포함할 것:
- 모든 AI 개념 설명 (토큰, LLM, 할루시네이션 등) — 예시 포함
- 4대 AI 비교 (ChatGPT/Claude/Gemini/Copilot) 차이점 전부
- 프롬프트 엔지니어링 원칙 전부 — Before/After 예시 포함
- 비즈니스 활용 사례 전부

출력: 마크다운. 섹션별로 ## 헤더 사용. 내용 누락 없이."""
    ),

    "kb_part2": (
        os.path.join(KB, "AI툴심화_자기강화루프.md"),
        "## ── AI 툴 심화 & 자기 강화 루프 ──",
        """이 문서는 'AI 툴 심화 & 자동화' 강의 전문이야.
모든 내용을 누락 없이 추출해.

포함할 것:
- AI 학습 프레임워크 5가지 전체 내용
- 자기 강화 루프 설계 방법 전부 (단계별)
- MCP(Model Context Protocol) 설명 전부
- NotebookLM, Perplexity Comet, Genspark 등 도구별 활용법 전부
- Input→Process→Output 워크플로우 전부
- 실습 과제/예시 전부

출력: 마크다운. 도구별로 ## 헤더 분리."""
    ),

    "kb_part3": (
        os.path.join(KB, "서비스기획_원칙_완전판.md"),
        "## ── 서비스 기획 원칙 완전판 ──",
        """이 문서는 '서비스 기획의 기초' 강의 전문이야.
기획자가 실무에서 쓰는 모든 원칙과 방법론을 빠짐없이 추출해.

포함할 것:
- 서비스 기획의 정의와 3대 이점 전부
- 서비스 생애주기 전 단계 설명
- 리서치 방법론 전부 (정성/정량, 인터뷰 방법 등)
- 문제 탐색·정의 프로세스 전부
- 확산(Diverge)→수렴(Converge) 방법 전부
- PM/PO/서비스기획자 역할 차이 전부
- 기획자 4대 핵심 역량 상세 (화면설계/기능정의/UX/개발명세) 전부
- 화면설계 방법 전부 (AI 활용 포함)
- 모든 예시와 케이스스터디 (카카오택시, 배민, 토스 등)

출력: 마크다운. 실무 바로 적용 가능한 체크리스트/템플릿도 포함."""
    ),

    "kb_part4": (
        os.path.join(KB, "UX_설계원칙_완전판.md"),
        "## ── UX 설계 원칙 완전판 ──",
        """이 문서는 'UX/UI & 사용자 중심 설계' 강의 전문이야.
UX 설계 원칙과 방법론을 전부 추출해.

포함할 것:
- UCD(사용자 중심 설계) 정의와 원칙 전부
- 린 스타트업 4가지 가설 (고객/문제/솔루션/비즈니스) 상세 설명 전부
- User Journey Map 작성 방법 전부 (단계별)
- 좋은 디자인 4원칙 (명확성/일관성/피드백/단순함) 상세 설명 전부
- 공감→정의→아이디어→프로토타입→테스트 전 과정
- Stitch/Figma/Readdy AI 활용법 전부
- UI/UX 프롬프트 작성법과 예시 전부
- 디자인 피드백 루프 방법

출력: 마크다운. 바로 쓸 수 있는 체크리스트 형태로."""
    ),

    "kb_part5": (
        os.path.join(KB, "프로토타이핑_IA_UJ_PRD_가이드.md"),
        "## ── 프로토타이핑 & IA/UJ/PRD 가이드 ──",
        """이 문서는 'AI 프로토타이핑 & 바이브코딩' 강의 전문이야.
기획→개발 전 과정을 빠짐없이 추출해.

포함할 것:
- 프로토타입/데모/MVP/PoC 정확한 구분과 언제 어떤 걸 써야 하는지
- IA(정보구조) 작성법 전부 — 예시 포함
- UJ(User Journey) 작성법 전부 — 예시 포함
- PRD(서비스 기획서) 작성법 전부 — 에어비앤비 클론 예시 포함
- IA→UJ→PRD→바이브코딩 전체 흐름
- AI Studio 프롬프트 작성법 전부 (Before/After 포함)
- Lovable, Firebase Studio, Google Stitch 활용법 전부
- 바이브코딩 실전 팁 전부 ("수정 요청은 한 번에 하나" 등)

출력: 마크다운. 템플릿은 코드블록으로."""
    ),

    "kb_part6": (
        os.path.join(KB, "린스타트업_방법론_완전판.md"),
        "## ── 린 스타트업 방법론 완전판 ──",
        """이 문서는 '린 스타트업 방법론' 강의 전문이야.
Eric Ries와 Ash Maurya의 방법론 전부를 추출해.

포함할 것:
- 린 스타트업 5가지 핵심 원칙 전부
- BML 루프 (Build→Measure→Learn) 상세 설명 전부
- 검증된 학습 vs 가짜 학습 구분법 전부
- Lean Canvas 9칸 각각 상세 설명 + 작성 예시
- 핵심 가설 찾기 방법 (가치 가설 + 성장 가설)
- Love the Problem 원칙 상세
- Customer Forces (커플러 포스) 전부
- 마피아 오퍼 개념과 적용법
- Mom Test 방법론 전부
- 피벗 유형별 옵션 전부 (언제 피벗하는가)
- 한국 사례 (배민/당근/토스) 전부
- AI 프롬프트 실습 예시 전부

출력: 마크다운. 즉시 실전 적용 가능한 형태로."""
    ),

    "kb_mkt": (
        os.path.join(KB, "마케팅퍼널_완전가이드.md"),
        "## ── 마케팅 퍼널 완전 가이드 ──",
        """이 문서는 'DotCom Secrets 기반 마케팅 설계자' 강의 전문이야.
Russell Brunson의 마케팅 방법론 전부를 추출해.

포함할 것:
- 세일즈 퍼널 개념과 4단계 전부 상세 설명
- 가치 사다리 (Value Ladder) 설계 방법 전부 — 구체적 예시 포함
- Hook→Story→Offer 구조 상세 전부 — 예시 포함
- 방문자 온도별 전략 (Cold/Warm/Hot) 전부
- 매력적인 캐릭터 4가지 유형 전부 상세
- 4가지 퍼널 유형 (리드/언박싱/프레젠테이션/전화) 전부
- 판매 페이지 4단계 (감정→논리→공포→주문) 전부
- PAS 스크립트 전부 — 예시 포함
- 골든서클 활용법 전부
- 써밋 퍼널 설명 전부
- AI 실습 예시 (Claude로 퍼널 설계, PAS 카피 작성법) 전부

출력: 마크다운. 즉시 쓸 수 있는 템플릿과 예시 전부 포함."""
    ),

    # ── Claude Code 에이전트 (.md) 주입 ──────────────────

    "cpo_part3": (
        os.path.join(CLAUDE_AGT, "cpo.md"),
        "## ── 서비스 기획 원칙 (Part 3 강의) ──",
        """이 문서는 '서비스 기획의 기초' 강의 전문이야.
CPO(Chief Product Officer) 에이전트의 시스템 프롬프트에 추가할 섹션을 작성해.

CPO가 실제 기획 작업 시 적용할 원칙들만 추출해:
- 문제 탐색·정의 프로세스 (리서치 방법론 포함)
- 확산(Diverge)→수렴(Converge) 방법
- 기획 3대 이점 (비용절감/방향성/사용자중심) 활용법
- 서비스 생애주기별 기획 전략
- 화면설계 원칙 (AI 활용법 포함)
- 기능 정의 체크리스트

형식: 마크다운 섹션. ## 헤더로 시작.
CPO가 바로 쓸 수 있는 체크리스트/원칙 형태로. 군더더기 없이."""
    ),

    "cpo_part5": (
        os.path.join(CLAUDE_AGT, "cpo.md"),
        "## ── IA→UJ→PRD 기획 프로세스 (Part 5 강의) ──",
        """이 문서는 'AI 프로토타이핑 & 바이브코딩' 강의 전문이야.
CPO가 기획 산출물 만들 때 적용할 내용만 추출해:

- 프로토타입/데모/MVP/PoC 정확한 구분 (CPO가 언제 뭘 선택하는가)
- IA 작성 원칙과 구조 (예시 포함)
- UJ 작성 원칙과 구조 (예시 포함)
- PRD 작성 원칙과 구조 (에어비앤비 클론 예시 수준으로 상세하게)
- "기획 산출물이 곧 프롬프트"라는 원칙 적용법

형식: 마크다운. ## 헤더로 시작. 즉시 적용 가능한 형태."""
    ),

    "pm_part3": (
        os.path.join(CLAUDE_AGT, "pm.md"),
        "## ── 서비스 기획 원칙 (Part 3 강의) ──",
        """이 문서는 '서비스 기획의 기초' 강의 전문이야.
PM(Product Manager) 에이전트가 User Story, 화면 플로우, 개발 우선순위 작업 시
적용할 원칙들만 추출해:

- PM/PO/서비스기획자 역할 차이와 PM이 집중해야 할 것
- 기획자 4대 핵심 역량 → PM 태스크에 적용하는 법
- 화면 설계 시 체크리스트
- 기능 정의 원칙 (개발자가 바로 쓸 수 있는 수준)
- 개발 명세 작성 원칙

형식: 마크다운. ## 헤더로 시작. 체크리스트 형태 선호."""
    ),

    "cdo_part4": (
        os.path.join(CLAUDE_AGT, "cdo.md"),
        "## ── UX 설계 원칙 (Part 4 강의) ──",
        """이 문서는 'UX/UI & 사용자 중심 설계' 강의 전문이야.
CDO(Chief Design Officer) 에이전트가 디자인 작업 시 적용할 원칙만 추출해:

- UCD 원칙 전부 ("내가 쓰고 싶은 거" 대신 "사용자가 필요한 거")
- 좋은 디자인 4원칙 (명확성/일관성/피드백/단순함) — 각각 구체적 적용법
- 공감→정의→아이디어→프로토타입→테스트 디자인 프로세스
- User Journey Map 기반 디자인 의사결정 방법
- 린 스타트업 4가지 가설이 디자인에 미치는 영향
- 전환 최적화에 UX 원칙 적용하는 법

형식: 마크다운. ## 헤더로 시작. CDO가 매 작업마다 체크할 수 있는 형태."""
    ),

    "fe_part4": (
        os.path.join(CLAUDE_AGT, "fe.md"),
        "## ── UX 구현 원칙 (Part 4 강의) ──",
        """이 문서는 'UX/UI & 사용자 중심 설계' 강의 전문이야.
FE(Frontend Engineer) 에이전트가 UI 구현 시 적용할 원칙만 추출해:

- 좋은 디자인 4원칙을 코드 레벨에서 구현하는 법
- 사용자 피드백(UI 피드백, 로딩, 에러 상태) 구현 원칙
- 단순함 원칙을 컴포넌트 설계에 적용하는 법
- 일관성 원칙 (디자인 시스템, 컴포넌트 재사용)
- 모바일 UX 원칙 구현법
- User Journey 흐름에 맞는 라우팅/상태 관리

형식: 마크다운. ## 헤더로 시작. 개발자가 바로 적용할 수 있는 원칙."""
    ),

    "marketing_mkt": (
        os.path.join(CLAUDE_AGT, "marketing.md"),
        "## ── 마케팅 퍼널 원칙 전체 (DotCom Secrets) ──",
        """이 문서는 'DotCom Secrets 기반 마케팅 설계자' 강의 전문이야.
마케팅 에이전트(수아)의 프롬프트에 추가할 내용을 추출해.

이미 있는 내용(세일즈 퍼널 4단계, 가치 사다리)은 제외하고,
없는 내용만 추가해:
- Hook→Story→Offer 구조 상세 적용법 (각 단계별 구체적 지침)
- 방문자 온도별 전략 (Cold/Warm/Hot) 상세 — 수아가 채널별로 적용하는 법
- 매력적인 캐릭터 4유형 — 콘텐츠 전략에 적용하는 법
- PAS 스크립트 원칙과 예시 — 수아가 카피 쓸 때 적용
- 판매 페이지 4단계 (감정→논리→공포→주문) 상세
- 퍼널 유형별 선택 기준 (언제 리드 퍼널 vs 언박싱 퍼널)

형식: 마크다운. ## 헤더로 시작. 수아가 직접 적용할 수 있는 지침."""
    ),
}

# ── Python 에이전트 주입 작업 ──────────────────────────────
PY_INJECTIONS = [
    {
        "file": os.path.join(AGENTS_PY, "sieun.py"),
        "label": "린스타트업_적용원칙",
        "source": "part6",
        "instruction": """이 문서는 '린 스타트업 방법론' 강의 전문이야.
시은(이사팀 오케스트레이터)이 아이디어 명확화와 팀 설계 시 적용할 원칙만 추출해.

시은에게 필요한 것:
- Love the Problem 원칙 — 아이디어 명확화 시 리안에게 물어볼 질문 유형
- 핵심 가설 4가지 (고객/문제/솔루션/비즈니스) — 리안 인터뷰 시 파악해야 할 항목
- BML 루프 관점에서 MVP 범위를 좁히도록 리안을 유도하는 방법
- 검증된 학습 기준 — GO/NO-GO 전에 시은이 체크해야 할 것

형식: 단락 형태 텍스트 (마크다운 헤더 없이). 시은이 실제로 쓸 원칙만. 200줄 이내."""
    },
    {
        "file": os.path.join(AGENTS_PY, "minsu.py"),
        "label": "전략수립_린캔버스_프레임워크",
        "source": "part6",
        "instruction": """이 문서는 '린 스타트업 방법론' 강의 전문이야.
민수(GPT-4o 전략가)가 전략 수립 시 적용할 프레임워크만 추출해.

민수에게 필요한 것:
- Lean Canvas 9칸 전부 (각 칸 상세 설명 + 작성 방법)
- 핵심 가설에서 수익 모델 도출하는 방법
- 가치 가설 + 성장 가설 기반 전략 수립 원칙
- 피벗 유형별 옵션 — 민수가 조건부 GO 시 대안 전략 제시에 활용

형식: 단락 형태 텍스트. 민수가 전략서에 바로 반영할 수 있는 구체적 원칙. 150줄 이내."""
    },
    {
        "file": os.path.join(AGENTS_PY, "junhyeok.py"),
        "label": "GO판단_린스타트업_기준",
        "source": "part6",
        "instruction": """이 문서는 '린 스타트업 방법론' 강의 전문이야.
준혁(Claude Opus, GO/NO-GO 최종 판단)이 판단 시 적용할 기준만 추출해.

준혁에게 필요한 것:
- BML 루프 관점에서 GO 판단 기준 (만들기 전에 검증 가능한가?)
- 핵심 가설 4가지가 충족됐는가 체크리스트
- 검증된 학습 기준 (행동의 변화만이 증거)
- 피벗 권고 기준 (언제 NO-GO 대신 CONDITIONAL_GO + 피벗 방향)
- Mom Test 관점에서 시장 조사 결과 신뢰도 평가법

형식: 단락 형태 텍스트. 준혁의 판단 채점에 직접 반영할 수 있는 기준. 150줄 이내."""
    },
    {
        "file": os.path.join(TEAMS, "offline_marketing", "copywriter.py"),
        "label": "마케팅퍼널_카피라이팅_원칙",
        "source": "mkt",
        "instruction": """이 문서는 'DotCom Secrets 기반 마케팅 설계자' 강의 전문이야.
예진(오프라인 마케팅팀 카피라이터)이 DM/문자 스크립트 작성 시 적용할 원칙만 추출해.

예진에게 필요한 것:
- PAS 스크립트 원칙 전부 + 소상공인 DM에 적용하는 예시
- Hook 작성 원칙 전부 (첫 문장에서 Pain을 때리는 법)
- Story 구조 (매력적인 캐릭터 유형 중 DM에 맞는 것)
- Offer 구조 (소상공인에게 제안하는 방식)
- Cold/Warm/Hot 온도별 DM 전략
- 판매 페이지 4단계를 DM 시퀀스에 적용하는 법

형식: 단락 형태 텍스트. 예진이 DM 쓸 때 바로 체크할 수 있는 원칙. 200줄 이내."""
    },
]


# ── 메인 실행 ─────────────────────────────────────────────
def main():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ GOOGLE_API_KEY 없음")
        sys.exit(1)

    client = genai.Client(api_key=api_key)
    os.makedirs(KB, exist_ok=True)

    # HTML 전부 읽기 (캐시)
    print("\n📖 HTML 파일 로딩 중...")
    texts = {}
    for key, fname in HTML.items():
        path = os.path.join(COURSE_DIR, fname)
        if not os.path.exists(path):
            print(f"  ⚠️  파일 없음: {fname}")
            continue
        texts[key] = strip_html(path)
        size_kb = len(texts[key]) // 1024
        print(f"  [{key}] {fname[:40]}... → {size_kb}KB 텍스트")

    total = len(INSTRUCTIONS) + len(PY_INJECTIONS)
    done = 0

    # ── 1단계: knowledge/base + .md 에이전트 주입 ──────────
    print(f"\n{'='*60}")
    print(f"  1단계: knowledge/base + .claude/agents 주입 ({len(INSTRUCTIONS)}건)")
    print(f"{'='*60}")

    for task_key, (target_path, marker, instruction) in INSTRUCTIONS.items():
        # source 파트 결정
        src_key = None
        for k in texts:
            if task_key.startswith(k) or task_key.endswith(k):
                src_key = k
                break
        # fallback
        if not src_key:
            if "part1" in task_key: src_key = "part1"
            elif "part2" in task_key: src_key = "part2"
            elif "part3" in task_key: src_key = "part3"
            elif "part4" in task_key: src_key = "part4"
            elif "part5" in task_key: src_key = "part5"
            elif "part6" in task_key: src_key = "part6"
            elif "mkt" in task_key: src_key = "mkt"

        if not src_key or src_key not in texts:
            print(f"  ⚠️  소스 없음: {task_key}")
            continue

        done += 1
        print(f"\n[{done}/{total}] {task_key}")
        print(f"  소스: {src_key} | 대상: {os.path.basename(target_path)}")
        print(f"  Gemini 호출 중...", end="", flush=True)

        try:
            extracted = call_gemini(client, texts[src_key], instruction)
            section = f"{marker}\n\n{extracted}\n"
            append_section(target_path, section, marker)
            print(f"  완료 ({len(extracted)//1024}KB 추출)")
        except Exception as e:
            print(f"\n  ❌ 오류: {e}")

    # ── 2단계: Python 에이전트 SYSTEM_PROMPT 주입 ──────────
    print(f"\n{'='*60}")
    print(f"  2단계: Python 에이전트 SYSTEM_PROMPT 주입 ({len(PY_INJECTIONS)}건)")
    print(f"{'='*60}")

    for task in PY_INJECTIONS:
        done += 1
        src_key = task["source"]
        print(f"\n[{done}/{total}] {os.path.basename(task['file'])} ← {src_key}")

        if src_key not in texts:
            print(f"  ⚠️  소스 없음")
            continue

        print(f"  Gemini 호출 중...", end="", flush=True)
        try:
            extracted = call_gemini(client, texts[src_key], task["instruction"])
            inject_into_py_prompt(task["file"], extracted, task["label"])
            print(f"  완료 ({len(extracted)//1024}KB)")
        except Exception as e:
            print(f"\n  ❌ 오류: {e}")

    # ── 완료 ──────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"  ✅ 전체 완료! {done}/{total}건 처리")
    print(f"{'='*60}")

    # 원본 파일 삭제 여부 확인
    print(f"\n원본 HTML 파일 삭제할까? (y/n): ", end="")
    try:
        ans = input().strip().lower()
    except EOFError:
        ans = "n"

    if ans == "y":
        for fname in HTML.values():
            path = os.path.join(COURSE_DIR, fname)
            if os.path.exists(path):
                os.remove(path)
                print(f"  🗑️  삭제: {fname[:50]}")
        print("원본 파일 삭제 완료.")
    else:
        print("원본 파일 유지.")


if __name__ == "__main__":
    main()
