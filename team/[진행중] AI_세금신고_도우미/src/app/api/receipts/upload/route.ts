import { NextRequest } from "next/server";
import { handleError } from "@/lib/handle-error";
import { created } from "@/lib/response";
import { requireAuth } from "@/lib/middleware/auth";
import { validateSchema } from "@/lib/middleware/validate";
import { UploadReceiptSchema } from "@/lib/schemas/receipt";
import { checkReceiptUploadLimit } from "@/services/usage.service";
import { processReceiptUpload } from "@/services/receipt.service";

/**
 * POST /api/receipts/upload
 * S3에 업로드된 이미지 키를 받아 OCR + AI 분류 실행
 *
 * Request body:
 * { imageKey: string, deleteAfterProcessing?: boolean }
 *
 * Flow:
 * 1. 인증 확인
 * 2. 무료 플랜 한도 체크 (20건/월)
 * 3. OCR (Google Vision → GPT-4o 폴백)
 * 4. AI 분류 (GPT-4o)
 * 5. Receipt + ExpenseItem DB 저장
 * 6. deleteAfterProcessing = true면 S3 원본 삭제
 */
export async function POST(req: NextRequest) {
  try {
    const { userId, planStatus } = await requireAuth();

    // 무료 플랜 한도 체크
    await checkReceiptUploadLimit(userId, planStatus);

    const body = await req.json();
    const input = await validateSchema(UploadReceiptSchema, body);

    const result = await processReceiptUpload({
      userId,
      imageKey: input.imageKey,
      deleteAfterProcessing: input.deleteAfterProcessing,
    });

    return created({
      receipt: result.receipt,
      expenseItem: result.expenseItem,
      // 법적 고지: AI 분류는 참고용이며 사용자 최종 확인 필수
      notice: "AI 분류 결과는 참고용입니다. 카테고리와 금액을 반드시 확인하세요.",
    });
  } catch (error) {
    return handleError(error, req.nextUrl.pathname);
  }
}
