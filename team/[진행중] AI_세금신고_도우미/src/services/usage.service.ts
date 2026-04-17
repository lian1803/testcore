// ──────────────────────────────────────────────
// 사용량 서비스 — 플랜 한도 체크 + 집계
// 무료: 영수증 20건/월, 신고서 1회/년
// ──────────────────────────────────────────────
import { prisma } from "@/lib/prisma";
import { UsageLimitError } from "@/lib/errors";

const FREE_PLAN_LIMITS = {
  RECEIPT_UPLOAD_PER_MONTH: 20,
  TAX_RETURN_PER_YEAR: 1,
} as const;

/**
 * 이번 달 영수증 업로드 횟수 조회
 */
export async function getMonthlyReceiptCount(userId: string): Promise<number> {
  const now = new Date();
  const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1);

  return prisma.usageLog.count({
    where: {
      userId,
      action: "RECEIPT_UPLOAD",
      createdAt: { gte: startOfMonth },
    },
  });
}

/**
 * 올해 신고서 생성 횟수 조회
 */
export async function getYearlyTaxReturnCount(
  userId: string,
  taxYear: number
): Promise<number> {
  const startOfYear = new Date(taxYear, 0, 1);
  const endOfYear = new Date(taxYear + 1, 0, 1);

  return prisma.usageLog.count({
    where: {
      userId,
      action: "TAX_RETURN_GENERATE",
      createdAt: { gte: startOfYear, lt: endOfYear },
    },
  });
}

/**
 * 무료 플랜 영수증 업로드 한도 체크
 * throws UsageLimitError if exceeded
 */
export async function checkReceiptUploadLimit(
  userId: string,
  planStatus: string
): Promise<void> {
  if (planStatus === "PREMIUM") return; // 유료 플랜은 무제한

  const used = await getMonthlyReceiptCount(userId);
  if (used >= FREE_PLAN_LIMITS.RECEIPT_UPLOAD_PER_MONTH) {
    throw new UsageLimitError(
      "영수증 업로드",
      FREE_PLAN_LIMITS.RECEIPT_UPLOAD_PER_MONTH
    );
  }
}

/**
 * 무료 플랜 신고서 생성 한도 체크
 * throws UsageLimitError if exceeded
 */
export async function checkTaxReturnLimit(
  userId: string,
  planStatus: string,
  taxYear: number
): Promise<void> {
  if (planStatus === "PREMIUM") return;

  const used = await getYearlyTaxReturnCount(userId, taxYear);
  if (used >= FREE_PLAN_LIMITS.TAX_RETURN_PER_YEAR) {
    throw new UsageLimitError(
      "신고서 생성",
      FREE_PLAN_LIMITS.TAX_RETURN_PER_YEAR
    );
  }
}

/**
 * 사용량 로그 기록
 */
export async function logUsage(
  userId: string,
  action: "RECEIPT_UPLOAD" | "TAX_RETURN_GENERATE" | "PDF_DOWNLOAD" | "EXCEL_DOWNLOAD",
  metadata?: Record<string, unknown>
): Promise<void> {
  await prisma.usageLog.create({
    data: {
      userId,
      action,
      metadata: metadata ?? null,
    },
  });
}

/**
 * 사용량 현황 조회 (GET /api/usage)
 */
export async function getUsageSummary(userId: string, planStatus: string) {
  const now = new Date();
  const taxYear = now.getFullYear() - 1; // 기본: 전년도 신고

  const [monthlyReceipts, yearlyTaxReturns] = await Promise.all([
    getMonthlyReceiptCount(userId),
    getYearlyTaxReturnCount(userId, taxYear),
  ]);

  return {
    planStatus,
    receipt: {
      used: monthlyReceipts,
      limit: planStatus === "PREMIUM" ? null : FREE_PLAN_LIMITS.RECEIPT_UPLOAD_PER_MONTH,
      resetAt: new Date(now.getFullYear(), now.getMonth() + 1, 1).toISOString(),
    },
    taxReturn: {
      used: yearlyTaxReturns,
      limit: planStatus === "PREMIUM" ? null : FREE_PLAN_LIMITS.TAX_RETURN_PER_YEAR,
      taxYear,
    },
  };
}
