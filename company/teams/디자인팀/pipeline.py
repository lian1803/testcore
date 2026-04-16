#!/usr/bin/env python3
"""
디자인팀 파이프라인 v2

플로우:
1. Creative Director → 3개 컨셉 카드 (Big Idea + 구체적 스펙)
2. 리안 선택 (A/B/C)
3. Builder → 선택된 컨셉 → 완성 HTML
4. 검증 → 이슈 있으면 재생성

사용:
  python run_디자인팀.py "프로젝트 설명"
  python run_디자인팀.py "프로젝트 설명" --auto A  # 자동으로 A 선택
"""

import os
import sys
import json
from datetime import datetime
import anthropic
from dotenv import load_dotenv

# 경로 설정
LIANCP_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, LIANCP_ROOT)
load_dotenv(os.path.join(LIANCP_ROOT, ".env"))

from teams.디자인팀.creative_director import run as run_creative_director, display_concepts
from teams.디자인팀.builder import build_html, validate_html, validate_html_browser

# 자동 레퍼런스 수집
try:
    from core.pre_research import auto_research
    HAS_PRE_RESEARCH = True
except ImportError:
    HAS_PRE_RESEARCH = False

OUTPUT_BASE = os.path.join(os.path.dirname(LIANCP_ROOT), "team", "디자인팀", "output")


def get_client() -> anthropic.Anthropic:
    return anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def save_file(path: str, content: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  💾 저장: {path}")


def run(project_desc: str, auto_pick: str = None) -> dict:
    client = get_client()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    output_dir = os.path.join(OUTPUT_BASE, f"{timestamp}_디자인")
    os.makedirs(output_dir, exist_ok=True)

    # 자동 레퍼런스 수집 (디자인 전)
    reference_context = ""
    if HAS_PRE_RESEARCH:
        try:
            research = auto_research(project_desc, max_accounts=3, posts_per_account=3)
            if research:
                reference_context = research
                save_file(os.path.join(output_dir, "00_자동레퍼런스.md"), research)
        except Exception as e:
            print(f"  자동 레퍼런스 수집 실패: {e}")

    # 미션 + 학습 자동 로드
    try:
        from core.pipeline_utils import enrich_context
        ctx = enrich_context({"project": project_desc}, team_slug="디자인팀")
        if ctx.get("mission"):
            reference_context += f"\n\n## 팀 미션\n{ctx['mission']}"
        if ctx.get("learning"):
            reference_context += f"\n\n## 학습 자료\n{ctx['learning']}"
    except Exception as e:
        print(f"  미션/학습 로드 실패: {e}")

    print(f"\n{'='*65}")
    print(f"🎨 디자인팀 v2")
    print(f"프로젝트: {project_desc[:60]}...")
    print(f"저장 위치: {output_dir}")
    print(f"{'='*65}")

    # ─────────────────────────────────────────────
    # STEP 1: Creative Director → 3개 컨셉
    # ─────────────────────────────────────────────
    print("\n[1/3] Creative Director — 컨셉 생성 중...")
    concepts_data = run_creative_director(project_desc, client)

    # 컨셉 JSON 저장
    save_file(
        os.path.join(output_dir, "concepts.json"),
        json.dumps(concepts_data, ensure_ascii=False, indent=2)
    )

    # 터미널에 컨셉 카드 출력
    display_concepts(concepts_data)

    # ─────────────────────────────────────────────
    # STEP 2: 리안 선택
    # ─────────────────────────────────────────────
    concepts = concepts_data.get("concepts", [])
    if not concepts:
        print("⚠️ 컨셉 생성 실패. 종료.")
        return {}

    if auto_pick:
        choice = auto_pick.upper()
        print(f"\n🤖 자동 선택: {choice}")
    else:
        print(f"\n어떤 컨셉으로 갈까? (A/B/C): ", end="")
        try:
            choice = "A"  # 자동 선택 (Phase 2)
        except EOFError:
            choice = "A"

    chosen = next((c for c in concepts if c["id"] == choice), concepts[0])
    print(f"\n✅ 선택: {chosen['id']} — {chosen['name']}")
    print(f"   Big Idea: {chosen['big_idea']}")

    # ─────────────────────────────────────────────
    # STEP 3: Builder → HTML
    # ─────────────────────────────────────────────
    print("\n[2/3] Builder — HTML 생성 중...")
    html = build_html(chosen, project_desc, client)

    # markdown 아티팩트 사전 제거 (backtick + single-quote 코드펜스)
    import re as _re
    html = _re.sub(r"```\w*\n?", '', html)
    html = _re.sub(r"'''\w*\n?", '', html)

    # HTML 저장
    html_path = os.path.join(output_dir, "index.html")
    save_file(html_path, html)

    # ─────────────────────────────────────────────
    # STEP 4: 검증 (문자열 + 브라우저)
    # ─────────────────────────────────────────────
    print("\n[3/3] 검증 중...")
    passed, issues = validate_html(html, chosen)

    # 브라우저 렌더링 검증
    print("  🌐 브라우저 렌더링 검증...")
    b_passed, b_issues = validate_html_browser(html_path)
    if not b_passed:
        issues = b_issues + issues
        passed = False

    critical = [i for i in issues if "CRITICAL" in i]

    if passed:
        print("  ✅ 검증 통과")
    else:
        print(f"  ⚠️ 이슈 {len(issues)}개 발견:")
        for issue in issues:
            print(f"     - {issue}")

        # CRITICAL 이슈 있으면 빌더 전체 재실행
        if critical:
            print(f"\n  🔴 CRITICAL 이슈 {len(critical)}개 — 전체 재빌드...")
            html = build_html(chosen, project_desc, client)
            html = _re.sub(r"```\w*\n?", '', html)
            html = _re.sub(r"'''\w*\n?", '', html)
            save_file(html_path, html)
            passed, issues = validate_html(html, chosen)
            b_passed, b_issues = validate_html_browser(html_path)
            if not b_passed:
                issues = b_issues + issues
                passed = False
            if passed:
                print("  ✅ 재빌드 후 검증 통과")
            else:
                print(f"  ⚠️ 재빌드 후 잔여 이슈: {issues}")

        # 경미한 이슈 → 수정 재생성 (1회)
        elif len(issues) <= 3:
            print("\n  🔄 이슈 수정 후 재생성...")
            fix_prompt = f"""아래 HTML에서 이슈를 수정해줘:

이슈:
{chr(10).join(f'- {i}' for i in issues)}

원본 HTML:
```html
{html[:6000]}
```

수정된 HTML을 ```html ... ``` 블록 안에 완성본으로 반환.
"""
            import anthropic as ant
            fix_client = ant.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            fix_resp = fix_client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=8000,
                messages=[{"role": "user", "content": fix_prompt}]
            )
            import re
            match = re.search(r'```html\s*([\s\S]+?)```', fix_resp.content[0].text)
            if match:
                html = match.group(1).strip()
                save_file(os.path.join(output_dir, "index.html"), html)
                print(f"  ✅ 재생성 완료")

    # ─────────────────────────────────────────────
    # STEP 5: 브라우저 실제 렌더링 검증
    # ─────────────────────────────────────────────
    print("\n[검증] 브라우저에서 실제 렌더링 확인...")
    browser_ok, browser_errors = validate_html_browser(html_path)

    if browser_ok:
        print("  ✅ 브라우저 검증 통과 — 렌더링 정상")
    else:
        print(f"  🔴 브라우저 검증 실패:")
        for err in browser_errors:
            print(f"     - {err}")

        # 최대 2회 재빌드 시도
        for retry in range(2):
            print(f"\n  🔄 재빌드 시도 {retry + 1}/2 (브라우저 에러 기반)...")
            error_context = "\n".join(browser_errors)
            html = build_html(chosen, f"{project_desc}\n\n⚠️ 이전 빌드에서 발생한 에러 (반드시 수정):\n{error_context}", client)
            import re as _re2
            html = _re2.sub(r"```\w*\n?", '', html)
            save_file(html_path, html)

            browser_ok, browser_errors = validate_html_browser(html_path)
            if browser_ok:
                print(f"  ✅ 재빌드 {retry + 1}회 후 검증 통과")
                break
            else:
                print(f"  ⚠️ 재빌드 {retry + 1}회 후 여전히 에러: {browser_errors}")

        if not browser_ok:
            print("\n  🔴 2회 재빌드 후에도 실패 — 리안에게 에러 보고")

    # 나머지 컨셉도 저장 (참고용)
    other_concepts = [c for c in concepts if c["id"] != choice]
    if other_concepts:
        save_file(
            os.path.join(output_dir, "other_concepts.json"),
            json.dumps(other_concepts, ensure_ascii=False, indent=2)
        )

    print(f"\n{'='*65}")
    print(f"✅ 완료")
    print(f"HTML: {html_path}")
    print(f"브라우저에서 열어봐: file:///{html_path.replace(chr(92), '/')}")
    print(f"{'='*65}")

    return {
        "concepts": concepts_data,
        "chosen": chosen,
        "html_path": html_path,
        "output_dir": output_dir,
        "issues": issues,
    }
