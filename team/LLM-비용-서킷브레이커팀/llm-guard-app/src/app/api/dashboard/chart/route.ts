import { NextRequest, NextResponse } from 'next/server';
import { generateRequestId } from '@/lib/utils';
import { verifyAuth } from '@/lib/auth-middleware';
import { d1QueryAll } from '@/lib/d1';


// GET /api/dashboard/chart — 7일 일별 비용 데이터
export async function GET(request: NextRequest) {
  const requestId = generateRequestId();

  try {
    const { searchParams } = new URL(request.url);
    const projectId = searchParams.get('project_id');
    const days = parseInt(searchParams.get('days') || '7', 10);

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

    // 프로젝트 소유권 확인
    const projects = await d1QueryAll(
      'SELECT id FROM projects WHERE id = ? AND user_id = ?',
      [projectId, auth.userId]
    );

    if (!projects || projects.length === 0) {
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

    // N일 전부터 오늘까지 일별 비용 조회
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - days);
    const startDateStr = startDate.toISOString().split('T')[0];

    const logs = await d1QueryAll(
      `SELECT called_at, cost_usd FROM usage_logs
       WHERE project_id = ? AND called_at >= ?
       ORDER BY called_at ASC`,
      [projectId, startDateStr]
    );

    // 일별 합계 계산
    const dailyData: { [date: string]: number } = {};

    for (let i = 0; i < days; i++) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      const dateStr = date.toISOString().split('T')[0];
      dailyData[dateStr] = 0;
    }

    logs?.forEach((log: any) => {
      const dateStr = typeof log.called_at === 'string'
        ? log.called_at.split('T')[0]
        : new Date(log.called_at).toISOString().split('T')[0];
      if (dailyData[dateStr] !== undefined) {
        dailyData[dateStr] += parseFloat(log.cost_usd?.toString() || '0');
      }
    });

    // 날짜순 정렬
    const chartData = Object.entries(dailyData)
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([date, cost]) => ({
        date,
        cost: parseFloat(cost.toFixed(4)),
      }));

    return NextResponse.json({ data: chartData }, { status: 200 });
  } catch (error) {
    console.error('[Chart GET Error]', error);
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
