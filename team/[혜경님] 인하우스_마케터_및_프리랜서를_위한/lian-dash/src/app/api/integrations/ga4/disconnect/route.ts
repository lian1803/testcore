export const dynamic = "force-dynamic";

import { NextRequest, NextResponse } from "next/server";
import { auth } from "@/auth";
import { prisma } from "@/lib/prisma";

export async function DELETE(req: NextRequest) {
  try {
    const session = await auth();
    if (!session?.user?.id) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const workspace = await prisma.workspace.findFirst({
      where: { userId: session.user.id },
    });

    if (!workspace) {
      return NextResponse.json({ error: "Workspace not found" }, { status: 404 });
    }

    await prisma.integration.updateMany({
      where: {
        workspaceId: workspace.id,
        channel: "GA4",
      },
      data: {
        status: "DISCONNECTED",
        accessToken: null,
        refreshToken: null,
      },
    });

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error("GA4 disconnect error:", error);
    return NextResponse.json(
      { error: "Failed to disconnect GA4" },
      { status: 500 }
    );
  }
}
