import { NextRequest, NextResponse } from 'next/server';
import { generateRequestId } from '@/lib/utils';
import { verifyAuth } from '@/lib/auth-middleware';
import { d1Execute } from '@/lib/d1';


// DELETE /api/dashboard/api-keys/[id] — API 키 비활성화
export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  const requestId = generateRequestId();

  try {
    // JWT 인증 확인
    const auth = await verifyAuth(request);
    if (!auth) {
      return NextResponse.json(
        {
          error: {
            code: 'UNAUTHORIZED',
            message: 'Not authenticated',
            requestId,
          },
        },
        { status: 401 }
      );
    }

    // 소유권 확인 후 비활성화
    await d1Execute(
      'UPDATE api_keys SET is_active = false WHERE id = ? AND user_id = ?',
      [id, auth.userId]
    );

    return NextResponse.json({ data: { id } }, { status: 200 });
  } catch (error) {
    console.error('[API Key DELETE Error]', error);
    return NextResponse.json(
      {
        error: {
          code: 'INTERNAL_ERROR',
          message: 'Internal server error',
          requestId,
        },
      },
      { status: 500 }
    );
  }
}
