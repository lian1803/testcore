import { auth } from "@/auth";
import { UnauthorizedError, ForbiddenError } from "@/lib/errors";
import { handleError } from "@/lib/handle-error";
import { NextRequest, NextResponse } from "next/server";

type RouteHandler = (
  req: NextRequest,
  context: { params: Record<string, string>; userId: string }
) => Promise<NextResponse>;

type RoleRouteHandler = (
  req: NextRequest,
  context: { params: Record<string, string>; userId: string; planStatus: string }
) => Promise<NextResponse>;

/**
 * withAuth — 인증된 사용자만 접근 가능한 Route Handler 래퍼
 * 사용: export const GET = withAuth(async (req, { userId }) => { ... })
 */
export function withAuth(handler: RouteHandler) {
  return async (
    req: NextRequest,
    context: { params: Record<string, string> }
  ): Promise<NextResponse> => {
    try {
      const session = await auth();
      if (!session?.user?.id) {
        throw new UnauthorizedError();
      }
      return await handler(req, { ...context, userId: session.user.id });
    } catch (error) {
      return handleError(error, req.nextUrl.pathname);
    }
  };
}

/**
 * withRole — 특정 플랜 이상의 사용자만 접근 가능
 * 사용: export const POST = withRole(["PREMIUM"], async (req, { userId, planStatus }) => { ... })
 */
export function withRole(allowedPlans: string[], handler: RoleRouteHandler) {
  return async (
    req: NextRequest,
    context: { params: Record<string, string> }
  ): Promise<NextResponse> => {
    try {
      const session = await auth();
      if (!session?.user?.id) {
        throw new UnauthorizedError();
      }
      const planStatus = (session.user as { planStatus?: string }).planStatus ?? "FREE";
      if (!allowedPlans.includes(planStatus)) {
        throw new ForbiddenError(`이 기능은 ${allowedPlans.join(", ")} 플랜에서만 사용할 수 있습니다.`);
      }
      return await handler(req, {
        ...context,
        userId: session.user.id,
        planStatus,
      });
    } catch (error) {
      return handleError(error, req.nextUrl.pathname);
    }
  };
}

/**
 * 세션에서 userId 추출 (서비스 레이어에서 직접 사용 시)
 * throws UnauthorizedError if not authenticated
 */
export async function requireAuth(): Promise<{ userId: string; planStatus: string }> {
  const session = await auth();
  if (!session?.user?.id) {
    throw new UnauthorizedError();
  }
  return {
    userId: session.user.id,
    planStatus: (session.user as { planStatus?: string }).planStatus ?? "FREE",
  };
}
