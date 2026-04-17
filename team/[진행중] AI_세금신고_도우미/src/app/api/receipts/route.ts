import { NextRequest } from "next/server";
import { prisma } from "@/lib/prisma";
import { handleError } from "@/lib/handle-error";
import { paginated } from "@/lib/response";
import { requireAuth } from "@/lib/middleware/auth";
import { parseQueryParams } from "@/lib/middleware/validate";
import { ReceiptListQuerySchema } from "@/lib/schemas/receipt";

/**
 * GET /api/receipts
 * 영수증 목록 조회 (페이지네이션, 날짜/상태 필터)
 */
export async function GET(req: NextRequest) {
  try {
    const { userId } = await requireAuth();

    const query = parseQueryParams(
      ReceiptListQuerySchema,
      req.nextUrl.searchParams
    );

    const where: Record<string, unknown> = { userId };
    if (query.status) where.status = query.status;
    if (query.startDate || query.endDate) {
      where.uploadedAt = {
        ...(query.startDate ? { gte: new Date(query.startDate) } : {}),
        ...(query.endDate ? { lte: new Date(query.endDate) } : {}),
      };
    }

    const skip = (query.page - 1) * query.limit;

    const [receipts, total] = await Promise.all([
      prisma.receipt.findMany({
        where,
        select: {
          id: true,
          imageUrl: true,
          imageDeleted: true,
          ocrConfidence: true,
          ocrEngine: true,
          status: true,
          uploadedAt: true,
          processedAt: true,
          expenseItems: {
            select: {
              id: true,
              merchantName: true,
              amount: true,
              category: true,
              userVerified: true,
            },
          },
        },
        orderBy: { uploadedAt: "desc" },
        skip,
        take: query.limit,
      }),
      prisma.receipt.count({ where }),
    ]);

    return paginated(receipts, total, query.page, query.limit);
  } catch (error) {
    return handleError(error, req.nextUrl.pathname);
  }
}
