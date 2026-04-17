// ──────────────────────────────────────────────
// 결제 서비스 — Stripe 구독 관리
// ──────────────────────────────────────────────
import Stripe from "stripe";
import { prisma } from "@/lib/prisma";

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: "2024-06-20",
  typescript: true,
});

const PRICE_IDS = {
  MONTHLY: process.env.STRIPE_PRICE_MONTHLY!,  // 월 9,900원
  ANNUAL: process.env.STRIPE_PRICE_ANNUAL!,    // 연 79,200원
} as const;

/**
 * Stripe Customer 생성 또는 조회
 * 기존 Subscription이 있으면 stripeCustomerId 반환
 */
async function getOrCreateStripeCustomer(
  userId: string,
  email: string,
  name: string | null
): Promise<string> {
  const existing = await prisma.subscription.findUnique({
    where: { userId },
    select: { stripeCustomerId: true },
  });

  if (existing?.stripeCustomerId) {
    return existing.stripeCustomerId;
  }

  const customer = await stripe.customers.create({
    email,
    name: name ?? undefined,
    metadata: { userId },
  });

  return customer.id;
}

/**
 * Stripe Checkout 세션 생성
 */
export async function createCheckoutSession(params: {
  userId: string;
  email: string;
  name: string | null;
  plan: "MONTHLY" | "ANNUAL";
  successUrl: string;
  cancelUrl: string;
}): Promise<{ url: string; sessionId: string }> {
  const customerId = await getOrCreateStripeCustomer(
    params.userId,
    params.email,
    params.name
  );

  const session = await stripe.checkout.sessions.create({
    customer: customerId,
    payment_method_types: ["card"],
    mode: "subscription",
    line_items: [
      {
        price: PRICE_IDS[params.plan],
        quantity: 1,
      },
    ],
    success_url: params.successUrl,
    cancel_url: params.cancelUrl,
    subscription_data: {
      metadata: { userId: params.userId },
    },
    metadata: {
      userId: params.userId,
      plan: params.plan,
    },
    locale: "ko",
    allow_promotion_codes: true,
  });

  if (!session.url) {
    throw new Error("Stripe Checkout 세션 URL 생성 실패");
  }

  return { url: session.url, sessionId: session.id };
}

/**
 * Stripe Customer Portal 세션 생성
 * 구독 관리 (결제 방법 변경, 취소 등)
 */
export async function createPortalSession(params: {
  userId: string;
  returnUrl: string;
}): Promise<{ url: string }> {
  const subscription = await prisma.subscription.findUnique({
    where: { userId: params.userId },
    select: { stripeCustomerId: true },
  });

  if (!subscription?.stripeCustomerId) {
    throw new Error("구독 정보를 찾을 수 없습니다.");
  }

  const session = await stripe.billingPortal.sessions.create({
    customer: subscription.stripeCustomerId,
    return_url: params.returnUrl,
  });

  return { url: session.url };
}

/**
 * Stripe Webhook 이벤트 처리
 * 멱등성 보장: stripeSubscriptionId를 기준으로 upsert
 */
export async function handleStripeWebhook(
  rawBody: string,
  signature: string
): Promise<void> {
  const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET!;

  let event: Stripe.Event;
  try {
    event = stripe.webhooks.constructEvent(rawBody, signature, webhookSecret);
  } catch (err) {
    throw new Error(`Stripe 서명 검증 실패: ${err instanceof Error ? err.message : String(err)}`);
  }

  switch (event.type) {
    case "checkout.session.completed": {
      const session = event.data.object as Stripe.Checkout.Session;
      await handleCheckoutCompleted(session);
      break;
    }
    case "customer.subscription.updated": {
      const subscription = event.data.object as Stripe.Subscription;
      await handleSubscriptionUpdated(subscription);
      break;
    }
    case "customer.subscription.deleted": {
      const subscription = event.data.object as Stripe.Subscription;
      await handleSubscriptionDeleted(subscription);
      break;
    }
    case "invoice.payment_failed": {
      const invoice = event.data.object as Stripe.Invoice;
      await handlePaymentFailed(invoice);
      break;
    }
    default:
      console.log(`[Stripe Webhook] 처리하지 않는 이벤트: ${event.type}`);
  }
}

async function handleCheckoutCompleted(
  session: Stripe.Checkout.Session
): Promise<void> {
  const userId = session.metadata?.userId;
  const plan = session.metadata?.plan as "MONTHLY" | "ANNUAL";
  const stripeSubscriptionId = session.subscription as string;

  if (!userId || !plan || !stripeSubscriptionId) {
    console.error("[Stripe] checkout.session.completed: metadata 누락", session.id);
    return;
  }

  const stripeSubscription = await stripe.subscriptions.retrieve(stripeSubscriptionId);

  await prisma.$transaction(async (tx) => {
    // Subscription upsert (멱등성)
    await tx.subscription.upsert({
      where: { userId },
      update: {
        plan,
        stripeSubscriptionId,
        stripePriceId: stripeSubscription.items.data[0]?.price.id ?? null,
        status: "ACTIVE",
        currentPeriodEnd: new Date(stripeSubscription.current_period_end * 1000),
        cancelAtPeriodEnd: false,
      },
      create: {
        userId,
        plan,
        stripeCustomerId: session.customer as string,
        stripeSubscriptionId,
        stripePriceId: stripeSubscription.items.data[0]?.price.id ?? null,
        status: "ACTIVE",
        currentPeriodEnd: new Date(stripeSubscription.current_period_end * 1000),
      },
    });

    // User planStatus PREMIUM으로 업데이트
    await tx.user.update({
      where: { id: userId },
      data: { planStatus: "PREMIUM" },
    });
  });

  console.log(`[Stripe] 결제 완료: userId=${userId}, plan=${plan}`);
}

async function handleSubscriptionUpdated(
  stripeSubscription: Stripe.Subscription
): Promise<void> {
  const userId = stripeSubscription.metadata?.userId;
  if (!userId) {
    console.error("[Stripe] subscription.updated: userId metadata 누락");
    return;
  }

  await prisma.subscription.updateMany({
    where: { stripeSubscriptionId: stripeSubscription.id },
    data: {
      status: mapStripeStatus(stripeSubscription.status),
      currentPeriodEnd: new Date(stripeSubscription.current_period_end * 1000),
      cancelAtPeriodEnd: stripeSubscription.cancel_at_period_end,
    },
  });
}

async function handleSubscriptionDeleted(
  stripeSubscription: Stripe.Subscription
): Promise<void> {
  const subscription = await prisma.subscription.findFirst({
    where: { stripeSubscriptionId: stripeSubscription.id },
    select: { userId: true },
  });

  if (!subscription) return;

  await prisma.$transaction(async (tx) => {
    await tx.subscription.updateMany({
      where: { stripeSubscriptionId: stripeSubscription.id },
      data: { status: "CANCELED" },
    });

    await tx.user.update({
      where: { id: subscription.userId },
      data: { planStatus: "EXPIRED" },
    });
  });

  console.log(`[Stripe] 구독 해지: userId=${subscription.userId}`);
}

async function handlePaymentFailed(invoice: Stripe.Invoice): Promise<void> {
  const subscription = await prisma.subscription.findFirst({
    where: { stripeSubscriptionId: invoice.subscription as string },
    select: { userId: true },
  });

  if (!subscription) return;

  await prisma.subscription.updateMany({
    where: { stripeSubscriptionId: invoice.subscription as string },
    data: { status: "PAST_DUE" },
  });

  console.warn(`[Stripe] 결제 실패: userId=${subscription.userId}`);
}

function mapStripeStatus(
  stripeStatus: string
): "ACTIVE" | "PAST_DUE" | "CANCELED" | "TRIALING" {
  const map: Record<string, "ACTIVE" | "PAST_DUE" | "CANCELED" | "TRIALING"> = {
    active: "ACTIVE",
    past_due: "PAST_DUE",
    canceled: "CANCELED",
    trialing: "TRIALING",
    unpaid: "PAST_DUE",
    incomplete: "PAST_DUE",
    incomplete_expired: "CANCELED",
    paused: "ACTIVE",
  };
  return map[stripeStatus] ?? "ACTIVE";
}
