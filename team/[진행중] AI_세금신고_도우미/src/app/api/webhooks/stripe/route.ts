import { NextRequest, NextResponse } from "next/server";
import { handleStripeWebhook } from "@/services/billing.service";

/**
 * POST /api/webhooks/stripe
 * Stripe Webhook 수신 처리
 *
 * 중요:
 * - 인증 없음 (Stripe 서명 검증으로 대체)
 * - raw body 필수 (서명 검증에 원본 바이트 필요)
 * - 멱등성 보장 (billing.service.ts에서 upsert 처리)
 * - 5초 내 200 응답 필수 (Stripe 재시도 방지)
 */
export async function POST(req: NextRequest) {
  const signature = req.headers.get("stripe-signature");

  if (!signature) {
    return NextResponse.json(
      { error: "stripe-signature 헤더가 없습니다." },
      { status: 400 }
    );
  }

  let rawBody: string;
  try {
    rawBody = await req.text();
  } catch {
    return NextResponse.json(
      { error: "요청 본문을 읽을 수 없습니다." },
      { status: 400 }
    );
  }

  try {
    await handleStripeWebhook(rawBody, signature);
    return NextResponse.json({ received: true }, { status: 200 });
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);

    // 서명 검증 실패 → 400 (Stripe가 재시도하지 않도록)
    if (message.includes("서명 검증 실패") || message.includes("signature")) {
      console.error("[Stripe Webhook] 서명 검증 실패:", message);
      return NextResponse.json({ error: message }, { status: 400 });
    }

    // 처리 중 오류 → 500 (Stripe가 재시도하도록)
    console.error("[Stripe Webhook] 처리 오류:", message);
    return NextResponse.json({ error: "웹훅 처리 중 오류가 발생했습니다." }, { status: 500 });
  }
}
