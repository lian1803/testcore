import { NextRequest, NextResponse } from 'next/server';
import { generateRequestId, getMonthPeriodStart } from '@/lib/utils';
import { verifyAuth } from '@/lib/auth-middleware';
import { d1QueryOne } from '@/lib/d1';


// GET /api/dashboard/usage — 현재 월 누적 비용 + 예산 대비 %
export async function GET(request: NextRequest) {
  const requestId = generateRequestId();

  try {
    const { searchParams } = new URL(request.url);
    const projectId = searchParams.get('project_id');

    if (!projectId) {
      return NextResponse.json(
        {
          error: {
            code: 'MISSING_PARAM',
            message: 'Missing project_id parameter',
            requestId,
          },
        },
        { status: 400 }
      );
    }

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

    // 프로젝트 조회 (소유권 확인)
    const project = await d1QueryOne<{ id: string; budget_usd: number; reset_day: number }>(
      'SELECT id, budget_usd, reset_day FROM projects WHERE id = ? AND user_id = ?',
      [projectId, auth.userId]
    );

    if (!project) {
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

    // 현재 월 예산 조회
    const periodStart = getMonthPeriodStart(project.reset_day);
    const periodStartStr = periodStart.toISOString().split('T')[0];

    const budget = await d1QueryOne<{ spent_usd: number; call_count: number; blocked_count: number }>(
      `SELECT spent_usd, call_count, blocked_count FROM budgets
       WHERE project_id = ? AND period_start = ?`,
      [projectId, periodStartStr]
    );

    const spentUsd = budget?.spent_usd ?? 0;
    const percentage = (spentUsd / project.budget_usd) * 100;

    return NextResponse.json(
      {
        data: {
          project_id: projectId,
          budget_usd: project.budget_usd,
          spent_usd: parseFloat(spentUsd.toString()),
          remaining_usd: Math.max(0, project.budget_usd - parseFloat(spentUsd.toString())),
          percentage: Math.min(100, percentage),
          period_start: periodStartStr,
          call_count: budget?.call_count ?? 0,
          blocked_count: budget?.blocked_count ?? 0,
        },
      },
      { status: 200 }
    );
  } catch (error) {
    console.error('[Usage GET Error]', error);
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
