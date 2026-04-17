import { NextRequest } from "next/server";
import crypto from "crypto";
import { prisma } from "@/lib/prisma";
import { handleError } from "@/lib/handle-error";
import { ok } from "@/lib/response";
import { validateSchema } from "@/lib/middleware/validate";
import { ForgotPasswordSchema } from "@/lib/schemas/auth";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const input = await validateSchema(ForgotPasswordSchema, body);

    // 보안: 존재 여부 노출 방지 — 항상 동일 메시지 반환
    const user = await prisma.user.findUnique({
      where: { email: input.email },
      select: { id: true, email: true, name: true },
    });

    if (user) {
      // 재설정 토큰 생성 (crypto.randomBytes 48 → URL-safe hex 96자)
      const token = crypto.randomBytes(48).toString("hex");
      const expires = new Date(Date.now() + 1000 * 60 * 60); // 1시간 후 만료

      // VerificationToken에 재설정 토큰 저장
      await prisma.verificationToken.upsert({
        where: {
          identifier_token: {
            identifier: `reset:${user.email}`,
            token,
          },
        },
        update: { expires },
        create: {
          identifier: `reset:${user.email}`,
          token,
          expires,
        },
      });

      // 이메일 발송 (Resend API)
      // 환경변수 RESEND_API_KEY가 설정된 경우에만 실제 발송
      if (process.env.RESEND_API_KEY) {
        const resetUrl = `${process.env.NEXT_PUBLIC_APP_URL}/reset-password?token=${token}`;
        await fetch("https://api.resend.com/emails", {
          method: "POST",
          headers: {
            Authorization: `Bearer ${process.env.RESEND_API_KEY}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            from: process.env.RESEND_FROM_EMAIL ?? "noreply@taxassist.ai",
            to: user.email,
            subject: "[AI 세금신고 도우미] 비밀번호 재설정 안내",
            html: `
              <h2>비밀번호 재설정</h2>
              <p>안녕하세요 ${user.name ?? user.email}님,</p>
              <p>아래 링크를 클릭하여 비밀번호를 재설정해주세요. 링크는 1시간 후 만료됩니다.</p>
              <a href="${resetUrl}" style="background:#1E3A5F;color:white;padding:12px 24px;border-radius:8px;text-decoration:none;display:inline-block;margin:16px 0">
                비밀번호 재설정
              </a>
              <p style="color:#6b7280;font-size:12px">본인이 요청하지 않은 경우 이 이메일을 무시해주세요.</p>
            `,
          }),
        });
      }
    }

    // 보안: 항상 동일 응답 (이메일 존재 여부 노출 방지)
    return ok({
      message: "등록된 이메일 주소로 비밀번호 재설정 링크를 발송했습니다.",
    });
  } catch (error) {
    return handleError(error, req.nextUrl.pathname);
  }
}
