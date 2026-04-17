import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import { handleError } from "@/lib/handle-error";
import { requireAuth } from "@/lib/middleware/auth";
import { parseQueryParams } from "@/lib/middleware/validate";
import { DownloadQuerySchema } from "@/lib/schemas/tax-return";
import { generateExcel, generatePdf } from "@/services/document.service";
import { logUsage } from "@/services/usage.service";
import { NotFoundError, ForbiddenError } from "@/lib/errors";

type Params = { params: { id: string } };

/**
 * GET /api/tax-return/[id]/download?format=pdf|excel
 * 신고서 PDF 또는 Excel 다운로드
 *
 * 주의: 이 파일은 참고용 초안입니다. 홈택스 자동 제출 기능 없음.
 */
export async function GET(req: NextRequest, { params }: Params) {
  try {
    const { userId } = await requireAuth();

    const { format } = parseQueryParams(DownloadQuerySchema, req.nextUrl.searchParams);

    // 신고서 조회 (관계 데이터 포함)
    const taxReturn = await prisma.taxReturn.findUnique({
      where: { id: params.id },
      include: {
        user: {
          select: {
            email: true,
            name: true,
            businessProfile: {
              select: {
                businessTypeLabel: true,
                taxationType: true,
                registrationNumber: true,
              },
            },
          },
        },
      },
    });

    if (!taxReturn) throw new NotFoundError("신고서", params.id);
    if (taxReturn.userId !== userId) throw new ForbiddenError();

    // 다운로드 상태 업데이트
    await prisma.taxReturn.update({
      where: { id: params.id },
      data: {
        downloadedAt: new Date(),
        status: "DOWNLOADED",
      },
    });

    if (format === "excel") {
      // Excel 생성
      const buffer = generateExcel(taxReturn);
      await logUsage(userId, "EXCEL_DOWNLOAD", { taxReturnId: params.id });

      return new NextResponse(buffer as unknown as BodyInit, {
        status: 200,
        headers: {
          "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
          "Content-Disposition": `attachment; filename="tax-return-${taxReturn.taxYear}-draft.xlsx"`,
          "Content-Length": String(buffer.length),
          "X-Document-Type": "reference-draft-only",
        },
      });
    } else {
      // PDF 생성
      const buffer = await generatePdf(taxReturn);
      await logUsage(userId, "PDF_DOWNLOAD", { taxReturnId: params.id });

      return new NextResponse(buffer as unknown as BodyInit, {
        status: 200,
        headers: {
          "Content-Type": "application/pdf",
          "Content-Disposition": `attachment; filename="tax-return-${taxReturn.taxYear}-draft.pdf"`,
          "Content-Length": String(buffer.length),
          "X-Document-Type": "reference-draft-only",
        },
      });
    }
  } catch (error) {
    return handleError(error, req.nextUrl.pathname);
  }
}
