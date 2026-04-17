import { auth } from "@/auth";
import { NextResponse } from "next/server";

const DEMO_MODE = process.env.NEXT_PUBLIC_DEMO_MODE === "true";

export const middleware = auth((req) => {
  // Demo mode: skip all auth checks — pages use mock data
  if (DEMO_MODE) {
    return NextResponse.next();
  }

  // Protect dashboard, settings, and onboarding routes
  const protectedPaths = [
    "/dashboard",
    "/settings",
    "/onboarding",
  ];

  const isProtectedPath = protectedPaths.some((path) =>
    req.nextUrl.pathname.startsWith(path)
  );

  if (isProtectedPath && !req.auth) {
    const loginUrl = new URL("/login", req.nextUrl.origin);
    loginUrl.searchParams.set("callbackUrl", req.nextUrl.pathname);
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
});

export const config = {
  matcher: [
    "/dashboard/:path*",
    "/settings/:path*",
    "/onboarding/:path*",
    "/api/dashboard/:path*",
    "/api/channels/:path*",
    "/api/insights/:path*",
  ],
};
