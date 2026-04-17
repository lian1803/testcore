import { NextRequest, NextResponse } from 'next/server';
import type { SDKReportRequest } from '@/types';
import { incrementSpent, releaseReservation } from '@/lib/cf-kv';
import { d1QueryOne, d1Execute } from '@/lib/d1';
import { generateRequestId, verifyApiKey, getMonthPeriodStart } from '@/lib/utils';

import { z } from 'zod';

const reportRequestSchema = z.object({
  model: z.string(),
  provider: z.enum(['openai', 'anthropic', 'google']),
  input_tokens: z.number().nonnegative(),
  output_tokens: z.number().nonnegative(),
  cost_usd: z.number().nonnegative(),
  latency_ms: z.number().nonnegative(),
  is_blocked: z.boolean(),
  request_hash: z.string(),
});

/**
 * POST /api/v1/sdk/report — 사용량 보고 (fire-and-forget)
 * Cloudflare D1 + KV 기반
 */
export async function POST(request: NextRequest) {
  const requestId = generateRequestId();

  try {
    // 1. 요청 파싱
    let body: SDKReportRequest;
    try {
      body = reportRequestSchema.parse(await request.json());
    } catch (error) {
      return NextResponse.json(
        {
          error: {
            code: 'INVALID_REQUEST',
            message: 'Invalid request body',
            requestId,
          },
        },
        { status: 400 }
      );
    }

    // 2. API Key 검증
    const apiKey = request.headers.get('X-LLM-Guard-Key');
    if (!apiKey) {
      return NextResponse.json(
        {
          error: {
            code: 'MISSING_API_KEY',
            message: 'Missing X-LLM-Guard-Key header',
            requestId,
          },
        },
        { status: 401 }
      );
    }

    type ApiKeyRow = {
      id: string;
      project_id: string;
      user_id: string;
      key_hash: string;
      is_active: number;
    };

    const apiKeyRecord = await d1QueryOne<ApiKeyRow>(
      'SELECT id, project_id, user_id, key_hash, is_active FROM api_keys WHERE key_prefix = ?',
      [apiKey.substring(0, 13)]
    );

    if (!apiKeyRecord || !apiKeyRecord.is_active) {
      return NextResponse.json(
        {
          error: {
            code: 'INVALID_API_KEY',
            message: 'Invalid API key',
            requestId,
          },
        },
        { status: 401 }
      );
    }

    const keyValid = await verifyApiKey(apiKey, apiKeyRecord.key_hash);
    if (!keyValid) {
      return NextResponse.json(
        {
          error: {
            code: 'INVALID_API_KEY',
            message: 'Invalid API key',
            requestId,
          },
        },
        { status: 401 }
      );
    }

    // 3. 즉시 200 반환 (fire-and-forget)
    // 실제 DB write는 백그라운드에서 진행
    const response = NextResponse.json({ received: true }, { status: 200 });

    // 4. 비동기 처리 (응답 후 진행)
    (async () => {
      try {
        const now = new Date().toISOString();
        const logId = generateRequestId();

        // 4a. usage_log 기록 (D1)
        await d1Execute(
          `INSERT INTO usage_logs
           (id, project_id, user_id, model, provider, input_tokens, output_tokens, cost_usd, is_blocked, block_reason, request_hash, latency_ms, called_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
          [
            logId,
            apiKeyRecord.project_id,
            apiKeyRecord.user_id,
            body.model,
            body.provider,
            body.input_tokens,
            body.output_tokens,
            body.cost_usd,
            body.is_blocked ? 1 : 0,
            body.is_blocked ? 'budget_exceeded' : null,
            body.request_hash,
            body.latency_ms,
            now,
          ]
        );

        // 4b. KV에 비용 증액 + check 시 예약분 해제
        await incrementSpent(apiKeyRecord.project_id, body.cost_usd);
        await releaseReservation(apiKeyRecord.project_id, body.cost_usd);

        // 4c. budgets 테이블 업데이트 (upsert)
        const periodStart = getMonthPeriodStart(1);
        const periodStartStr = periodStart.toISOString().split('T')[0];

        // D1에서 직접 upsert (INSERT OR REPLACE는 SQLite 문법)
        const budgetId = generateRequestId();
        await d1Execute(
          `INSERT INTO budgets (id, project_id, user_id, period_start, spent_usd, call_count, blocked_count, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)
           ON CONFLICT(project_id, period_start) DO UPDATE SET
             spent_usd = spent_usd + ?,
             call_count = call_count + ?,
             blocked_count = blocked_count + ?,
             updated_at = ?`,
          [
            budgetId,
            apiKeyRecord.project_id,
            apiKeyRecord.user_id,
            periodStartStr,
            body.cost_usd,
            body.is_blocked ? 0 : 1,
            body.is_blocked ? 1 : 0,
            now,
            body.cost_usd,
            body.is_blocked ? 0 : 1,
            body.is_blocked ? 1 : 0,
            now,
          ]
        );
      } catch (bgError) {
        console.error('[Report] Background task error:', bgError);
        // 에러 로깅만 하고 계속
      }
    })();

    return response;
  } catch (error) {
    console.error('[SDK Report Error]', error);
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
