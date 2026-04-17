export const dynamic = "force-dynamic";

import { NextRequest, NextResponse } from "next/server";
import { auth } from "@/auth";
import { prisma } from "@/lib/prisma";
import { MetaAdapter } from "@/lib/channels/meta";

export async function GET(req: NextRequest) {
  try {
    const session = await auth();
    if (!session?.user?.id) {
      return NextResponse.redirect(new URL("/login", req.nextUrl.origin));
    }

    const code = req.nextUrl.searchParams.get("code");
    const error = req.nextUrl.searchParams.get("error");

    if (error) {
      return NextResponse.redirect(
        new URL(`/onboarding?error=meta_${error}`, req.nextUrl.origin)
      );
    }

    if (!code) {
      return NextResponse.json({ error: "No authorization code" }, { status: 400 });
    }

    // Get workspace
    const workspace = await prisma.workspace.findFirst({
      where: { userId: session.user.id },
    });

    if (!workspace) {
      return NextResponse.json({ error: "Workspace not found" }, { status: 404 });
    }

    // Exchange code for tokens
    const tokens = await MetaAdapter.handleCallback(code);

    // Save integration
    await prisma.integration.upsert({
      where: {
        workspaceId_channel: {
          workspaceId: workspace.id,
          channel: "META",
        },
      },
      update: {
        accessToken: tokens.accessToken,
        refreshToken: tokens.refreshToken,
        tokenExpiry: tokens.expiresAt,
        status: "CONNECTED",
      },
      create: {
        workspaceId: workspace.id,
        channel: "META",
        status: "CONNECTED",
        accessToken: tokens.accessToken,
        refreshToken: tokens.refreshToken,
        tokenExpiry: tokens.expiresAt,
      },
    });

    return NextResponse.redirect(
      new URL("/onboarding?meta=connected", req.nextUrl.origin)
    );
  } catch (error) {
    console.error("Meta callback error:", error);
    return NextResponse.redirect(
      new URL("/onboarding?error=meta_connection_failed", req.nextUrl.origin)
    );
  }
}
