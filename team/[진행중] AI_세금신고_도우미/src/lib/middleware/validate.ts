// eslint-disable-next-line @typescript-eslint/no-unused-vars
import { ZodType, ZodError } from "zod";
import { ValidationError } from "@/lib/errors";

/**
 * validateSchema — Zod 스키마로 데이터 검증
 * throws ValidationError (400) if invalid
 *
 * 사용:
 * const body = await validateSchema(CreateReceiptSchema, await req.json())
 */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export async function validateSchema<TOutput>(
  schema: ZodType<TOutput, any, any>,
  data: unknown
): Promise<TOutput> {
  const result = schema.safeParse(data);
  if (!result.success) {
    throw new ValidationError(
      "입력 데이터가 올바르지 않습니다.",
      result.error.flatten().fieldErrors
    );
  }
  return result.data;
}

/**
 * parseQueryParams — URL 쿼리 파라미터를 Zod 스키마로 검증
 */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function parseQueryParams<T>(
  schema: ZodType<T, any, any>,
  searchParams: URLSearchParams
): T {
  const raw: Record<string, string> = {};
  searchParams.forEach((value, key) => {
    raw[key] = value;
  });
  const result = schema.safeParse(raw);
  if (!result.success) {
    throw new ValidationError(
      "쿼리 파라미터가 올바르지 않습니다.",
      result.error.flatten().fieldErrors
    );
  }
  return result.data;
}
