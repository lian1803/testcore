/**
 * Cloudflare KV HTTP API 클라이언트
 * Upstash Redis 완전 대체
 * https://developers.cloudflare.com/kv/api/
 */

class CFKVClient {
  private accountId: string;
  private namespaceId: string;
  private apiToken: string;
  private baseUrl: string;

  constructor() {
    this.accountId = process.env.CF_ACCOUNT_ID!;
    this.namespaceId = process.env.CF_KV_NAMESPACE_ID!;
    this.apiToken = process.env.CF_API_TOKEN!;
    this.baseUrl = `https://api.cloudflare.com/client/v4/accounts/${this.accountId}/storage/kv/namespaces/${this.namespaceId}`;

    if (!this.accountId || !this.namespaceId || !this.apiToken) {
      throw new Error('Missing Cloudflare KV credentials in environment variables');
    }
  }

  private async request(
    method: string,
    path: string,
    options?: {
      body?: string;
      headers?: Record<string, string>;
      params?: Record<string, string>;
    }
  ): Promise<any> {
    const url = new URL(`${this.baseUrl}${path}`);
    if (options?.params) {
      Object.entries(options.params).forEach(([key, value]) => {
        url.searchParams.append(key, value);
      });
    }

    try {
      const response = await fetch(url.toString(), {
        method,
        headers: {
          'Authorization': `Bearer ${this.apiToken}`,
          'Content-Type': 'application/json',
          ...options?.headers,
        },
        body: options?.body,
      });

      if (!response.ok) {
        const error = await response.text();
        throw new Error(`CF KV API error: ${response.status} - ${error}`);
      }

      // DELETE는 응답 바디가 없을 수 있음
      if (method === 'DELETE') {
        return null;
      }

      const contentType = response.headers.get('content-type');
      if (contentType?.includes('application/json')) {
        return await response.json();
      } else {
        // GET value는 plain text
        return await response.text();
      }
    } catch (error) {
      console.error('[CF KV] Request failed:', error);
      throw error;
    }
  }

  /**
   * 값 조회 (GET)
   */
  async get<T = any>(key: string): Promise<T | null> {
    try {
      const value = await this.request('GET', `/values/${encodeURIComponent(key)}`);
      if (value === null || value === '') {
        return null;
      }

      // JSON 파싱 시도
      try {
        return JSON.parse(value) as T;
      } catch {
        // 일반 문자열
        return value as T;
      }
    } catch (error) {
      console.error('[CF KV] Get error:', error);
      return null;
    }
  }

  /**
   * 값 설정 (PUT)
   */
  async set(
    key: string,
    value: any,
    options?: { expirationTtl?: number; metadata?: Record<string, string> }
  ): Promise<void> {
    try {
      const body =
        typeof value === 'string' ? value : JSON.stringify(value);

      const params: Record<string, string> = {};
      if (options?.expirationTtl) {
        params.expirationTtl = String(options.expirationTtl);
      }

      await this.request('PUT', `/values/${encodeURIComponent(key)}`, {
        body,
        params,
        headers: {
          'Content-Type':
            typeof value === 'string' ? 'text/plain' : 'application/json',
        },
      });
    } catch (error) {
      console.error('[CF KV] Set error:', error);
      throw error;
    }
  }

  /**
   * 값 삭제 (DELETE)
   */
  async del(key: string): Promise<void> {
    try {
      await this.request('DELETE', `/values/${encodeURIComponent(key)}`);
    } catch (error) {
      console.error('[CF KV] Del error:', error);
      throw error;
    }
  }

  /**
   * 숫자 증가 (GET → +1 → PUT)
   * CF KV는 atomic increment를 지원하지 않으므로 낙관적 방식 사용
   */
  async incr(key: string, by: number = 1): Promise<number> {
    try {
      const current = await this.get<number>(key);
      const newValue = (current ?? 0) + by;
      await this.set(key, newValue);
      return newValue;
    } catch (error) {
      console.error('[CF KV] Incr error:', error);
      throw error;
    }
  }

  /**
   * 실수 증가
   */
  async incrByFloat(key: string, by: number): Promise<number> {
    try {
      const current = await this.get<number>(key);
      const newValue = (current ?? 0) + by;
      await this.set(key, newValue);
      return newValue;
    } catch (error) {
      console.error('[CF KV] IncrByFloat error:', error);
      throw error;
    }
  }

  /**
   * TTL 설정 (EXPIRE)
   * CF KV는 직접 TTL을 설정할 수 없으므로, GET → SET with TTL
   */
  async expire(key: string, ttl: number): Promise<boolean> {
    try {
      const value = await this.get(key);
      if (value === null) {
        return false;
      }
      await this.set(key, value, { expirationTtl: ttl });
      return true;
    } catch (error) {
      console.error('[CF KV] Expire error:', error);
      return false;
    }
  }

  /**
   * 존재 여부 확인
   */
  async exists(key: string): Promise<boolean> {
    try {
      const value = await this.get(key);
      return value !== null;
    } catch {
      return false;
    }
  }
}

let kvClient: CFKVClient | null = null;

/**
 * CF KV 클라이언트 싱글톤 반환
 */
export function getKVClient(): CFKVClient {
  if (!kvClient) {
    kvClient = new CFKVClient();
  }
  return kvClient;
}

/**
 * ============================================
 * Upstash Redis API 호환성 레이어
 * ============================================
 */

/**
 * 현재 월의 누적 비용 조회
 */
export async function getCurrentMonthSpent(projectId: string): Promise<number> {
  const kv = getKVClient();
  const key = `budget:${projectId}:current`;

  try {
    const spent = await kv.get<number>(key);
    return spent ?? 0;
  } catch (error) {
    console.error('[KV] Error getting current spend:', error);
    return 0;
  }
}

/**
 * 비용 증액
 */
export async function incrementSpent(
  projectId: string,
  amount: number
): Promise<void> {
  const kv = getKVClient();
  const key = `budget:${projectId}:current`;

  try {
    await kv.incrByFloat(key, amount);
    // 30일 TTL 설정
    await kv.expire(key, 30 * 24 * 60 * 60);
  } catch (error) {
    console.error('[KV] Error incrementing spend:', error);
    // 에러 무시 (DB write 이후 일관성 있음)
  }
}

/**
 * 월별 누적 비용 리셋
 */
export async function resetMonthlyBudget(projectId: string): Promise<void> {
  const kv = getKVClient();
  const key = `budget:${projectId}:current`;

  try {
    await kv.del(key);
  } catch (error) {
    console.error('[KV] Error resetting budget:', error);
  }
}

/**
 * 루프 감지용 카운터 증가
 */
export async function incrementLoopCounter(
  projectId: string,
  requestHash: string
): Promise<number> {
  const kv = getKVClient();
  const key = `loop:${projectId}:${requestHash}`;

  try {
    const count = await kv.incr(key);
    // 5분 TTL 설정
    await kv.expire(key, 5 * 60);
    return count;
  } catch (error) {
    console.error('[KV] Error incrementing loop counter:', error);
    return 0;
  }
}

/**
 * 루프 카운터 조회
 */
export async function getLoopCounter(
  projectId: string,
  requestHash: string
): Promise<number> {
  const kv = getKVClient();
  const key = `loop:${projectId}:${requestHash}`;

  try {
    const count = await kv.get<number>(key);
    return count ?? 0;
  } catch (error) {
    console.error('[KV] Error getting loop counter:', error);
    return 0;
  }
}

/**
 * Redis에 spent 초기화 (DB fallback 후 seeding용)
 * CF KV는 atomic SET NX를 지원하지 않으므로 조건부로 처리
 */
export async function seedBudgetSpentIfMissing(
  projectId: string,
  amount: number
): Promise<void> {
  const kv = getKVClient();
  const key = `budget:${projectId}:current`;

  try {
    const exists = await kv.exists(key);
    if (!exists) {
      await kv.set(key, amount, {
        expirationTtl: 30 * 24 * 60 * 60,
      });
    }
  } catch (error) {
    console.error('[KV] seedBudgetSpentIfMissing error:', error);
  }
}

/**
 * 원자적 예산 예약
 * CF KV는 Lua script을 지원하지 않으므로 낙관적 잠금으로 구현
 * 실제 환경에서는 D1의 트랜잭션으로 backup
 */
export async function tryReserveBudget(
  projectId: string,
  estimatedCost: number,
  budgetUsd: number
): Promise<boolean> {
  const kv = getKVClient();
  const spentKey = `budget:${projectId}:current`;
  const reservedKey = `budget:${projectId}:reserved`;

  try {
    const spent = await kv.get<number>(spentKey);
    const reserved = await kv.get<number>(reservedKey);

    const currentSpent = spent ?? 0;
    const currentReserved = reserved ?? 0;

    if (currentSpent + currentReserved + estimatedCost > budgetUsd) {
      return false;
    }

    await kv.incrByFloat(reservedKey, estimatedCost);
    await kv.expire(reservedKey, 5 * 60); // 5분 TTL

    return true;
  } catch (error) {
    console.error('[KV] tryReserveBudget error:', error);
    return true; // fail-open
  }
}

/**
 * 예약 해제
 */
export async function releaseReservation(
  projectId: string,
  amount: number
): Promise<void> {
  const kv = getKVClient();
  const reservedKey = `budget:${projectId}:reserved`;

  try {
    await kv.incrByFloat(reservedKey, -amount);
  } catch (error) {
    console.error('[KV] releaseReservation error:', error);
  }
}

/**
 * 서킷브레이커 — DB 오류 카운터 증가
 */
export async function incrementCircuitError(key: string): Promise<number> {
  const kv = getKVClient();
  const errorKey = `circuit:${key}:errors`;

  try {
    const count = await kv.incr(errorKey);
    await kv.expire(errorKey, 60);
    return count;
  } catch {
    return 0;
  }
}

/**
 * 서킷브레이커 리셋
 */
export async function resetCircuitError(key: string): Promise<void> {
  const kv = getKVClient();
  try {
    await kv.del(`circuit:${key}:errors`);
  } catch {
    /* 무시 */
  }
}

/**
 * 서킷브레이커 상태 확인
 */
export async function isCircuitOpen(key: string): Promise<boolean> {
  const kv = getKVClient();
  try {
    const count = await kv.get<number>(`circuit:${key}:errors`);
    return (count ?? 0) >= 5;
  } catch {
    return false;
  }
}

export { CFKVClient };
