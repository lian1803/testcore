import { NextRequest, NextResponse } from 'next/server';
import { d1QueryOne, d1Execute } from '@/lib/d1';
import { createJWT } from '@/lib/auth';
import { generateRequestId } from '@/lib/utils';

interface GoogleTokenResponse {
  access_token: string;
  expires_in: number;
  refresh_token?: string;
  scope: string;
  token_type: string;
}

interface GoogleUserInfo {
  id: string;
  email: string;
  name: string;
  picture: string;
  verified_email: boolean;
}

interface UserRow {
  id: string;
  email: string;
  plan: string;
}

/**
 * GET /api/auth/google/callback — Google OAuth 콜백
 * Authorization Code를 Access Token으로 교환하고 사용자 정보 조회
 */
export async function GET(request: NextRequest) {
  const requestId = generateRequestId();
  const code = request.nextUrl.searchParams.get('code');
  const error = request.nextUrl.searchParams.get('error');
  const appUrl = process.env.NEXT_PUBLIC_APP_URL || 'https://llm-guard-app.lian1803.workers.dev';

  // OAuth 거부 또는 오류 처리
  if (error || !code) {
    const errorMessage = error || 'oauth_denied';
    return NextResponse.redirect(`${appUrl}/auth/login?error=${errorMessage}&requestId=${requestId}`);
  }

  try {
    // 1. Authorization Code → Access Token 교환
    const tokenRes = await fetch('https://oauth2.googleapis.com/token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({
        code,
        client_id: process.env.GOOGLE_CLIENT_ID!,
        client_secret: process.env.GOOGLE_CLIENT_SECRET!,
        redirect_uri: `${appUrl}/api/auth/google/callback`,
        grant_type: 'authorization_code',
      }),
    });

    if (!tokenRes.ok) {
      const errorText = await tokenRes.text();
      console.error('[Google OAuth] Token exchange failed:', errorText);
      throw new Error('Token exchange failed');
    }

    const tokens = await tokenRes.json() as GoogleTokenResponse;

    // 2. Google 사용자 정보 조회
    const userInfoRes = await fetch('https://www.googleapis.com/oauth2/v2/userinfo', {
      headers: { Authorization: `Bearer ${tokens.access_token}` },
    });

    if (!userInfoRes.ok) {
      console.error('[Google OAuth] User info fetch failed:', userInfoRes.status);
      throw new Error('Failed to get user info');
    }

    const googleUser = await userInfoRes.json() as GoogleUserInfo;

    // 3. 기존 사용자 확인 (google_id 또는 email로)
    let user = await d1QueryOne<UserRow>(
      'SELECT id, email, plan FROM users WHERE google_id = ? OR email = ?',
      [googleUser.id, googleUser.email]
    );

    const now = new Date().toISOString();

    if (user) {
      // 기존 사용자 — google_id, avatar_url 업데이트
      await d1Execute(
        'UPDATE users SET google_id = ?, avatar_url = ?, updated_at = ? WHERE id = ?',
        [googleUser.id, googleUser.picture, now, user.id]
      );
    } else {
      // 신규 사용자 생성 (password = '' — Google OAuth 전용)
      const userId = generateRequestId();
      await d1Execute(
        `INSERT INTO users (id, email, password, google_id, avatar_url, plan, created_at, updated_at)
         VALUES (?, ?, '', ?, ?, 'free', ?, ?)`,
        [userId, googleUser.email, googleUser.id, googleUser.picture, now, now]
      );

      // 기본 프로젝트 생성
      const projectId = generateRequestId();
      await d1Execute(
        `INSERT INTO projects (id, user_id, name, budget_usd, reset_day, is_active, created_at)
         VALUES (?, ?, 'Default Project', 10.0, 1, 1, ?)`,
        [projectId, userId, now]
      );

      user = { id: userId, email: googleUser.email, plan: 'free' };
    }

    // 4. JWT 발급 (기존 시스템 재사용)
    const token = await createJWT({ sub: user.id, email: user.email });

    // 5. 쿠키 설정 후 대시보드로 리다이렉트
    const response = NextResponse.redirect(`${appUrl}/dashboard`);
    response.cookies.set('auth_token', token, {
      httpOnly: true,
      secure: true,
      sameSite: 'lax',
      maxAge: 7 * 24 * 60 * 60,
      path: '/',
    });

    return response;
  } catch (error) {
    console.error('[Google OAuth Callback]', error);
    return NextResponse.redirect(
      `${appUrl}/auth/login?error=oauth_failed&requestId=${requestId}`
    );
  }
}
