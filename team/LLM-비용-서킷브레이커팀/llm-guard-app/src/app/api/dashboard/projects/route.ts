import { NextRequest, NextResponse } from 'next/server';
import { generateRequestId } from '@/lib/utils';
import { verifyAuth } from '@/lib/auth-middleware';
import { d1QueryAll, d1Execute } from '@/lib/d1';
import { z } from 'zod';


const createProjectSchema = z.object({
  name: z.string().min(1).max(100),
  description: z.string().max(500).optional(),
  budget_usd: z.number().positive().default(10.0),
  reset_day: z.number().min(1).max(28).default(1),
});

// GET /api/dashboard/projects — 내 프로젝트 목록
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

    const projects = await d1QueryAll(
      `SELECT id, name, description, budget_usd, reset_day, is_active, created_at
       FROM projects
       WHERE user_id = ?
       ORDER BY created_at DESC`,
      [auth.userId]
    );

    return NextResponse.json({ data: projects }, { status: 200 });
  } catch (error) {
    console.error('[Projects GET Error]', error);
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

// POST /api/dashboard/projects — 프로젝트 생성
export async function POST(request: NextRequest) {
  const requestId = generateRequestId();

  try {
    const body = createProjectSchema.parse(await request.json());

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

    // 프로젝트 생성
    const projectId = generateRequestId();
    const now = new Date().toISOString();

    await d1Execute(
      `INSERT INTO projects (id, user_id, name, description, budget_usd, reset_day, is_active, created_at)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?)`,
      [projectId, auth.userId, body.name, body.description || null, body.budget_usd, body.reset_day, true, now]
    );

    // 초기 budget 레코드 생성
    const periodStart = new Date();
    periodStart.setDate(body.reset_day);
    if (periodStart < new Date()) {
      periodStart.setMonth(periodStart.getMonth() + 1);
    }

    const budgetId = generateRequestId();
    const periodStartStr = periodStart.toISOString().split('T')[0];

    await d1Execute(
      `INSERT INTO budgets (id, project_id, user_id, period_start, spent_usd, call_count, blocked_count)
       VALUES (?, ?, ?, ?, ?, ?, ?)`,
      [budgetId, projectId, auth.userId, periodStartStr, 0, 0, 0]
    ).catch(() => {
      // 무시
    });

    return NextResponse.json({ data: { id: projectId, user_id: auth.userId, name: body.name, description: body.description, budget_usd: body.budget_usd, reset_day: body.reset_day, is_active: true, created_at: now } }, { status: 201 });
  } catch (error) {
    console.error('[Projects POST Error]', error);
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
