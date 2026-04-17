import { NextRequest } from "next/server";
import { z } from "zod";
import { prisma } from "@/lib/prisma";
import { handleError } from "@/lib/handle-error";
import { ok, created } from "@/lib/response";
import { requireAuth } from "@/lib/middleware/auth";
import { validateSchema } from "@/lib/middleware/validate";
import { NotFoundError, ConflictError } from "@/lib/errors";

const ProfileSchema = z.object({
  businessType: z.string().min(1, "업종코드를 입력해주세요.").max(10),
  businessTypeLabel: z.string().min(1, "업종명을 입력해주세요.").max(100),
  taxationType: z.enum(["GENERAL", "SIMPLIFIED", "TAX_FREE", "INCOME_ONLY"]),
  registrationNumber: z
    .string()
    .regex(/^\d{10}$/, "사업자등록번호는 10자리 숫자입니다.")
    .nullable()
    .optional(),
  taxYear: z
    .number()
    .int()
    .min(2020)
    .max(new Date().getFullYear()),
});

const UpdateProfileSchema = ProfileSchema.partial();

export async function GET(req: NextRequest) {
  try {
    const { userId } = await requireAuth();

    const profile = await prisma.businessProfile.findUnique({
      where: { userId },
    });

    if (!profile) {
      throw new NotFoundError("사업자 프로필");
    }

    return ok(profile);
  } catch (error) {
    return handleError(error, req.nextUrl.pathname);
  }
}

export async function POST(req: NextRequest) {
  try {
    const { userId } = await requireAuth();

    // 이미 프로필이 있으면 충돌
    const existing = await prisma.businessProfile.findUnique({
      where: { userId },
      select: { id: true },
    });
    if (existing) {
      throw new ConflictError(
        "이미 사업자 프로필이 존재합니다. PATCH 요청으로 수정해주세요."
      );
    }

    const body = await req.json();
    const input = await validateSchema(ProfileSchema, body);

    const profile = await prisma.businessProfile.create({
      data: {
        userId,
        ...input,
        registrationNumber: input.registrationNumber ?? null,
      },
    });

    return created(profile);
  } catch (error) {
    return handleError(error, req.nextUrl.pathname);
  }
}

export async function PATCH(req: NextRequest) {
  try {
    const { userId } = await requireAuth();

    const existing = await prisma.businessProfile.findUnique({
      where: { userId },
      select: { id: true },
    });
    if (!existing) {
      throw new NotFoundError("사업자 프로필");
    }

    const body = await req.json();
    const input = await validateSchema(UpdateProfileSchema, body);

    const profile = await prisma.businessProfile.update({
      where: { userId },
      data: input,
    });

    return ok(profile);
  } catch (error) {
    return handleError(error, req.nextUrl.pathname);
  }
}
