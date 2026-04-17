import { NextResponse } from "next/server";
import { ZodError } from "zod";
import { AppError } from "./errors";

// RFC 9457 Problem Details 형식
export interface ProblemDetails {
  type: string;
  title: string;
  status: number;
  detail: string;
  instance?: string;
  errors?: unknown;
}

/**
 * 중앙 에러 핸들러
 * Route Handler catch 블록에서 handleError(error) 호출
 */
export function handleError(error: unknown, instance?: string): NextResponse {
  // Zod 유효성 검사 오류
  if (error instanceof ZodError) {
    const body: ProblemDetails = {
      type: "https://httpstatuses.com/400",
      title: "유효성 검사 오류",
      status: 400,
      detail: "요청 데이터가 올바르지 않습니다.",
      instance,
      errors: error.flatten().fieldErrors,
    };
    return NextResponse.json(body, { status: 400 });
  }

  // AppError 및 하위 클래스
  if (error instanceof AppError) {
    const body: ProblemDetails = {
      type: `https://httpstatuses.com/${error.statusCode}`,
      title: error.name,
      status: error.statusCode,
      detail: error.message,
      instance,
      errors: error.details,
    };
    return NextResponse.json(body, { status: error.statusCode });
  }

  // 예상치 못한 오류 (500)
  console.error("[handleError] 예상치 못한 오류:", error);
  const body: ProblemDetails = {
    type: "https://httpstatuses.com/500",
    title: "서버 내부 오류",
    status: 500,
    detail: "일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
    instance,
  };
  return NextResponse.json(body, { status: 500 });
}
