import { auth } from "@/auth";
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

// 인증 없이 접근 가능한 경로
const PUBLIC_ROUTES = [
  "/",
  "/login",
  "/signup",
  "/forgot-password",
  "/reset-password",
];

// API 경로 중 인증 불필요한 것
const PUBLIC_API_ROUTES = [
  "/api/auth",        // NextAuth 핸들러
  "/api/webhooks",    // Stripe Webhook (Stripe 서명 검증으로 보호)
];

export default auth((req: NextRequest & { auth?: unknown }) => {
  const { pathname } = req.nextUrl;
  const session = (req as { auth?: { user?: { id?: string } } }).auth;

  // Public API routes — pass through
  if (PUBLIC_API_ROUTES.some((route) => pathname.startsWith(route))) {
    return NextResponse.next();
  }

  // API routes — 401 반환 (미인증 시)
  if (pathname.startsWith("/api/")) {
    if (!session?.user?.id) {
      return NextResponse.json(
        {
          type: "https://httpstatuses.com/401",
          title: "UnauthorizedError",
          status: 401,
          detail: "인증이 필요합니다.",
        },
        { status: 401 }
      );
    }
    return NextResponse.next();
  }

  // Public pages — pass through
  if (PUBLIC_ROUTES.includes(pathname)) {
    // 이미 로그인한 사용자가 로그인/회원가입 페이지 접근 시 대시보드로 리다이렉트
    if (session?.user?.id && (pathname === "/login" || pathname === "/signup")) {
      return NextResponse.redirect(new URL("/dashboard", req.url));
    }
    return NextResponse.next();
  }

  // Onboarding — 인증 필요
  if (pathname.startsWith("/onboarding")) {
    if (!session?.user?.id) {
      const loginUrl = new URL("/login", req.url);
      loginUrl.searchParams.set("callbackUrl", pathname);
      return NextResponse.redirect(loginUrl);
    }
    return NextResponse.next();
  }

  // Dashboard and protected pages — 인증 필요
  if (pathname.startsWith("/dashboard") || pathname.startsWith("/settings")) {
    if (!session?.user?.id) {
      const loginUrl = new URL("/login", req.url);
      loginUrl.searchParams.set("callbackUrl", pathname);
      return NextResponse.redirect(loginUrl);
    }
    return NextResponse.next();
  }

  return NextResponse.next();
});

export const config = {
  matcher: [
    /*
     * Match all request paths except for:
     * - _next/static (static files)
     * - _next/image (image optimization)
     * - favicon.ico, sitemap.xml, robots.txt
     * - public folder
     */
    "/((?!_next/static|_next/image|favicon.ico|sitemap.xml|robots.txt|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)",
  ],
};
