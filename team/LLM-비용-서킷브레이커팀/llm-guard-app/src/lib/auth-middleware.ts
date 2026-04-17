/**
 * JWT 기반 인증 미들웨어 (Edge Runtime 호환)
 */

import { NextRequest } from 'next/server';
import { verifyJWT, JWTPayload } from './auth';

export async function verifyAuth(request: NextRequest): Promise<{ userId: string; payload: JWTPayload } | null> {
  try {
    // 1. Authorization 헤더 (API 클라이언트)
    const authHeader = request.headers.get('authorization');
    let token: string | null = null;

    if (authHeader) {
      token = authHeader.split(' ')[1] || null;
    }

    // 2. HttpOnly 쿠키 (브라우저) — raw Cookie 헤더에서 파싱
    if (!token) {
      const cookieHeader = request.headers.get('cookie') || '';
      for (const part of cookieHeader.split(';')) {
        const [name, ...rest] = part.trim().split('=');
        if (name.trim() === 'auth_token') {
          token = rest.join('=') || null;
          break;
        }
      }
    }

    if (!token) return null;

    const payload = await verifyJWT(token);
    if (!payload) return null;

    return { userId: payload.sub, payload };
  } catch (error) {
    console.error('[Auth Middleware] Error:', error);
    return null;
  }
}
