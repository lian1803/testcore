"""
launch_prep.py — Layer 3: 런칭 준비 파이프라인

GO 판정 후, 개발/실행 전에 돌리는 단계.
"누구한테 뭘 얼마에 어떻게 팔건데?" 를 구체화한다.

사용법:
    from core.launch_prep import run_launch_prep
    result = run_launch_prep(context, client)

또는 직접 실행:
    python -m core.launch_prep "프로젝트 설명"
"""
import os
os.environ.setdefault("PYTHONUTF8", "1")
import anthropic
from dotenv import load_dotenv
from core.context_loader import inject_context
from core.research_loop import research_before_task
from core.models import CLAUDE_SONNET

load_dotenv()

MODEL = CLAUDE_SONNET

LAUNCH_PREP_PROMPT = """너는 시은이야. 이사팀 GO 판정이 났고, 이제 런칭 준비를 해야 해.

개발/실행에 들어가기 전에 반드시 이것들을 구체화해야 해:

1. **타겟 구체화** — "소상공인"이 아니라 "월매출 500만 이상 네이버 스마트스토어 셀러" 수준으로
2. **경쟁사 상품/가격** — 실제 대행사들이 뭘 얼마에 파는지 (리서치 결과 참고)
3. **우리 상품 정의** — 우리가 팔 것 + 가격 + 포함 내용
4. **영업 채널** — DM? 이메일? 광고? 각 채널의 자동화 가능 여부 + 법적 제한
5. **마케팅 채널** — 인스타 컨셉, 블로그 플랫폼, 광고 예산
6. **첫 주 액션플랜** — 런칭 후 첫 7일 동안 매일 뭘 할건지

출력 형식:
## 1. 타겟
| 항목 | 내용 |
|------|------|
| 구체적 타겟 | |
| 타겟이 모이는 곳 | |
| 예상 TAM | |
| 얼리어답터 특성 | |

## 2. 경쟁사 벤치마크
| 경쟁사 | 상품 | 가격 | 우리 대비 약점 |
|--------|------|------|--------------|

## 3. 우리 상품
| 플랜 | 가격 | 포함 내용 | 타겟 등급 |
|------|------|---------|----------|

## 4. 영업 채널
| 채널 | 자동화 가능? | 법적 제한 | 우선순위 |
|------|------------|---------|---------|

## 5. 마케팅 채널
| 채널 | 컨셉/방향 | 비용 | 기대 효과 |
|------|---------|------|---------|

## 6. 첫 주 액션플랜
| Day | 할 것 | 담당 | 산출물 |
|-----|------|------|--------|

현실적으로. "이론적으로 가능"이 아니라 "내일 당장 이렇게"로."""


def pre_launch_check(project_dir: str) -> bool:
    """배포 전 '실제로 작동하는가' 자동 검증."""
    import json, re
    issues = []

    # 1. package.json에 백엔드 의존성 있는지
    pkg_path = os.path.join(project_dir, "package.json")
    if os.path.exists(pkg_path):
        try:
            pkg = json.loads(open(pkg_path, encoding="utf-8").read())
            deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
            backend_deps = ["@supabase/supabase-js", "stripe", "@stripe/stripe-js", "next-auth", "hono"]
            found = [d for d in backend_deps if d in deps]
            if not found:
                issues.append("package.json에 백엔드 의존성 없음 (supabase/stripe/next-auth 중 하나 필요)")
        except Exception:
            pass

    # 2. .env.example에 필요한 키 있는지
    env_path = os.path.join(project_dir, ".env.example")
    if not os.path.exists(env_path):
        issues.append(".env.example 없음 — 필요한 환경변수 목록 미정의")
    else:
        env_content = open(env_path, encoding="utf-8").read()
        if "DATABASE_URL" not in env_content and "SUPABASE" not in env_content:
            issues.append(".env.example에 DB 연결 정보 없음")

    # 3. API 엔드포인트 파일 존재하는지
    api_dirs = [
        os.path.join(project_dir, "src", "app", "api"),
        os.path.join(project_dir, "src", "routes"),
        os.path.join(project_dir, "app", "api"),
        os.path.join(project_dir, "pages", "api"),
    ]
    has_api = any(os.path.isdir(d) for d in api_dirs)
    if not has_api:
        issues.append("API 엔드포인트 폴더 없음 (app/api, pages/api, src/routes 중 하나 필요)")

    # 4. 하드코딩 mock 데이터 검색
    mock_patterns = [r'\bTODO\s*:\s*백엔드', r'\bMOCK\b', r'hardcoded', r'// 나중에 API']
    src_dir = os.path.join(project_dir, "src")
    if os.path.isdir(src_dir):
        for root, _, files in os.walk(src_dir):
            for fname in files:
                if fname.endswith((".ts", ".tsx", ".js", ".jsx")):
                    try:
                        content = open(os.path.join(root, fname), encoding="utf-8", errors="ignore").read()
                        for pat in mock_patterns:
                            if re.search(pat, content, re.IGNORECASE):
                                rel = os.path.relpath(os.path.join(root, fname), project_dir)
                                issues.append(f"하드코딩/미연결 코드 발견: {rel} ({pat})")
                                break
                    except Exception:
                        pass

    if issues:
        print("⚠️ 배포 차단 — 작동 검증 미통과:")
        for i in issues:
            print(f"  - {i}")
        return False

    print("✅ 작동 검증 통과 — 배포 가능")
    return True


def run_launch_prep(context: dict, client: anthropic.Anthropic) -> str:
    """런칭 준비 파이프라인 실행."""
    print(f"\n{'='*60}")
    print("🚀 Layer 3: 런칭 준비")
    print("='*60")

    idea = context.get("clarified", context.get("idea", ""))
    strategy = context.get("minsu", "")[:500]
    market = context.get("seoyun", "")[:500]

    # 작업 전 리서치 — 경쟁사/트렌드 최신 수집
    research = research_before_task(
        role="런칭 준비",
        task=idea[:50],
        queries=[
            f"{idea[:30]} 경쟁사 가격 비교 2026",
            f"{idea[:30]} 마케팅 채널 전략 2026",
            f"{idea[:30]} 영업 자동화 방법",
        ]
    )

    user_msg = f"""프로젝트: {idea}

이사팀 전략 요약:
{strategy}

시장조사 요약:
{market}

최신 리서치:
{research[:2000]}

런칭 준비 구체화해줘."""

    full_response = ""
    with client.messages.stream(
        model=MODEL,
        max_tokens=3000,
        system=inject_context(LAUNCH_PREP_PROMPT),
        messages=[{"role": "user", "content": user_msg}],
        temperature=0.3,
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
            full_response += text

    print()

    # 기획서 기반 마케팅 전략 수립 (사이트 없어도 지금 바로)
    try:
        from core.marketing_planner import plan_from_brief, print_confirmation_prompt
        context["launch_plan"] = full_response
        pre_plan = plan_from_brief(context, idea, client)
        print(print_confirmation_prompt(idea, pre_plan))
        context["marketing_plan_prelaunch"] = pre_plan
    except Exception as e:
        print(f"\n  ⚠️  마케팅 전략 수립 실패: {e}")

    # 랜딩페이지 자동 생성 + Cloudflare 배포
    _deploy_landing_page(context, full_response)

    # 배포 후 사이트 분석으로 전략 보완 (배포 URL 있으면)
    deployed_url = context.get("deployed_url", "")
    if deployed_url:
        try:
            from core.product_analyzer import analyze_product
            from core.marketing_planner import plan_marketing, print_confirmation_prompt
            print(f"\n{'='*60}")
            print("📣 마케팅 자동 연결 시작")
            print("="*60)
            analysis = analyze_product(deployed_url, idea, client)
            plan = plan_marketing(analysis, idea, client)
            print(print_confirmation_prompt(idea, plan))
        except Exception as e:
            print(f"\n  ⚠️  마케팅 자동 연결 실패: {e}")
    else:
        print("\n  ℹ️  배포 URL 없음 — 나중에 수동으로: from core.product_analyzer import analyze_product")

    return full_response


def _deploy_landing_page(context: dict, launch_plan: str):
    """Stitch HTML 생성 후 Cloudflare Pages 자동 배포."""
    import subprocess, re, shutil, tempfile

    project_name = context.get("idea", "프로젝트")[:20].replace(" ", "-").replace("/", "-")
    slug = re.sub(r"[^a-z0-9-]", "", project_name.lower().replace(" ", "-"))[:30] or "lian-project"
    deploy_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                              "team", project_name)
    os.makedirs(deploy_dir, exist_ok=True)

    html_path = os.path.join(deploy_dir, "index.html")
    if not os.path.exists(html_path):
        print(f"\n  ⚠️  index.html 없음 — Stitch 생성 필요 (Claude Code에서 실행)")
        return

    # Cloudflare Pages 배포
    print(f"\n  🌐 Cloudflare Pages 배포 중 ({slug})...")
    try:
        try:
            # 프로젝트 생성 시도 (이미 있으면 무시)
            subprocess.run(
                ["npx", "wrangler", "pages", "project", "create", slug, "--production-branch", "main"],
                capture_output=True, cwd=deploy_dir, timeout=60
            )
        except Exception as e:
            print(f"  ⚠️  프로젝트 생성 실패 (계속 진행): {e}")

        try:
            result = subprocess.run(
                ["npx", "wrangler", "pages", "deploy", ".", "--project-name", slug, "--branch", "main"],
                capture_output=True, text=True, cwd=deploy_dir, timeout=120
            )
        except subprocess.TimeoutExpired:
            print(f"  ⚠️  배포 타임아웃 (120초)")
            return
        except Exception as e:
            print(f"  ⚠️  배포 subprocess 에러: {e}")
            return
        if "Deployment complete" in result.stdout or "pages.dev" in result.stdout:
            url = re.search(r"https://[\w.-]+\.pages\.dev", result.stdout)
            url_str = url.group(0) if url else f"https://{slug}.pages.dev"
            print(f"  ✅ 배포 완료: {url_str}")
            # 보고사항들.md에 URL 기록
            report_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                       "보고사항들.md")
            try:
                entry = f"\n\n## 랜딩페이지 배포 완료\n\n- 프로젝트: {project_name}\n- URL: {url_str}\n\n---\n"
                existing = open(report_path, encoding="utf-8").read() if os.path.exists(report_path) else ""
                with open(report_path, "w", encoding="utf-8") as f:
                    f.write(existing + entry)
            except Exception:
                pass
            # QA 자동 실행
            try:
                from core.qa_loop import run_qa
                import time
                time.sleep(5)  # 배포 반영 대기
                run_qa(url_str, project_name)
            except Exception as e:
                print(f"  ⚠️  QA 스킵: {e}")
        else:
            print(f"  ⚠️  배포 실패: {result.stderr[:200]}")
    except Exception as e:
        print(f"  ⚠️  배포 오류: {e}")
