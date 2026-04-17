"use client";

import Link from "next/link";
import { motion, useScroll, useTransform } from "framer-motion";
import { ArrowRight, BarChart3, Shield, Network, CheckCircle, Zap, Users, TrendingUp, Brain, Sparkles } from "lucide-react";
import { useRef } from "react";
import dynamic from "next/dynamic";

const HeroScene = dynamic(() => import("./components/HeroScene"), {
  ssr: false,
  loading: () => <div className="absolute inset-0" />,
});
const ProblemScene3D = dynamic(() => import("./components/ProblemScene3D"), {
  ssr: false,
  loading: () => <div className="absolute inset-0" />,
});
const DataWaveScene3D = dynamic(() => import("./components/DataWaveScene3D"), {
  ssr: false,
  loading: () => <div className="absolute inset-0" />,
});
const PricingScene3D = dynamic(() => import("./components/PricingScene3D"), {
  ssr: false,
  loading: () => <div className="absolute inset-0" />,
});
const CTAScene3D = dynamic(() => import("./components/CTAScene3D"), {
  ssr: false,
  loading: () => <div className="absolute inset-0" />,
});

/* ─── Animation variants ──────────────────────────────────────── */
const fadeUp = {
  hidden: { opacity: 0, y: 32 },
  visible: (i: number = 0) => ({
    opacity: 1,
    y: 0,
    transition: { duration: 0.65, delay: i * 0.1, ease: [0.16, 1, 0.3, 1] },
  }),
};

const stagger = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.09 } },
};

const scaleIn = {
  hidden: { opacity: 0, scale: 0.92 },
  visible: (i: number = 0) => ({
    opacity: 1,
    scale: 1,
    transition: { duration: 0.55, delay: i * 0.1, ease: [0.16, 1, 0.3, 1] },
  }),
};

/* ─── Features Bento Data ─────────────────────────────────────── */
const features = [
  {
    icon: Sparkles,
    title: "AI 자동 인사이트",
    desc: '"이번 주 네이버SA CTR이 12% 하락했습니다. 키워드 입찰가를 점검하세요." GPT-4o가 매일 아침 3가지 액션 포인트를 자동 생성합니다.',
    span: "md:col-span-2",
    colorClass: "bento-violet",
    accentClass: "bento-card-accent-violet",
  },
  {
    icon: BarChart3,
    title: "실시간 채널 통합",
    desc: "GA4·메타·네이버SA를 단 하나의 화면에서. 지연 없이.",
    span: "md:col-span-1",
    colorClass: "bento-meta",
    accentClass: "bento-card-accent-meta",
  },
  {
    icon: Shield,
    title: "엔터프라이즈 보안",
    desc: "클라이언트별 완전 격리된 워크스페이스. 데이터 혼합 없음.",
    span: "md:col-span-1",
    colorClass: "bento-naver",
    accentClass: "bento-card-accent-naver",
  },
  {
    icon: Network,
    title: "한국 플랫폼 최초 지원",
    desc: "Databox·Whatagraph가 지원하지 않는 네이버SA·카카오모먼트를 최초로 통합한 국내 마케터 전용 솔루션.",
    span: "md:col-span-2",
    colorClass: "bento-ga4",
    accentClass: "bento-card-accent-ga4",
  },
];

/* ─── Social Proof ────────────────────────────────────────────── */
const stats = [
  { value: "1,200+", label: "마케터 사용 중" },
  { value: "월 4.7시간", label: "평균 시간 절약" },
  { value: "89%", label: "리포트 자동화" },
  { value: "4.9/5", label: "평점 (★★★★★)" },
];

/* ─── Pain Points ────────────────────────────────────────────── */
const painPoints = [
  { icon: BarChart3, time: "30분", label: "GA4 데이터 확인" },
  { icon: BarChart3, time: "20분", label: "메타 성과 취합" },
  { icon: BarChart3, time: "15분", label: "네이버SA 분석" },
];

/* ─── Pricing Plans ──────────────────────────────────────────── */
const pricingPlans = [
  {
    name: "Starter",
    price: 29,
    description: "개인 마케터 및 프리랜서용",
    features: [
      "GA4 + 메타 + 네이버SA 통합",
      "월 10회 AI 인사이트",
      "기본 리포팅",
      "실시간 알림",
      "이메일 지원",
    ],
    cta: "무료로 시작하기",
    popular: false,
  },
  {
    name: "Pro",
    price: 99,
    description: "팀 및 에이전시용",
    features: [
      "Starter 모든 기능",
      "무제한 AI 인사이트",
      "커스텀 리포팅",
      "2명 팀원 추가",
      "우선 지원",
      "화이트라벨 (준비 중)",
    ],
    cta: "Pro 시작하기",
    popular: true,
  },
  {
    name: "Agency",
    price: 299,
    description: "대형 에이전시용",
    features: [
      "Pro 모든 기능",
      "무제한 팀원",
      "무제한 워크스페이스",
      "커스텀 통합",
      "24/7 전용 지원",
      "SLA 보장",
    ],
    cta: "Agency 문의하기",
    popular: false,
  },
];

/* ─── Nav Bar ────────────────────────────────────────────────── */
function Navbar() {
  return (
    <header className="fixed top-0 w-full z-50 h-14 glass-nav border-b" style={{ borderColor: "var(--border-faint)" }}>
      <div className="max-w-7xl mx-auto px-6 h-full flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 bg-white rounded-lg flex items-center justify-center">
            <Zap className="w-4 h-4 text-black" />
          </div>
          <span className="font-bold text-white text-sm">Lian Dash</span>
        </div>
        <div className="flex items-center gap-3">
          <Link href="/login" className="text-sm text-zinc-400 hover:text-white transition-colors">로그인</Link>
          <Link href="/signup"
            className="px-5 py-2 rounded-lg bg-white text-black font-semibold text-sm hover:bg-zinc-100 transition-all">
            무료 시작
          </Link>
        </div>
      </div>
    </header>
  );
}

/* ─── Hero Section ───────────────────────────────────────────── */
function HeroSection() {
  return (
    <section className="relative w-full h-screen flex flex-col items-center justify-center overflow-hidden hero-bg pt-14">
      {/* 3D Background */}
      <div className="absolute inset-0 z-0">
        <HeroScene />
      </div>

      {/* Content overlay */}
      <div className="relative z-10 flex flex-col items-center justify-center h-full px-6 max-w-2xl mx-auto text-center">
        {/* Badge */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-white/10 bg-white/5 mb-8">
          <span className="text-xs font-semibold text-zinc-400">한국 마케터 최초</span>
          <div className="flex gap-1.5">
            {["GA4", "Meta", "Naver"].map((ch) => (
              <span key={ch} className="text-xs font-mono text-white/60">{ch}</span>
            ))}
          </div>
        </motion.div>

        {/* Main headline */}
        <motion.h1
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
          className="text-hero font-bold text-white mb-6 text-gradient-white leading-tight">
          마케터의 모든 데이터,<br />하나의 화면에서.
        </motion.h1>

        {/* Subheadline */}
        <motion.p
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
          className="text-lg text-zinc-300 mb-8 max-w-xl leading-relaxed">
          GA4·메타·네이버SA를 실시간으로 통합하고<br />GPT-4o가 오늘 할 일을 알려줍니다.
        </motion.p>

        {/* CTA Buttons */}
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.3, ease: [0.16, 1, 0.3, 1] }}
          className="flex flex-col sm:flex-row gap-3 items-center">
          <Link href="/signup"
            className="px-7 py-3 bg-white text-black font-semibold rounded-xl hover:bg-zinc-100 transition-all flex items-center gap-2 shimmer-btn">
            무료로 시작하기 <ArrowRight className="w-4 h-4" />
          </Link>
          <button className="px-7 py-3 border border-white/20 text-white rounded-xl hover:bg-white/5 transition-all">
            데모 보기
          </button>
        </motion.div>

        {/* Scroll hint */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.6 }}
          className="absolute bottom-8 left-1/2 -translate-x-1/2">
          <div className="flex flex-col items-center gap-2">
            <span className="text-xs text-zinc-500">스크롤</span>
            <motion.div
              animate={{ y: [0, 6, 0] }}
              transition={{ duration: 2, repeat: Infinity }}
              className="w-5 h-8 border border-white/20 rounded-full flex items-center justify-center">
              <div className="w-1 h-2 bg-white/50 rounded-full" />
            </motion.div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}

/* ─── Social Proof Bar ───────────────────────────────────────── */
function SocialProofBar() {
  return (
    <section className="w-full py-8 border-y" style={{ background: "var(--bg-surface)", borderColor: "var(--border-faint)" }}>
      <div className="max-w-7xl mx-auto px-6">
        <div className="flex flex-wrap justify-center gap-8 text-sm">
          {stats.map((stat, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 8 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              viewport={{ once: true }}
              className="flex flex-col items-center">
              <span className="text-white font-bold text-lg">{stat.value}</span>
              <span className="text-zinc-500 text-xs">{stat.label}</span>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ─── Problem Section ────────────────────────────────────────── */
function ProblemSection() {
  return (
    <section className="relative w-full py-20 overflow-hidden" style={{ background: "var(--bg-base)" }}>
      {/* 3D DNA helix — fragmented data visualization */}
      <div className="absolute right-0 top-0 w-72 h-full opacity-60 pointer-events-none hidden lg:block">
        <ProblemScene3D />
      </div>
      <div className="max-w-7xl mx-auto px-6">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="text-center mb-12">
          <h2 className="text-3xl font-bold text-white mb-4">매일 이런 짓 하고 계신가요?</h2>
          <p className="text-zinc-400">마케터들이 데이터 취합에 쓰는 시간, Lian Dash가 단 3분으로 줄여드립니다.</p>
        </motion.div>

        {/* Pain points with arrows */}
        <div className="flex flex-col md:flex-row items-center gap-4 md:gap-6 justify-center">
          {painPoints.map((pain, i) => (
            <div key={i}>
              <motion.div
                initial={{ opacity: 0, y: 16 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.15 }}
                viewport={{ once: true }}
                className="surface-card p-6 text-center">
                <div className="w-10 h-10 rounded-lg bg-white/8 flex items-center justify-center mx-auto mb-3">
                  <pain.icon className="w-5 h-5 text-zinc-400" />
                </div>
                <p className="text-sm font-semibold text-white mb-2">{pain.label}</p>
                <span className="inline-block px-2 py-1 rounded text-xs font-bold text-red-400 bg-red-400/10">{pain.time}</span>
              </motion.div>
              {i < painPoints.length - 1 && (
                <div className="hidden md:flex items-center justify-center px-4">
                  <ArrowRight className="w-4 h-4 text-zinc-600" />
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Total time waste */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          whileInView={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.4 }}
          viewport={{ once: true }}
          className="mt-8 text-center">
          <p className="text-lg font-bold text-white text-gradient-white">
            매일 1.5시간을 데이터 복붙에 씁니다
          </p>
        </motion.div>
      </div>
    </section>
  );
}

/* ─── Features Bento ─────────────────────────────────────────── */
function FeaturesSection() {
  return (
    <section className="relative w-full py-20 overflow-hidden" style={{ background: "var(--bg-base)" }}>
      {/* 3D data wave — full-width behind the bento grid */}
      <div className="absolute inset-x-0 bottom-0 h-72 opacity-40 pointer-events-none">
        <DataWaveScene3D />
      </div>
      <div className="max-w-7xl mx-auto px-6">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="text-center mb-12">
          <h2 className="text-3xl font-bold text-white">Lian Dash의 강점</h2>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {features.map((feat, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              viewport={{ once: true }}
              className={`bento-card ${feat.colorClass} ${feat.accentClass} p-8 min-h-64 flex flex-col ${feat.span}`}>
              <div className="w-10 h-10 rounded-lg bg-white/8 flex items-center justify-center mb-4">
                <feat.icon className="w-5 h-5 text-white" />
              </div>
              <h3 className="text-xl font-bold text-white mb-3">{feat.title}</h3>
              <p className="text-zinc-400 text-sm leading-relaxed flex-1">{feat.desc}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ─── Pricing Section ────────────────────────────────────────── */
function PricingSection() {
  return (
    <section className="relative w-full py-20 overflow-hidden" style={{ background: "var(--bg-base)" }}>
      {/* 3D crystalline shards floating above the pricing cards */}
      <div className="absolute inset-x-0 top-0 h-56 opacity-55 pointer-events-none">
        <PricingScene3D />
      </div>
      {/* extra top padding so content clears the 3D layer */}
      <div className="relative z-10 pt-24">
      <div className="max-w-7xl mx-auto px-6">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="text-center mb-12">
          <h2 className="text-3xl font-bold text-white mb-2">간단한 가격 정책</h2>
          <p className="text-zinc-400">모든 플랜에 14일 무료 체험 포함. 신용카드 필요 없음.</p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {pricingPlans.map((plan, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.15 }}
              viewport={{ once: true }}
              className={`surface-card p-8 flex flex-col ${plan.popular ? "md:scale-105" : ""}`}>
              {plan.popular && (
                <div className="mb-4 inline-block px-3 py-1 rounded-full text-xs font-semibold bg-white/10 text-white w-fit">
                  가장 인기
                </div>
              )}
              <h3 className="text-xl font-bold text-white mb-2">{plan.name}</h3>
              <p className="text-sm text-zinc-500 mb-4">{plan.description}</p>

              <div className="mb-6">
                <span className="text-4xl font-bold text-white">${plan.price}</span>
                <span className="text-sm text-zinc-500">/월</span>
              </div>

              <button className={`py-3 rounded-lg font-semibold mb-6 transition-all ${plan.popular ? "bg-white text-black hover:bg-zinc-100" : "border border-white/20 text-white hover:bg-white/5"}`}>
                {plan.cta}
              </button>

              <div className="space-y-3 flex-1">
                {plan.features.map((feature, j) => (
                  <div key={j} className="flex items-start gap-3">
                    <CheckCircle className="w-4 h-4 text-green-400 shrink-0 mt-0.5" />
                    <span className="text-sm text-zinc-300">{feature}</span>
                  </div>
                ))}
              </div>
            </motion.div>
          ))}
        </div>
      </div>
      </div>{/* close relative z-10 pt-24 */}
    </section>
  );
}

/* ─── Final CTA ──────────────────────────────────────────────── */
function FinalCTASection() {
  return (
    <section className="relative w-full py-20 overflow-hidden" style={{ background: "var(--bg-base)" }}>
      {/* 3D converging particles — all channels merging to one */}
      <div className="absolute inset-0 opacity-50 pointer-events-none">
        <CTAScene3D />
      </div>
      <div className="relative z-10 max-w-2xl mx-auto px-6 text-center">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}>
          <h2 className="text-4xl font-bold text-white mb-4">모든 채널을 하나로.</h2>
          <p className="text-lg text-zinc-400 mb-8">지금 바로 시작하세요.</p>

          <Link href="/signup"
            className="inline-block px-8 py-4 bg-white text-black font-semibold rounded-xl hover:bg-zinc-100 transition-all mb-4 shimmer-btn">
            14일 무료 체험 시작 →
          </Link>

          <p className="text-sm text-zinc-500">신용카드 필요 없음 · 설치 불필요 · 5분 셋업</p>
        </motion.div>
      </div>
    </section>
  );
}

/* ─── Footer ─────────────────────────────────────────────────── */
function Footer() {
  return (
    <footer className="w-full py-12 border-t" style={{ background: "var(--bg-surface)", borderColor: "var(--border-faint)" }}>
      <div className="max-w-7xl mx-auto px-6">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-8">
          <div>
            <p className="text-xs font-semibold text-white mb-4 uppercase">Product</p>
            <ul className="space-y-2 text-sm text-zinc-500">
              <li><Link href="#" className="hover:text-white transition">Features</Link></li>
              <li><Link href="#" className="hover:text-white transition">Pricing</Link></li>
              <li><Link href="#" className="hover:text-white transition">Docs</Link></li>
            </ul>
          </div>
          <div>
            <p className="text-xs font-semibold text-white mb-4 uppercase">Company</p>
            <ul className="space-y-2 text-sm text-zinc-500">
              <li><Link href="#" className="hover:text-white transition">About</Link></li>
              <li><Link href="#" className="hover:text-white transition">Blog</Link></li>
              <li><Link href="#" className="hover:text-white transition">Careers</Link></li>
            </ul>
          </div>
          <div>
            <p className="text-xs font-semibold text-white mb-4 uppercase">Legal</p>
            <ul className="space-y-2 text-sm text-zinc-500">
              <li><Link href="#" className="hover:text-white transition">Privacy</Link></li>
              <li><Link href="#" className="hover:text-white transition">Terms</Link></li>
            </ul>
          </div>
          <div>
            <p className="text-xs font-semibold text-white mb-4 uppercase">Social</p>
            <ul className="space-y-2 text-sm text-zinc-500">
              <li><Link href="#" className="hover:text-white transition">Twitter</Link></li>
              <li><Link href="#" className="hover:text-white transition">GitHub</Link></li>
            </ul>
          </div>
        </div>

        <div className="border-t pt-8" style={{ borderColor: "var(--border-faint)" }}>
          <p className="text-sm text-zinc-600 text-center">© 2026 Lian Dash. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
}

/* ─── Main Page ──────────────────────────────────────────────── */
export default function HomePage() {
  return (
    <div className="w-full overflow-hidden" style={{ background: "var(--bg-base)", color: "var(--text-primary)" }}>
      <Navbar />
      <HeroSection />
      <SocialProofBar />
      <ProblemSection />
      <FeaturesSection />
      <PricingSection />
      <FinalCTASection />
      <Footer />
    </div>
  );
}
