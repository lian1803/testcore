import { NextRequest, NextResponse } from 'next/server';
import type { SDKCheckRequest, SDKCheckResponse } from '@/types';
import {
  getLoopCounter,
  incrementLoopCounter,
  getCurrentMonthSpent,
  incrementCircuitError,
  isCircuitOpen,
  seedBudgetSpentIfMissing,
  tryReserveBudget,
} from '@/lib/cf-kv';

import { d1QueryOne, d1QueryAll } from '@/lib/d1';
import { calculateCost, getModelPricing } from '@/lib/token-pricing';
import { generateRequestId, verifyApiKey, DUMMY_HASH } from '@/lib/utils';
import { z } from 'zod';

const checkRequestSchema = z.object({
  model: z.string(),
  provider: z.enum(['openai', 'anthropic', 'google']),
  estimated_tokens: z.number().positive(),
  request_hash: z.string(),
  context_count: z.number().nonnegative(),
});

const ALLOW_THROUGH: SDKCheckResponse = {
  allowed: true,
  current_spend_usd: 0,
  budget_usd: 0,
  remaining_usd: 0,
  estimated_cost_usd: 0,
};

// C-1: 1.8초 타임아웃 래퍼
function withTimeout<T>(promise: Promise<T>, ms: number): Promise<T> {
  return Promise.race([
    promise,
    new Promise<never>((_, reject) =>
      setTimeout(() => reject(new Error('TIMEOUT')), ms)
    ),
  ]);
}

/**
 * POST /api/v1/sdk/check — 예산 체크 및 예약
 * Cloudflare D1 + KV 기반
 */
export async function POST(request: NextRequest) {
  const requestId = generateRequestId();

  try {
    // 1. 요청 파싱
    let body: SDKCheckRequest;
    try {
      body = checkRequestSchema.parse(await request.json());
    } catch {
      return NextResponse.json(
        { error: { code: 'INVALID_REQUEST', message: 'Invalid request body', requestId } },
        { status: 400 }
      );
    }

    // 2. API Key 검증
    const apiKey = request.headers.get('X-LLM-Guard-Key');
    if (!apiKey) {
      return NextResponse.json(
        { error: { code: 'MISSING_API_KEY', message: 'Missing X-LLM-Guard-Key header', requestId } },
        { status: 401 }
      );
    }

    // C-2: 서킷브레이커 — DB 연속 오류 5회 이상이면 즉시 allow-through
    const circuitKey = `sdk-check`;
    if (await isCircuitOpen(circuitKey)) {
      return NextResponse.json(ALLOW_THROUGH, { status: 200 });
    }

    // 3. API Key 조회 (D1)
    type ApiKeyRow = {
      id: string;
      project_id: string;
      user_id: string;
      key_hash: string;
      is_active: number;
    };

    let apiKeyRecord: ApiKeyRow | null = null;
    try {
      apiKeyRecord = await withTimeout(
        d1QueryOne<ApiKeyRow>(
          'SELECT id, project_id, user_id, key_hash, is_active FROM api_keys WHERE key_prefix = ?',
          [apiKey.substring(0, 13)]
        ),
        1800
      );
    } catch (error) {
      // C-1/C-2: 타임아웃 or DB 오류
      console.error('[SDK Check] DB timeout:', error);
      await incrementCircuitError(circuitKey).catch(() => {});
      return NextResponse.json(ALLOW_THROUGH, { status: 200 });
    }

    // C-3: prefix 불일치 시에도 더미 bcrypt 실행 (응답 시간 동일화)
    if (!apiKeyRecord) {
      await verifyApiKey(apiKey, DUMMY_HASH);
      return NextResponse.json(
        { error: { code: 'INVALID_API_KEY', message: 'Invalid API key', requestId } },
        { status: 401 }
      );
    }

    if (!apiKeyRecord.is_active) {
      return NextResponse.json(
        {
          error: {
            code: 'API_KEY_DISABLED',
            message: 'API key is disabled',
            requestId,
          },
        },
        { status: 403 }
      );
    }

    // bcrypt 검증
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

    // 4. 프로젝트 & 예산 조회 (D1)
    type ProjectRow = {
      id: string;
      budget_usd: number;
      reset_day: number;
      is_active: number;
    };

    const project = await d1QueryOne<ProjectRow>(
      'SELECT id, budget_usd, reset_day, is_active FROM projects WHERE id = ?',
      [apiKeyRecord.project_id]
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

    if (!project.is_active) {
      return NextResponse.json(
        {
          error: {
            code: 'PROJECT_INACTIVE',
            message: 'Project is inactive',
            requestId,
          },
        },
        { status: 403 }
      );
    }

    // 5. 예상 비용 계산
    const pricing = getModelPricing(body.provider, body.model);
    const estimatedCost = pricing
      ? calculateCost(body.provider, body.model, body.estimated_tokens, 0)
      : 0;

    // 6. KV에서 누적 비용 조회 (D1 fallback + seeding)
    let currentSpent = await getCurrentMonthSpent(project.id);
    if (currentSpent === 0) {
      // KV miss — D1에서 조회 후 seed
      type BudgetRow = { spent_usd: number };
      const budgetRecord = await d1QueryOne<BudgetRow>(
        `SELECT spent_usd FROM budgets
         WHERE project_id = ?
         AND period_start >= date('now', '-35 days')
         ORDER BY period_start DESC
         LIMIT 1`,
        [project.id]
      );

      currentSpent = budgetRecord?.spent_usd ?? 0;
      if (currentSpent > 0) {
        await seedBudgetSpentIfMissing(project.id, currentSpent);
      }
    }

    // 7. 루프 감지 (예산 예약 전 — loop면 예약 불필요)
    let loopCount = await getLoopCounter(project.id, body.request_hash);
    loopCount = loopCount + 1;
    await incrementLoopCounter(project.id, body.request_hash);
    const loopDetected = loopCount >= 10;

    if (loopDetected) {
      return NextResponse.json(
        {
          allowed: false,
          current_spend_usd: currentSpent,
          budget_usd: project.budget_usd,
          remaining_usd: Math.max(0, project.budget_usd - currentSpent),
          estimated_cost_usd: estimatedCost,
          reason: 'loop_detected',
        } satisfies SDKCheckResponse,
        { status: 200 }
      );
    }

    // 8. 원자적 예산 예약 (KV 기반, race condition 방지 최선)
    const budgetAllowed = await tryReserveBudget(
      project.id,
      estimatedCost,
      project.budget_usd
    );

    // 응답 생성
    const response: SDKCheckResponse = {
      allowed: budgetAllowed,
      current_spend_usd: currentSpent,
      budget_usd: project.budget_usd,
      remaining_usd: Math.max(0, project.budget_usd - currentSpent),
      estimated_cost_usd: estimatedCost,
      reason: !budgetAllowed ? 'budget_exceeded' : undefined,
    };

    // 로그: last_used_at 업데이트 (비동기, fire-and-forget)
    void d1QueryOne(
      'UPDATE api_keys SET last_used_at = ? WHERE id = ?',
      [new Date().toISOString(), apiKeyRecord.id]
    ).catch(() => {});

    return NextResponse.json(response, { status: 200 });
  } catch (error) {
    // C-1/C-2: 타임아웃 or DB 오류 → 서킷브레이커 카운터 증가 + allow-through
    const errMsg = error instanceof Error ? error.message : String(error);
    console.error('[SDK Check Error]', errMsg);
    await incrementCircuitError('sdk-check').catch(() => {});

    return NextResponse.json(ALLOW_THROUGH, { status: 200 });
  }
}
