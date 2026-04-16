"""
비전 리뷰 — Lian Dash 시각 디자인 자동 평가

역할:
- 실제 배포된 랜딩페이지 스크린샷 수집
- Gemini Vision으로 디자인 검수
- 개선 피드백 저장
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# API 키 로드
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# ── Playwright 체크 ────────────────────────────────────────────

def check_playwright():
    """Playwright 설치 확인"""
    try:
        from playwright.sync_api import sync_playwright
        return True
    except ImportError:
        print("\n❌ Playwright 미설치")
        print("   설치 명령: pip install playwright")
        print("   브라우저: playwright install chromium")
        return False


# ── Gemini 초기화 ────────────────────────────────────────────

def init_gemini():
    """Gemini Vision 클라이언트 초기화"""
    try:
        from google import genai
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("❌ GOOGLE_API_KEY 환경변수 없음")
            return None
        client = genai.Client(api_key=api_key)
        return client
    except ImportError:
        print("❌ google-genai 미설치: pip install google-generativeai")
        return None


# ── 스크린샷 수집 ────────────────────────────────────────────

def capture_screenshots():
    """Lian Dash 스크린샷 수집 (landing + dashboard)"""
    if not check_playwright():
        return []

    try:
        from playwright.sync_api import sync_playwright
        from PIL import Image
    except ImportError as e:
        print(f"❌ 필수 라이브러리 미설치: {e}")
        return []

    # 스냅샷 디렉토리 생성
    snap_dir = os.path.join(
        os.path.dirname(__file__),
        "knowledge", "base", "visual_snapshots"
    )
    os.makedirs(snap_dir, exist_ok=True)

    screenshots = []
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()

            # 랜딩페이지 스크린샷
            print("\n📸 랜딩페이지 스크린샷 수집 중...")
            try:
                page.goto("https://lian-dash.vercel.app", timeout=10000)
                page.wait_for_timeout(3000)  # 3초 대기
                landing_path = os.path.join(
                    snap_dir, f"landing_{timestamp}.png"
                )
                page.screenshot(path=landing_path, full_page=True)
                screenshots.append({
                    "path": landing_path,
                    "route": "/",
                    "name": "Landing Page"
                })
                print(f"   ✅ 저장: {landing_path}")
            except Exception as e:
                print(f"   ⚠️  랜딩페이지 실패: {e}")

            # 대시보드 스크린샷
            print("\n📸 대시보드 스크린샷 수집 중...")
            try:
                page.goto("https://lian-dash.vercel.app/dashboard", timeout=10000)
                page.wait_for_timeout(3000)
                dashboard_path = os.path.join(
                    snap_dir, f"dashboard_{timestamp}.png"
                )
                page.screenshot(path=dashboard_path, full_page=True)
                screenshots.append({
                    "path": dashboard_path,
                    "route": "/dashboard",
                    "name": "Dashboard"
                })
                print(f"   ✅ 저장: {dashboard_path}")
            except Exception as e:
                print(f"   ⚠️  대시보드 실패: {e}")

            browser.close()

    except Exception as e:
        print(f"❌ Playwright 오류: {e}")
        return []

    return screenshots


# ── Gemini Vision 검수 ────────────────────────────────────────

def review_screenshot(client, screenshot_path: str, page_name: str) -> str:
    """Gemini Vision으로 스크린샷 검수"""
    if not client:
        return ""

    try:
        from PIL import Image
        import base64
        from io import BytesIO

        # 이미지 로드 및 base64 인코딩
        with Image.open(screenshot_path) as img:
            # 이미지 리사이징 (토큰 최적화)
            img.thumbnail((1920, 1080), Image.Resampling.LANCZOS)

            buffered = BytesIO()
            img.save(buffered, format="PNG")
            img_data = base64.standard_b64encode(buffered.getvalue()).decode()

        system_prompt = """너는 나은이야. 리안 컴퍼니의 비전 디자이너이자 검수 전문가야.

이미지는 인하우스 마케터 SaaS(Lian Dash)의 UI 스크린샷이야.
시각 디자인 품질을 냉정하게 평가해줘."""

        user_prompt = f"""# {page_name} 시각 설계 검수

아래 기준으로 평가해줘:

1. **채널 3색 적용 상황**
   - 오렌지: #E37400
   - 파랑: #1877F2
   - 초록: #03C75A
   → 이 색상들이 디자인을 주도하고 있는가?
   → 과다/부족한 부분?

2. **배경 + 명도 대비**
   - 배경이 충분히 어둡고(#050507 수준) 고급스러운가?
   - 텍스트/요소 명도 대비는 충분한가?

3. **타이포그래피 계층**
   - 제목-본문-보조 텍스트의 크기 차이가 명확한가?
   - 폰트 선택이 일관성 있는가?

4. **전반적 임팩트 (1-10점)**
   - 첫눈에 프리미엄으로 느껴지는가?

5. **개선 필요 항목 3가지**
   - [항목 1]: [개선 방안]
   - [항목 2]: [개선 방안]
   - [항목 3]: [개선 방안]

6. **다음 액션**
   - 가장 우선순위 높은 개선사항은?"""

        # Gemini Vision 호출
        from google.genai import types

        response_text = ""
        for chunk in client.models.generate_content_stream(
            model="gemini-2.0-flash",
            contents=[
                {
                    "role": "user",
                    "parts": [
                        {"text": user_prompt},
                        {
                            "inline_data": {
                                "mime_type": "image/png",
                                "data": img_data
                            }
                        }
                    ]
                }
            ],
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.7
            )
        ):
            chunk_text = chunk.text or ""
            response_text += chunk_text
            print(chunk_text, end="", flush=True)

        print()
        return response_text

    except ImportError as e:
        print(f"❌ 필수 라이브러리 미설치: {e}")
        return ""
    except Exception as e:
        print(f"❌ Gemini Vision 오류: {e}")
        return ""


# ── 보고서 저장 ────────────────────────────────────────────

def save_review_report(reviews: dict):
    """검수 결과를 보고사항들.md에 추가"""
    try:
        from knowledge.manager import write_report
    except ImportError:
        print("⚠️  knowledge.manager import 실패")
        return

    # 검수 결과 종합
    report_content = "# Lian Dash 비전 검수 결과\n\n"

    for page_name, review_data in reviews.items():
        if review_data["review"]:
            report_content += f"## {page_name}\n\n{review_data['review']}\n\n---\n\n"

    write_report(
        agent_name="[나은] 비전 리뷰",
        role="디자인 검수",
        content=report_content
    )


# ── JSON 요약 저장 ────────────────────────────────────────

def save_json_summary(reviews: dict, timestamp: str):
    """검수 결과를 JSON으로 저장"""
    snap_dir = os.path.join(
        os.path.dirname(__file__),
        "knowledge", "base", "visual_snapshots"
    )

    summary = {
        "timestamp": timestamp,
        "url": "https://lian-dash.vercel.app",
        "pages_reviewed": list(reviews.keys()),
        "reviews": {}
    }

    for page_name, review_data in reviews.items():
        summary["reviews"][page_name] = {
            "screenshot": review_data["path"],
            "route": review_data["route"],
            "review_length": len(review_data["review"])
        }

    json_path = os.path.join(snap_dir, f"review_{timestamp}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print(f"\n📊 JSON 요약 저장: {json_path}")


# ── Main ────────────────────────────────────────────

def main():
    """메인 파이프라인"""
    print("\n" + "="*60)
    print("🎨 나은 | 비전 리뷰 (Gemini Vision)")
    print("="*60)

    # 1. Gemini 클라이언트 초기화
    client = init_gemini()
    if not client:
        sys.exit(1)

    # 2. 스크린샷 수집
    screenshots = capture_screenshots()
    if not screenshots:
        print("\n❌ 스크린샷 수집 실패")
        sys.exit(1)

    print(f"\n✅ {len(screenshots)}개 스크린샷 수집됨")

    # 3. 각 스크린샷 검수
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    reviews = {}

    for ss in screenshots:
        page_name = ss["name"]
        print(f"\n{'='*60}")
        print(f"🔍 {page_name} 검수 중...")
        print(f"{'='*60}\n")

        review = review_screenshot(client, ss["path"], page_name)
        reviews[page_name] = {
            "path": ss["path"],
            "route": ss["route"],
            "review": review
        }

    # 4. 보고서 저장
    print(f"\n{'='*60}")
    print("📝 보고서 저장 중...")
    print(f"{'='*60}")

    save_review_report(reviews)
    save_json_summary(reviews, timestamp)

    print("\n✅ 비전 리뷰 완료!")
    print(f"   스크린샷: company/knowledge/base/visual_snapshots/")
    print(f"   보고서: 보고사항들.md")


if __name__ == "__main__":
    main()
