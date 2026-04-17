// ──────────────────────────────────────────────
// 중앙 에러 클래스 정의
// RFC 9457 (Problem Details for HTTP APIs) 형식 준수
// ──────────────────────────────────────────────

export class AppError extends Error {
  constructor(
    public message: string,
    public statusCode: number = 500,
    public code: string = "INTERNAL_ERROR",
    public details?: unknown
  ) {
    super(message);
    this.name = "AppError";
    // V8 스택 트레이스 캡처
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, this.constructor);
    }
  }
}

export class NotFoundError extends AppError {
  constructor(resource: string, id?: string) {
    super(
      id ? `${resource}(${id})을(를) 찾을 수 없습니다.` : `${resource}을(를) 찾을 수 없습니다.`,
      404,
      "NOT_FOUND"
    );
    this.name = "NotFoundError";
  }
}

export class ValidationError extends AppError {
  constructor(message: string, details?: unknown) {
    super(message, 400, "VALIDATION_ERROR", details);
    this.name = "ValidationError";
  }
}

export class UnauthorizedError extends AppError {
  constructor(message = "인증이 필요합니다.") {
    super(message, 401, "UNAUTHORIZED");
    this.name = "UnauthorizedError";
  }
}

export class ForbiddenError extends AppError {
  constructor(message = "접근 권한이 없습니다.") {
    super(message, 403, "FORBIDDEN");
    this.name = "ForbiddenError";
  }
}

export class ConflictError extends AppError {
  constructor(message: string) {
    super(message, 409, "CONFLICT");
    this.name = "ConflictError";
  }
}

export class PaymentRequiredError extends AppError {
  constructor(message = "유료 플랜이 필요합니다.") {
    super(message, 402, "PAYMENT_REQUIRED");
    this.name = "PaymentRequiredError";
  }
}

export class UsageLimitError extends AppError {
  constructor(resource: string, limit: number) {
    super(
      `무료 플랜 한도 초과: ${resource} ${limit}건 제한에 도달했습니다.`,
      402,
      "USAGE_LIMIT_EXCEEDED",
      { resource, limit }
    );
    this.name = "UsageLimitError";
  }
}
