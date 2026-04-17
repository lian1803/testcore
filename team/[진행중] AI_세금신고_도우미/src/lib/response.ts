import { NextResponse } from "next/server";

// ──────────────────────────────────────────────
// 일관된 API 응답 포맷
// ──────────────────────────────────────────────

export interface ApiResponse<T> {
  success: true;
  data: T;
}

export interface PaginatedResponse<T> {
  success: true;
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
    hasNext: boolean;
    hasPrev: boolean;
  };
}

export interface CursorPaginatedResponse<T> {
  success: true;
  data: T[];
  nextCursor: string | null;
  hasMore: boolean;
}

/** 단건 응답 */
export function ok<T>(data: T, status = 200): NextResponse {
  const body: ApiResponse<T> = { success: true, data };
  return NextResponse.json(body, { status });
}

/** 생성 성공 응답 */
export function created<T>(data: T): NextResponse {
  return ok(data, 201);
}

/** 페이지네이션 응답 (offset 기반) */
export function paginated<T>(
  data: T[],
  total: number,
  page: number,
  limit: number
): NextResponse {
  const totalPages = Math.ceil(total / limit);
  const body: PaginatedResponse<T> = {
    success: true,
    data,
    pagination: {
      page,
      limit,
      total,
      totalPages,
      hasNext: page < totalPages,
      hasPrev: page > 1,
    },
  };
  return NextResponse.json(body);
}

/** 커서 기반 페이지네이션 응답 */
export function cursorPaginated<T>(
  data: T[],
  nextCursor: string | null
): NextResponse {
  const body: CursorPaginatedResponse<T> = {
    success: true,
    data,
    nextCursor,
    hasMore: nextCursor !== null,
  };
  return NextResponse.json(body);
}

/** 204 No Content */
export function noContent(): NextResponse {
  return new NextResponse(null, { status: 204 });
}
