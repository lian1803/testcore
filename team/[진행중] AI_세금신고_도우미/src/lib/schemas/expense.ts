import { z } from "zod";

const ExpenseCategoryEnum = z.enum([
  "OFFICE_SUPPLIES",
  "COMMUNICATION",
  "TRANSPORTATION",
  "MEAL",
  "EDUCATION",
  "EQUIPMENT",
  "RENT",
  "INSURANCE",
  "ADVERTISING",
  "PROFESSIONAL_FEE",
  "OTHER",
]);

export const CreateExpenseSchema = z.object({
  date: z.string().datetime("날짜 형식이 올바르지 않습니다."),
  amount: z
    .number()
    .int("금액은 정수(원 단위)여야 합니다.")
    .positive("금액은 양수여야 합니다.")
    .max(1_000_000_000, "단일 경비 금액은 10억 원을 초과할 수 없습니다."),
  merchantName: z
    .string()
    .min(1, "상호명을 입력해주세요.")
    .max(200, "상호명은 200자 이하여야 합니다."),
  category: ExpenseCategoryEnum,
  isBusinessExpense: z.boolean().default(true),
  memo: z.string().max(500, "메모는 500자 이하여야 합니다.").nullable().optional(),
  taxYear: z
    .number()
    .int()
    .min(2020)
    .max(new Date().getFullYear() + 1),
  receiptId: z.string().optional(), // 영수증 연결 (선택)
});

export type CreateExpenseInput = z.infer<typeof CreateExpenseSchema>;

export const UpdateExpenseSchema = z.object({
  date: z.string().datetime().optional(),
  amount: z.number().int().positive().max(1_000_000_000).optional(),
  merchantName: z.string().min(1).max(200).optional(),
  category: ExpenseCategoryEnum.optional(),
  isBusinessExpense: z.boolean().optional(),
  memo: z.string().max(500).nullable().optional(),
  userVerified: z.boolean().optional(),
});

export type UpdateExpenseInput = z.infer<typeof UpdateExpenseSchema>;

export const ExpenseListQuerySchema = z.object({
  page: z.coerce.number().int().min(1).default(1),
  limit: z.coerce.number().int().min(1).max(100).default(20),
  taxYear: z.coerce.number().int().optional(),
  category: ExpenseCategoryEnum.optional(),
  month: z.coerce.number().int().min(1).max(12).optional(),
  isBusinessExpense: z
    .enum(["true", "false"])
    .transform((v) => v === "true")
    .optional(),
  userVerified: z
    .enum(["true", "false"])
    .transform((v) => v === "true")
    .optional(),
  sortBy: z.enum(["date", "amount", "createdAt"]).default("date"),
  sortOrder: z.enum(["asc", "desc"]).default("desc"),
});

export type ExpenseListQuery = z.infer<typeof ExpenseListQuerySchema>;
