import { NextRequest } from "next/server";
import { prisma } from "@/lib/prisma";
import { handleError } from "@/lib/handle-error";
import { ok } from "@/lib/response";
import { requireAuth } from "@/lib/middleware/auth";

/**
 * GET /api/expenses/summary
 * 대시보드 KPI 카드 + 월별 차트 데이터
 */
export async function GET(req: NextRequest) {
  try {
    const { userId } = await requireAuth();

    const taxYear = parseInt(
      req.nextUrl.searchParams.get("taxYear") ?? String(new Date().getFullYear() - 1),
      10
    );

    const yearStart = new Date(taxYear, 0, 1);
    const yearEnd = new Date(taxYear + 1, 0, 1);

    // 이번 달 & 지난달 범위
    const now = new Date();
    const thisMonthStart = new Date(now.getFullYear(), now.getMonth(), 1);
    const prevMonthStart = new Date(now.getFullYear(), now.getMonth() - 1, 1);
    const prevMonthEnd = thisMonthStart;

    // 연간 경비 전체 집계
    const [
      allExpenses,
      thisMonthExpenses,
      prevMonthExpenses,
      thisMonthReceipts,
      prevMonthReceipts,
    ] = await Promise.all([
      prisma.expenseItem.aggregate({
        where: { userId, taxYear, isBusinessExpense: true },
        _sum: { amount: true },
        _count: true,
      }),
      prisma.expenseItem.aggregate({
        where: {
          userId,
          isBusinessExpense: true,
          date: { gte: thisMonthStart },
        },
        _sum: { amount: true },
      }),
      prisma.expenseItem.aggregate({
        where: {
          userId,
          isBusinessExpense: true,
          date: { gte: prevMonthStart, lt: prevMonthEnd },
        },
        _sum: { amount: true },
      }),
      prisma.receipt.count({
        where: { userId, uploadedAt: { gte: thisMonthStart } },
      }),
      prisma.receipt.count({
        where: { userId, uploadedAt: { gte: prevMonthStart, lt: prevMonthEnd } },
      }),
    ]);

    const totalExpense = allExpenses._sum.amount ?? 0;
    const thisMonthTotal = thisMonthExpenses._sum.amount ?? 0;
    const prevMonthTotal = prevMonthExpenses._sum.amount ?? 0;

    // 절세 추정액: 총 경비 × 기본 소득세율 추정치 (24%)
    const TAX_RATE_ESTIMATE = 0.24;
    const estimatedSaving = Math.round(totalExpense * TAX_RATE_ESTIMATE);
    const estimatedTax = Math.round(totalExpense * 0.15); // 보수적 세금 추정

    // 전월 대비 변화율 계산
    const calcChange = (curr: number, prev: number) =>
      prev === 0 ? 0 : Math.round(((curr - prev) / prev) * 100);

    // KPI 데이터
    const kpi = {
      totalExpense,
      totalExpensePrevMonthChange: calcChange(thisMonthTotal, prevMonthTotal),
      estimatedTax,
      estimatedTaxPrevMonthChange: 0, // 추정치이므로 0 고정
      receiptCount: allExpenses._count,
      receiptCountPrevMonthChange: calcChange(thisMonthReceipts, prevMonthReceipts),
      estimatedSaving,
      estimatedSavingPrevMonthChange: calcChange(thisMonthTotal, prevMonthTotal),
    };

    // 월별 카테고리별 집계 (1~12월)
    const monthlyRaw = await prisma.expenseItem.groupBy({
      by: ["category"],
      where: { userId, taxYear, isBusinessExpense: true, date: { gte: yearStart, lt: yearEnd } },
      _sum: { amount: true },
    });

    // 월별 데이터 생성 — Prisma groupBy가 month를 지원하지 않으므로 raw query 사용
    const monthlyData = await prisma.$queryRaw<
      Array<{ month: number; category: string; total: bigint }>
    >`
      SELECT
        EXTRACT(MONTH FROM date)::int AS month,
        category,
        SUM(amount) AS total
      FROM "ExpenseItem"
      WHERE "userId" = ${userId}
        AND "taxYear" = ${taxYear}
        AND "isBusinessExpense" = true
        AND date >= ${yearStart}
        AND date < ${yearEnd}
      GROUP BY month, category
      ORDER BY month
    `;

    // 월별 배열로 변환 (1~12월)
    const CATEGORIES = ["MEAL", "TRANSPORTATION", "COMMUNICATION", "OFFICE_SUPPLIES", "EDUCATION", "OTHER"] as const;
    const monthly = Array.from({ length: 12 }, (_, i) => {
      const m = i + 1;
      const monthStr = `${taxYear}-${String(m).padStart(2, "0")}`;
      const monthEntries = monthlyData.filter((r: { month: number; category: string; total: bigint }) => r.month === m);
      const byCategory: Record<string, number> = {};
      for (const cat of CATEGORIES) byCategory[cat] = 0;
      for (const entry of monthEntries) {
        const cat = CATEGORIES.includes(entry.category as typeof CATEGORIES[number])
          ? entry.category
          : "OTHER";
        byCategory[cat] = (byCategory[cat] ?? 0) + Number(entry.total);
      }
      return {
        month: monthStr,
        total: monthEntries.reduce((sum: number, r: { month: number; category: string; total: bigint }) => sum + Number(r.total), 0),
        ...byCategory,
      };
    });

    return ok({ kpi, monthly });
  } catch (error) {
    return handleError(error);
  }
}
