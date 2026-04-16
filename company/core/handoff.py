"""
PipelineHandoff — 이사팀 산출물 + jihun PRD → UltraProduct 브리핑 문서 자동 생성

생성 파일:
  team/{프로젝트명}/CLAUDE.md         — /work가 읽는 메인 컨텍스트 (간결)
  team/{프로젝트명}/PRD.md            — 지훈이 작성한 PRD 전문
  team/{프로젝트명}/기획문서/          — 이사팀 산출물 전체 복사 (Phase 1)
  team/{프로젝트명}/기획문서/INDEX.md — 역할별 필독 가이드
"""

import os
import shutil
from pathlib import Path
from datetime import datetime


# 역할별 필독 파일 매핑 — context_loader.py와 동기화 필수
ROLE_REQUIRED_FILES = {
    "fe":        ["05_PRD_지훈.md", "02c_비즈니스모델_설계자.md"],
    "be":        ["05_PRD_지훈.md", "02c_비즈니스모델_설계자.md"],
    "cto":       ["05_PRD_지훈.md", "02b_전략브리프_설계자.md"],
    "marketing": ["02c_비즈니스모델_설계자.md", "01_시장조사_서윤.md"],
    "sales":     ["02c_비즈니스모델_설계자.md", "01_시장조사_서윤.md"],
    "qa":        ["05_PRD_지훈.md", "03_검증_하은.md"],
}

# 파일 설명 (정적)
FILE_DESCRIPTIONS = {
    "00_이사팀_보고서.md": "전체 요약 (먼저 읽기)",
    "01_시장조사_서윤.md": "50개 Pain Point + 경쟁사 후보",
    "02_전략_민수.md": "전략 + 1순위 pick",
    "02b_전략브리프_설계자.md": "OKR + 필터 + TOP5 + 킬러 오퍼 (설계자 1call)",
    "02c_비즈니스모델_설계자.md": "Problem Statement + STP + VPC + Lean Canvas (설계자 2call)",
    "03_검증_하은.md": "숫자 검증 + 반론",
    "03b_토론_결과.md": "민수↔하은 토론",
    "04_최종판단_준혁.json": "Go/No-Go + 점수",
    "04b_큰그림체크_시은.md": "놓친 것들 체크",
    "04c_최종재검토_시은.md": "최종 델타",
    "05_PRD_지훈.md": "PRD 전문 (P0/P1/P2)",
    "05_리안인터뷰_시은.md": "리안 워크플로우 인터뷰",
    "06_이사팀_컨텍스트.md": "팀 교육용 요약",
    "06_팀설계_시은.md": "팀 구성 설계",
    "07_런칭준비.md": "런칭 준비 (마케팅 채널/첫 주 플랜)",
    "08_트렌드_태호.md": "트렌드 + 경쟁사 역기획",
}


class PipelineHandoff:
    def __init__(self, context: dict, output_dir: str):
        self.context = context
        self.output_dir = output_dir
        self.project_name = context.get("idea", "프로젝트")[:30].strip()
        self.safe_name = self.project_name.replace(" ", "_").replace("/", "_")

    def generate(self) -> str:
        """브리핑 문서 생성 후 프로젝트 폴더 경로 반환"""
        team_root = Path(__file__).parent.parent.parent.parent / "team"
        project_dir = team_root / self.safe_name
        project_dir.mkdir(parents=True, exist_ok=True)

        prd_path = project_dir / "PRD.md"
        claude_path = project_dir / "CLAUDE.md"

        # PRD.md 저장
        prd_path.write_text(self.context.get("prd", ""), encoding="utf-8")

        # CLAUDE.md 생성
        claude_content = self._build_claude_md()
        claude_path.write_text(claude_content, encoding="utf-8")

        # ── Phase 1: 기획문서 전체 복사 + 인덱스 생성 ──
        self._copy_planning_docs(project_dir)

        return str(project_dir)

    def _copy_planning_docs(self, project_dir: Path):
        """outputs/{프로젝트}/ 의 md + json 전부 → team/{프로젝트}/기획문서/ 복사.

        + 각 md 파일 4줄 요약 자동 생성 (캐시 있으면 재사용)
        + 요약이 박힌 INDEX.md 생성
        """
        planning_dir = project_dir / "기획문서"
        planning_dir.mkdir(parents=True, exist_ok=True)

        outputs_path = Path(self.output_dir)
        if not outputs_path.exists():
            print(f"⚠️  outputs 폴더 없음: {outputs_path}")
            return

        copied = []
        for pattern in ("*.md", "*.json"):
            for src in outputs_path.glob(pattern):
                dest = planning_dir / src.name
                shutil.copy2(src, dest)
                copied.append(src.name)

        # ── 자동 요약 생성 (캐시 활용) ──
        summaries = self._generate_summaries(outputs_path)

        # 인덱스 파일 생성 (요약 포함)
        index_content = self._build_planning_index(copied, summaries)
        (planning_dir / "INDEX.md").write_text(index_content, encoding="utf-8")

        # 요약 JSON 도 기획문서/ 폴더에 복사 (실행팀이 직접 로드 가능)
        summaries_src = outputs_path / "_summaries.json"
        if summaries_src.exists():
            shutil.copy2(summaries_src, planning_dir / "_summaries.json")

        print(f"📚 기획문서 {len(copied)}개 + 요약 {len(summaries)}개 + INDEX.md: {planning_dir}")

    def _generate_summaries(self, outputs_path: Path) -> dict:
        """outputs/ 의 md 파일 자동 요약. 캐시 있으면 재사용."""
        try:
            from core.planning_summarizer import (
                summarize_planning_dir,
                load_summaries,
                save_summaries,
            )
        except ImportError:
            print("⚠️  planning_summarizer 없음 — 정적 설명으로 폴백")
            return {}

        # 캐시 먼저
        summaries = load_summaries(str(outputs_path))
        if summaries:
            print(f"  💾 요약 캐시 사용: {len(summaries)}개")
            return summaries

        # 새로 생성 — Anthropic client
        try:
            import anthropic
            import os
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                print("⚠️  ANTHROPIC_API_KEY 없음 — 요약 스킵")
                return {}
            client = anthropic.Anthropic(api_key=api_key)
        except Exception as e:
            print(f"⚠️  Anthropic client 생성 실패: {e}")
            return {}

        print(f"  🤖 자동 요약 생성 중 (~1분)...")
        try:
            summaries = summarize_planning_dir(str(outputs_path), client)
            save_summaries(summaries, str(outputs_path))
            return summaries
        except Exception as e:
            print(f"⚠️  요약 생성 실패: {e}")
            return {}

    def _build_planning_index(self, filenames: list, summaries: dict = None) -> str:
        """기획문서 INDEX.md — 파일별 핵심 요약 + 역할별 가이드.

        summaries가 있으면 각 파일의 실제 요약(4줄)을 박고,
        없으면 정적 설명으로 폴백.
        """
        if summaries is None:
            summaries = {}

        lines = [
            "# 기획문서 INDEX",
            "",
            "> 이사팀이 생성한 전체 기획 산출물.",
            "> 실행팀은 아래 **파일별 요약**만 읽어도 충분. 원본 필요 시 파일명 지정 로드.",
            "",
        ]

        if summaries:
            lines.extend([
                "## 파일별 핵심 요약 (자동 생성)",
                "",
            ])
            for fname in sorted(summaries.keys()):
                s = summaries[fname]
                lines.append(f"### `{fname}`")
                if "error" in s:
                    lines.append(f"- ⚠️ 요약 실패")
                else:
                    lines.append(f"- **핵심 결론**: {s.get('핵심결론', '-')}")
                    lines.append(f"- **타겟**: {s.get('타겟', '-')}")
                    lines.append(f"- **핵심 숫자**: {s.get('핵심숫자', '-')}")
                    lines.append(f"- **팀 전달**: {s.get('팀전달포인트', '-')}")
                lines.append("")

            # 요약 안 된 파일(json 등)도 나열
            non_summarized = [f for f in filenames if f not in summaries]
            if non_summarized:
                lines.extend(["## 요약 없는 파일", ""])
                for fname in sorted(non_summarized):
                    desc = FILE_DESCRIPTIONS.get(fname, "")
                    lines.append(f"- `{fname}` — {desc}")
                lines.append("")
        else:
            # 폴백: 정적 설명
            lines.extend([
                "## 전체 파일 목록",
                "",
            ])
            for fname in sorted(filenames):
                desc = FILE_DESCRIPTIONS.get(fname, "")
                lines.append(f"- `{fname}` — {desc}")

        lines.extend([
            "",
            "## 역할별 필독 가이드",
            "",
            "### FE (Frontend)",
            "- **필수**: `05_PRD_지훈.md`, `02c_비즈니스모델_설계자.md` (페르소나·VPC·톤)",
            "- **참고**: `02b_전략브리프_설계자.md`, `04b_큰그림체크_시은.md`",
            "",
            "### BE (Backend)",
            "- **필수**: `05_PRD_지훈.md` (P0/P1/P2 기능)",
            "- **참고**: `02c_비즈니스모델_설계자.md` (도메인 이해)",
            "",
            "### CTO / 아키텍트",
            "- **필수**: `05_PRD_지훈.md`, `02b_전략브리프_설계자.md` (OKR·제약)",
            "- **참고**: `01_시장조사_서윤.md` (경쟁사 기술 스택)",
            "",
            "### 마케팅",
            "- **필수**: `02c_비즈니스모델_설계자.md` (STP·VPC·페르소나), `01_시장조사_서윤.md` (Pain 50개)",
            "- **참고**: `07_런칭준비.md` (있으면), `08_트렌드_태호.md`",
            "",
            "### 영업",
            "- **필수**: `02c_비즈니스모델_설계자.md` (페르소나·Pain), `01_시장조사_서윤.md`",
            "- **참고**: `02b_전략브리프_설계자.md` (킬러 오퍼)",
            "",
            "### QA",
            "- **필수**: `05_PRD_지훈.md` (기능 검증 기준)",
            "- **참고**: `03_검증_하은.md` (리스크)",
            "",
            "---",
            "",
            "## 규칙",
            "1. 작업 시작 전 자기 역할의 **필수** 파일부터 읽는다.",
            "2. 톤·페르소나·Pain Point는 기획문서가 단일 진실 공급원(Single Source of Truth).",
            "3. 기획문서와 충돌하는 결과물 만들지 않는다.",
        ])

        return "\n".join(lines)

    def _build_claude_md(self) -> str:
        ctx = self.context
        verdict = ctx.get("verdict", "GO")
        score = ctx.get("score", "")
        is_commercial = ctx.get("is_commercial", False)

        taeho = ctx.get("taeho", "")[:400]
        seoyun = ctx.get("seoyun", "")[:600]
        minsu = ctx.get("minsu", "")[:600]
        haeun = ctx.get("haeun", "")[:400]
        junhyeok_text = ctx.get("junhyeok_text", "")[:400]

        date_str = datetime.now().strftime("%Y-%m-%d")
        project_type = "상용화" if is_commercial else "개인 툴"

        return f"""# {self.project_name} — UltraProduct 브리핑

> 생성일: {date_str}
> 이사팀 판정: {verdict} ({score}점)
> 프로젝트 유형: {project_type}

---

## 이 파일 사용법

`/work` 명령어 실행 시 **반드시 이 순서로** 읽어라:

1. **`기획문서/INDEX.md`** — 이사팀이 만든 15개 문서의 핵심 요약 (4줄씩)
2. `PRD.md` — 지훈 PRD 전문 (기능 목록)
3. 이 파일 (아이디어·판정·지시)

Wave 1~2 기획 완료. **Wave 3 (CTO 아키텍처)부터 시작**.

**⚠️ 단일 진실 공급원 원칙:**
- 페르소나·Pain·톤·숫자는 `기획문서/INDEX.md` 가 기준
- 부족하면 `기획문서/{{파일명}}` 원본 지정 로드
- INDEX와 충돌하는 결과물 만들지 마라
- 실측 결과: INDEX 하나만 읽어도 기획 핵심 전달 90% 보장

---

## 아이디어 원문

{ctx.get("clarified", ctx.get("idea", ""))}

---

## 이사팀 분석 요약

### 트렌드 (태호)
{taeho}

### 시장조사 (서윤)
{seoyun}

### 전략/수익모델 (민수)
{minsu}

### 검증/반론 (하은)
{haeun}

### 최종 판단 (준혁)
{junhyeok_text}

---

## PRD 요약

PRD 전문은 `PRD.md` 참조.

---

## UltraProduct 실행 지시

- **시작 Wave**: Wave 3 (CTO 아키텍처 + CDO Stitch 디자인)
- **프로젝트 유형**: {project_type}
- **Wave 5 마케팅**: {"실행" if is_commercial else "스킵 (개인 툴)"}
- **CDO 작업**: Stitch MCP로 디자인 생성 → DESIGN.md → 민준(FE) 핸드오프

---

## 핵심 원칙

- 리안은 비개발자 CEO. 개입 최소화.
- PRD.md의 Must Have 기능만 구현. 범위 확장 금지.
- Cloudflare Pages/Workers/D1/R2 스택 사용. Vercel/Supabase 금지.
"""
