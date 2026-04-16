"""
naver_auth.py — 네이버 블로그 OAuth 인증

네이버 블로그 API 사용을 위한 OAuth 토큰 발급 및 갱신.

사용법:
    python utils/naver_auth.py --get-token
    python utils/naver_auth.py --refresh
"""

import os
import sys
import json
import webbrowser
from urllib.parse import urlencode, parse_qs
from urllib.request import urlopen
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from dotenv import load_dotenv

load_dotenv()


class OAuth2CallbackHandler(BaseHTTPRequestHandler):
    """OAuth2 콜백 핸들러."""

    auth_code = None

    def do_GET(self):
        """콜백 URL에서 authorization code 추출."""
        query = parse_qs(self.path.split('?')[1] if '?' in self.path else '')

        if 'code' in query:
            OAuth2CallbackHandler.auth_code = query['code'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(b"""
            <html>
            <head><title>OAuth2 Success</title></head>
            <body style="font-family: Arial; text-align: center; margin-top: 50px;">
            <h1>인증 성공!</h1>
            <p>이 창을 닫고 터미널로 돌아가세요.</p>
            </body>
            </html>
            """.encode())
        else:
            self.send_response(400)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Authorization code not found')

    def log_message(self, format, *args):
        """로그 메시지 억제."""
        pass


class NaverBlogOAuth:
    """네이버 블로그 OAuth 관리."""

    def __init__(self):
        self.client_id = os.getenv("NAVER_BLOG_CLIENT_ID")
        self.client_secret = os.getenv("NAVER_BLOG_CLIENT_SECRET")
        self.redirect_uri = "http://localhost:8888/callback"
        self.auth_url = "https://nid.naver.com/oauth2.0/authorize"
        self.token_url = "https://nid.naver.com/oauth2.0/token"

    def get_authorization_url(self) -> str:
        """인증 URL 생성."""
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "state": "company_oauth",
        }
        return f"{self.auth_url}?{urlencode(params)}"

    def get_access_token(self) -> str:
        """OAuth2 플로우로 액세스 토큰 발급.

        1. 브라우저에서 사용자 인증
        2. authorization code 받음
        3. 토큰 교환
        """
        if not self.client_id or not self.client_secret:
            print("❌ NAVER_BLOG_CLIENT_ID 또는 NAVER_BLOG_CLIENT_SECRET이 설정되지 않았습니다.")
            print("   SETUP_PUBLISH.md의 '2-1. 네이버 개발자 등록' 섹션을 참고하세요.")
            return None

        print("\n" + "="*60)
        print("🔐 네이버 블로그 OAuth 인증 시작")
        print("="*60)

        # Step 1: 로컬 서버 시작 (콜백 수신)
        server = HTTPServer(("localhost", 8888), OAuth2CallbackHandler)
        print("\n✓ 로컬 서버 시작: http://localhost:8888")

        # Step 2: 브라우저에서 인증
        auth_url = self.get_authorization_url()
        print("\n⏳ 브라우저에서 인증을 진행해주세요...")
        webbrowser.open(auth_url)

        # Step 3: 콜백 대기
        print("   (인증 후 이 창으로 돌아옵니다)")
        server.timeout = 120
        server.handle_request()
        server.server_close()

        if not OAuth2CallbackHandler.auth_code:
            print("❌ 인증이 취소되었거나 시간이 초과되었습니다.")
            return None

        auth_code = OAuth2CallbackHandler.auth_code
        print(f"\n✓ Authorization code 받음")

        # Step 4: 토큰 교환
        print("  토큰 교환 중...")
        try:
            token_params = {
                "grant_type": "authorization_code",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "code": auth_code,
                "redirect_uri": self.redirect_uri,
            }
            token_url_with_params = f"{self.token_url}?{urlencode(token_params)}"

            response = urlopen(token_url_with_params)
            token_data = json.loads(response.read().decode())

            if "access_token" in token_data:
                access_token = token_data["access_token"]
                expires_in = token_data.get("expires_in", 3600)

                print(f"✅ 토큰 발급 성공!")
                print(f"   유효기간: {expires_in}초 ({expires_in/3600:.1f}시간)")
                print(f"\n📝 .env 파일에 다음을 추가하세요:")
                print(f"   NAVER_BLOG_ACCESS_TOKEN={access_token}")

                return access_token
            else:
                error = token_data.get("error_description", "알 수 없는 에러")
                print(f"❌ 토큰 발급 실패: {error}")
                return None

        except Exception as e:
            print(f"❌ 토큰 교환 실패: {str(e)}")
            return None

    def refresh_access_token(self, refresh_token: str) -> str:
        """Refresh token을 사용하여 새 액세스 토큰 발급."""
        print("\n" + "="*60)
        print("🔄 토큰 갱신 시작")
        print("="*60)

        try:
            token_params = {
                "grant_type": "refresh_token",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "refresh_token": refresh_token,
            }
            token_url_with_params = f"{self.token_url}?{urlencode(token_params)}"

            response = urlopen(token_url_with_params)
            token_data = json.loads(response.read().decode())

            if "access_token" in token_data:
                new_access_token = token_data["access_token"]
                expires_in = token_data.get("expires_in", 3600)

                print(f"✅ 토큰 갱신 성공!")
                print(f"   새 토큰 유효기간: {expires_in}초")
                print(f"\n📝 .env 파일의 NAVER_BLOG_ACCESS_TOKEN을 다음으로 업데이트하세요:")
                print(f"   NAVER_BLOG_ACCESS_TOKEN={new_access_token}")

                return new_access_token
            else:
                error = token_data.get("error_description", "알 수 없는 에러")
                print(f"❌ 토큰 갱신 실패: {error}")
                return None

        except Exception as e:
            print(f"❌ 토큰 갱신 실패: {str(e)}")
            return None


# ── CLI ──────────────────────────────────────────────────────


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법:")
        print("  python utils/naver_auth.py --get-token    # 새 토큰 발급")
        print("  python utils/naver_auth.py --refresh       # 토큰 갱신 (구현 예정)")
        sys.exit(1)

    command = sys.argv[1]
    oauth = NaverBlogOAuth()

    if command == "--get-token":
        token = oauth.get_access_token()
        if token:
            print("\n" + "="*60)
            print("다음 단계:")
            print("1. .env 파일에 복사하기")
            print("2. python -m core.auto_publish process_queue 실행")
            print("="*60 + "\n")

    elif command == "--refresh":
        print("⚠️  Refresh token 갱신 기능은 추후 구현됩니다.")
        print("   현재는 --get-token으로 새 토큰을 발급하세요.")

    else:
        print(f"❌ 알 수 없는 명령어: {command}")
        print("   --get-token 또는 --refresh를 사용하세요.")
