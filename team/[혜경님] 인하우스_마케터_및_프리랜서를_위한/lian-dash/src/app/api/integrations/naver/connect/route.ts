export const dynamic = "force-dynamic";

import { NextRequest, NextResponse } from "next/server";
import { auth } from "@/auth";
import { prisma } from "@/lib/prisma";
import { NaverAdapter } from "@/lib/channels/naver";

export async function POST(req: NextRequest) {
  try {
    const session = await auth();
    if (!session?.user?.id) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const body = await req.json() as {
      apiKey?: string;
      secret?: string;
    };

    if (!body.apiKey || !body.secret) {
      return NextResponse.json(
        { error: "apiKey and secret required" },
        { status: 400 }
      );
    }

    const workspace = await prisma.workspace.findFirst({
      where: { userId: session.user.id },
    });

    if (!workspace) {
      return NextResponse.json({ error: "Workspace not found" }, { status: 404 });
    }

    const tokens = await NaverAdapter.handleConnect(body.apiKey, body.secret);

    // Start as MOCK status until PoC validation
    await prisma.integration.upsert({
      where: {
        workspaceId_channel: {
          workspaceId: workspace.id,
          channel: "NAVER_SA",
        },
      },
      update: {
        accessToken: tokens.accessToken,
        refreshToken: tokens.refreshToken,
        status: "MOCK",
      },
      create: {
        workspaceId: workspace.id,
        channel: "NAVER_SA",
        status: "MOCK",
        accessToken: tokens.accessToken,
        refreshToken: tokens.refreshToken,
      },
    });

    return NextResponse.json({ success: true, status: "MOCK" });
  } catch (error) {
    console.error("Naver connect error:", error);
    return NextResponse.json(
      { error: "Failed to save Naver SA credentials" },
      { status: 500 }
    );
  }
}
