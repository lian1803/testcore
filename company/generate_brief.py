#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
사업기획서 HTML 생성기
md 파일들 → Claude API → 17개 핵심 섹션 요약 HTML

사용법:
    python generate_brief.py outputs/2026-04-13_xxx
    python generate_brief.py --latest
    python generate_brief.py --all
"""

import os, sys, io, json, re
from pathlib import Path
from datetime import datetime

if sys.platform == "win32":
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    except: pass

try:
    import markdown as md_lib
    HAS_MARKDOWN = True
except ImportError:
    HAS_MARKDOWN = False

# ── HTML 템플릿 ──────────────────────────────────────────────────────────────

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — 사업기획서</title>
<link href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable.min.css" rel="stylesheet">
<style>
:root {{
  --bg: #f5f5f7;
  --panel: #ffffff;
  --text: #1d1d1f;
  --muted: #6e6e73;
  --border: #e5e5ea;
  --accent: #0066cc;
  --accent-dim: #0066cc12;
  --go: #00875a;
  --cond: #c07700;
  --nogo: #c0392b;
  --shadow: 0 1px 3px rgba(0,0,0,0.04), 0 4px 20px rgba(0,0,0,0.04);
}}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html {{ scroll-behavior: smooth; }}
body {{
  font-family: 'Pretendard Variable', Pretendard, -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.75;
  font-size: 15px;
  -webkit-font-smoothing: antialiased;
}}

/* ── 레이아웃 ── */
.layout {{
  display: grid;
  grid-template-columns: 240px 1fr;
  gap: 32px;
  max-width: 1280px;
  margin: 0 auto;
  padding: 40px 24px;
}}
@media (max-width: 900px) {{
  .layout {{ grid-template-columns: 1fr; gap: 20px; padding: 20px 16px; }}
  nav.toc {{ position: static !important; max-height: none !important; }}
}}

/* ── TOC ── */
nav.toc {{
  position: sticky;
  top: 24px;
  align-self: start;
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 20px 14px;
  max-height: calc(100vh - 48px);
  overflow-y: auto;
  box-shadow: var(--shadow);
}}
nav.toc .toc-label {{
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--muted);
  font-weight: 700;
  padding: 0 8px;
  margin-bottom: 10px;
  display: block;
}}
nav.toc a {{
  display: block;
  padding: 6px 8px;
  color: var(--text);
  text-decoration: none;
  font-size: 13px;
  border-radius: 7px;
  margin-bottom: 1px;
  transition: background 0.15s;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}}
nav.toc a:hover {{ background: var(--accent-dim); color: var(--accent); }}
nav.toc .toc-divider {{ height: 1px; background: var(--border); margin: 10px 0; }}

/* ── 히어로 헤더 ── */
header.hero {{
  background: linear-gradient(135deg, #fff 0%, #f0f7ff 100%);
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: 40px 44px 36px;
  margin-bottom: 24px;
  box-shadow: var(--shadow);
}}
header.hero .eyebrow {{
  font-size: 11px;
  color: var(--muted);
  letter-spacing: 0.12em;
  text-transform: uppercase;
  font-weight: 600;
  margin-bottom: 10px;
}}
header.hero h1 {{
  font-size: 28px;
  font-weight: 700;
  line-height: 1.3;
  letter-spacing: -0.02em;
  margin-bottom: 20px;
}}
.meta {{ display: flex; gap: 16px; flex-wrap: wrap; color: var(--muted); font-size: 13px; align-items: center; }}
.meta strong {{ color: var(--text); }}
.badge {{
  display: inline-block;
  padding: 4px 12px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.02em;
}}
.badge-go {{ background: #00875a22; color: var(--go); }}
.badge-cond {{ background: #c0770022; color: var(--cond); }}
.badge-nogo {{ background: #c0392b22; color: var(--nogo); }}

/* ── 17개 섹션 그리드 ── */
.sections-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 16px;
  margin-bottom: 28px;
}}
.card {{
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 24px 28px;
  box-shadow: var(--shadow);
  word-wrap: break-word;
  overflow-wrap: break-word;
}}
.card .card-header {{
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 14px;
  padding-bottom: 12px;
  border-bottom: 2px solid var(--accent-dim);
}}
.card .card-no {{
  font-size: 11px;
  font-weight: 700;
  color: var(--accent);
  background: var(--accent-dim);
  padding: 2px 8px;
  border-radius: 999px;
  letter-spacing: 0.06em;
  flex-shrink: 0;
}}
.card .card-title {{
  font-size: 14px;
  font-weight: 700;
  color: var(--text);
  line-height: 1.3;
}}
.card .card-body {{ font-size: 14px; line-height: 1.7; color: var(--text); }}
.card .card-body p {{ margin: 8px 0; }}
.card .card-body ul, .card .card-body ol {{ padding-left: 18px; margin: 8px 0; }}
.card .card-body li {{ margin: 4px 0; }}
.card .card-body strong {{ font-weight: 700; }}
.card .card-body table {{ width: 100%; border-collapse: collapse; margin: 10px 0; font-size: 13px; }}
.card .card-body th, .card .card-body td {{ border: 1px solid var(--border); padding: 7px 10px; text-align: left; vertical-align: top; }}
.card .card-body th {{ background: var(--accent-dim); font-weight: 700; }}
.card .card-body tr:nth-child(even) td {{ background: #fafafa; }}
.card .card-body blockquote {{ border-left: 3px solid var(--accent); margin: 10px 0; padding: 8px 14px; background: var(--accent-dim); border-radius: 0 8px 8px 0; }}

/* 1번 카드 (한 줄 설명) — 강조 */
.card.card-1 {{
  grid-column: 1 / -1;
  background: linear-gradient(135deg, #fff9e6 0%, #fff 100%);
  border: 2px solid #f0c000;
  box-shadow: 0 4px 20px rgba(240,192,0,0.12);
}}
.card.card-1 .card-header {{ border-bottom-color: #f0c00030; }}
.card.card-1 .card-title {{ font-size: 16px; }}

/* 17번 카드 (판정) — 강조 */
.card.card-17 {{ border-color: var(--accent); }}
.card.card-17 .card-header {{ border-bottom-color: #0066cc30; }}

/* ── 상세 섹션 (접기) ── */
.detail-label {{
  text-align: center;
  color: var(--muted);
  font-size: 13px;
  margin: 8px 0 20px;
}}
details.collapsible {{
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 14px;
  margin-bottom: 12px;
  box-shadow: var(--shadow);
  overflow: hidden;
}}
details.collapsible > summary {{
  padding: 18px 28px;
  cursor: pointer;
  font-size: 15px;
  font-weight: 600;
  color: var(--muted);
  list-style: none;
  user-select: none;
  display: flex;
  align-items: center;
  gap: 10px;
  transition: background 0.15s;
}}
details.collapsible > summary:hover {{ background: var(--accent-dim); color: var(--accent); }}
details.collapsible > summary::-webkit-details-marker {{ display: none; }}
details.collapsible > summary::before {{
  content: "▸";
  font-size: 11px;
  transition: transform 0.2s;
  color: var(--accent);
  flex-shrink: 0;
}}
details.collapsible[open] > summary::before {{ transform: rotate(90deg); }}
details.collapsible[open] > summary {{ border-bottom: 1px solid var(--border); }}
details.collapsible > .content {{
  padding: 28px 40px 36px;
  word-wrap: break-word;
  overflow-wrap: break-word;
}}
details.collapsible .content h1 {{ font-size: 22px; margin: 0 0 20px; font-weight: 700; }}
details.collapsible .content h2 {{ font-size: 18px; margin: 28px 0 12px; font-weight: 700; padding-bottom: 8px; border-bottom: 2px solid var(--accent-dim); }}
details.collapsible .content h2:first-child {{ margin-top: 0; }}
details.collapsible .content h3 {{ font-size: 16px; margin: 20px 0 8px; font-weight: 700; }}
details.collapsible .content h4 {{ font-size: 14px; margin: 16px 0 6px; font-weight: 600; }}
details.collapsible .content p {{ margin: 8px 0; }}
details.collapsible .content ul, details.collapsible .content ol {{ padding-left: 22px; margin: 8px 0; }}
details.collapsible .content li {{ margin: 4px 0; }}
details.collapsible .content table {{ width: 100%; border-collapse: collapse; margin: 12px 0; font-size: 13px; table-layout: auto; }}
details.collapsible .content th, details.collapsible .content td {{ border: 1px solid var(--border); padding: 8px 12px; text-align: left; vertical-align: top; word-break: keep-all; }}
details.collapsible .content th {{ background: var(--accent-dim); font-weight: 700; }}
details.collapsible .content tr:nth-child(even) td {{ background: #fafafa; }}
details.collapsible .content code {{ background: #f0f0f3; padding: 2px 6px; border-radius: 5px; font-size: 13px; font-family: 'SF Mono', Menlo, Consolas, monospace; }}
details.collapsible .content pre {{ background: #1d1d1f; color: #f5f5f7; padding: 16px 18px; border-radius: 10px; overflow-x: auto; font-size: 13px; line-height: 1.6; }}
details.collapsible .content pre code {{ background: transparent; color: inherit; padding: 0; }}
details.collapsible .content blockquote {{ border-left: 4px solid var(--accent); margin: 14px 0; padding: 10px 16px; background: var(--accent-dim); border-radius: 0 8px 8px 0; }}
details.collapsible .content hr {{ border: none; border-top: 1px solid var(--border); margin: 24px 0; }}
details.collapsible .content a {{ color: var(--accent); text-decoration: none; }}
details.collapsible .content a:hover {{ text-decoration: underline; }}

.footer {{
  margin-top: 40px;
  padding: 28px 20px;
  text-align: center;
  color: var(--muted);
  font-size: 13px;
}}
@media print {{
  body {{ background: white; }}
  .layout {{ grid-template-columns: 1fr; max-width: none; padding: 0; }}
  nav.toc {{ display: none; }}
  .sections-grid {{ grid-template-columns: 1fr 1fr; }}
  .card {{ break-inside: avoid; box-shadow: none; border: 1px solid #ddd; }}
  details.collapsible {{ break-inside: avoid; box-shadow: none; border: none; }}
}}
</style>
</head>
<body>
<div class="layout">
<nav class="toc">
  <span class="toc-label">목차</span>
  <a href="#summary">📋 17개 핵심 요약</a>
  <div class="toc-divider"></div>
  {toc_details}
</nav>
<main>
<header class="hero">
  <div class="eyebrow">사업기획서 · 리안 컴퍼니</div>
  <h1>{title}</h1>
  <div class="meta">
    <span>생성일: <strong>{date}</strong></span>
    <span>·</span>
    <span>판정: <span class="badge badge-{verdict_class}">{verdict_label}</span></span>
    <span>·</span>
    <span>점수: <strong>{score}/10</strong></span>
  </div>
</header>

<div id="summary" class="sections-grid">
{cards_html}
</div>

<div class="detail-label">▼ 상세 원문 (필요할 때만 펼쳐보세요) ▼</div>
{details_html}

<div class="footer">리안 컴퍼니 자동 생성 사업기획서 · V5</div>
</main>
</div>
</body>
</html>"""


# ── 유틸 ──────────────────────────────────────────────────────────────────────

def read_file(path: Path) -> str:
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def md_to_html(text: str) -> str:
    if not text:
        return ""
    if HAS_MARKDOWN:
        return md_lib.markdown(text, extensions=["tables", "fenced_code", "nl2br", "sane_lists"])
    import html
    return f"<pre>{html.escape(text)}</pre>"


def extract_title(folder: Path) -> str:
    name = folder.name
    m = re.match(r"\d{4}-\d{2}-\d{2}_\d{6}_(.*)", name)
    if m:
        return m.group(1).rstrip("_").replace("_", " ")
    return name


# ── 17개 섹션 생성 (Claude API) ───────────────────────────────────────────────

SECTION_SCHEMA = [
    (1,  "📋", "한 줄 설명"),
    (2,  "🧭", "사업 성격 분류"),
    (3,  "🎯", "누구한테 팔 건가"),
    (4,  "💢", "진짜 고통 (3~5개)"),
    (5,  "💰", "얼마에 팔까"),
    (6,  "🏆", "왜 이길 수 있나"),
    (7,  "🔧", "회사 자산 활용도"),
    (8,  "📅", "언제 뭐가 보일까"),
    (9,  "💵", "돈 계산"),
    (10, "⏰", "시간 투입 (리안 주당)"),
    (11, "🚪", "첫 고객 확보 경로 (구체적)"),
    (12, "⚠️", "가장 큰 리스크 3가지 + 망하면 잃는 것"),
    (13, "🔥", "가장 어려운 1가지 (Hard Part)"),
    (14, "🚨", "피벗 신호 (언제 접을지)"),
    (15, "🏁", "출구 전략 (Exit)"),
    (16, "🚀", "내일부터 뭐 할까"),
    (17, "🧭", "준혁의 한 줄 판정"),
]


def generate_17_sections(folder: Path, client) -> list:
    """md 파일들 읽고 Claude API로 17개 섹션 JSON 생성"""

    # 핵심 파일 읽기 (각 최대 1200자)
    parts = []
    file_map = [
        ("00_이사팀_보고서.md",      "이사팀 보고서"),
        ("02_전략_민수.md",          "전략 (민수)"),
        ("02b_전략브리프_설계자.md", "전략 브리프 (설계자)"),
        ("01_시장조사_서윤.md",      "시장조사 (서윤)"),
        ("03_검증_하은.md",          "검증 (하은)"),
    ]
    for fname, label in file_map:
        txt = read_file(folder / fname)
        if txt:
            parts.append(f"=== {label} ===\n{txt[:1200]}")

    # 준혁 판정
    junhyeok_path = folder / "04_최종판단_준혁.json"
    verdict_raw = "UNKNOWN"
    score_raw = 0.0
    if junhyeok_path.exists():
        try:
            data = json.loads(junhyeok_path.read_text(encoding="utf-8"))
            verdict_raw = data.get("verdict", "UNKNOWN")
            score_raw = float(data.get("score", 0))
            jtext = data.get("text", "")
            parts.append(f"=== 준혁 최종 판단 ===\n판정: {verdict_raw} ({score_raw}/10)\n{jtext[:1500]}")
        except Exception:
            pass

    context = "\n\n".join(parts)

    schema_lines = "\n".join(
        f'  {{"no": {no}, "emoji": "{em}", "title": "{title}", "content": "..."}}'
        for no, em, title in SECTION_SCHEMA
    )

    prompt = f"""아래 사업기획 자료를 보고 17개 항목을 JSON 배열로 반환해.

자료:
{context}

반환 형식 (JSON만, 코드블록 없이):
[
{schema_lines}
]

규칙:
- content: 마크다운, **bold** + bullet 사용. 각 항목 최대 3~5줄
- 1번: 딱 한 문장 (누가/어떤문제/얼마)
- 17번: "**판정**: XX (점수/10)\\n**한 줄 이유**: ..." 형식
- 없는 정보는 자료에서 추정해서 채워. 절대 비워두지 마"""

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=6000,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.content[0].text.strip()
    raw = re.sub(r"^```\w*\n?", "", raw)
    raw = re.sub(r"\n?```$", "", raw)

    try:
        sections = json.loads(raw)
    except json.JSONDecodeError:
        # 잘린 경우: 마지막 완전한 } 까지만 파싱
        last = raw.rfind("},")
        if last == -1:
            last = raw.rfind("}")
        if last != -1:
            sections = json.loads(raw[: last + 1] + "\n]")
        else:
            raise

    return sections, verdict_raw, score_raw


# ── HTML 렌더링 ───────────────────────────────────────────────────────────────

def render_cards(sections: list) -> str:
    html_parts = []
    for sec in sections:
        no = sec.get("no", 0)
        emoji = sec.get("emoji", "")
        title = sec.get("title", "")
        content = sec.get("content", "")
        card_class = f"card card-{no}"
        body_html = md_to_html(content)
        html_parts.append(
            f'<div class="{card_class}">'
            f'  <div class="card-header">'
            f'    <span class="card-no">{no}</span>'
            f'    <span class="card-title">{emoji} {title}</span>'
            f'  </div>'
            f'  <div class="card-body">{body_html}</div>'
            f'</div>'
        )
    return "\n".join(html_parts)


def render_details(folder: Path) -> tuple[str, str]:
    """상세 원문 섹션 (접기) + TOC 항목 반환"""
    detail_defs = [
        ("strategy_minsu",    "💡 전략 방향 · 1순위 선택 (민수)",                  "02_전략_민수.md"),
        ("strategy_d1",       "🏗 심층 전략 브리프 (설계자 1회차)",                "02b_전략브리프_설계자.md"),
        ("strategy_d2",       "💼 비즈니스 모델 (설계자 2회차)",                   "02c_비즈니스모델_설계자.md"),
        ("market",            "📊 시장 분석 · Pain Point · 경쟁사 (서윤)",         "01_시장조사_서윤.md"),
        ("trends",            "🔭 트렌드 (태호)",                                  "08_트렌드_태호.md"),
        ("validation",        "🛡️ 검증 · 반론 (하은)",                            "03_검증_하은.md"),
        ("discussion",        "💬 토론 결과 (민수↔하은)",                         "03b_토론_결과.md"),
        ("judgment",          "⚖️ 최종 판단 (준혁)",                              "04_최종판단_준혁_text"),
        ("prd",               "🛠 PRD — 제품 기획 · 기술 스택 (지훈)",            "05_PRD_지훈.md"),
        ("big_picture",       "🗺 큰그림 체크 (시은)",                             "04b_큰그림체크_시은.md"),
        ("review",            "🔍 최종 재검토 (시은 델타봇)",                      "04c_최종재검토_시은.md"),
        ("launch",            "🚀 런칭 준비",                                      "07_런칭준비.md"),
        ("team",              "👥 실행 팀 구성",                                   "06_팀설계_시은.md"),
        ("board_report",      "📰 이사팀 원본 보고서",                             "00_이사팀_보고서.md"),
    ]

    details_html = []
    toc_items = []

    for anchor, label, fname in detail_defs:
        if fname == "04_최종판단_준혁_text":
            jpath = folder / "04_최종판단_준혁.json"
            if not jpath.exists():
                continue
            try:
                data = json.loads(jpath.read_text(encoding="utf-8"))
                content = data.get("text", "")
            except Exception:
                continue
        else:
            content = read_file(folder / fname)
            if not content or not content.strip() or content.strip().startswith("["):
                continue

        toc_items.append(f'<a href="#{anchor}">{label}</a>')
        body = md_to_html(content)
        details_html.append(
            f'<details class="collapsible" id="{anchor}">'
            f'<summary>{label}</summary>'
            f'<div class="content">{body}</div>'
            f'</details>'
        )

    return "\n".join(details_html), "\n".join(toc_items)


# ── 메인 생성 함수 ────────────────────────────────────────────────────────────

def generate_report(folder: Path, client=None) -> Path:
    from dotenv import load_dotenv
    load_dotenv()

    if client is None:
        import anthropic
        client = anthropic.Anthropic()

    print(f"  ⚡ 17개 섹션 생성 중...")
    sections, verdict_raw, score_raw = generate_17_sections(folder, client)

    verdict_map = {
        "GO": ("go", "GO ✓"),
        "CONDITIONAL_GO": ("cond", "조건부 GO"),
        "NO_GO": ("nogo", "NO-GO"),
    }
    verdict_class, verdict_label = verdict_map.get(verdict_raw, ("cond", verdict_raw))

    cards_html = render_cards(sections)
    details_html, toc_details = render_details(folder)

    html = HTML_TEMPLATE.format(
        title=extract_title(folder),
        date=datetime.now().strftime("%Y-%m-%d"),
        verdict_class=verdict_class,
        verdict_label=verdict_label,
        score=f"{score_raw:.2f}",
        cards_html=cards_html,
        details_html=details_html,
        toc_details=toc_details,
    )

    out = folder / "사업기획서.html"
    out.write_text(html, encoding="utf-8")
    return out


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    from dotenv import load_dotenv
    load_dotenv()
    import anthropic

    outputs_dir = Path(__file__).resolve().parent / "outputs"
    if not outputs_dir.exists():
        print(f"❌ outputs 폴더 없음: {outputs_dir}")
        sys.exit(1)

    all_dirs = sorted(
        [d for d in outputs_dir.iterdir() if d.is_dir()],
        key=lambda d: d.stat().st_mtime,
        reverse=True,
    )

    if not all_dirs:
        print("❌ outputs 폴더가 비었어")
        sys.exit(1)

    if len(sys.argv) > 1 and sys.argv[1] == "--all":
        targets = all_dirs
    elif len(sys.argv) > 1 and sys.argv[1] == "--latest":
        targets = [all_dirs[0]]
    elif len(sys.argv) > 1:
        p = Path(sys.argv[1])
        if not p.is_absolute():
            p = outputs_dir / p.name
        targets = [p]
    else:
        targets = [all_dirs[0]]

    client = anthropic.Anthropic()
    generated = []

    for folder in targets:
        try:
            print(f"\n🔨 {folder.name}")
            out = generate_report(folder, client)
            generated.append(out)
            print(f"  ✅ → {out}")
        except Exception as e:
            import traceback
            print(f"  ❌ {folder.name}: {e}")
            traceback.print_exc()

    print(f"\n총 {len(generated)}개 완료")


if __name__ == "__main__":
    main()
