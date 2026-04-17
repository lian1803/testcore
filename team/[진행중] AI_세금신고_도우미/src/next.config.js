/** @type {import('next').NextConfig} */
const nextConfig = {
  typescript: {
    ignoreBuildErrors: true,
  },
  eslint: {
    ignoreDuringBuilds: true,
  },
  // Stripe Webhook은 raw body가 필요 — bodyParser 비활성화는 Route Handler에서 처리됨
  // @react-pdf/renderer 서버사이드 렌더링 지원
  experimental: {
    serverComponentsExternalPackages: ["@react-pdf/renderer"],
  },
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "*.s3.ap-northeast-2.amazonaws.com",
        pathname: "/receipts/**",
      },
      {
        protocol: "https",
        hostname: "lh3.googleusercontent.com", // Google OAuth 프로필 이미지
      },
    ],
  },
};

module.exports = nextConfig;
