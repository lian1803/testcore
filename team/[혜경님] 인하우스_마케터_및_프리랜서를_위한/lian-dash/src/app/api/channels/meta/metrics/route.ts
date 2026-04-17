export const dynamic = "force-dynamic";

import { NextRequest, NextResponse } from "next/server";
import { auth } from "@/auth";
import { prisma } from "@/lib/prisma";
import { checkTrialStatus } from "@/lib/middleware/trialCheck";
import { MetaAdapter } from "@/lib/channels/meta";

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
          where: { channel: "META" },
        },
      },
    });

    if (!workspace) {
      return NextResponse.json({ error: "Workspace not found" }, { status: 404 });
    }

    const meta = workspace.integrations[0];

    if (!meta?.accessToken) {
      return NextResponse.json(
        { error: "Meta not connected" },
        { status: 404 }
      );
    }

    const metrics = await MetaAdapter.getMetrics(meta.accessToken, {
      startDate,
      endDate,
    });

    await prisma.usageLog.create({
      data: {
        userId: session.user.id,
        workspaceId: workspace.id,
        integrationId: meta.id,
        logType: "CHANNEL_API_CALL",
        channel: "META",
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
    console.error("Meta metrics error:", error);
    return NextResponse.json(
      { error: "Failed to fetch Meta metrics" },
      { status: 500 }
    );
  }
}
