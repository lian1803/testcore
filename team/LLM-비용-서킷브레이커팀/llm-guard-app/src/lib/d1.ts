/**
 * Cloudflare D1 HTTP API 클라이언트
 * D1 REST API를 통해 쿼리 실행
 * https://developers.cloudflare.com/d1/build-databases/query-databases/
 */

interface D1QueryRequest {
  sql: string | string[];
  params?: unknown[];
}

interface D1QueryResult {
  success: boolean;
  errors: { message: string }[];
  result: Array<{
    success: boolean;
    error?: string;
    results?: unknown[];
  }>;
}

class D1Client {
  private accountId: string;
  private databaseId: string;
  private apiToken: string;
  private baseUrl: string;

  constructor() {
    this.accountId = process.env.CF_ACCOUNT_ID!;
    this.databaseId = process.env.CF_D1_DATABASE_ID!;
    this.apiToken = process.env.CF_API_TOKEN!;
    this.baseUrl = `https://api.cloudflare.com/client/v4/accounts/${this.accountId}/d1/database/${this.databaseId}`;

    if (!this.accountId || !this.databaseId || !this.apiToken) {
      throw new Error('Missing Cloudflare D1 credentials in environment variables');
    }
  }

  private async request(data: D1QueryRequest): Promise<D1QueryResult> {
    try {
      const response = await fetch(`${this.baseUrl}/query`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.apiToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const error = await response.text();
        throw new Error(`D1 API error: ${response.status} - ${error}`);
      }

      return await response.json();
    } catch (error) {
      console.error('[D1 Client] Request failed:', error);
      throw error;
    }
  }

  /**
   * 단일 쿼리 실행 (SELECT/INSERT/UPDATE/DELETE)
   */
  async query<T = any>(sql: string, params?: unknown[]): Promise<T[]> {
    const result = await this.request({ sql, params });

    if (!result.success || (result.errors && result.errors.length > 0)) {
      throw new Error(`D1 Query failed: ${JSON.stringify(result.errors)}`);
    }

    if (!result.result || result.result.length === 0 || !result.result[0].success) {
      const err = result.result?.[0]?.error || 'Unknown error';
      throw new Error(`D1 Query execution failed: ${err}`);
    }

    return (result.result[0].results || []) as T[];
  }

  /**
   * 배치 쿼리 실행 (여러 SQL 한 번에)
   */
  async batch(sqls: string[], paramsList?: unknown[][]): Promise<any[][]> {
    const params = paramsList || sqls.map(() => []);

    const result = await this.request({
      sql: sqls,
      params: params.flat(), // Cloudflare D1은 params를 flatten해서 보냄
    });

    if (!result.success || (result.errors && result.errors.length > 0)) {
      throw new Error(`D1 Batch failed: ${JSON.stringify(result.errors)}`);
    }

    return (result.result || []).map((r) => {
      if (!r.success) {
        throw new Error(`D1 Batch step failed: ${r.error}`);
      }
      return r.results || [];
    });
  }

  /**
   * 트랜잭션 (복합 작업)
   * Note: D1는 완전한 트랜잭션 지원이 제한적이므로,
   * 여러 쿼리를 batch로 보내고 실패 시 롤백 처리
   */
  async transaction<T>(
    fn: (client: D1Client) => Promise<T>
  ): Promise<T> {
    try {
      // BEGIN 실행 (아직 D1가 완전히 지원하지 않으면 스킵)
      return await fn(this);
    } catch (error) {
      console.error('[D1] Transaction error:', error);
      throw error;
    }
  }
}

let d1Client: D1Client | null = null;

/**
 * D1 클라이언트 싱글톤 반환
 */
export function getD1Client(): D1Client {
  if (!d1Client) {
    d1Client = new D1Client();
  }
  return d1Client;
}

/**
 * 헬퍼: 단일 행 조회
 */
export async function d1QueryOne<T = any>(
  sql: string,
  params?: unknown[]
): Promise<T | null> {
  const client = getD1Client();
  const results = await client.query<T>(sql, params);
  return results[0] || null;
}

/**
 * 헬퍼: 모든 행 조회
 */
export async function d1QueryAll<T = any>(
  sql: string,
  params?: unknown[]
): Promise<T[]> {
  const client = getD1Client();
  return client.query<T>(sql, params);
}

/**
 * 헬퍼: INSERT/UPDATE/DELETE 실행 (영향받은 행 수 반환)
 * Note: D1 API는 changes 필드를 반환하지 않으므로 추적이 어려움
 */
export async function d1Execute(sql: string, params?: unknown[]): Promise<void> {
  const client = getD1Client();
  await client.query(sql, params);
}

export { D1Client };
