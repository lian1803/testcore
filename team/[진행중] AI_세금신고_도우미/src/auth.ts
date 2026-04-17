import NextAuth from "next-auth";
import { PrismaAdapter } from "@auth/prisma-adapter";
import GoogleProvider from "next-auth/providers/google";
import CredentialsProvider from "next-auth/providers/credentials";
import bcrypt from "bcryptjs";
import { prisma } from "@/lib/prisma";

export const { handlers, auth, signIn, signOut } = NextAuth({
  adapter: PrismaAdapter(prisma),
  session: {
    strategy: "jwt",
    maxAge: 30 * 24 * 60 * 60, // 30일
  },
  pages: {
    signIn: "/login",
    newUser: "/onboarding",
    error: "/login",
  },
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
      profile(profile) {
        return {
          id: profile.sub,
          name: profile.name,
          email: profile.email,
          image: profile.picture,
          emailVerified: new Date(),
        };
      },
    }),
    CredentialsProvider({
      name: "credentials",
      credentials: {
        email: { label: "이메일", type: "email" },
        password: { label: "비밀번호", type: "password" },
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) {
          return null;
        }

        const user = await prisma.user.findUnique({
          where: { email: credentials.email as string },
          select: {
            id: true,
            email: true,
            name: true,
            image: true,
            passwordHash: true,
            planStatus: true,
            emailVerified: true,
          },
        });

        if (!user || !user.passwordHash) {
          return null;
        }

        const isValid = await bcrypt.compare(
          credentials.password as string,
          user.passwordHash
        );

        if (!isValid) {
          return null;
        }

        return {
          id: user.id,
          email: user.email,
          name: user.name,
          image: user.image,
          planStatus: user.planStatus,
        };
      },
    }),
  ],
  callbacks: {
    async jwt({ token, user, trigger }) {
      // 최초 로그인 시 DB에서 planStatus 로드
      if (user) {
        token.userId = user.id;
        token.planStatus = (user as { planStatus?: string }).planStatus ?? "FREE";
      }
      // 세션 업데이트 트리거 시 DB에서 최신 정보 재조회
      if (trigger === "update") {
        const dbUser = await prisma.user.findUnique({
          where: { id: token.userId as string },
          select: { planStatus: true },
        });
        if (dbUser) {
          token.planStatus = dbUser.planStatus;
        }
      }
      return token;
    },
    async session({ session, token }) {
      if (session.user) {
        session.user.id = token.userId as string;
        (session.user as { planStatus?: string }).planStatus =
          token.planStatus as string;
      }
      return session;
    },
  },
  events: {
    // 소셜 로그인으로 신규 가입 시 이메일 인증 완료 처리
    async createUser({ user }) {
      if (user.email) {
        await prisma.user.update({
          where: { id: user.id! },
          data: { emailVerified: new Date() },
        });
      }
    },
  },
});
