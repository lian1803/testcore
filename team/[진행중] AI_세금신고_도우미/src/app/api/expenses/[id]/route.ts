import { NextRequest } from "next/server";
import { prisma } from "@/lib/prisma";
import { handleError } from "@/lib/handle-error";
import { ok, noContent } from "@/lib/response";
import { requireAuth } from "@/lib/middleware/auth";
import { validateSchema } from "@/lib/middleware/validate";
import { UpdateExpenseSchema } from "@/lib/schemas/expense";
import { updateExpense, deleteExpense } from "@/services/expense.service";
import { NotFoundError, ForbiddenError } from "@/lib/errors";

type Params = { params: { id: string } };

export async function GET(req: NextRequest, { params }: Params) {
  try {
    const { userId } = await requireAuth();

    const expense = await prisma.expenseItem.findUnique({
      where: { id: params.id },
      include: {
        receipt: {
          select: {
            id: true,
            status: true,
            ocrConfidence: true,
            imageDeleted: true,
          },
        },
      },
    });

    if (!expense) throw new NotFoundError("경비 항목", params.id);
    if (expense.userId !== userId) throw new ForbiddenError();

    return ok(expense);
  } catch (error) {
    return handleError(error, req.nextUrl.pathname);
  }
}

export async function PATCH(req: NextRequest, { params }: Params) {
  try {
    const { userId } = await requireAuth();

    const body = await req.json();
    const input = await validateSchema(UpdateExpenseSchema, body);

    const updated = await updateExpense(params.id, userId, input);

    return ok(updated);
  } catch (error) {
    return handleError(error, req.nextUrl.pathname);
  }
}

export async function DELETE(req: NextRequest, { params }: Params) {
  try {
    const { userId } = await requireAuth();

    await deleteExpense(params.id, userId);

    return noContent();
  } catch (error) {
    return handleError(error, req.nextUrl.pathname);
  }
}
