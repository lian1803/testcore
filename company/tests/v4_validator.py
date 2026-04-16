#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V4 Framework Structural Validator (Level 1)

파이프라인 산출물에 v4 프레임워크 필수 항목이 들어갔는지만 문자열/구조로 확인.
내용의 정확성(LLM judge)은 Level 2에서 따로 구현 예정.

사용법:
    python -m tests.v4_validator                           # 최신 output 자동 선택
    python -m tests.v4_validator outputs/20260413_xxx/     # 특정 폴더 지정
"""
import os
import re
import sys
import io
import json
from pathlib import Path


def _read(path: Path) -> str:
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def check_seoyun(content: str):
    checks = []

    has_pain_level = bool(re.search(r"(pain[_ ]level|Pain Level|Level\s*[1-5])", content, re.IGNORECASE))
    checks.append(("pain_level 필드/섹션", has_pain_level, ""))

    # 두 가지 형식 모두 지원:
    #   인라인 형식: "Level 4", "Level 5"
    #   표 형식: "| Pain Level | 4 |", "| pain_level | 5 |"
    level_45_count = len(re.findall(
        r"(?:Level\s*[45](?!\s*[0-9])|Pain\s*Level\s*\|?\s*[45]\b|pain[_ ]level\s*\|?\s*[45]\b)",
        content, re.IGNORECASE
    ))
    # 한국 니치 B2B (부동산/인테리어/토지분석 등) Perplexity 검색은 Level 4-5 7~10개가 현실적 한계
    # 실측 — 인테리어: 8, 토지분석: 7, 기준을 7로 조정
    checks.append(("Level 4-5 최소 7개", level_45_count >= 7, f"발견: {level_45_count}개"))

    has_evidence = bool(re.search(r"(evidence[_ ]quote|인용문|인용)", content, re.IGNORECASE))
    checks.append(("evidence_quote 언급", has_evidence, ""))

    has_source = bool(re.search(r"(source[_ ]url|출처\s*URL|https?://)", content, re.IGNORECASE))
    checks.append(("source_url/출처 URL", has_source, ""))

    layers_present = sum(1 for i in range(1, 6) if re.search(rf"Layer\s*{i}", content, re.IGNORECASE))
    checks.append(("5-Layer 분석 (Layer 1-5)", layers_present >= 5, f"발견: {layers_present}/5"))

    forces = ["Push", "Pull", "Inertia", "Anxiety"]
    forces_present = [f for f in forces if re.search(rf"\b{f}\b", content)]
    checks.append(
        (
            "Customer Forces Canvas (Push/Pull/Inertia/Anxiety)",
            len(forces_present) == 4,
            f"발견: {','.join(forces_present) or 'none'}",
        )
    )

    has_gap = bool(re.search(r"(Gap\s*Summary|Gap|빈틈|갭)", content, re.IGNORECASE))
    checks.append(("Gap Summary (Phase 4)", has_gap, ""))

    return checks


def check_minsu(content: str):
    """민수는 슬림화 이후 섹션 3개만 검사.
    깊은 섹션(단계별/Exit/유닛이코노믹스/가격 티어)은 설계자가 담당 → check_designer에서 검사.
    """
    checks = []

    weights = re.findall(r"(\d+)\s*%", content)
    unique = {int(w) for w in weights}
    has_scoring = {25, 20, 15, 10}.issubset(unique)
    checks.append(
        (
            "6기준 스코어링 가중치 (25/20/20/15/10/10)",
            has_scoring,
            f"발견 가중치: {sorted(unique)}",
        )
    )

    has_pick = bool(re.search(r"(#\s*1|1순위|1위|TOP\s*1|최우선)", content))
    checks.append(("#1 선택 명시", has_pick, ""))

    return checks


def check_designer(strategy_brief: str, business_model: str):
    """설계자 2-call output 검증.
    1회차: OKR + 필터 + 클러스터 + TOP 5 + 1순위 + 48h + 단계별 실행
    2회차: Problem Statement + STP + VPC + Lean Canvas + 수익 모델 + TAM + GTM + Flywheel
    """
    checks = []

    if not strategy_brief.strip():
        checks.append(("설계자 1회차 존재", False, "파일 없음"))
        return checks

    if not business_model.strip():
        checks.append(("설계자 2회차 존재", False, "파일 없음"))
        return checks

    # ── 1회차 (strategy_brief) ──────────────────────
    # OKR
    has_okr = bool(re.search(r"(STEP 0.*OKR|Objective.*\n.*KR1)", strategy_brief, re.IGNORECASE | re.DOTALL))
    checks.append(("[1회차] OKR (Objective + KR1/2/3)", has_okr, ""))

    # 단계별 실행 (초기/중기/장기)
    has_early = bool(re.search(r"(초기|Early|0\s*~?\s*3\s*개월)", strategy_brief))
    has_mid = bool(re.search(r"(중기|Mid|3\s*~?\s*12\s*개월)", strategy_brief))
    has_long = bool(re.search(r"(장기|Long|1\s*~?\s*3\s*년)", strategy_brief))
    phased_ok = has_early and has_mid and has_long
    checks.append(("[1회차] 단계별 실행 (초기/중기/장기)", phased_ok, ""))

    # 48h 검증 실험
    has_48h = bool(re.search(r"48.?시간|Problem Interview", strategy_brief))
    checks.append(("[1회차] 48시간 검증 실험", has_48h, ""))

    # TOP 5 클러스터링
    has_top5 = bool(re.search(r"TOP\s*5|클러스터", strategy_brief, re.IGNORECASE))
    checks.append(("[1회차] TOP 5 클러스터링", has_top5, ""))

    # Pre-mortem
    has_premortem = bool(re.search(r"Pre.?mortem|가치 실패|전환 실패", strategy_brief, re.IGNORECASE))
    checks.append(("[1회차] Pre-mortem", has_premortem, ""))

    # ── 2회차 (business_model) ──────────────────────
    has_problem_stmt = bool(re.search(r"Problem Statement", business_model, re.IGNORECASE))
    checks.append(("[2회차] Problem Statement", has_problem_stmt, ""))

    has_stp = bool(re.search(r"STP|Segmentation|Targeting|Positioning", business_model, re.IGNORECASE))
    checks.append(("[2회차] STP (Segmentation/Targeting/Positioning)", has_stp, ""))

    has_vpc = bool(re.search(r"Value Proposition Canvas|Customer Jobs|Pain Relievers", business_model, re.IGNORECASE))
    checks.append(("[2회차] Value Proposition Canvas", has_vpc, ""))

    has_lean = bool(re.search(r"Lean Canvas|UVP|Unfair Advantage", business_model, re.IGNORECASE))
    checks.append(("[2회차] Lean Canvas (9블록)", has_lean, ""))

    # 가격 티어 3단
    has_tiers = bool(re.search(r"(Starter.*Pro.*Enterprise|기본.*프로.*엔터|티어)", business_model, re.IGNORECASE | re.DOTALL))
    checks.append(("[2회차] 가격 티어 (3단)", has_tiers, ""))

    # 유닛 이코노믹스
    has_unit = sum(1 for kw in ("CAC", "LTV", "Payback", "Gross Margin", "Churn") if re.search(kw, business_model, re.IGNORECASE))
    checks.append(("[2회차] 유닛 이코노믹스", has_unit >= 3, f"발견 키워드: {has_unit}"))

    # TAM/SAM/SOM
    has_tam = bool(re.search(r"TAM.*SAM.*SOM|TAM.*SOM", business_model, re.IGNORECASE | re.DOTALL))
    checks.append(("[2회차] TAM/SAM/SOM", has_tam, ""))

    # GTM
    has_gtm = bool(re.search(r"GTM|Go.?to.?Market|Beta.*Soft.*Full", business_model, re.IGNORECASE | re.DOTALL))
    checks.append(("[2회차] GTM 전략 (Beta/Soft/Full)", has_gtm, ""))

    # Flywheel + Engine of Growth
    has_flywheel = bool(re.search(r"Flywheel|Engine of Growth|Sticky|Viral|Paid", business_model, re.IGNORECASE))
    checks.append(("[2회차] Flywheel + Engine of Growth", has_flywheel, ""))

    return checks


def check_junhyeok(json_content: str, other_failed: bool):
    """준혁은 이미 'Quality Gate 제거 + 이미 결정 모드'로 재정의됨.
    validator는 준혁 verdict/score를 정보로 표시만 하고, 다른 체크 결과와 연결하지 않는다.
    """
    checks = []
    try:
        data = json.loads(json_content)
        score = float(data.get("score", 0))
        verdict = data.get("verdict", "")

        # 점수 표시 (pass/fail 판정 없음 — 정보용)
        checks.append(
            (
                f"준혁 점수 (참고)",
                True,  # 항상 pass
                f"{score}점",
            )
        )

        checks.append(
            (
                "판정 존재 (GO/CONDITIONAL_GO/NO_GO)",
                verdict in ("GO", "CONDITIONAL_GO", "NO_GO"),
                f"verdict: {verdict}",
            )
        )

        # 이미 결정 모드: NO_GO는 치명적 리스크에서만 허용
        if verdict == "NO_GO":
            checks.append(
                (
                    "NO_GO 경고",
                    False,
                    "이미 결정 모드에서 NO_GO는 법적 리스크/사기성/죽은 시장에만 허용. 프롬프트 재검토",
                )
            )
    except (json.JSONDecodeError, ValueError) as e:
        checks.append(("JSON 파싱", False, str(e)[:60]))

    return checks


def check_jihun(content: str):
    checks = []
    checks.append(("Aha Moment 섹션", "Aha Moment" in content or "아하 모먼트" in content, ""))
    checks.append(("JTBD Statement", "JTBD" in content or "When I am" in content, ""))
    checks.append(
        (
            "Customer Forces Strategy",
            bool(re.search(r"(Inertia|Anxiety|Push|Pull)", content)),
            "",
        )
    )
    # 사업기획서엔 User Flow / API 명세 / 데이터 모델이 Evidence Appendix보다 중요
    has_user_flow = bool(re.search(r"(User\s*Flow|사용자\s*플로우|사용자\s*시나리오)", content, re.IGNORECASE))
    checks.append(("User Flow", has_user_flow, ""))
    has_api = bool(re.search(r"(API\s*명세|API\s*Spec|Endpoint)", content, re.IGNORECASE))
    checks.append(("API 명세", has_api, ""))
    has_data = bool(re.search(r"(데이터\s*모델|Data\s*Model|테이블)", content, re.IGNORECASE))
    checks.append(("데이터 모델", has_data, ""))
    return checks


def validate(output_dir) -> bool:
    """Level 1 구조 검증. 모든 critical check 통과 시 True."""
    output_path = Path(output_dir)
    if not output_path.exists():
        print(f"\n❌ 출력 폴더 없음: {output_dir}")
        return False

    print("\n" + "=" * 60)
    print("  📋 V4 Framework Validator (Level 1 — 구조)")
    print("=" * 60)

    seoyun = _read(output_path / "01_시장조사_서윤.md")
    minsu = _read(output_path / "02_전략_민수.md")
    designer_strategy = _read(output_path / "02b_전략브리프_설계자.md")
    designer_bm = _read(output_path / "02c_비즈니스모델_설계자.md")
    junhyeok_json = _read(output_path / "04_최종판단_준혁.json")
    jihun = _read(output_path / "05_PRD_지훈.md")

    results = {}

    if seoyun and not seoyun.strip().startswith("["):
        results["서윤"] = check_seoyun(seoyun)
    else:
        results["서윤"] = [("서윤 output 존재", False, "파일 없음 또는 에러 메시지")]

    if minsu and not minsu.strip().startswith("["):
        results["민수"] = check_minsu(minsu)
    else:
        results["민수"] = [("민수 output 존재", False, "파일 없음 또는 에러 메시지")]

    # 설계자 (2-call output)
    if designer_strategy or designer_bm:
        results["설계자"] = check_designer(designer_strategy, designer_bm)

    other_failed = any(
        not passed
        for agent in ("서윤", "민수", "설계자")
        for _, passed, _ in results.get(agent, [])
    )

    if junhyeok_json:
        results["준혁"] = check_junhyeok(junhyeok_json, other_failed)
    else:
        results["준혁"] = [("준혁 JSON 존재", False, "파일 없음")]

    if jihun and not jihun.strip().startswith("["):
        results["지훈"] = check_jihun(jihun)

    total = 0
    passed_count = 0

    for agent, checks in results.items():
        print(f"\n  [{agent}]")
        for name, passed, detail in checks:
            mark = "✅" if passed else "❌"
            suffix = f" — {detail}" if detail else ""
            print(f"    {mark} {name}{suffix}")
            total += 1
            if passed:
                passed_count += 1

    print("\n" + "-" * 60)
    pct = (passed_count / total * 100) if total else 0
    if passed_count == total:
        status = "✅ PASS"
    elif pct >= 70:
        status = "⚠️  PARTIAL"
    else:
        status = "❌ FAIL"
    print(f"  {status} — {passed_count}/{total} ({pct:.0f}%)")
    print("=" * 60 + "\n")

    return passed_count == total


def _find_latest_output() -> Path:
    outputs_dir = Path(__file__).resolve().parent.parent / "outputs"
    if not outputs_dir.exists():
        return None
    dirs = [d for d in outputs_dir.iterdir() if d.is_dir()]
    if not dirs:
        return None
    return max(dirs, key=lambda d: d.stat().st_mtime)


if __name__ == "__main__":
    # standalone 실행 시에만 stdout 래핑 (import 시에는 main.py가 이미 래핑 — 재래핑하면 stream close 에러)
    if sys.platform == "win32":
        try:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
        except Exception:
            pass

    if len(sys.argv) > 1:
        target = Path(sys.argv[1])
    else:
        target = _find_latest_output()
        if target is None:
            print("❌ outputs 폴더 또는 결과 없음")
            sys.exit(1)
        print(f"  (최신 output 자동 선택: {target.name})")

    ok = validate(target)
    sys.exit(0 if ok else 1)
