import NextAuth from "next-auth";
import { PrismaAdapter } from "@auth/prisma-adapter";
import GoogleProvider from "next-auth/providers/google";
import { prisma } from "@/lib/prisma";

const DEMO_MODE = process.env.NEXT_PUBLIC_DEMO_MODE === "true";

declare module "next-auth" {
  interface Session {
    user: {
      id: string;
      email?: string | null;
      name?: string | null;
      image?: string | null;
      planStatus?: string;
      trialStartedAt?: Date | null;
      workspaceId?: string;
    };
  }
}


export const { handlers, auth, signIn, signOut } = NextAuth({
  adapter: DEMO_MODE ? undefined : PrismaAdapter(prisma),
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID || "demo",
      clientSecret: process.env.GOOGLE_CLIENT_SECRET || "demo",
    }),
  ],
  session: {
    strategy: "jwt",
    maxAge: 30 * 24 * 60 * 60, // 30 days
  },
  callbacks: {
    async signIn() {
      return true;
    },
    async session({ session, token }) {
      if (session.user && token) {
        session.user.id = token.sub!;
        if (!DEMO_MODE) {
          const dbUser = await prisma.user.findUnique({
            where: { id: token.sub },
            select: {
              planStatus: true,
              trialStartedAt: true,
              workspaces: { select: { id: true }, take: 1 },
            },
          });
          if (dbUser) {
            session.user.planStatus = dbUser.planStatus;
            session.user.trialStartedAt = dbUser.trialStartedAt;
            session.user.workspaceId = dbUser.workspaces[0]?.id;
          }
        }
      }
      return session;
    },
    async jwt({ token, user }) {
      if (user) token.sub = user.id;
      return token;
    },
    async redirect({ url, baseUrl }) {
      if (url.startsWith("/")) return `${baseUrl}${url}`;
      else if (new URL(url).origin === baseUrl) return url;
      return baseUrl;
    },
  },
  pages: {
    signIn: "/login",
    error: "/login",
  },
});
