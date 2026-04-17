import { NextRequest } from "next/server";
import { handleError } from "@/lib/handle-error";
import { created } from "@/lib/response";
import { requireAuth } from "@/lib/middleware/auth";
import { createPortalSession } from "@/services/billing.service";

/**
 * POST /api/billing/portal
 * Stripe Customer Portal 세션 생성
 * 구독 취소, 결제 방법 변경, 청구서 확인 가능
 */
export async function POST(req: NextRequest) {
  try {
    const { userId } = await requireAuth();

    const appUrl = process.env.NEXT_PUBLIC_APP_URL ?? "http://localhost:3000";

    const session = await createPortalSession({
      userId,
      returnUrl: `${appUrl}/settings/billing`,
    });

    return created({ url: session.url });
  } catch (error) {
    return handleError(error, req.nextUrl.pathname);
  }
}
