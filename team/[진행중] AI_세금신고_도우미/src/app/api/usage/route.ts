import { NextRequest } from "next/server";
import { handleError } from "@/lib/handle-error";
import { ok } from "@/lib/response";
import { requireAuth } from "@/lib/middleware/auth";
import { getUsageSummary } from "@/services/usage.service";

/**
 * GET /api/usage
 * 무료 플랜 사용량 조회
 * - 이번 달 영수증 업로드 수 / 한도
 * - 올해 신고서 생성 수 / 한도
 * - 다음 리셋 날짜
 */
export async function GET(req: NextRequest) {
  try {
    const { userId, planStatus } = await requireAuth();

    const usage = await getUsageSummary(userId, planStatus);

    return ok(usage);
  } catch (error) {
    return handleError(error, req.nextUrl.pathname);
  }
}
