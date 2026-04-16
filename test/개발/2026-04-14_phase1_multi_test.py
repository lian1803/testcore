#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 1 다각도 검증 스크립트 — 리안 밥 먹는 동안 돌릴 종합 테스트.

Test 1: 다른 역할 검증 (FE, BE, sales) — 토지분석 기반
Test 2: 다른 도메인 검증 — 혜경 대시보드로 marketing 재실행
Test 3: 할루시네이션 정밀 검증 — AFTER 결과물의 숫자·명사 역검색 (코드만)
Test 4: 랜덤성 검증 — 같은 입력 AFTER 3회, 품질 일관성
Test 5: 파일 수 증가 효과 — marketing 2개 vs 5개 비교

결과: phase1_results/multi_test_{timestamp}/
"""
import sys
import os
import io
import json
import shutil
from pathlib import Path
from datetime import datetime

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

COMPANY_DIR = Path(__file__).resolve().parents[2] / "company"
CORE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(COMPANY_DIR))
os.chdir(str(COMPANY_DIR))

from dotenv import load_dotenv
load_dotenv(COMPANY_DIR / ".env")

import anthropic
from core.context_loader import load_planning_docs
from core.handoff import PipelineHandoff

MODEL = "claude-sonnet-4-5-20250929"
RESULTS_DIR = Path(__file__).parent / "phase1_results" / f"multi_{datetime.now():%H%M%S}"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


# ── 역할별 시스템 프롬프트 + 태스크 ──────────────────────────────

ROLE_TASKS = {
    "marketing": {
        "system": """너는 B2B SaaS 마케팅 카피라이터.
랜딩 페이지 히어로 섹션 카피를 작성해.

형식:
[헤드라인] 25자 이내
[서브헤드] 60~100자
[CTA 버튼] 12자 이내
[핵심 가치 Bullet 3개] 각 20자 이내

규칙:
- 구체 페르소나 의식
- Pain은 숫자로 (금액·시간·비율)
- "AI/자동화/혁신/스마트/차세대" 금지
- 추상 표현 금지, 구체 명사·숫자 중심
""",
        "user_suffix": "위 context 읽고 랜딩 히어로 카피 작성.",
    },
    "fe": {
        "system": """너는 시니어 프론트엔드 아키텍트.
제품의 랜딩 페이지 컴포넌트 계층을 설계해.

형식:
## 컴포넌트 트리
```
<Page>
  <Section1 />
  ...
</Page>
```

## 각 섹션 목적 (2~3줄씩)
1. Section1: [페르소나가 여기서 뭘 느껴야 하는지]
2. ...

규칙:
- 섹션 5~7개
- 각 섹션이 기획의 어떤 Pain Point/Value를 겨냥하는지 구체적으로
- 단순 "About, Features, Pricing" 같은 템플릿 금지
""",
        "user_suffix": "위 context 읽고 랜딩 페이지 컴포넌트 계층 설계.",
    },
    "be": {
        "system": """너는 시니어 백엔드 엔지니어.
MVP P0 기능 기준으로 핵심 API 엔드포인트 5개를 설계해.

형식:
| # | Method | Path | 역할 | Request | Response |
|---|--------|------|------|---------|----------|

각 엔드포인트 아래:
- 기획의 어떤 P0 기능을 구현하는지 한 줄
- 예상 부하/지연 주의점 한 줄

규칙:
- 기획의 실제 기능 기반 (일반적 CRUD 금지)
- 에러 응답 코드 명시
""",
        "user_suffix": "위 context 읽고 MVP P0 기반 API 엔드포인트 5개 설계.",
    },
    "sales": {
        "system": """너는 B2B 엔터프라이즈 세일즈 전문가.
타겟 페르소나에게 보낼 콜드 메일 3종을 작성해.

형식:
## Short (80자, 3문장 이내)
[subject]
[body]

## Medium (200자, 5~7문장)
[subject]
[body]

## Long (400자 이내, hook-pain-solution-CTA)
[subject]
[body]

규칙:
- 페르소나 호명 구체적으로
- Pain을 숫자로 찍음
- 일반 영업 클리셰 금지 ("혹시 시간 되시면", "귀사의 성공을 기원" 금지)
- CTA는 구체 (15분 미팅 + 날짜 제안)
""",
        "user_suffix": "위 context 읽고 콜드메일 3종 작성.",
    },
}


# ── 유틸 ────────────────────────────────────────────────────────

def call_claude(system: str, user: str, max_tokens: int = 1500) -> dict:
    """단일 API 호출."""
    resp = client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return {
        "text": resp.content[0].text,
        "in": resp.usage.input_tokens,
        "out": resp.usage.output_tokens,
    }


def prepare_project(project_src: Path, project_slug: str) -> Path:
    """바탕화면 기획 → company/outputs/ 복사 후 PipelineHandoff 돌려서 team/ 준비."""
    outputs_path = COMPANY_DIR / "outputs" / project_slug
    if outputs_path.exists():
        shutil.rmtree(outputs_path)
    outputs_path.mkdir(parents=True)

    for f in project_src.iterdir():
        if f.is_file():
            shutil.copy2(f, outputs_path / f.name)

    # Handoff 실행
    prd_file = outputs_path / "05_PRD_지훈.md"
    prd_content = prd_file.read_text(encoding="utf-8") if prd_file.exists() else ""

    context = {
        "idea": project_slug,
        "prd": prd_content,
        "verdict": "GO",
        "score": 7.5,
        "is_commercial": True,
        "is_software": True,
        "clarified": project_slug,
        "taeho": "", "seoyun": "", "minsu": "", "haeun": "", "junhyeok_text": "",
    }
    handoff = PipelineHandoff(context, str(outputs_path))
    project_dir = handoff.generate()
    return Path(project_dir)


def get_before_context(team_dir: Path) -> str:
    claude_md = (team_dir / "CLAUDE.md").read_text(encoding="utf-8")
    prd = (team_dir / "PRD.md").read_text(encoding="utf-8")
    return f"{claude_md}\n\n---\n\n# PRD\n{prd}"


def keyword_match_score(text: str, keywords: list) -> dict:
    hits = [kw for kw in keywords if kw in text]
    return {
        "hits": len(hits),
        "total": len(keywords),
        "matched": hits,
    }


# ── Test 1: 다른 역할 검증 ─────────────────────────────────────

def test_1_roles(team_dir: Path, keywords: list) -> dict:
    print("\n" + "=" * 70)
    print("TEST 1: 다른 역할 검증 (FE, BE, sales)")
    print("=" * 70)

    before_ctx = get_before_context(team_dir)
    results = {}

    for role in ["fe", "be", "sales"]:
        task = ROLE_TASKS[role]
        after_ctx = load_planning_docs(str(team_dir), role=role)

        before_user = f"{task['user_suffix']}\n\n=== context ===\n{before_ctx}"
        after_user = f"{task['user_suffix']}\n\n=== context ===\n{after_ctx}"

        print(f"\n[{role}] BEFORE 호출...")
        b = call_claude(task["system"], before_user)
        print(f"[{role}] AFTER  호출...")
        a = call_claude(task["system"], after_user)

        b_score = keyword_match_score(b["text"], keywords)
        a_score = keyword_match_score(a["text"], keywords)

        results[role] = {
            "before": {**b, "score": b_score},
            "after": {**a, "score": a_score},
            "improvement": a_score["hits"] - b_score["hits"],
        }

        print(f"  키워드: BEFORE={b_score['hits']}/{b_score['total']}, AFTER={a_score['hits']}/{a_score['total']} (+{results[role]['improvement']})")

        # 저장
        (RESULTS_DIR / f"test1_{role}_before.md").write_text(b["text"], encoding="utf-8")
        (RESULTS_DIR / f"test1_{role}_after.md").write_text(a["text"], encoding="utf-8")

    return results


# ── Test 2: 다른 도메인 (혜경 대시보드) ─────────────────────────

def test_2_domain(team_dir: Path, keywords: list) -> dict:
    print("\n" + "=" * 70)
    print("TEST 2: 다른 도메인 검증 (혜경 대시보드)")
    print("=" * 70)

    before_ctx = get_before_context(team_dir)
    after_ctx = load_planning_docs(str(team_dir), role="marketing")

    task = ROLE_TASKS["marketing"]
    before_user = f"{task['user_suffix']}\n\n=== context ===\n{before_ctx}"
    after_user = f"{task['user_suffix']}\n\n=== context ===\n{after_ctx}"

    print("[marketing] BEFORE 호출...")
    b = call_claude(task["system"], before_user)
    print("[marketing] AFTER  호출...")
    a = call_claude(task["system"], after_user)

    b_score = keyword_match_score(b["text"], keywords)
    a_score = keyword_match_score(a["text"], keywords)

    print(f"  키워드: BEFORE={b_score['hits']}/{b_score['total']}, AFTER={a_score['hits']}/{a_score['total']}")

    (RESULTS_DIR / "test2_domain_before.md").write_text(b["text"], encoding="utf-8")
    (RESULTS_DIR / "test2_domain_after.md").write_text(a["text"], encoding="utf-8")

    return {
        "before": {**b, "score": b_score},
        "after": {**a, "score": a_score},
        "improvement": a_score["hits"] - b_score["hits"],
    }


# ── Test 3: 할루시네이션 정밀 검증 ──────────────────────────────

def test_3_hallucination(text: str, planning_dir: Path) -> dict:
    """AFTER 카피의 숫자·고유명이 기획문서에 실제로 있는지 역검색."""
    print("\n" + "=" * 70)
    print("TEST 3: 할루시네이션 정밀 검증 (AFTER 카피 역검색)")
    print("=" * 70)

    # 기획문서 전체 텍스트 합치기
    all_planning_text = ""
    for f in planning_dir.glob("*.md"):
        all_planning_text += f.read_text(encoding="utf-8")

    # 숫자·퍼센트·금액 패턴 추출
    import re
    patterns = {
        "숫자+%": re.findall(r"\d+%", text),
        "숫자+만원": re.findall(r"\d+만원", text),
        "숫자+억": re.findall(r"\d+억", text),
        "숫자+시간": re.findall(r"\d+시간", text),
        "숫자+일": re.findall(r"\d+일", text),
        "숫자+개월": re.findall(r"\d+개월", text),
    }

    verified = {}
    for kind, values in patterns.items():
        verified[kind] = {"all": list(set(values)), "in_planning": [], "fabricated": []}
        for v in set(values):
            if v in all_planning_text:
                verified[kind]["in_planning"].append(v)
            else:
                verified[kind]["fabricated"].append(v)

    # 출력
    total_all = 0
    total_verified = 0
    for kind, d in verified.items():
        if d["all"]:
            print(f"\n  {kind}: {d['all']}")
            print(f"    ✓ 기획문서에 있음: {d['in_planning']}")
            if d["fabricated"]:
                print(f"    ✗ 지어낸 것 의심: {d['fabricated']}")
            total_all += len(d["all"])
            total_verified += len(d["in_planning"])

    print(f"\n  전체 숫자 표현 {total_all}개 중 {total_verified}개 검증됨 ({100*total_verified/max(total_all,1):.0f}%)")

    return verified


# ── Test 4: 랜덤성 검증 (AFTER 3회) ─────────────────────────────

def test_4_consistency(team_dir: Path, keywords: list) -> dict:
    print("\n" + "=" * 70)
    print("TEST 4: 랜덤성 검증 (AFTER marketing 3회 호출)")
    print("=" * 70)

    after_ctx = load_planning_docs(str(team_dir), role="marketing")
    task = ROLE_TASKS["marketing"]
    user_msg = f"{task['user_suffix']}\n\n=== context ===\n{after_ctx}"

    results = []
    for i in range(3):
        print(f"  AFTER 호출 {i+1}/3...")
        r = call_claude(task["system"], user_msg)
        score = keyword_match_score(r["text"], keywords)
        results.append({**r, "score": score})
        (RESULTS_DIR / f"test4_after_run{i+1}.md").write_text(r["text"], encoding="utf-8")
        print(f"    키워드: {score['hits']}/{score['total']}")

    hits = [r["score"]["hits"] for r in results]
    print(f"\n  분산: min={min(hits)}, max={max(hits)}, 평균={sum(hits)/3:.1f}")

    return results


# ── Test 5: 파일 수 증가 효과 ───────────────────────────────────

def test_5_file_count(team_dir: Path, keywords: list) -> dict:
    print("\n" + "=" * 70)
    print("TEST 5: 파일 수 증가 효과 (marketing 2 vs 5개)")
    print("=" * 70)

    # 현재 로직 (2개)
    ctx_2 = load_planning_docs(str(team_dir), role="marketing")

    # 5개로 늘린 버전 — 수동 조합
    planning_dir = team_dir / "기획문서"
    files_5 = [
        "02c_비즈니스모델_설계자.md",
        "01_시장조사_서윤.md",
        "02b_전략브리프_설계자.md",
        "04b_큰그림체크_시은.md",
        "08_트렌드_태호.md",
    ]
    parts = []
    total = 0
    max_chars = 50000
    for fn in files_5:
        fp = planning_dir / fn
        if not fp.exists():
            continue
        text = fp.read_text(encoding="utf-8")
        section = f"## {fn}\n\n{text}"
        if total + len(section) > max_chars:
            remaining = max_chars - total
            if remaining > 500:
                parts.append(section[:remaining] + "\n\n...(잘림)")
            break
        parts.append(section)
        total += len(section)
    ctx_5 = "=== 기획문서 (marketing, 5파일) ===\n\n" + "\n\n---\n\n".join(parts)

    task = ROLE_TASKS["marketing"]
    user_2 = f"{task['user_suffix']}\n\n{ctx_2}"
    user_5 = f"{task['user_suffix']}\n\n{ctx_5}"

    print(f"  context 길이: 2파일={len(ctx_2)}, 5파일={len(ctx_5)}")
    print("  2파일 호출...")
    r2 = call_claude(task["system"], user_2)
    print("  5파일 호출...")
    r5 = call_claude(task["system"], user_5)

    s2 = keyword_match_score(r2["text"], keywords)
    s5 = keyword_match_score(r5["text"], keywords)

    print(f"  2파일: {s2['hits']}/{s2['total']}, in={r2['in']}, out={r2['out']}")
    print(f"  5파일: {s5['hits']}/{s5['total']}, in={r5['in']}, out={r5['out']}")
    print(f"  차이: +{s5['hits'] - s2['hits']} 키워드")

    (RESULTS_DIR / "test5_2files.md").write_text(r2["text"], encoding="utf-8")
    (RESULTS_DIR / "test5_5files.md").write_text(r5["text"], encoding="utf-8")

    return {
        "2_files": {**r2, "score": s2},
        "5_files": {**r5, "score": s5},
        "improvement": s5["hits"] - s2["hits"],
    }


# ── Main ─────────────────────────────────────────────────────────

def main():
    # 토지분석: 이미 준비됨 (team/phase1_test_토지분석)
    land_team = CORE_DIR.parent / "team" / "phase1_test_토지분석"

    land_keywords = [
        "김철수", "시행사", "인허가", "5억", "48시간", "75%",
        "컨설턴트", "500만원", "69만원", "2주", "거절", "대표", "매입", "특례법",
        "중소", "수도권",
    ]

    # 혜경 대시보드: 새로 준비
    hk_src = Path(r"C:\Users\lian1\Desktop\사업기획서_결과\혜경_인하우스마케터_대시보드")
    print("\n혜경 대시보드 기획 준비 중...")
    hk_team = prepare_project(hk_src, "phase1_test_혜경대시보드")
    print(f"  → {hk_team}")

    hk_keywords = []
    # 혜경 대시보드 기획에서 키워드 추출
    planning_dir = hk_team / "기획문서"
    if planning_dir.exists():
        # 02c에서 페르소나·숫자 몇 개 뽑기
        bm_file = planning_dir / "02c_비즈니스모델_설계자.md"
        if bm_file.exists():
            import re
            text = bm_file.read_text(encoding="utf-8")
            # 숫자+만원 / 숫자+% / 숫자+시간 / 숫자+명
            nums = re.findall(r"\d+[만억]원|\d+%|\d+시간|\d+명|\d+건", text)
            hk_keywords = list(set(nums))[:12]
    if not hk_keywords:
        hk_keywords = ["마케터", "프리랜서", "대시보드", "만원", "시간"]

    print(f"\n토지분석 키워드: {land_keywords[:8]}...")
    print(f"혜경 키워드: {hk_keywords}")

    # ── Test 실행 ──
    all_results = {}

    try:
        all_results["test_1_roles"] = test_1_roles(land_team, land_keywords)
    except Exception as e:
        print(f"\n⚠️  Test 1 실패: {e}")
        all_results["test_1_roles"] = {"error": str(e)}

    try:
        all_results["test_2_domain"] = test_2_domain(hk_team, hk_keywords)
    except Exception as e:
        print(f"\n⚠️  Test 2 실패: {e}")
        all_results["test_2_domain"] = {"error": str(e)}

    # Test 3: marketing AFTER 카피 (단계 2 결과) 재사용 가능 or 새로 생성
    try:
        # 단계 2 AFTER 결과 재사용
        after_file = Path(__file__).parent / "phase1_results" / "after.md"
        if after_file.exists():
            after_text = after_file.read_text(encoding="utf-8")
            planning_dir = land_team / "기획문서"
            all_results["test_3_hallucination"] = test_3_hallucination(after_text, planning_dir)
    except Exception as e:
        print(f"\n⚠️  Test 3 실패: {e}")
        all_results["test_3_hallucination"] = {"error": str(e)}

    try:
        all_results["test_4_consistency"] = test_4_consistency(land_team, land_keywords)
    except Exception as e:
        print(f"\n⚠️  Test 4 실패: {e}")
        all_results["test_4_consistency"] = {"error": str(e)}

    try:
        all_results["test_5_file_count"] = test_5_file_count(land_team, land_keywords)
    except Exception as e:
        print(f"\n⚠️  Test 5 실패: {e}")
        all_results["test_5_file_count"] = {"error": str(e)}

    # 결과 저장 (요약)
    summary = {
        "timestamp": datetime.now().isoformat(),
        "results_dir": str(RESULTS_DIR),
        "tests": {},
    }

    if "test_1_roles" in all_results and "error" not in all_results["test_1_roles"]:
        summary["tests"]["test_1_roles"] = {
            role: {
                "before_hits": r["before"]["score"]["hits"],
                "after_hits": r["after"]["score"]["hits"],
                "improvement": r["improvement"],
            }
            for role, r in all_results["test_1_roles"].items()
        }

    if "test_2_domain" in all_results and "error" not in all_results["test_2_domain"]:
        r = all_results["test_2_domain"]
        summary["tests"]["test_2_domain"] = {
            "before_hits": r["before"]["score"]["hits"],
            "after_hits": r["after"]["score"]["hits"],
            "improvement": r["improvement"],
        }

    if "test_3_hallucination" in all_results and "error" not in all_results["test_3_hallucination"]:
        r = all_results["test_3_hallucination"]
        total_all = sum(len(d["all"]) for d in r.values())
        total_verified = sum(len(d["in_planning"]) for d in r.values())
        summary["tests"]["test_3_hallucination"] = {
            "total_numerics": total_all,
            "verified_in_planning": total_verified,
            "fabrication_rate": round(1 - total_verified / max(total_all, 1), 2),
        }

    if "test_4_consistency" in all_results and "error" not in all_results["test_4_consistency"]:
        runs = all_results["test_4_consistency"]
        hits = [r["score"]["hits"] for r in runs]
        summary["tests"]["test_4_consistency"] = {
            "hits_per_run": hits,
            "min": min(hits),
            "max": max(hits),
            "avg": sum(hits) / len(hits),
        }

    if "test_5_file_count" in all_results and "error" not in all_results["test_5_file_count"]:
        r = all_results["test_5_file_count"]
        summary["tests"]["test_5_file_count"] = {
            "2_files_hits": r["2_files"]["score"]["hits"],
            "5_files_hits": r["5_files"]["score"]["hits"],
            "improvement": r["improvement"],
            "in_tokens_2": r["2_files"]["in"],
            "in_tokens_5": r["5_files"]["in"],
        }

    (RESULTS_DIR / "SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print("\n" + "=" * 70)
    print("종합 요약")
    print("=" * 70)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"\n결과 전체: {RESULTS_DIR}")


if __name__ == "__main__":
    main()
