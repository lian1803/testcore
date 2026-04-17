"use client";

import { useState } from "react";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import {
  Zap, ArrowRight, Check, Eye, EyeOff,
  BarChart3, Brain, LayoutDashboard,
} from "lucide-react";

/* ─── Types ──────────────────────────────────────────── */
type Step = 1 | 2 | 3 | 4;
type ConnState = "idle" | "connecting" | "done";

/* ─── Data ───────────────────────────────────────────── */
const channels = [
  {
    id: "ga4",
    name: "Google Analytics 4",
    abbr: "GA4",
    color: "#E37400",
    bg: "rgba(227,116,0,0.12)",
    desc: "웹사이트 트래픽 · 사용자 행동 · 전환 추적",
  },
  {
    id: "meta",
    name: "Meta (Facebook + Instagram)",
    abbr: "Meta",
    color: "#1877F2",
    bg: "rgba(24,119,242,0.12)",
    desc: "페이스북 · 인스타그램 광고 성과 분석",
  },
  {
    id: "naver",
    name: "네이버 서치애드",
    abbr: "네이버SA",
    color: "#03C75A",
    bg: "rgba(3,199,90,0.12)",
    desc: "네이버 검색광고 입찰 · 키워드 · 전환 분석",
  },
];

/* ─── Side previews per step ────────────────────────── */
const stepPreviews = [
  {
    title: "마케팅 인텔리전스",
    desc: "한국 마케터를 위한 유일한 통합 데이터 플랫폼",
    visual: (
      <div className="w-full rounded-xl border border-white/8 overflow-hidden"
        style={{ background: "rgba(255,255,255,0.03)" }}>
        <div className="p-4 border-b border-white/6">
          <div className="flex items-center gap-2 mb-3">
            <div className="w-5 h-5 bg-white rounded flex items-center justify-center">
              <Zap className="w-3 h-3 text-black" />
            </div>
            <span className="text-xs font-bold text-white">Lian Dash</span>
          </div>
          <div className="grid grid-cols-3 gap-2">
            {[
              { l: "GA4", v: "12.4K", c: "#E37400" },
              { l: "메타", v: "3.8x", c: "#1877F2" },
              { l: "네이버", v: "842", c: "#03C75A" },
            ].map((k) => (
              <div key={k.l} className="rounded-lg p-2 border border-white/6"
                style={{ background: "rgba(255,255,255,0.04)" }}>
                <div className="w-1.5 h-1.5 rounded-full mb-1.5" style={{ background: k.c }} />
                <p className="text-[9px] text-zinc-500">{k.l}</p>
                <p className="text-xs font-bold text-white font-mono">{k.v}</p>
              </div>
            ))}
          </div>
        </div>
        <div className="p-4">
          <div className="flex items-center gap-2 mb-2">
            <Brain className="w-3.5 h-3.5 text-zinc-400" />
            <span className="text-[10px] text-zinc-400 font-semibold uppercase tracking-wider">AI 인사이트</span>
          </div>
          <p className="text-[11px] text-zinc-400 leading-relaxed">
            &ldquo;네이버SA CTR이 지난주 대비 12% 하락. 상위 5개 키워드 입찰가 조정을 권장합니다.&rdquo;
          </p>
        </div>
      </div>
    ),
  },
  {
    title: "빠른 시작",
    desc: "워크스페이스 이름을 설정하면 맞춤 환경이 준비됩니다",
    visual: (
      <div className="w-full rounded-xl border border-white/8 p-4"
        style={{ background: "rgba(255,255,255,0.03)" }}>
        <div className="flex items-center gap-2 mb-4">
          <LayoutDashboard className="w-4 h-4 text-zinc-400" />
          <span className="text-xs font-semibold text-zinc-300">워크스페이스 미리보기</span>
        </div>
        {["클라이언트 A", "클라이언트 B", "자사몰"].map((ws, i) => (
          <div key={ws} className={`flex items-center gap-3 p-2.5 rounded-lg mb-2 border ${i === 0 ? "border-white/15 bg-white/6" : "border-white/5"}`}>
            <div className="w-6 h-6 rounded-md flex items-center justify-center text-[10px] font-bold text-white"
              style={{ background: `hsl(${i * 120}, 60%, 30%)` }}>
              {ws[0]}
            </div>
            <span className="text-xs text-zinc-300">{ws}</span>
            {i === 0 && <span className="ml-auto text-[9px] text-zinc-500 bg-white/8 px-2 py-0.5 rounded-full">활성</span>}
          </div>
        ))}
      </div>
    ),
  },
  {
    title: "채널 연결",
    desc: "OAuth로 안전하게 연동. 데이터는 암호화됩니다",
    visual: (
      <div className="w-full space-y-3">
        {channels.map((ch) => (
          <div key={ch.id} className="flex items-center gap-3 p-3 rounded-xl border border-white/7"
            style={{ background: "rgba(255,255,255,0.03)" }}>
            <div className="w-8 h-8 rounded-lg flex items-center justify-center text-[10px] font-bold text-white"
              style={{ background: ch.bg, border: `1px solid ${ch.color}30` }}>
              {ch.abbr[0]}
            </div>
            <div className="flex-1">
              <p className="text-xs font-semibold text-white">{ch.name}</p>
              <p className="text-[9px] text-zinc-500 mt-0.5">{ch.desc}</p>
            </div>
            <div className="w-4 h-4 rounded-full border border-white/15" />
          </div>
        ))}
      </div>
    ),
  },
  {
    title: "준비 완료!",
    desc: "대시보드에서 실시간 데이터를 확인하세요",
    visual: (
      <div className="w-full rounded-xl border border-white/8 overflow-hidden"
        style={{ background: "rgba(255,255,255,0.03)" }}>
        <div className="p-4 flex flex-col items-center justify-center gap-3">
          <div className="w-14 h-14 rounded-2xl bg-white/10 flex items-center justify-center animate-pulse">
            <BarChart3 className="w-7 h-7 text-white" />
          </div>
          <p className="text-sm font-bold text-white">데이터 수집 중...</p>
          <div className="w-full bg-white/8 rounded-full h-1.5 overflow-hidden">
            <motion.div className="h-full rounded-full bg-white"
              initial={{ width: "0%" }} animate={{ width: "80%" }}
              transition={{ duration: 2, ease: "easeOut" }} />
          </div>
          <p className="text-[10px] text-zinc-500">평균 5-10분 소요됩니다</p>
        </div>
      </div>
    ),
  },
];

const slideVariants = {
  enter: (d: number) => ({ opacity: 0, x: d > 0 ? 40 : -40 }),
  center: { opacity: 1, x: 0 },
  exit:  (d: number) => ({ opacity: 0, x: d > 0 ? -40 : 40 }),
};

/* ─── Input component ───────────────────────────────── */
function Input({
  label, type = "text", placeholder, value, onChange, right,
}: {
  label: string; type?: string; placeholder: string;
  value: string; onChange: (v: string) => void; right?: React.ReactNode;
}) {
  return (
    <div>
      <label className="block text-xs font-semibold text-zinc-400 mb-2 uppercase tracking-wider">{label}</label>
      <div className="relative">
        <input
          type={type}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3.5 text-sm text-white placeholder:text-zinc-600
            focus:outline-none focus:border-white/30 focus:bg-white/8 transition-all"
        />
        {right && <div className="absolute right-3.5 top-1/2 -translate-y-1/2">{right}</div>}
      </div>
    </div>
  );
}

/* ─── Page ───────────────────────────────────────────── */
export default function OnboardingPage() {
  const [step, setStep]       = useState<Step>(1);
  const [dir, setDir]         = useState(1);
  const [showPw, setShowPw]   = useState(false);

  /* Form state */
  const [email, setEmail]       = useState("");
  const [name, setName]         = useState("");
  const [password, setPassword] = useState("");
  const [workspace, setWorkspace] = useState("");

  /* Channel connect state */
  const [connState, setConnState] = useState<Record<string, ConnState>>({
    ga4: "idle", meta: "idle", naver: "idle",
  });

  const preview = stepPreviews[step - 1];

  const go = (next: Step) => {
    setDir(next > step ? 1 : -1);
    setStep(next);
  };

  const handleConnect = async (id: string) => {
    setConnState((p) => ({ ...p, [id]: "connecting" }));
    await new Promise((r) => setTimeout(r, 1800));
    setConnState((p) => ({ ...p, [id]: "done" }));
  };

  const doneCount = Object.values(connState).filter((s) => s === "done").length;

  return (
    <div className="min-h-screen flex" style={{ background: "var(--bg-base)" }}>

      {/* ── Left panel ───────────────────────────────── */}
      <div className="hidden lg:flex w-[420px] xl:w-[480px] shrink-0 flex-col justify-between p-10 border-r relative overflow-hidden"
        style={{ borderColor: "var(--border-subtle)", background: "var(--bg-surface)" }}>
        {/* Ambient */}
        <div className="absolute inset-0 pointer-events-none"
          style={{ background: "radial-gradient(ellipse 60% 50% at 50% 0%, rgba(255,255,255,0.04) 0%, transparent 70%)" }} />

        {/* Logo */}
        <div className="relative z-10 flex items-center gap-2.5">
          <div className="w-7 h-7 bg-white rounded-lg flex items-center justify-center">
            <Zap className="w-4 h-4 text-black" />
          </div>
          <span className="font-bold text-white tracking-tight">Lian Dash</span>
        </div>

        {/* Preview */}
        <div className="relative z-10 flex-1 flex flex-col justify-center py-12">
          <AnimatePresence mode="wait" custom={dir}>
            <motion.div key={step}
              custom={dir}
              variants={slideVariants}
              initial="enter" animate="center" exit="exit"
              transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}>
              <p className="text-xs font-mono uppercase tracking-widest text-zinc-500 mb-3">
                {`단계 ${step} / 4`}
              </p>
              <h3 className="text-xl font-bold text-white mb-2">{preview.title}</h3>
              <p className="text-sm text-zinc-400 mb-8 leading-relaxed">{preview.desc}</p>
              {preview.visual}
            </motion.div>
          </AnimatePresence>
        </div>

        {/* Step dots */}
        <div className="relative z-10 flex items-center gap-2">
          {([1, 2, 3, 4] as Step[]).map((s) => (
            <div key={s}
              className={`step-dot ${s < step ? "done" : s === step ? "active" : ""}`} />
          ))}
          <span className="ml-auto text-xs text-zinc-600 font-mono">
            {Math.round(((step - 1) / 3) * 100)}% 완료
          </span>
        </div>
      </div>

      {/* ── Right panel (form) ───────────────────────── */}
      <div className="flex-1 flex items-center justify-center px-6 py-12">
        <div className="w-full max-w-md">
          {/* Mobile logo */}
          <div className="flex items-center gap-2 mb-10 lg:hidden">
            <div className="w-7 h-7 bg-white rounded-lg flex items-center justify-center">
              <Zap className="w-4 h-4 text-black" />
            </div>
            <span className="font-bold text-white">Lian Dash</span>
          </div>

          <AnimatePresence mode="wait" custom={dir}>
            <motion.div key={step}
              custom={dir}
              variants={slideVariants}
              initial="enter" animate="center" exit="exit"
              transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}>

              {/* ── Step 1: Account ── */}
              {step === 1 && (
                <div className="space-y-6">
                  <div>
                    <h2 className="text-2xl font-bold text-white mb-1">계정 만들기</h2>
                    <p className="text-zinc-500 text-sm">14일 무료 체험. 신용카드 불필요.</p>
                  </div>

                  <div className="space-y-4">
                    <Input label="이름" placeholder="홍길동" value={name} onChange={setName} />
                    <Input label="이메일" type="email" placeholder="hong@company.com" value={email} onChange={setEmail} />
                    <Input
                      label="비밀번호"
                      type={showPw ? "text" : "password"}
                      placeholder="8자 이상"
                      value={password}
                      onChange={setPassword}
                      right={
                        <button type="button" onClick={() => setShowPw(!showPw)}
                          className="text-zinc-500 hover:text-zinc-300 transition-colors">
                          {showPw ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                        </button>
                      }
                    />
                  </div>

                  <button
                    onClick={() => go(2)}
                    disabled={!name || !email || password.length < 8}
                    className="shimmer-btn w-full bg-white text-black py-3.5 rounded-xl font-semibold text-sm
                      flex items-center justify-center gap-2 group hover:bg-zinc-100 transition-all
                      disabled:opacity-30 disabled:cursor-not-allowed">
                    계속하기
                    <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
                  </button>

                  <p className="text-center text-xs text-zinc-600">
                    이미 계정이 있나요?{" "}
                    <a href="#" className="text-zinc-300 hover:text-white transition-colors">로그인</a>
                  </p>

                  <div className="relative flex items-center gap-4">
                    <div className="flex-1 h-px" style={{ background: "var(--border-subtle)" }} />
                    <span className="text-xs text-zinc-600">또는</span>
                    <div className="flex-1 h-px" style={{ background: "var(--border-subtle)" }} />
                  </div>

                  <button className="w-full py-3.5 rounded-xl border border-white/10 text-sm text-zinc-300 font-medium
                    flex items-center justify-center gap-3 hover:bg-white/5 transition-all">
                    <svg className="w-4 h-4" viewBox="0 0 24 24">
                      <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                      <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                      <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
                      <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
                    </svg>
                    Google로 계속하기
                  </button>
                </div>
              )}

              {/* ── Step 2: Workspace ── */}
              {step === 2 && (
                <div className="space-y-6">
                  <div>
                    <h2 className="text-2xl font-bold text-white mb-1">워크스페이스 설정</h2>
                    <p className="text-zinc-500 text-sm">나중에 언제든지 변경할 수 있습니다.</p>
                  </div>

                  <Input
                    label="워크스페이스 이름"
                    placeholder="예: 홍길동 마케팅 / ABC 에이전시"
                    value={workspace}
                    onChange={setWorkspace}
                  />

                  <div className="space-y-2">
                    <p className="text-xs font-semibold text-zinc-400 uppercase tracking-wider">역할 선택</p>
                    {["인하우스 마케터", "프리랜서 마케터", "마케팅 에이전시"].map((role, i) => (
                      <button key={role}
                        className={`w-full text-left px-4 py-3.5 rounded-xl border text-sm font-medium transition-all ${
                          i === 0
                            ? "border-white/25 bg-white/8 text-white"
                            : "border-white/7 text-zinc-400 hover:border-white/15 hover:text-zinc-200"
                        }`}>
                        {role}
                      </button>
                    ))}
                  </div>

                  <button
                    onClick={() => go(3)}
                    disabled={!workspace}
                    className="shimmer-btn w-full bg-white text-black py-3.5 rounded-xl font-semibold text-sm
                      flex items-center justify-center gap-2 group hover:bg-zinc-100 transition-all
                      disabled:opacity-30 disabled:cursor-not-allowed">
                    다음
                    <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
                  </button>
                  <button onClick={() => go(1)}
                    className="w-full text-center text-xs text-zinc-600 hover:text-zinc-400 transition-colors">
                    ← 이전 단계
                  </button>
                </div>
              )}

              {/* ── Step 3: Channel connect ── */}
              {step === 3 && (
                <div className="space-y-6">
                  <div>
                    <h2 className="text-2xl font-bold text-white mb-1">채널 연결</h2>
                    <p className="text-zinc-500 text-sm">연결할 채널을 선택하세요. 나중에 추가할 수도 있습니다.</p>
                  </div>

                  <div className="space-y-3">
                    {channels.map((ch) => {
                      const state = connState[ch.id];
                      return (
                        <div key={ch.id}
                          className="flex items-center gap-4 p-4 rounded-xl border transition-all"
                          style={{
                            borderColor: state === "done" ? `${ch.color}50` : "rgba(255,255,255,0.08)",
                            background: state === "done" ? `${ch.color}08` : "rgba(255,255,255,0.03)",
                          }}>
                          {/* Icon */}
                          <div className="w-10 h-10 rounded-xl flex items-center justify-center font-bold text-xs text-white shrink-0"
                            style={{ background: ch.bg, border: `1px solid ${ch.color}30` }}>
                            {ch.abbr[0]}
                          </div>
                          {/* Info */}
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-semibold text-white">{ch.name}</p>
                            <p className="text-xs text-zinc-500 mt-0.5 truncate">{ch.desc}</p>
                          </div>
                          {/* Action */}
                          {state === "idle" && (
                            <button onClick={() => handleConnect(ch.id)}
                              className="px-4 py-2 rounded-lg border border-white/15 text-xs font-semibold text-white
                                hover:bg-white/10 transition-all shrink-0">
                              연결
                            </button>
                          )}
                          {state === "connecting" && (
                            <div className="w-5 h-5 rounded-full border-2 border-zinc-600 border-t-white animate-spin shrink-0" />
                          )}
                          {state === "done" && (
                            <motion.div
                              initial={{ scale: 0 }} animate={{ scale: 1 }}
                              className="w-6 h-6 rounded-full flex items-center justify-center shrink-0"
                              style={{ background: ch.color }}>
                              <Check className="w-3.5 h-3.5 text-white" strokeWidth={3} />
                            </motion.div>
                          )}
                        </div>
                      );
                    })}
                  </div>

                  {doneCount > 0 && (
                    <motion.button
                      initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
                      onClick={() => go(4)}
                      className="shimmer-btn w-full bg-white text-black py-3.5 rounded-xl font-semibold text-sm
                        flex items-center justify-center gap-2 group hover:bg-zinc-100 transition-all">
                      {doneCount}개 채널로 시작하기
                      <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
                    </motion.button>
                  )}
                  <Link href="/dashboard"
                    className="block text-center text-xs text-zinc-600 hover:text-zinc-400 transition-colors">
                    건너뛰고 대시보드로 →
                  </Link>
                </div>
              )}

              {/* ── Step 4: Done ── */}
              {step === 4 && (
                <div className="space-y-6 text-center">
                  <motion.div
                    initial={{ scale: 0.5, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    transition={{ type: "spring", stiffness: 200, damping: 15 }}
                    className="w-20 h-20 rounded-3xl bg-white/10 border border-white/15 flex items-center justify-center mx-auto glow-white">
                    <Check className="w-10 h-10 text-white" strokeWidth={2.5} />
                  </motion.div>

                  <div>
                    <h2 className="text-2xl font-bold text-white mb-2">준비 완료!</h2>
                    <p className="text-zinc-400 text-sm leading-relaxed">
                      {doneCount > 0
                        ? `${doneCount}개 채널이 연결됐습니다. 데이터 수집이 시작됐어요.`
                        : "대시보드에서 채널을 연결하고 분석을 시작하세요."}
                    </p>
                  </div>

                  {/* Connected channels summary */}
                  {doneCount > 0 && (
                    <div className="flex justify-center gap-2">
                      {channels.filter((c) => connState[c.id] === "done").map((ch) => (
                        <div key={ch.id} className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold"
                          style={{ background: `${ch.color}15`, color: ch.color, border: `1px solid ${ch.color}30` }}>
                          <div className="w-1.5 h-1.5 rounded-full" style={{ background: ch.color }} />
                          {ch.abbr}
                        </div>
                      ))}
                    </div>
                  )}

                  <Link href="/dashboard" className="block">
                    <button className="shimmer-btn w-full bg-white text-black py-3.5 rounded-xl font-bold text-sm
                      flex items-center justify-center gap-2 group hover:bg-zinc-100 transition-all glow-white">
                      대시보드로 이동
                      <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
                    </button>
                  </Link>
                </div>
              )}

            </motion.div>
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}
