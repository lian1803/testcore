import { NextRequest } from "next/server";
import { handleError } from "@/lib/handle-error";
import { ok } from "@/lib/response";
import { requireAuth } from "@/lib/middleware/auth";
import { getTaxReturn } from "@/services/tax-return.service";

type Params = { params: { id: string } };

/**
 * GET /api/tax-return/[id]
 * 신고서 상세 조회
 */
export async function GET(req: NextRequest, { params }: Params) {
  try {
    const { userId } = await requireAuth();

    const taxReturn = await getTaxReturn(params.id, userId);

    return ok({
      ...taxReturn,
      disclaimer:
        "이 신고서는 참고용 초안입니다. 실제 신고는 홈택스(hometax.go.kr)에서 직접 진행하세요.",
    });
  } catch (error) {
    return handleError(error, req.nextUrl.pathname);
  }
}
