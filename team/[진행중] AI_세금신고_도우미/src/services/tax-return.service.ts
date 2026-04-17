// ──────────────────────────────────────────────
// 종합소득세 신고서 생성 서비스
// 기준: 소득세법 (2025년 귀속분 기준)
// 주의: 참고용 초안. 실제 신고는 홈택스에서 사용자가 직접 진행.
// ──────────────────────────────────────────────
import { prisma } from "@/lib/prisma";
import { ConflictError, NotFoundError, ForbiddenError } from "@/lib/errors";
import { logUsage } from "./usage.service";
import { CreateTaxReturnInput } from "@/lib/schemas/tax-return";

// ──────────────────────────────────────────────
// 종합소득세 세율 (소득세법 §55, 2025년 귀속분)
// 과세표준 구간별 누진세율 + 누진공제액
// ──────────────────────────────────────────────
// BUG FIX: 기존 코드는 bracket === TAX_BRACKETS[0] 비교로 as const 배열에서
// 타입 불일치가 발생하고, indexOf()가 런타임에서 -1을 반환할 위험이 있었음.
// 누진공제 방식으로 단순화: 세액 = 과세표준 × 세율 - 누진공제액
// ──────────────────────────────────────────────
const TAX_BRACKETS = [
  { max: 14_000_000,  rate: 0.06, deduction: 0 },             // 6%
  { max: 50_000_000,  rate: 0.15, deduction: 1_260_000 },     // 15%, 누진공제 126만원
  { max: 88_000_000,  rate: 0.24, deduction: 5_760_000 },     // 24%, 누진공제 576만원
  { max: 150_000_000, rate: 0.35, deduction: 15_440_000 },    // 35%, 누진공제 1,544만원
  { max: 300_000_000, rate: 0.38, deduction: 19_940_000 },    // 38%, 누진공제 1,994만원
  { max: 500_000_000, rate: 0.40, deduction: 25_940_000 },    // 40%, 누진공제 2,594만원
  { max: Infinity,    rate: 0.42, deduction: 35_940_000 },    // 42%, 누진공제 3,594만원
];

/**
 * 과세표준에 따른 종합소득세액 계산
 * 소득세법 §55 (누진공제 방식)
 * 세액 = 과세표준 × 해당구간세율 - 누진공제액
 */
function calculateIncomeTax(taxBase: number): number {
  if (taxBase <= 0) return 0;
  for (const bracket of TAX_BRACKETS) {
    if (taxBase <= bracket.max) {
      return Math.floor(taxBase * bracket.rate - bracket.deduction);
    }
  }
  // Infinity 구간 처리 (안전장치)
  const last = TAX_BRACKETS[TAX_BRACKETS.length - 1];
  return Math.floor(taxBase * last.rate - last.deduction);
}

/**
 * 지방소득세 계산 (종합소득세의 10%)
 * 지방세법 §91
 */
function calculateLocalTax(incomeTax: number): number {
  return Math.floor(incomeTax * 0.1);
}

/**
 * 인적공제 계산 (소득세법 §50~52)
 * - 본인 기본공제: 150만원 (§50①1)
 * - 부양가족 기본공제: 1인당 150만원 (§50①3)
 * - 경로우대 추가공제: 70세 이상 1인당 100만원 (§51①3)
 * - 장애인 추가공제: 1인당 200만원 (§51①1)
 * - 한부모 공제: 100만원 (§51①4, 부녀자 공제와 중복불가)
 */
function calculatePersonalDeductions(params: {
  dependents: number;
  elderlyDependents: number;
  disabledDependents: number;
  isSingleParent: boolean;
}): {
  basicDeduction: number;
  elderlyDeduction: number;
  disabledDeduction: number;
  singleParentDeduction: number;
  total: number;
  breakdown: Record<string, number>;
} {
  const BASIC_PER_PERSON = 1_500_000;      // §50 기본공제 150만원
  const ELDERLY_ADDITIONAL = 1_000_000;     // §51①3 경로우대 100만원
  const DISABLED_ADDITIONAL = 2_000_000;   // §51①1 장애인 200만원
  const SINGLE_PARENT = 1_000_000;          // §51①4 한부모 100만원

  // 본인 기본공제 + 부양가족 기본공제
  const basicDeduction = BASIC_PER_PERSON * (1 + params.dependents);
  // 경로우대 추가공제
  const elderlyDeduction = ELDERLY_ADDITIONAL * params.elderlyDependents;
  // 장애인 추가공제
  const disabledDeduction = DISABLED_ADDITIONAL * params.disabledDependents;
  // 한부모 공제
  const singleParentDeduction = params.isSingleParent ? SINGLE_PARENT : 0;

  const total = basicDeduction + elderlyDeduction + disabledDeduction + singleParentDeduction;

  return {
    basicDeduction,
    elderlyDeduction,
    disabledDeduction,
    singleParentDeduction,
    total,
    breakdown: {
      "본인 기본공제 (소득세법 §50①1)": BASIC_PER_PERSON,
      "부양가족 기본공제 (§50①3)": BASIC_PER_PERSON * params.dependents,
      "경로우대 추가공제 (§51①3)": elderlyDeduction,
      "장애인 추가공제 (§51①1)": disabledDeduction,
      "한부모 공제 (§51①4)": singleParentDeduction,
    },
  };
}

/**
 * 사회보험료 공제 계산 (소득세법 §51의3)
 * - 국민연금 본인 납부액: 전액 공제
 * - 건강보험료 본인 납부액: 전액 공제 (장기요양보험료 포함)
 */
function calculateSocialInsuranceDeduction(params: {
  nationalPensionPaid: number;
  healthInsurancePaid: number;
}): { total: number; breakdown: Record<string, number> } {
  const total = params.nationalPensionPaid + params.healthInsurancePaid;
  return {
    total,
    breakdown: {
      "국민연금 공제 (소득세법 §51의3①)": params.nationalPensionPaid,
      "건강보험료 공제 (§51의3①)": params.healthInsurancePaid,
    },
  };
}

/**
 * 업종별 기준경비율/단순경비율 (국세청 고시)
 * MVP에서는 단순경비율을 표준공제 대용으로 사용
 * 실제 신고 시 반드시 국세청 홈택스에서 업종코드별 경비율 확인 필요
 */
function getStandardExpenseRate(businessType: string): number {
  // 주요 업종코드별 단순경비율 (2024 귀속분 기준, 국세청 고시)
  const rates: Record<string, number> = {
    "940909": 0.644, // 프리랜서/소프트웨어 개발 (64.4%)
    "921501": 0.620, // 유튜버/크리에이터 (62.0%)
    "721401": 0.637, // 디자이너 (63.7%)
    "859001": 0.618, // 강사/튜터 (61.8%)
    "493200": 0.773, // 배달라이더 (77.3%)
    "472101": 0.820, // 소매업 (82.0%)
    "960901": 0.637, // 기타 서비스업 (63.7%)
    "741100": 0.615, // 작가/번역가 (61.5%)
    "731200": 0.640, // 사진작가 (64.0%)
    "900001": 0.630, // 기타 프리랜서 (63.0%)
  };
  return rates[businessType] ?? 0.63; // 미등록 업종 기본값 63%
}

export interface TaxReturnCalculation {
  taxYear: number;
  totalIncome: number;
  totalExpense: number;          // DB 경비 합계
  standardExpenseRate: number;   // 업종별 경비율
  standardExpenseAmount: number; // 경비율 적용 금액 (비교용)
  actualExpenseUsed: number;     // 실제 적용 경비 (max: DB경비, 경비율 중 큰 쪽)
  personalDeductions: number;    // 인적공제 합계
  socialInsuranceDeduction: number;
  taxBase: number;               // 과세표준
  incomeTax: number;             // 종합소득세
  localTax: number;              // 지방소득세 (10%)
  totalTax: number;              // 최종 납부세액
  effectiveTaxRate: number;      // 실효세율 (%)
  deductionBreakdown: Record<string, number>;
  disclaimer: string;            // 법적 고지문
}

/**
 * 종합소득세 신고서 초안 계산
 * 주의: 이 계산은 참고용입니다. 실제 신고는 홈택스를 이용하세요.
 */
export async function generateTaxReturn(
  userId: string,
  input: CreateTaxReturnInput
): Promise<TaxReturnCalculation & { id: string }> {
  // 1. 사업자 프로필 조회 (업종코드 필요)
  const profile = await prisma.businessProfile.findUnique({
    where: { userId },
    select: { businessType: true, taxationType: true },
  });

  if (!profile) {
    throw new NotFoundError("사업자 프로필이 없습니다. 온보딩을 먼저 완료해주세요.");
  }

  // 2. 해당 연도 경비 합계 조회 (사용자 검증 완료 + 업무 관련 경비만)
  const expenseResult = await prisma.expenseItem.aggregate({
    where: {
      userId,
      taxYear: input.taxYear,
      isBusinessExpense: true,
    },
    _sum: { amount: true },
  });

  const totalExpense = expenseResult._sum.amount ?? 0;
  const totalIncome = input.totalIncome + input.otherIncome;

  // 3. 경비 계산: DB 실제 경비 vs 업종별 단순경비율 → 큰 쪽 적용 (납세자에게 유리한 방향)
  const standardExpenseRate = getStandardExpenseRate(profile.businessType);
  const standardExpenseAmount = Math.floor(totalIncome * standardExpenseRate);
  // 보수적 처리: 불확실한 경우 표준경비율 사용 (과소납부 리스크 방지)
  const actualExpenseUsed = Math.max(totalExpense, standardExpenseAmount);

  // 4. 인적공제 계산 (소득세법 §50~52)
  const personalDeductionCalc = calculatePersonalDeductions({
    dependents: input.dependents,
    elderlyDependents: input.elderlyDependents,
    disabledDependents: input.disabledDependents,
    isSingleParent: input.isSingleParent,
  });

  // 5. 사회보험료 공제 (소득세법 §51의3)
  const socialInsuranceCalc = calculateSocialInsuranceDeduction({
    nationalPensionPaid: input.nationalPensionPaid,
    healthInsurancePaid: input.healthInsurancePaid,
  });

  // 6. 과세표준 계산
  // 과세표준 = 총수입 - 필요경비 - 인적공제 - 사회보험료 공제
  const totalDeductions = personalDeductionCalc.total + socialInsuranceCalc.total;
  const taxBase = Math.max(0, totalIncome - actualExpenseUsed - totalDeductions);

  // 7. 세액 계산 (소득세법 §55)
  const incomeTax = calculateIncomeTax(taxBase);
  const localTax = calculateLocalTax(incomeTax); // 지방세법 §91
  const totalTax = incomeTax + localTax;
  const effectiveTaxRate = totalIncome > 0 ? Math.round((totalTax / totalIncome) * 1000) / 10 : 0;

  // 8. DB 저장 (기존 신고서가 있으면 업데이트)
  const existing = await prisma.taxReturn.findUnique({
    where: { userId_taxYear: { userId, taxYear: input.taxYear } },
    select: { id: true },
  });

  const taxReturnData = {
    taxYear: input.taxYear,
    totalIncome: totalIncome,
    totalExpense: actualExpenseUsed,
    standardDeduction: totalDeductions,
    taxBase,
    estimatedTax: totalTax,
    status: "READY" as const,
    generatedAt: new Date(),
  };

  let taxReturn;
  if (existing) {
    taxReturn = await prisma.taxReturn.update({
      where: { id: existing.id },
      data: taxReturnData,
      select: { id: true },
    });
  } else {
    taxReturn = await prisma.taxReturn.create({
      data: { userId, ...taxReturnData },
      select: { id: true },
    });
  }

  // 9. 사용량 로그 기록
  await logUsage(userId, "TAX_RETURN_GENERATE", {
    taxReturnId: taxReturn.id,
    taxYear: input.taxYear,
  });

  const deductionBreakdown = {
    ...personalDeductionCalc.breakdown,
    ...socialInsuranceCalc.breakdown,
    "경비 공제 (실제 경비)": actualExpenseUsed,
  };

  return {
    id: taxReturn.id,
    taxYear: input.taxYear,
    totalIncome,
    totalExpense,
    standardExpenseRate,
    standardExpenseAmount,
    actualExpenseUsed,
    personalDeductions: personalDeductionCalc.total,
    socialInsuranceDeduction: socialInsuranceCalc.total,
    taxBase,
    incomeTax,
    localTax,
    totalTax,
    effectiveTaxRate,
    deductionBreakdown,
    disclaimer:
      "이 신고서는 참고용 초안입니다. 실제 납부세액은 홈택스(hometax.go.kr)에서 직접 확인하고 신고하세요. " +
      "AI 계산에는 오류가 있을 수 있으며, 최종 책임은 납세자에게 있습니다. " +
      "복잡한 소득 구조나 특별 공제 항목이 있는 경우 세무사 상담을 권장합니다.",
  };
}

/**
 * 신고서 조회 (소유권 확인)
 */
export async function getTaxReturn(taxReturnId: string, userId: string) {
  const taxReturn = await prisma.taxReturn.findUnique({
    where: { id: taxReturnId },
    include: {
      user: {
        select: {
          businessProfile: {
            select: { businessType: true, businessTypeLabel: true, taxationType: true },
          },
        },
      },
    },
  });

  if (!taxReturn) throw new NotFoundError("신고서", taxReturnId);
  if (taxReturn.userId !== userId) throw new ForbiddenError();

  return taxReturn;
}
