export const dynamic = "force-dynamic";

import { NextRequest, NextResponse } from "next/server";
import { auth } from "@/auth";
import { prisma } from "@/lib/prisma";
import { checkTrialStatus } from "@/lib/middleware/trialCheck";
import { NaverAdapter } from "@/lib/channels/naver";

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
          where: { channel: "NAVER_SA" },
        },
      },
    });

    if (!workspace) {
      return NextResponse.json({ error: "Workspace not found" }, { status: 404 });
    }

    const naver = workspace.integrations[0];

    if (!naver?.accessToken) {
      return NextResponse.json(
        { error: "Naver SA not connected" },
        { status: 404 }
      );
    }

    const metrics = await NaverAdapter.getMetrics(naver.accessToken, {
      startDate,
      endDate,
    });

    await prisma.usageLog.create({
      data: {
        userId: session.user.id,
        workspaceId: workspace.id,
        integrationId: naver.id,
        logType: "CHANNEL_API_CALL",
        channel: "NAVER_SA",
        apiCalls: 1,
      },
    });

    return NextResponse.json(
      {
        data: metrics,
        isMock: naver.status === "MOCK",
      },
      {
        headers: {
          "Cache-Control": "max-age=300",
        },
      }
    );
  } catch (error) {
    console.error("Naver metrics error:", error);
    return NextResponse.json(
      { error: "Failed to fetch Naver metrics" },
      { status: 500 }
    );
  }
}
