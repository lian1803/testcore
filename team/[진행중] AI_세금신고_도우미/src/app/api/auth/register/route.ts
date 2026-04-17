import { NextRequest, NextResponse } from "next/server";
import bcrypt from "bcryptjs";
import { prisma } from "@/lib/prisma";
import { handleError } from "@/lib/handle-error";
import { created } from "@/lib/response";
import { validateSchema } from "@/lib/middleware/validate";
import { RegisterSchema } from "@/lib/schemas/auth";
import { ConflictError } from "@/lib/errors";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const input = await validateSchema(RegisterSchema, body);

    // 이메일 중복 확인
    const existing = await prisma.user.findUnique({
      where: { email: input.email },
      select: { id: true },
    });
    if (existing) {
      throw new ConflictError("이미 사용 중인 이메일 주소입니다.");
    }

    // 비밀번호 해싱 (bcrypt cost factor 12)
    const passwordHash = await bcrypt.hash(input.password, 12);

    // 사용자 생성
    const user = await prisma.user.create({
      data: {
        email: input.email,
        name: input.name ?? null,
        passwordHash,
        planStatus: "FREE",
      },
      select: {
        id: true,
        email: true,
        name: true,
        planStatus: true,
        createdAt: true,
      },
    });

    return created({
      user,
      message: "회원가입이 완료되었습니다. 로그인해주세요.",
    });
  } catch (error) {
    return handleError(error, req.nextUrl.pathname);
  }
}
