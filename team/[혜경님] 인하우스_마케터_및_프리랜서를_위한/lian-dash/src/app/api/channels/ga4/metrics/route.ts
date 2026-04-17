export const dynamic = "force-dynamic";

import { NextRequest, NextResponse } from "next/server";
import { auth } from "@/auth";
import { prisma } from "@/lib/prisma";
import { checkTrialStatus } from "@/lib/middleware/trialCheck";
import { GA4Adapter } from "@/lib/channels/ga4";

export async function GET(req: NextRequest) {
  try {
    const trialError = await checkTrialStatus(req);
    if (trialError) return trialError;

    const session = await auth();
    if (!session?.user?.id) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const startDate = req.nextUrl.searchParams.get("startDate");
    const endDate = req.nextUrl.searchParams.get("endDate");

    if (!startDate || !endDate) {
      return NextResponse.json(
        { error: "startDate and endDate required" },
        { status: 400 }
      );
    }

    const workspace = await prisma.workspace.findFirst({
      where: { userId: session.user.id },
      include: {
        integrations: {
          where: { channel: "GA4" },
        },
      },
    });

    if (!workspace) {
      return NextResponse.json({ error: "Workspace not found" }, { status: 404 });
    }

    const ga4 = workspace.integrations[0];

    if (!ga4?.accessToken) {
      return NextResponse.json(
        { error: "GA4 not connected" },
        { status: 404 }
      );
    }

    const metrics = await GA4Adapter.getMetrics(ga4.accessToken, {
      startDate,
      endDate,
    });

    await prisma.usageLog.create({
      data: {
        userId: session.user.id,
        workspaceId: workspace.id,
        integrationId: ga4.id,
        logType: "CHANNEL_API_CALL",
        channel: "GA4",
        apiCalls: 1,
      },
    });

    return NextResponse.json(
      { data: metrics },
      {
        headers: {
          "Cache-Control": "max-age=300",
        },
      }
    );
  } catch (error) {
    console.error("GA4 metrics error:", error);
    return NextResponse.json(
      { error: "Failed to fetch GA4 metrics" },
      { status: 500 }
    );
  }
}
