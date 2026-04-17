// ──────────────────────────────────────────────
// 경비 서비스 — CRUD + 집계
// ──────────────────────────────────────────────
import { prisma } from "@/lib/prisma";
import { NotFoundError, ForbiddenError } from "@/lib/errors";
import { CreateExpenseInput, UpdateExpenseInput } from "@/lib/schemas/expense";

/**
 * 경비 항목 수동 생성
 */
export async function createExpense(userId: string, input: CreateExpenseInput) {
  return prisma.expenseItem.create({
    data: {
      userId,
      receiptId: input.receiptId ?? null,
      date: new Date(input.date),
      amount: input.amount,
      merchantName: input.merchantName,
      category: input.category,
      isBusinessExpense: input.isBusinessExpense,
      memo: input.memo ?? null,
      taxYear: input.taxYear,
      userVerified: true, // 수동 입력은 사용자가 직접 입력했으므로 verified
    },
    select: {
      id: true,
      date: true,
      amount: true,
      merchantName: true,
      category: true,
      isBusinessExpense: true,
      userVerified: true,
      memo: true,
      taxYear: true,
      createdAt: true,
    },
  });
}

/**
 * 경비 항목 수정 (소유권 확인 포함)
 */
export async function updateExpense(
  expenseId: string,
  userId: string,
  input: UpdateExpenseInput
) {
  const existing = await prisma.expenseItem.findUnique({
    where: { id: expenseId },
    select: { userId: true },
  });
  if (!existing) throw new NotFoundError("경비 항목", expenseId);
  if (existing.userId !== userId) throw new ForbiddenError();

  return prisma.expenseItem.update({
    where: { id: expenseId },
    data: {
      ...(input.date ? { date: new Date(input.date) } : {}),
      ...(input.amount !== undefined ? { amount: input.amount } : {}),
      ...(input.merchantName !== undefined ? { merchantName: input.merchantName } : {}),
      ...(input.category !== undefined ? { category: input.category } : {}),
      ...(input.isBusinessExpense !== undefined ? { isBusinessExpense: input.isBusinessExpense } : {}),
      ...(input.memo !== undefined ? { memo: input.memo } : {}),
      ...(input.userVerified !== undefined ? { userVerified: input.userVerified } : {}),
    },
    select: {
      id: true,
      date: true,
      amount: true,
      merchantName: true,
      category: true,
      isBusinessExpense: true,
      userVerified: true,
      memo: true,
      taxYear: true,
      updatedAt: true,
    },
  });
}

/**
 * 경비 항목 삭제 (소유권 확인 포함)
 */
export async function deleteExpense(expenseId: string, userId: string) {
  const existing = await prisma.expenseItem.findUnique({
    where: { id: expenseId },
    select: { userId: true },
  });
  if (!existing) throw new NotFoundError("경비 항목", expenseId);
  if (existing.userId !== userId) throw new ForbiddenError();

  await prisma.expenseItem.delete({ where: { id: expenseId } });
}

/**
 * 연간/월별 경비 집계 (대시보드용)
 * - 카테고리별 합계
 * - 월별 합계
 * - 업무 관련 경비 합계 (isBusinessExpense = true)
 */
export async function getExpenseSummary(userId: string, taxYear: number) {
  const where = {
    userId,
    taxYear,
    isBusinessExpense: true,
  };

  // 1. 전체 합계
  const totalResult = await prisma.expenseItem.aggregate({
    where,
    _sum: { amount: true },
    _count: { id: true },
  });

  // 2. 카테고리별 합계
  const categoryBreakdown = await prisma.expenseItem.groupBy({
    by: ["category"],
    where,
    _sum: { amount: true },
    _count: { id: true },
    orderBy: { _sum: { amount: "desc" } },
  });

  // 3. 월별 합계 (1~12월)
  const allExpenses = await prisma.expenseItem.findMany({
    where,
    select: { date: true, amount: true },
  });

  const monthlyData: Record<number, number> = {};
  for (let m = 1; m <= 12; m++) monthlyData[m] = 0;
  for (const exp of allExpenses) {
    const month = exp.date.getMonth() + 1;
    monthlyData[month] += exp.amount;
  }

  // 4. 미확인(userVerified = false) 경비 수
  const unverifiedCount = await prisma.expenseItem.count({
    where: { ...where, userVerified: false },
  });

  return {
    taxYear,
    total: totalResult._sum.amount ?? 0,
    count: totalResult._count.id,
    unverifiedCount,
    categoryBreakdown: categoryBreakdown.map((item) => ({
      category: item.category,
      amount: item._sum.amount ?? 0,
      count: item._count.id,
    })),
    monthlyBreakdown: Object.entries(monthlyData).map(([month, amount]) => ({
      month: Number(month),
      amount,
    })),
  };
}
