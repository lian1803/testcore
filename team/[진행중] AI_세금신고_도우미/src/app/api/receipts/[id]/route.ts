import { NextRequest } from "next/server";
import { prisma } from "@/lib/prisma";
import { handleError } from "@/lib/handle-error";
import { ok, noContent } from "@/lib/response";
import { requireAuth } from "@/lib/middleware/auth";
import { validateSchema } from "@/lib/middleware/validate";
import { UpdateReceiptSchema } from "@/lib/schemas/receipt";
import { NotFoundError, ForbiddenError } from "@/lib/errors";
import { deleteS3Object } from "@/services/s3.service";

type Params = { params: { id: string } };

export async function GET(req: NextRequest, { params }: Params) {
  try {
    const { userId } = await requireAuth();

    const receipt = await prisma.receipt.findUnique({
      where: { id: params.id },
      include: {
        expenseItems: {
          select: {
            id: true,
            date: true,
            amount: true,
            merchantName: true,
            category: true,
            isBusinessExpense: true,
            userVerified: true,
            memo: true,
          },
        },
      },
    });

    if (!receipt) throw new NotFoundError("영수증", params.id);
    if (receipt.userId !== userId) throw new ForbiddenError();

    return ok(receipt);
  } catch (error) {
    return handleError(error, req.nextUrl.pathname);
  }
}

export async function PATCH(req: NextRequest, { params }: Params) {
  try {
    const { userId } = await requireAuth();

    const existing = await prisma.receipt.findUnique({
      where: { id: params.id },
      select: { userId: true },
    });
    if (!existing) throw new NotFoundError("영수증", params.id);
    if (existing.userId !== userId) throw new ForbiddenError();

    const body = await req.json();
    const input = await validateSchema(UpdateReceiptSchema, body);

    // expenseItem 수정 (merchantName, amount, date, category, isBusinessExpense, memo, userVerified)
    const expenseUpdateData: Record<string, unknown> = {};
    if (input.merchantName !== undefined) expenseUpdateData.merchantName = input.merchantName;
    if (input.amount !== undefined) expenseUpdateData.amount = input.amount;
    if (input.date !== undefined) expenseUpdateData.date = new Date(input.date);
    if (input.category !== undefined) expenseUpdateData.category = input.category;
    if (input.isBusinessExpense !== undefined) expenseUpdateData.isBusinessExpense = input.isBusinessExpense;
    if (input.memo !== undefined) expenseUpdateData.memo = input.memo;
    if (input.userVerified !== undefined) expenseUpdateData.userVerified = input.userVerified;

    if (Object.keys(expenseUpdateData).length > 0) {
      await prisma.expenseItem.updateMany({
        where: { receiptId: params.id, userId },
        data: expenseUpdateData,
      });
    }

    const updated = await prisma.receipt.findUnique({
      where: { id: params.id },
      include: {
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
    });

    return ok(updated);
  } catch (error) {
    return handleError(error, req.nextUrl.pathname);
  }
}

export async function DELETE(req: NextRequest, { params }: Params) {
  try {
    const { userId } = await requireAuth();

    const receipt = await prisma.receipt.findUnique({
      where: { id: params.id },
      select: { userId: true, imageUrl: true, imageDeleted: true },
    });
    if (!receipt) throw new NotFoundError("영수증", params.id);
    if (receipt.userId !== userId) throw new ForbiddenError();

    // S3 원본 이미지 삭제 (아직 삭제 안 된 경우)
    if (!receipt.imageDeleted && receipt.imageUrl) {
      await deleteS3Object(receipt.imageUrl).catch((err) => {
        console.error("[Receipt DELETE] S3 삭제 실패:", err);
      });
    }

    // ExpenseItem cascade delete → Receipt 삭제
    await prisma.receipt.delete({ where: { id: params.id } });

    return noContent();
  } catch (error) {
    return handleError(error, req.nextUrl.pathname);
  }
}
