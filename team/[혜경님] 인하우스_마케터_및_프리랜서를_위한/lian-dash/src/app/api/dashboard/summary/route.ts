export const dynamic = "force-dynamic";

import { NextRequest, NextResponse } from "next/server";
import { auth } from "@/auth";
import { prisma } from "@/lib/prisma";
import { checkTrialStatus } from "@/lib/middleware/trialCheck";
import { GA4Adapter } from "@/lib/channels/ga4";
import { MetaAdapter } from "@/lib/channels/meta";
import { NaverAdapter } from "@/lib/channels/naver";

export async function GET(req: NextRequest) {
  try {
    // Check trial status
    const trialError = await checkTrialStatus(req);
    if (trialError) return trialError;

    const session = await auth();
    if (!session?.user?.id) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const dateRange = req.nextUrl.searchParams.get("dateRange") || "7d";

    // Calculate date range
    const endDate = new Date();
    const startDate = new Date();
    if (dateRange === "7d") {
      startDate.setDate(startDate.getDate() - 7);
    } else if (dateRange === "30d") {
      startDate.setDate(startDate.getDate() - 30);
    }

    const startDateStr = startDate.toISOString().split("T")[0];
    const endDateStr = endDate.toISOString().split("T")[0];

    const workspace = await prisma.workspace.findFirst({
      where: { userId: session.user.id },
      include: {
        integrations: true,
      },
    });

    if (!workspace) {
      return NextResponse.json({ error: "Workspace not found" }, { status: 404 });
    }

    // Fetch metrics from all connected channels in parallel
    const [ga4Metrics, metaMetrics, naverMetrics] = await Promise.all([
      (async () => {
        const ga4 = workspace.integrations.find((i) => i.channel === "GA4");
        if (ga4?.status === "CONNECTED" && ga4.accessToken) {
          try {
            return await GA4Adapter.getMetrics(ga4.accessToken, {
              startDate: startDateStr,
              endDate: endDateStr,
            });
          } catch {
            return null;
          }
        }
        return null;
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
            return null;
          }
        }
        return null;
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
            return null;
          }
        }
        return null;
      })(),
    ]);

    // Log usage
    await prisma.usageLog.create({
      data: {
        userId: session.user.id,
        workspaceId: workspace.id,
        logType: "CHANNEL_API_CALL",
        apiCalls: 3, // 3 channels queried
      },
    });

    const response = {
      channels: {
        ga4: ga4Metrics,
        meta: metaMetrics,
        naver: naverMetrics,
      },
      summary: {
        totalSessions: (ga4Metrics?.sessions || 0),
        totalImpressions:
          (metaMetrics?.impressions || 0) + (naverMetrics?.impressions || 0),
        totalClicks:
          (metaMetrics?.clicks || 0) + (naverMetrics?.clicks || 0),
        totalSpend: metaMetrics?.spend || 0,
        averageROAS: metaMetrics?.roas || 0,
      },
      dateRange: { startDate: startDateStr, endDate: endDateStr },
    };

    return NextResponse.json(response, {
      headers: {
        "Cache-Control": "max-age=300", // 5 minutes
      },
    });
  } catch (error) {
    console.error("Dashboard summary error:", error);
    return NextResponse.json(
      { error: "Failed to fetch dashboard summary" },
      { status: 500 }
    );
  }
}
