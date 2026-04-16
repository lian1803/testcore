"""
captcha.py — 캡챠 자동 해결 모듈

2captcha API 또는 AntiCaptcha API를 사용해서 캡챠를 자동으로 해결.
Playwright 자동화와 함께 사용.

지원 유형:
- reCAPTCHA v2 (구글 I'm not a robot)
- reCAPTCHA v3
- 이미지 캡챠 (텍스트)
- hCaptcha

설치:
    pip install 2captcha-python

환경변수 (.env):
    TWOCAPTCHA_API_KEY=your_key_here

사용법:
    from core.captcha import solve_recaptcha, solve_image

    # reCAPTCHA v2
    token = solve_recaptcha("https://site.com", "site_key_here")

    # 이미지 캡챠
    text = solve_image("captcha.png")
"""
import os
import time
import base64
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("TWOCAPTCHA_API_KEY", "")


def _check_key():
    if not API_KEY:
        raise ValueError(
            "TWOCAPTCHA_API_KEY가 .env에 없음.\n"
            "1. https://2captcha.com 가입\n"
            "2. API 키 발급 (1000 캡챠당 약 $3)\n"
            "3. .env에 TWOCAPTCHA_API_KEY=your_key 추가"
        )


def solve_recaptcha(page_url: str, site_key: str, version: str = "v2") -> str:
    """reCAPTCHA 자동 해결. 토큰 반환.

    Args:
        page_url: 캡챠가 있는 페이지 URL
        site_key: reCAPTCHA site key (페이지 소스에서 data-sitekey 값)
        version: "v2" 또는 "v3"

    Returns:
        g-recaptcha-response 토큰 (폼에 넣으면 됨)
    """
    _check_key()

    try:
        from twocaptcha import TwoCaptcha
    except ImportError:
        raise ImportError("pip install 2captcha-python 실행 필요")

    solver = TwoCaptcha(API_KEY)
    print(f"[캡챠] reCAPTCHA {version} 해결 중... (약 20~30초)")

    if version == "v3":
        result = solver.recaptcha(sitekey=site_key, url=page_url, version="v3", score=0.7, action="submit")
    else:
        result = solver.recaptcha(sitekey=site_key, url=page_url)

    token = result["code"]
    print(f"[캡챠] 해결 완료. 토큰: {token[:30]}...")
    return token


def solve_image(image_path: str) -> str:
    """이미지 캡챠 텍스트 추출.

    Args:
        image_path: 캡챠 이미지 파일 경로

    Returns:
        캡챠 텍스트
    """
    _check_key()

    try:
        from twocaptcha import TwoCaptcha
    except ImportError:
        raise ImportError("pip install 2captcha-python 실행 필요")

    solver = TwoCaptcha(API_KEY)
    print(f"[캡챠] 이미지 캡챠 해결 중...")

    result = solver.normal(image_path)
    text = result["code"]
    print(f"[캡챠] 해결: {text}")
    return text


def solve_hcaptcha(page_url: str, site_key: str) -> str:
    """hCaptcha 자동 해결."""
    _check_key()

    try:
        from twocaptcha import TwoCaptcha
    except ImportError:
        raise ImportError("pip install 2captcha-python 실행 필요")

    solver = TwoCaptcha(API_KEY)
    print(f"[캡챠] hCaptcha 해결 중...")

    result = solver.hcaptcha(sitekey=site_key, url=page_url)
    return result["code"]


def inject_recaptcha_token(page, token: str):
    """Playwright 페이지에 reCAPTCHA 토큰 주입.

    사용법:
        from playwright.sync_api import sync_playwright
        from core.captcha import solve_recaptcha, inject_recaptcha_token

        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto("https://site.com/login")

            site_key = page.get_attribute('[data-sitekey]', 'data-sitekey')
            token = solve_recaptcha(page.url, site_key)
            inject_recaptcha_token(page, token)

            page.click('#submit')
    """
    page.evaluate(f"""
        document.getElementById('g-recaptcha-response').innerHTML = '{token}';
        if (typeof ___grecaptcha_cfg !== 'undefined') {{
            Object.entries(___grecaptcha_cfg.clients).forEach(([key, val]) => {{
                if (val.callback) val.callback('{token}');
            }});
        }}
    """)
    print("[캡챠] 토큰 주입 완료")


def check_balance() -> float:
    """2captcha 잔액 확인 (달러)."""
    _check_key()

    try:
        from twocaptcha import TwoCaptcha
    except ImportError:
        raise ImportError("pip install 2captcha-python 실행 필요")

    solver = TwoCaptcha(API_KEY)
    balance = solver.balance()
    print(f"[캡챠] 현재 잔액: ${balance}")
    return float(balance)


if __name__ == "__main__":
    print("캡챠 모듈 상태 확인")
    print(f"API 키: {'설정됨' if API_KEY else '없음 (.env에 TWOCAPTCHA_API_KEY 추가 필요)'}")
    if API_KEY:
        try:
            check_balance()
        except Exception as e:
            print(f"잔액 확인 실패: {e}")
