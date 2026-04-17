import type { Metadata } from "next";
import "./globals.css";
import { QueryProvider } from "@/providers/query-provider";

export const metadata: Metadata = {
  title: "세금신고 도우미 — 1인 사업자·프리랜서 AI 절세 파트너",
  description:
    "영수증 사진 한 장으로 경비 자동 분류, 종합소득세 신고서 초안 자동 생성. 세무사 없이 혼자 신고하는 1인 사업자·프리랜서를 위한 AI 세금 신고 준비 도구.",
  keywords: ["종합소득세", "신고서", "프리랜서", "1인 사업자", "경비 분류", "OCR", "절세"],
  openGraph: {
    title: "세금신고 도우미",
    description: "영수증 찍으면 세금신고 끝. AI가 경비를 자동 분류하고 신고서 초안을 만들어드려요.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ko">
      <body>
        <QueryProvider>{children}</QueryProvider>
      </body>
    </html>
  );
}
