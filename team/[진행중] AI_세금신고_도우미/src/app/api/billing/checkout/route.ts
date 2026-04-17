import { NextRequest } from "next/server";
import { z } from "zod";
import { prisma } from "@/lib/prisma";
import { handleError } from "@/lib/handle-error";
import { created } from "@/lib/response";
import { requireAuth } from "@/lib/middleware/auth";
import { validateSchema } from "@/lib/middleware/validate";
import { createCheckoutSession } from "@/services/billing.service";

const CheckoutSchema = z.object({
  plan: z.enum(["MONTHLY", "ANNUAL"]),
});

/**
 * POST /api/billing/checkout
 * Stripe Checkout 세션 생성 → 결제 페이지 URL 반환
 */
export async function POST(req: NextRequest) {
  try {
    const { userId } = await requireAuth();

    const body = await req.json();
    const input = await validateSchema(CheckoutSchema, body);

    const user = await prisma.user.findUnique({
      where: { id: userId },
      select: { email: true, name: true, planStatus: true },
    });

    if (!user) {
      throw new Error("사용자 정보를 찾을 수 없습니다.");
    }

    const appUrl = process.env.NEXT_PUBLIC_APP_URL ?? "http://localhost:3000";

    const session = await createCheckoutSession({
      userId,
      email: user.email,
      name: user.name,
      plan: input.plan,
      successUrl: `${appUrl}/dashboard?upgrade=success`,
      cancelUrl: `${appUrl}/settings/billing?upgrade=canceled`,
    });

    return created({
      url: session.url,
      sessionId: session.sessionId,
    });
  } catch (error) {
    return handleError(error, req.nextUrl.pathname);
  }
}
