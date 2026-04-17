import { NextRequest } from "next/server";
import { prisma } from "@/lib/prisma";
import { handleError } from "@/lib/handle-error";
import { ok, created, paginated } from "@/lib/response";
import { requireAuth } from "@/lib/middleware/auth";
import { validateSchema, parseQueryParams } from "@/lib/middleware/validate";
import { CreateExpenseSchema, ExpenseListQuerySchema } from "@/lib/schemas/expense";
import { createExpense } from "@/services/expense.service";

export async function GET(req: NextRequest) {
  try {
    const { userId } = await requireAuth();

    const query = parseQueryParams(
      ExpenseListQuerySchema,
      req.nextUrl.searchParams
    );

    const where: Record<string, unknown> = { userId };
    if (query.taxYear) where.taxYear = query.taxYear;
    if (query.category) where.category = query.category;
    if (query.isBusinessExpense !== undefined) where.isBusinessExpense = query.isBusinessExpense;
    if (query.userVerified !== undefined) where.userVerified = query.userVerified;
    if (query.month && query.taxYear) {
      const year = query.taxYear;
      const month = query.month;
      where.date = {
        gte: new Date(year, month - 1, 1),
        lt: new Date(year, month, 1),
      };
    }

    const skip = (query.page - 1) * query.limit;
    const orderBy: Record<string, string> = { [query.sortBy]: query.sortOrder };

    // BUG FIX: N+1 쿼리 — 기존 코드는 count/aggregate를 순차적으로 3번 실행.
    // Promise.all로 4개 쿼리 병렬 실행으로 개선.
    const summaryWhere = { userId, ...(query.taxYear ? { taxYear: query.taxYear } : {}), isBusinessExpense: true };

    const [expenses, total, unverifiedCount, sumResult] = await Promise.all([
      prisma.expenseItem.findMany({
        where,
        select: {
          id: true,
          receiptId: true,
          date: true,
          amount: true,
          merchantName: true,
          category: true,
          isBusinessExpense: true,
          userVerified: true,
          memo: true,
          taxYear: true,
          createdAt: true,
          updatedAt: true,
        },
        orderBy,
        skip,
        take: query.limit,
      }),
      prisma.expenseItem.count({ where }),
      prisma.expenseItem.count({ where: { ...where, userVerified: false } }),
      prisma.expenseItem.aggregate({ where: summaryWhere, _sum: { amount: true } }),
    ]);

    return ok({
      data: expenses,
      pagination: {
        page: query.page,
        limit: query.limit,
        total,
        totalPages: Math.ceil(total / query.limit),
        hasNext: query.page < Math.ceil(total / query.limit),
        hasPrev: query.page > 1,
      },
      summary: {
        totalAmount: sumResult._sum.amount ?? 0,
        unverifiedCount,
      },
    });
  } catch (error) {
    return handleError(error, req.nextUrl.pathname);
  }
}

export async function POST(req: NextRequest) {
  try {
    const { userId } = await requireAuth();

    const body = await req.json();
    const input = await validateSchema(CreateExpenseSchema, body);

    const expense = await createExpense(userId, input);

    return created(expense);
  } catch (error) {
    return handleError(error, req.nextUrl.pathname);
  }
}
