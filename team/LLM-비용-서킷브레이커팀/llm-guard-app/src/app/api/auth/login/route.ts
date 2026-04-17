import { NextRequest, NextResponse } from 'next/server';
import { login } from '@/lib/auth';
import { generateRequestId } from '@/lib/utils';
import { z } from 'zod';


const loginSchema = z.object({
  email: z.string().email(),
  password: z.string().min(1, 'Password required'),
});

/**
 * POST /api/auth/login — 로그인
 * D1 + JWT 기반 인증
 */
export async function POST(request: NextRequest) {
  const requestId = generateRequestId();

  try {
    // 1. 요청 파싱
    let body: { email: string; password: string };
    try {
      body = loginSchema.parse(await request.json());
    } catch (error) {
      return NextResponse.json(
        {
          error: {
            code: 'INVALID_REQUEST',
            message:
              error instanceof z.ZodError
                ? error.issues[0].message
                : 'Invalid request body',
            requestId,
          },
        },
        { status: 400 }
      );
    }

    // 2. 로그인 처리
    const { user, token } = await login(body.email, body.password);

    // 3. JWT를 쿠키로 설정
    const response = NextResponse.json(
      {
        data: {
          user_id: user.id,
          email: user.email,
          plan: user.plan,
          message: 'Login successful',
        },
      },
      { status: 200 }
    );

    // HttpOnly 쿠키로 토큰 설정 (OAuth 리다이렉트 호환성을 위해 lax 사용)
    response.cookies.set('auth_token', token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      maxAge: 7 * 24 * 60 * 60, // 7 days
      path: '/',
    });

    return response;
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Internal server error';
    console.error('[Login Error]', error);

    return NextResponse.json(
      {
        error: {
          code: 'AUTH_ERROR',
          message,
          requestId,
        },
      },
      { status: 401 }
    );
  }
}
