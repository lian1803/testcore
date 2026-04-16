"""
visual_qa_loop.py — 디자인 시각 품질 자동 평가 루프

Playwright로 웹사이트 또는 HTML 파일 스크린샷 캡처 → Gemini Vision으로 디자인 평가
→ 기준 미달시 재생성 지시사항 제공.

사용법:
    from core.visual_qa_loop import run_qa

    # URL 또는 HTML 파일 경로로 실행
    result = run_qa(
        "https://example.com",
        "path/to/SCENE.md",
        max_iterations=3
    )

    print(f"점수: {result['score']}/100")
    print(f"통과: {result['passed']}")
    if result['issues']:
        print(f"문제: {result['issues']}")
"""
import os
import json
from pathlib import Path
from typing import Optional, Union
from dotenv import load_dotenv

load_dotenv()

# Gemini 초기화 (나중에 임포트)
_GEMINI_CLIENT = None


def _get_gemini_client():
    """Google Generative AI 클라이언트 초기화."""
    global _GEMINI_CLIENT
    if _GEMINI_CLIENT is None:
        try:
            import google.generativeai as genai

            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("[ERROR] GOOGLE_API_KEY 환경변수가 설정되지 않음")
            genai.configure(api_key=api_key)
            _GEMINI_CLIENT = genai
        except ImportError:
            raise ImportError("[ERROR] google-generativeai 패키지가 설치되지 않음. pip install google-generativeai")
    return _GEMINI_CLIENT


QA_EVALUATION_PROMPT = """당신은 웹 디자인 평가 전문가입니다.
제공된 스크린샷을 분석하고 다음 5가지 기준으로 점수를 매깁니다.

## 평가 기준

1. **레퍼런스 유사도 (Reference Similarity)** — 0~20점
   - SCENE.md 명세 기준으로 디자인이 얼마나 정확히 구현되었는가?
   - 배경, 오브젝트, 조명, 카메라가 계획과 일치하는가?
   - 3D/2D 경계가 명확한가?

2. **여백과 밀도 균형 (Spacing & Density)** — 0~20점
   - 공간 활용이 자연스러운가? (과하거나 너무 비어있지 않은가?)
   - 텍스트와 요소 간 호흡이 적절한가?
   - 요소들의 시각적 무게가 균등하게 분배되었는가?

3. **타이포그래피 일관성 (Typography Consistency)** — 0~20점
   - 글꼴 크기, 굵기, 행간이 계층적으로 정렬되었는가?
   - 텍스트 색상 대비가 충분한가? (접근성)
   - 장문과 단문의 기울기/스타일이 일관적인가?

4. **모션 과다 여부 (Motion Appropriateness)** — 0~20점
   - 애니메이션이 지나치게 많거나 산만하지 않은가?
   - 스크롤 애니메이션이 자연스러운 속도인가?
   - 깜박임, 떨림, 불필요한 전환은 없는가?

5. **3D/2D 경계 자연스러움 (3D-2D Boundary)** — 0~10점
   - 3D 영역과 2D UI 영역의 경계가 어색하지 않은가?
   - 3D 오브젝트와 텍스트 오버레이의 조화가 좋은가?
   - 둘의 시각적 깊이감이 자연스러운가?

6. **에너지 계층 (Energy Hierarchy)** — 0~10점
   - 히어로가 확실히 가장 강한 시각 섹션인가?
   - 아래로 갈수록 점진적으로 차분해지는가?
   - 섹션 간 불필요한 시각적 경쟁이 있는가?
   - 전체 페이지가 균일하게 시끄럽지 않고 의도적으로 페이싱되는가?

## 평가 방식

각 기준마다:
- 10점: 완벽함. 기준을 초과 충족.
- 8-9점: 우수함. 기준 충족.
- 6-7점: 보통. 기준 충족하되 개선 필요.
- 4-5점: 미흡함. 기준 미달, 수정 필요.
- 0-3점: 부족함. 기준 크게 미달, 재작성 권장.

## 총점 해석

- 85점 이상: 통과 (배포 가능)
- 70~84점: 조건부 통과 (사소한 수정 후 배포)
- 50~69점: 재검토 권장 (주요 항목 수정)
- 50점 미만: 불통과 (재설계 필요)

## 응답 형식

반드시 아래 JSON만 응답하세요:

{
  "scores": {
    "reference_similarity": (0~20),
    "spacing_density": (0~20),
    "typography_consistency": (0~20),
    "motion_appropriateness": (0~20),
    "3d_2d_boundary": (0~20)
  },
  "total_score": (0~100),
  "passed": (true/false),
  "issues": [
    "문제 1",
    "문제 2",
    ...
  ],
  "suggestions": [
    "개선 제안 1",
    "개선 제안 2",
    ...
  ],
  "summary": "한 문단으로 요약"
}

JSON만 출력하세요. 다른 텍스트는 금지.
"""


def run_qa(
    url_or_path: str,
    scene_md_path: str,
    max_iterations: int = 3,
    headless: bool = True,
    viewport_width: int = 1920,
    viewport_height: int = 1080,
) -> dict:
    """디자인 시각 품질 자동 평가.

    Args:
        url_or_path: 평가할 URL (https://...) 또는 HTML 파일 경로
        scene_md_path: SCENE.md 경로 (평가 기준 제공)
        max_iterations: 최대 평가 반복 횟수
        headless: Playwright 헤드리스 모드
        viewport_width: 스크린샷 가로 (픽셀)
        viewport_height: 스크린샷 세로 (픽셀)

    Returns:
        {
            "score": 0-100 (최종 점수),
            "passed": bool,
            "issues": [...],
            "suggestions": [...],
            "iterations": int (몇 번 평가했는가),
            "history": [
                {"iteration": 1, "score": 60, "issues": [...]},
                ...
            ]
        }

    Raises:
        FileNotFoundError: SCENE.md 없음
        ImportError: playwright 미설치
        ValueError: URL/경로 유효하지 않음
    """
    # SCENE.md 읽기
    scene_path = Path(scene_md_path)
    if not scene_path.exists():
        raise FileNotFoundError(f"❌ SCENE.md를 찾을 수 없음: {scene_md_path}")

    scene_content = scene_path.read_text(encoding="utf-8")

    # Playwright 임포트
    try:
        from playwright.async_api import async_playwright
        import asyncio
    except ImportError:
        raise ImportError("[ERROR] playwright 패키지가 설치되지 않음. pip install playwright")

    # Gemini 클라이언트
    genai = _get_gemini_client()

    async def _evaluate_once(screenshot_bytes: bytes) -> dict:
        """한 번의 평가 실행."""
        try:
            # Gemini Vision API에 이미지 전송
            image_part = {
                "mime_type": "image/png",
                "data": screenshot_bytes,
            }

            model = genai.GenerativeModel("gemini-2.0-flash")
            response = model.generate_content(
                [
                    {
                        "role": "user",
                        "parts": [
                            image_part,
                            {
                                "text": f"""SCENE.md 명세:

{scene_content}

---

위 명세를 참고해서 제공된 스크린샷을 평가해주세요.

평가 기준:
{QA_EVALUATION_PROMPT}
""",
                            },
                        ],
                    }
                ]
            )

            response_text = response.text.strip()

            # JSON 파싱
            try:
                result = json.loads(response_text)
                return result
            except json.JSONDecodeError:
                print(f"[WARN] Gemini 응답이 유효한 JSON이 아님:\n{response_text}")
                # 파싱 실패 시 기본값 반환
                return {
                    "total_score": 0,
                    "passed": False,
                    "issues": ["Gemini 평가 응답 파싱 실패"],
                    "suggestions": ["다시 시도하세요"],
                }

        except Exception as e:
            print(f"[ERROR] Gemini 평가 중 에러: {e}")
            return {
                "total_score": 0,
                "passed": False,
                "issues": [f"평가 실패: {str(e)}"],
                "suggestions": [],
            }

    async def _run_evaluation():
        """메인 평가 루프 (async)."""
        history = []

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=headless)
            page = await browser.new_page(
                viewport={"width": viewport_width, "height": viewport_height}
            )

            try:
                # URL 또는 파일 경로로 네비게이션
                if url_or_path.startswith("http://") or url_or_path.startswith("https://"):
                    print(f"[LOAD] URL 로드: {url_or_path}")
                    await page.goto(url_or_path, wait_until="networkidle")
                else:
                    file_path = Path(url_or_path).resolve()
                    if not file_path.exists():
                        raise FileNotFoundError(f"[ERROR] 파일을 찾을 수 없음: {url_or_path}")
                    print(f"[LOAD] HTML 파일 로드: {file_path}")
                    await page.goto(f"file://{file_path}", wait_until="load")

                # 스크린샷 캡처
                print("[CAPTURE] 스크린샷 캡처 중...")
                screenshot_bytes = await page.screenshot()

                # 반복 평가
                for iteration in range(1, max_iterations + 1):
                    print(f"\n[EVAL] 평가 {iteration}/{max_iterations}...")

                    eval_result = await _evaluate_once(screenshot_bytes)

                    score = eval_result.get("total_score", 0)
                    passed = eval_result.get("passed", False)
                    issues = eval_result.get("issues", [])
                    suggestions = eval_result.get("suggestions", [])

                    history.append(
                        {
                            "iteration": iteration,
                            "score": score,
                            "passed": passed,
                            "issues": issues,
                        }
                    )

                    print(f"   점수: {score}/100, 통과: {passed}")
                    if issues:
                        print(f"   문제: {', '.join(issues[:2])}")

                    # 통과했거나 마지막 반복
                    if passed or iteration == max_iterations:
                        return {
                            "score": score,
                            "passed": passed,
                            "issues": issues,
                            "suggestions": suggestions,
                            "summary": eval_result.get("summary", ""),
                            "iterations": iteration,
                            "history": history,
                        }

            finally:
                await browser.close()

        # 루프 종료 (통과 못함)
        return {
            "score": history[-1].get("score", 0) if history else 0,
            "passed": False,
            "issues": history[-1].get("issues", []) if history else ["평가 미완료"],
            "suggestions": [],
            "iterations": len(history),
            "history": history,
        }

    # 비동기 실행
    try:
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(_run_evaluation())
        return result
    except RuntimeError:
        # 기존 루프 사용
        return asyncio.run(_run_evaluation())


def format_qa_result(result: dict) -> str:
    """평가 결과를 읽기 좋은 텍스트로 포맷."""
    lines = ["\n[QA_RESULT] === 디자인 시각 품질 평가 결과 ===\n"]

    score = result.get("score", 0)
    passed = result.get("passed", False)

    # 점수
    status = "[OK]" if passed else "[FAIL]"
    lines.append(f"{status} 최종 점수: {score}/100")
    lines.append(f"   통과 기준: 85점 이상\n")

    # 반복 이력
    iterations = result.get("iterations", 0)
    lines.append(f"[HISTORY] 평가 반복: {iterations}회\n")

    # 이슈
    issues = result.get("issues", [])
    if issues:
        lines.append(f"[ISSUES] 발견된 문제:")
        for i, issue in enumerate(issues[:5], 1):
            lines.append(f"   {i}. {issue}")
        if len(issues) > 5:
            lines.append(f"   ... 외 {len(issues) - 5}개")
        lines.append("")

    # 제안
    suggestions = result.get("suggestions", [])
    if suggestions:
        lines.append(f"[SUGGESTIONS] 개선 제안:")
        for i, suggestion in enumerate(suggestions[:5], 1):
            lines.append(f"   {i}. {suggestion}")
        if len(suggestions) > 5:
            lines.append(f"   ... 외 {len(suggestions) - 5}개")
        lines.append("")

    # 요약
    summary = result.get("summary", "")
    if summary:
        lines.append(f"[SUMMARY] 평가 요약:\n   {summary}\n")

    # 이력
    history = result.get("history", [])
    if history:
        lines.append(f"[EVAL_HISTORY] 평가 이력:")
        for h in history:
            iter_num = h.get("iteration", 0)
            iter_score = h.get("score", 0)
            lines.append(f"   반복 {iter_num}: {iter_score}점")
        lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    # 테스트 (실제 URL/파일 필요)
    import sys
    import io

    # Windows 콘솔 인코딩 수정
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    if len(sys.argv) < 2:
        print(
            """
Usage:
  python visual_qa_loop.py <URL or HTML file path> <SCENE.md path>

Examples:
  python visual_qa_loop.py https://example.com ./templates/SCENE.md
  python visual_qa_loop.py ./dist/index.html ./templates/SCENE.md
"""
        )
        sys.exit(1)

    url_or_path = sys.argv[1]
    scene_path = sys.argv[2] if len(sys.argv) > 2 else "./templates/SCENE.md"

    print(f"[START] 디자인 QA 루프 시작...")
    print(f"   대상: {url_or_path}")
    print(f"   기준: {scene_path}\n")

    try:
        result = run_qa(url_or_path, scene_path, max_iterations=2)
        print(format_qa_result(result))
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback

        traceback.print_exc()
