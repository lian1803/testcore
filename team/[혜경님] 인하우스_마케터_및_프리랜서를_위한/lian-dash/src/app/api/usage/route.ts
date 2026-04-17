export const dynamic = "force-dynamic";

import { NextRequest, NextResponse } from "next/server";
import { auth } from "@/auth";
import { getMonthlyUsage } from "@/lib/usage/logger";

export async function GET(req: NextRequest) {
  try {
    const session = await auth();
    if (!session?.user?.id) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    // Note: workspaceId should come from session or query params
    // For now, we'll get the user's first workspace
    const { workspaces } = (session.user as any) || {};
    const workspaceId = req.nextUrl.searchParams.get("workspaceId") || workspaces?.[0]?.id;

    if (!workspaceId) {
      return NextResponse.json({ error: "Workspace not found" }, { status: 404 });
    }

    const usage = await getMonthlyUsage(session.user.id, workspaceId);

    return NextResponse.json(usage);
  } catch (error) {
    console.error("Usage retrieval error:", error);
    return NextResponse.json(
      { error: "Failed to fetch usage data" },
      { status: 500 }
    );
  }
}
