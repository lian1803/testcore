import { NextRequest } from "next/server";
import { prisma } from "@/lib/prisma";
import { handleError } from "@/lib/handle-error";
import { ok, created, paginated } from "@/lib/response";
import { requireAuth } from "@/lib/middleware/auth";
import { validateSchema } from "@/lib/middleware/validate";
import { CreateTaxReturnSchema } from "@/lib/schemas/tax-return";
import { checkTaxReturnLimit } from "@/services/usage.service";
import { generateTaxReturn } from "@/services/tax-return.service";

/**
 * GET /api/tax-return
 * 신고서 목록 조회
 */
export async function GET(req: NextRequest) {
  try {
    const { userId } = await requireAuth();

    const page = Number(req.nextUrl.searchParams.get("page") ?? "1");
    const limit = Math.min(Number(req.nextUrl.searchParams.get("limit") ?? "10"), 50);
    const skip = (page - 1) * limit;

    const [taxReturns, total] = await Promise.all([
      prisma.taxReturn.findMany({
        where: { userId },
        select: {
          id: true,
          taxYear: true,
          totalIncome: true,
          totalExpense: true,
          estimatedTax: true,
          taxBase: true,
          standardDeduction: true,
          status: true,
          generatedAt: true,
          downloadedAt: true,
        },
        orderBy: { taxYear: "desc" },
        skip,
        take: limit,
      }),
      prisma.taxReturn.count({ where: { userId } }),
    ]);

    return paginated(taxReturns, total, page, limit);
  } catch (error) {
    return handleError(error, req.nextUrl.pathname);
  }
}

/**
 * POST /api/tax-return
 * 신고서 생성 (소득 입력 → 공제 계산 → 초안 생성)
 *
 * 무료 플랜: 연 1회 제한
 * 유료 플랜: 무제한
 *
 * 주의: 홈택스 자동 제출 기능 없음. 참고용 초안만 생성.
 */
export async function POST(req: NextRequest) {
  try {
    const { userId, planStatus } = await requireAuth();

    const body = await req.json();
    const input = await validateSchema(CreateTaxReturnSchema, body);

    // 무료 플랜 한도 체크
    await checkTaxReturnLimit(userId, planStatus, input.taxYear);

    const result = await generateTaxReturn(userId, input);

    return created({
      ...result,
      // 법적 고지 및 사용자 최종 확인 요청
      notice: {
        disclaimer: result.disclaimer,
        action: "이 신고서는 참고용 초안입니다. 홈택스에서 반드시 직접 확인하고 신고하세요.",
        hometaxUrl: "https://www.hometax.go.kr",
      },
    });
  } catch (error) {
    return handleError(error, req.nextUrl.pathname);
  }
}
