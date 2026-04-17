export const dynamic = "force-dynamic";

import { NextRequest, NextResponse } from "next/server";
import { auth } from "@/auth";
import { prisma } from "@/lib/prisma";
import { checkTrialStatus } from "@/lib/middleware/trialCheck";
import { generateInsight } from "@/lib/ai/insight";
import { GA4Adapter } from "@/lib/channels/ga4";
import { MetaAdapter } from "@/lib/channels/meta";
import { NaverAdapter } from "@/lib/channels/naver";

export async function POST(req: NextRequest) {
  try {
    const trialError = await checkTrialStatus(req);
    if (trialError) return trialError;

    const session = await auth();
    if (!session?.user?.id) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    // Check monthly usage limit (10 calls per month)
    const now = new Date();
    const monthStart = new Date(now.getFullYear(), now.getMonth(), 1);

    const monthlyInsights = await prisma.insightLog.count({
      where: {
        userId: session.user.id,
        createdAt: {
          gte: monthStart,
        },
      },
    });

    if (monthlyInsights >= 10) {
      return NextResponse.json(
        { error: "Monthly insight limit reached (10/month)" },
        { status: 429 }
      );
    }

    const workspace = await prisma.workspace.findFirst({
      where: { userId: session.user.id },
      include: {
        integrations: true,
      },
    });

    if (!workspace) {
      return NextResponse.json({ error: "Workspace not found" }, { status: 404 });
    }

    // Get last 7 days data from all channels
    const endDate = new Date();
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - 7);

    const startDateStr = startDate.toISOString().split("T")[0];
    const endDateStr = endDate.toISOString().split("T")[0];

    const [ga4Data, metaData, naverData] = await Promise.all([
      (async () => {
        const ga4 = workspace.integrations.find((i) => i.channel === "GA4");
        if (ga4?.status === "CONNECTED" && ga4.accessToken) {
          try {
            return await GA4Adapter.getMetrics(ga4.accessToken, {
              startDate: startDateStr,
              endDate: endDateStr,
            });
          } catch {
            return {};
          }
        }
        return {};
      })(),
      (async () => {
        const meta = workspace.integrations.find((i) => i.channel === "META");
        if (meta?.status === "CONNECTED" && meta.accessToken) {
          try {
            return await MetaAdapter.getMetrics(meta.accessToken, {
              startDate: startDateStr,
              endDate: endDateStr,
            });
          } catch {
            return {};
          }
        }
        return {};
      })(),
      (async () => {
        const naver = workspace.integrations.find((i) => i.channel === "NAVER_SA");
        if ((naver?.status === "CONNECTED" || naver?.status === "MOCK") && naver.accessToken) {
          try {
            return await NaverAdapter.getMetrics(naver.accessToken, {
              startDate: startDateStr,
              endDate: endDateStr,
            });
          } catch {
            return {};
          }
        }
        return {};
      })(),
    ]);

    // Generate insight using GPT-4o
    const insightResult = await generateInsight(ga4Data, metaData, naverData);

    // Save insight log
    const insightLog = await prisma.insightLog.create({
      data: {
        userId: session.user.id,
        workspaceId: workspace.id,
        content: JSON.stringify(insightResult.insights),
        inputTokens: insightResult.inputTokens,
        outputTokens: insightResult.outputTokens,
      },
    });

    // Calculate cost
    const estimatedCost =
      insightResult.inputTokens * 0.000005 +
      insightResult.outputTokens * 0.000015;

    // Log usage
    await prisma.usageLog.create({
      data: {
        userId: session.user.id,
        workspaceId: workspace.id,
        logType: "AI_INSIGHT",
        apiCalls: 1,
        tokensUsed:
          insightResult.inputTokens + insightResult.outputTokens,
        costEstimate: estimatedCost,
      },
    });

    return NextResponse.json({
      insights: insightResult.insights,
      inputTokens: insightResult.inputTokens,
      outputTokens: insightResult.outputTokens,
      estimatedCost,
    });
  } catch (error) {
    console.error("Insight generation error:", error);
    return NextResponse.json(
      { error: "Failed to generate insights" },
      { status: 500 }
    );
  }
}
