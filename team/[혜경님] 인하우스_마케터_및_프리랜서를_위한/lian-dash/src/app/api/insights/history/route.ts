export const dynamic = "force-dynamic";

import { NextRequest, NextResponse } from "next/server";
import { auth } from "@/auth";
import { prisma } from "@/lib/prisma";
import { checkTrialStatus } from "@/lib/middleware/trialCheck";

export async function GET(req: NextRequest) {
  try {
    const trialError = await checkTrialStatus(req);
    if (trialError) return trialError;

    const session = await auth();
    if (!session?.user?.id) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const limit = parseInt(req.nextUrl.searchParams.get("limit") || "10");

    // Get current month usage
    const now = new Date();
    const monthStart = new Date(now.getFullYear(), now.getMonth(), 1);

    const monthlyUsage = await prisma.insightLog.count({
      where: {
        userId: session.user.id,
        createdAt: {
          gte: monthStart,
        },
      },
    });

    // Get insight history
    const insights = await prisma.insightLog.findMany({
      where: {
        userId: session.user.id,
      },
      orderBy: {
        createdAt: "desc",
      },
      take: limit,
    });

    const parsedInsights = insights.map((insight) => ({
      id: insight.id,
      createdAt: insight.createdAt,
      insights: JSON.parse(insight.content),
      inputTokens: insight.inputTokens,
      outputTokens: insight.outputTokens,
    }));

    return NextResponse.json({
      data: parsedInsights,
      monthlyUsage,
      monthlyLimit: 10,
    });
  } catch (error) {
    console.error("Insight history error:", error);
    return NextResponse.json(
      { error: "Failed to fetch insight history" },
      { status: 500 }
    );
  }
}
