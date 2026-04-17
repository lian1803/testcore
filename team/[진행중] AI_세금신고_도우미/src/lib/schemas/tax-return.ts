import { z } from "zod";

export const CreateTaxReturnSchema = z.object({
  taxYear: z
    .number()
    .int()
    .min(2020)
    .max(new Date().getFullYear()),
  // 연간 총 수입 (원 단위) — 사용자가 직접 입력
  totalIncome: z
    .number()
    .int("수입은 원 단위 정수여야 합니다.")
    .min(0, "수입은 0원 이상이어야 합니다.")
    .max(10_000_000_000, "수입이 너무 큽니다."),
  // 기타 소득 (배당소득, 이자소득 등) — 선택
  otherIncome: z.number().int().min(0).default(0),
  // 인적공제 — 본인(필수) + 추가 부양가족 수
  dependents: z
    .number()
    .int()
    .min(0)
    .max(20)
    .default(0),
  // 노인(70세 이상) 부양가족 수 — 추가 공제 100만원/인
  elderlyDependents: z.number().int().min(0).max(20).default(0),
  // 장애인 부양가족 수 — 추가 공제 200만원/인
  disabledDependents: z.number().int().min(0).max(20).default(0),
  // 한부모 공제 여부
  isSingleParent: z.boolean().default(false),
  // 국민연금 본인 납부액
  nationalPensionPaid: z.number().int().min(0).default(0),
  // 건강보험료 본인 납부액
  healthInsurancePaid: z.number().int().min(0).default(0),
});

export type CreateTaxReturnInput = z.infer<typeof CreateTaxReturnSchema>;

export const DownloadQuerySchema = z.object({
  format: z.enum(["pdf", "excel"]).default("pdf"),
});

export type DownloadQuery = z.infer<typeof DownloadQuerySchema>;
