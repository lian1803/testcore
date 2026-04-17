import { z } from "zod";

export const UploadReceiptSchema = z.object({
  imageKey: z.string().min(1, "S3 이미지 키가 필요합니다."),
  // 원본 삭제 옵션 — 처리 후 S3에서 원본 삭제 여부 (개인정보 보호)
  deleteAfterProcessing: z.boolean().default(false),
});

export type UploadReceiptInput = z.infer<typeof UploadReceiptSchema>;

export const UpdateReceiptSchema = z.object({
  merchantName: z.string().min(1).max(200).optional(),
  amount: z.number().int().positive("금액은 양수여야 합니다.").optional(),
  date: z.string().datetime().optional(),
  category: z
    .enum([
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
    ])
    .optional(),
  isBusinessExpense: z.boolean().optional(),
  memo: z.string().max(500).nullable().optional(),
  userVerified: z.boolean().optional(),
});

export type UpdateReceiptInput = z.infer<typeof UpdateReceiptSchema>;

export const ReceiptListQuerySchema = z.object({
  page: z.coerce.number().int().min(1).default(1),
  limit: z.coerce.number().int().min(1).max(100).default(20),
  status: z
    .enum(["PENDING", "PROCESSING", "COMPLETED", "FAILED", "MANUAL"])
    .optional(),
  startDate: z.string().optional(),
  endDate: z.string().optional(),
});

export type ReceiptListQuery = z.infer<typeof ReceiptListQuerySchema>;
