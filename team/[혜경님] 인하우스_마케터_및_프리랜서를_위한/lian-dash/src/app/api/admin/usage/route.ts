export const dynamic = "force-dynamic";

import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";

export async function GET(req: NextRequest) {
  try {
    // Admin authentication - check X-Admin-Key header
    const adminKey = req.headers.get("x-admin-key");
    if (adminKey !== process.env.ADMIN_SECRET_KEY) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const now = new Date();
    const monthStart = new Date(now.getFullYear(), now.getMonth(), 1);

    // Get AI insight usage
    const aiUsage = await prisma.usageLog.aggregate({
      where: {
        logType: "AI_INSIGHT",
        createdAt: { gte: monthStart },
      },
      _sum: {
        apiCalls: true,
        tokensUsed: true,
        costEstimate: true,
      },
      _count: true,
    });

    // Get channel API usage
    const channelUsage = await prisma.usageLog.groupBy({
      by: ["channel"],
      where: {
        logType: "CHANNEL_API_CALL",
        createdAt: { gte: monthStart },
      },
      _sum: { apiCalls: true },
    });

    // Get cost warnings
    const costByUser = await prisma.usageLog.groupBy({
      by: ["userId"],
      where: {
        createdAt: { gte: monthStart },
      },
      _sum: { costEstimate: true },
    });

    const highCostUsers = costByUser.filter((item) => (item._sum.costEstimate || 0) > 50);

    if (highCostUsers.length > 0) {
      console.warn(
        `[COST ALERT] High usage detected for users: ${highCostUsers.map((u) => u.userId).join(", ")}`
      );
    }

    return NextResponse.json({
      period: { start: monthStart, end: now },
      aiInsights: {
        totalCalls: aiUsage._count,
        totalTokens: aiUsage._sum.tokensUsed || 0,
        totalCost: aiUsage._sum.costEstimate || 0,
      },
      channelApiCalls: Object.fromEntries(
        channelUsage.map((item) => [item.channel, item._sum.apiCalls || 0])
      ),
      costWarnings: highCostUsers.map((item) => ({
        userId: item.userId,
        estimatedCost: item._sum.costEstimate || 0,
      })),
    });
  } catch (error) {
    console.error("Admin usage error:", error);
    return NextResponse.json(
      { error: "Failed to fetch admin usage data" },
      { status: 500 }
    );
  }
}
