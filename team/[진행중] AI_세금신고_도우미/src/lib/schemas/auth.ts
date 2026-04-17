import { z } from "zod";

export const RegisterSchema = z.object({
  email: z
    .string()
    .email("유효한 이메일 주소를 입력해주세요.")
    .max(255, "이메일은 255자 이하여야 합니다."),
  password: z
    .string()
    .min(8, "비밀번호는 최소 8자 이상이어야 합니다.")
    .max(100, "비밀번호는 100자 이하여야 합니다.")
    .regex(
      /^(?=.*[a-zA-Z])(?=.*[0-9!@#$%^&*])/,
      "비밀번호는 영문자와 숫자 또는 특수문자를 포함해야 합니다."
    ),
  name: z
    .string()
    .min(1, "이름을 입력해주세요.")
    .max(50, "이름은 50자 이하여야 합니다.")
    .optional(),
});

export type RegisterInput = z.infer<typeof RegisterSchema>;

export const ForgotPasswordSchema = z.object({
  email: z.string().email("유효한 이메일 주소를 입력해주세요."),
});

export type ForgotPasswordInput = z.infer<typeof ForgotPasswordSchema>;

export const ResetPasswordSchema = z.object({
  token: z.string().min(1, "토큰이 필요합니다."),
  password: z
    .string()
    .min(8, "비밀번호는 최소 8자 이상이어야 합니다.")
    .regex(
      /^(?=.*[a-zA-Z])(?=.*[0-9!@#$%^&*])/,
      "비밀번호는 영문자와 숫자 또는 특수문자를 포함해야 합니다."
    ),
});

export type ResetPasswordInput = z.infer<typeof ResetPasswordSchema>;
