import { NextRequest, NextResponse } from "next/server";
import { auth } from "@/auth";
import { prisma } from "@/lib/prisma";

export async function checkTrialStatus(req: NextRequest) {
  const session = await auth();

  if (!session?.user?.id) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const user = await prisma.user.findUnique({
    where: { id: session.user.id },
    select: {
      planStatus: true,
      trialStartedAt: true,
    },
  });

  if (!user) {
    return NextResponse.json({ error: "User not found" }, { status: 404 });
  }

  // Check if trial expired
  const now = new Date();
  const trialEnd = new Date(user.trialStartedAt);
  trialEnd.setDate(trialEnd.getDate() + 14);

  if (user.planStatus === "TRIAL" && now > trialEnd) {
    return NextResponse.json(
      { error: "Trial expired. Please upgrade to continue." },
      { status: 402 }
    );
  }

  if (user.planStatus === "EXPIRED") {
    return NextResponse.json(
      { error: "Payment required. Please upgrade to continue." },
      { status: 402 }
    );
  }

  return null; // No error
}
