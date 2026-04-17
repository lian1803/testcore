import { NextRequest, NextResponse } from 'next/server';
import { generateApiKey, hashApiKey, generateRequestId } from '@/lib/utils';
import { verifyAuth } from '@/lib/auth-middleware';
import { d1QueryAll, d1Execute } from '@/lib/d1';
import { z } from 'zod';


const createKeySchema = z.object({
  project_id: z.string(),
  name: z.string().min(1).max(100),
});

// GET /api/dashboard/api-keys — 내 API 키 목록 조회
export async function GET(request: NextRequest) {
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

    // 내 API 키 조회
    const apiKeys = await d1QueryAll(
      `SELECT id, project_id, name, key_prefix, last_used_at, is_active, created_at
       FROM api_keys
       WHERE user_id = ?
       ORDER BY created_at DESC`,
      [auth.userId]
    );

    return NextResponse.json({ data: apiKeys }, { status: 200 });
  } catch (error) {
    console.error('[API Keys GET Error]', error);
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

// POST /api/dashboard/api-keys — 신규 API 키 발급
export async function POST(request: NextRequest) {
  const requestId = generateRequestId();

  try {
    const body = createKeySchema.parse(await request.json());

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

    // 프로젝트 소유권 확인
    const project = await d1QueryAll(
      'SELECT id FROM projects WHERE id = ? AND user_id = ?',
      [body.project_id, auth.userId]
    );

    if (!project || project.length === 0) {
      return NextResponse.json(
        {
          error: {
            code: 'PROJECT_NOT_FOUND',
            message: 'Project not found',
            requestId,
          },
        },
        { status: 404 }
      );
    }

    // 새 API 키 생성
    const { key, prefix } = generateApiKey();
    const keyHash = await hashApiKey(key);
    const keyId = generateRequestId();
    const now = new Date().toISOString();

    // DB 저장
    await d1Execute(
      `INSERT INTO api_keys (id, user_id, project_id, name, key_hash, key_prefix, is_active, created_at)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?)`,
      [keyId, auth.userId, body.project_id, body.name, keyHash, prefix, true, now]
    );

    // 응답: 원본 키는 1회만 노출
    return NextResponse.json(
      {
        data: {
          key, // 원본 (1회만)
          prefix,
          message: 'Save this key securely. You will not be able to see it again.',
        },
      },
      { status: 201 }
    );
  } catch (error) {
    console.error('[API Keys POST Error]', error);
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
