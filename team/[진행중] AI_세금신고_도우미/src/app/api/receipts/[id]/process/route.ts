import { NextRequest } from "next/server";
import { handleError } from "@/lib/handle-error";
import { ok } from "@/lib/response";
import { requireAuth } from "@/lib/middleware/auth";
import { reprocessReceipt } from "@/services/receipt.service";

type Params = { params: { id: string } };

/**
 * POST /api/receipts/[id]/process
 * OCR 재처리 (실패한 영수증 재시도 또는 재분류 요청)
 */
export async function POST(req: NextRequest, { params }: Params) {
  try {
    const { userId } = await requireAuth();

    await reprocessReceipt(params.id, userId);

    return ok({
      message: "OCR 재처리가 완료되었습니다.",
      receiptId: params.id,
    });
  } catch (error) {
    return handleError(error, req.nextUrl.pathname);
  }
}
