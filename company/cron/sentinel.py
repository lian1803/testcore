import os
import requests
import time
from . import notify

PROJECT_URL = os.getenv("PROJECT_URL", "https://example.cloudflare.app")
HEALTH_CHECK_INTERVAL = 30 * 60  # 30분


def run_health_check():
    """프로젝트 URL 헬스체크 실행"""
    try:
        start = time.time()
        response = requests.get(PROJECT_URL, timeout=10)
        elapsed = time.time() - start

        if response.status_code == 200:
            notify.notify_health_check(PROJECT_URL, "OK", elapsed)
            return True
        else:
            notify.notify_health_check(PROJECT_URL, f"HTTP {response.status_code}", elapsed)
            return False

    except requests.exceptions.Timeout:
        notify.notify_health_check(PROJECT_URL, "TIMEOUT", 10.0)
        return False
    except requests.exceptions.ConnectionError:
        notify.notify_health_check(PROJECT_URL, "CONNECTION_ERROR", 0)
        return False
    except Exception as e:
        notify.notify_error_detected("HEALTH_CHECK", str(e))
        return False


def scan_error_logs():
    """에러 로그 스캔 (구현 예시)"""
    # 실제 구현: 프로젝트 로그 API에서 에러 가져오기
    # Cloudflare Analytics API, GitHub Actions logs 등
    pass


if __name__ == "__main__":
    print("🔍 센티넬 실행 (헬스체크만 테스트)")
    run_health_check()
