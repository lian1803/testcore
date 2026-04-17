export const dynamic = "force-dynamic";

import { NextRequest, NextResponse } from "next/server";
import { auth } from "@/auth";
import { prisma } from "@/lib/prisma";
import { GA4Adapter } from "@/lib/channels/ga4";

export async function GET(req: NextRequest) {
  try {
    const session = await auth();
    if (!session?.user?.id) {
      return NextResponse.redirect(new URL("/login", req.nextUrl.origin));
    }

    const code = req.nextUrl.searchParams.get("code");
    const state = req.nextUrl.searchParams.get("state");

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
    const tokens = await GA4Adapter.handleCallback(code);

    // Save integration
    await prisma.integration.upsert({
      where: {
        workspaceId_channel: {
          workspaceId: workspace.id,
          channel: "GA4",
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
        channel: "GA4",
        status: "CONNECTED",
        accessToken: tokens.accessToken,
        refreshToken: tokens.refreshToken,
        tokenExpiry: tokens.expiresAt,
      },
    });

    // Redirect to onboarding or dashboard
    return NextResponse.redirect(
      new URL("/onboarding?ga4=connected", req.nextUrl.origin)
    );
  } catch (error) {
    console.error("GA4 callback error:", error);
    return NextResponse.redirect(
      new URL("/onboarding?error=ga4_connection_failed", req.nextUrl.origin)
    );
  }
}
