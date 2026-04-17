import { NextRequest, NextResponse } from 'next/server';
import { generateRequestId } from '@/lib/utils';


/**
 * POST /api/auth/signout — 로그아웃
 */
export async function POST(request: NextRequest) {
  const requestId = generateRequestId();

  try {
    const response = NextResponse.json(
      {
        data: {
          message: 'Signout successful',
        },
      },
      { status: 200 }
    );

    // 쿠키 삭제
    response.cookies.delete('auth_token');

    return response;
  } catch (error) {
    console.error('[Signout Error]', error);

    return NextResponse.json(
      {
        error: {
          code: 'SIGNOUT_ERROR',
          message: 'Failed to sign out',
          requestId,
        },
      },
      { status: 500 }
    );
  }
}
