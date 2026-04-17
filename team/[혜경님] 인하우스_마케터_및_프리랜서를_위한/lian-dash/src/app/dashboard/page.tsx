"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  TrendingUp, TrendingDown, Brain, Download, Search, RefreshCw, X, ChevronRight, Sparkles,
} from "lucide-react";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend, AreaChart, Area,
} from "recharts";
import { toast } from "sonner";

/* ─── Mock Data ───────────────────────────────────────────────── */
const kpiDataByFilter = {
  today: {
    totalSpend: { label: "총 광고비", value: "₩3,240,000", change: 3 },
    totalConversions: { label: "총 전환", value: "2,840", change: 8 },
    roas: { label: "ROAS", value: "3.8x", change: 5 },
    cpa: { label: "CPA", value: "₩1,140", change: -3 },
    ctr: { label: "CTR", value: "3.2%", change: 2 },
    totalClicks: { label: "총 클릭", value: "42.8K", change: 4 },
  },
  "7d": {
    totalSpend: { label: "총 광고비", value: "₩21,450,000", change: 5 },
    totalConversions: { label: "총 전환", value: "18,240", change: 12 },
    roas: { label: "ROAS", value: "3.6x", change: 2 },
    cpa: { label: "CPA", value: "₩1,175", change: 1 },
    ctr: { label: "CTR", value: "3.1%", change: -1 },
    totalClicks: { label: "총 클릭", value: "298.5K", change: 8 },
  },
  "30d": {
    totalSpend: { label: "총 광고비", value: "₩87,600,000", change: 7 },
    totalConversions: { label: "총 전환", value: "71,800", change: 15 },
    roas: { label: "ROAS", value: "3.4x", change: -2 },
    cpa: { label: "CPA", value: "₩1,219", change: 4 },
    ctr: { label: "CTR", value: "3.0%", change: 1 },
    totalClicks: { label: "총 클릭", value: "1.2M", change: 10 },
  },
};

const chartData = [
  { date: "1/1", ga4: 2400, meta: 2210, naver: 1200 },
  { date: "1/2", ga4: 3398, meta: 2290, naver: 1398 },
  { date: "1/3", ga4: 2800, meta: 1908, naver: 1398 },
  { date: "1/4", ga4: 2780, meta: 2800, naver: 968 },
  { date: "1/5", ga4: 1890, meta: 2390, naver: 1800 },
  { date: "1/6", ga4: 2390, meta: 2410, naver: 1891 },
  { date: "1/7", ga4: 3490, meta: 2100, naver: 2100 },
];

const pieData = [
  { name: "GA4", value: 45, color: "#E37400" },
  { name: "메타", value: 35, color: "#1877F2" },
  { name: "네이버SA", value: 20, color: "#03C75A" },
];

const channelPerformance = [
  { channel: "ga4", label: "GA4", spend: "₩8.4M", roas: "4.2x", clicks: "185.2K", conversions: "45.8K" },
  { channel: "meta", label: "메타", spend: "₩7.2M", roas: "3.1x", clicks: "92.5K", conversions: "18.3K" },
  { channel: "naver", label: "네이버SA", spend: "₩2.8M", roas: "2.9x", clicks: "38.6K", conversions: "7.3K" },
];

const channelColors: Record<string, string> = {
  ga4: "#E37400",
  meta: "#1877F2",
  naver: "#03C75A",
};

const insights = [
  { id: 1, title: "GA4 CTR 상승", description: "지난주 대비 12% 증가. 새 광고 크리에이티브가 성공한 신호입니다.", severity: "info", channel: "ga4" },
  { id: 2, title: "메타 CPA 경고", description: "네이버SA 대비 38% 높은 CPA. 타겟팅 재검토 권장.", severity: "warning", channel: "meta" },
  { id: 3, title: "네이버 전환율 하락", description: "지난주 4.1% → 금주 3.2%. 입찰가 점검 필요.", severity: "danger", channel: "naver" },
];

/* ─── KPI Card Component ──────────────────────────────────────── */
function KpiCard({
  label, value, change, isCpa, glowColor, index, isBig = false,
}: {
  label: string; value: string; change: number; isCpa: boolean; glowColor: string; index: number; isBig?: boolean;
}) {
  const isPositive = isCpa ? change < 0 : change > 0;

  if (isBig) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: index * 0.06, duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
        className="kpi-card p-6 cursor-default group col-span-3"
        style={{ "--glow-color": glowColor } as React.CSSProperties}
        onMouseEnter={(e) => {
          (e.currentTarget as HTMLElement).style.boxShadow = `0 0 24px ${glowColor}`;
        }}
        onMouseLeave={(e) => {
          (e.currentTarget as HTMLElement).style.boxShadow = "";
        }}>
        <p className="text-xs uppercase tracking-widest text-zinc-500 font-mono mb-4">{label}</p>
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-baseline gap-3 mb-2">
              <span className="text-4xl font-bold text-white kpi-number">{value}</span>
              {change !== 0 && (
                <span className={`text-sm font-bold flex items-center gap-1 ${isPositive ? "text-green-400" : "text-red-400"}`}>
                  {isPositive ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
                  {Math.abs(change)}%
                </span>
              )}
            </div>
          </div>
          {/* Sparkline placeholder */}
          <div className="w-24 h-12 rounded-lg" style={{ background: "rgba(255,255,255,0.03)" }} />
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.06, duration: 0.5, ease: [0.16, 1, 0.3, 1] }}>
      <div className="kpi-card p-5 cursor-default group"
        style={{ "--glow-color": glowColor } as React.CSSProperties}
        onMouseEnter={(e) => {
          (e.currentTarget as HTMLElement).style.boxShadow = `0 0 24px ${glowColor}`;
        }}
        onMouseLeave={(e) => {
          (e.currentTarget as HTMLElement).style.boxShadow = "";
        }}>
        <p className="text-xs uppercase tracking-widest text-zinc-500 font-mono mb-3">{label}</p>
        <div className="flex items-baseline gap-2">
          <span className="text-2xl font-bold text-white kpi-number">{value}</span>
          {change !== 0 && (
            <span className={`text-xs font-bold flex items-center gap-0.5 ${isPositive ? "text-green-400" : "text-red-400"}`}>
              {isPositive ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
              {Math.abs(change)}%
            </span>
          )}
        </div>
      </div>
    </motion.div>
  );
}

/* ─── Custom Chart Tooltip ────────────────────────────────────── */
const ChartTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-xl border border-white/10 px-4 py-3 shadow-2xl"
      style={{ background: "var(--bg-elevated)", minWidth: 140 }}>
      <p className="text-xs text-zinc-500 font-mono uppercase mb-2">{label}</p>
      {payload.map((p: any) => (
        <div key={p.dataKey} className="flex items-center gap-2 text-xs mb-1">
          <div className="w-2 h-2 rounded-full shrink-0" style={{ background: p.color }} />
          <span className="text-zinc-400">{p.name}</span>
          <span className="ml-auto font-bold text-white font-mono">{p.value.toLocaleString()}</span>
        </div>
      ))}
    </div>
  );
};

/* ─── Insight Drawer ──────────────────────────────────────────── */
function InsightDrawer({ open, onClose }: { open: boolean; onClose: () => void }) {
  const getSeverityClass = (s: string) => {
    if (s === "danger") return "severity-danger border-l-4";
    if (s === "warning") return "severity-warning border-l-4";
    return "severity-info border-l-4";
  };

  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/40 z-40 backdrop-blur-sm"
            onClick={onClose}
          />

          <motion.div
            initial={{ x: "100%" }} animate={{ x: 0 }} exit={{ x: "100%" }}
            transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
            className="fixed right-0 top-0 h-full w-96 z-50 flex flex-col border-l overflow-hidden"
            style={{ background: "var(--bg-surface)", borderColor: "var(--border-subtle)" }}>
            {/* Header */}
            <div className="flex items-center justify-between px-6 py-5 border-b shrink-0"
              style={{ borderColor: "var(--border-subtle)" }}>
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-xl bg-white/8 flex items-center justify-center">
                  <Brain className="w-4 h-4 text-white" />
                </div>
                <div>
                  <p className="text-sm font-bold text-white">AI 인사이트</p>
                  <p className="text-xs text-zinc-500">GPT-4o 자동 분석</p>
                </div>
              </div>
              <button onClick={onClose}
                className="w-7 h-7 rounded-lg flex items-center justify-center text-zinc-500 hover:text-white hover:bg-white/8 transition-all">
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Insights */}
            <div className="flex-1 overflow-y-auto p-5 space-y-3">
              {insights.map((ins, i) => (
                <motion.div
                  key={ins.id}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.08 }}
                  className={`p-4 rounded-xl ${getSeverityClass(ins.severity)}`}
                  style={{ background: "var(--bg-elevated)" }}>
                  <div className="flex items-start justify-between gap-2 mb-2">
                    <h4 className="text-sm font-semibold text-white leading-snug">{ins.title}</h4>
                    <span className="px-2 py-0.5 rounded-full text-xs font-bold uppercase tracking-wider shrink-0 badge-ga4">
                      {ins.channel.toUpperCase()}
                    </span>
                  </div>
                  <p className="text-xs text-zinc-400 leading-relaxed">{ins.description}</p>
                </motion.div>
              ))}

              <button
                onClick={() => toast.success("인사이트 재생성 중... (데모)")}
                className="w-full py-3 rounded-xl border border-white/8 text-xs text-zinc-500 hover:text-zinc-300 hover:border-white/15 transition-all flex items-center justify-center gap-2">
                <RefreshCw className="w-3.5 h-3.5" />
                인사이트 재생성
              </button>
            </div>

            {/* Footer */}
            <div className="border-t p-4 shrink-0" style={{ borderColor: "var(--border-subtle)" }}>
              <p className="text-xs text-zinc-600 text-center font-mono">월 10회 중 3회 사용 · 잔여 7회</p>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}

/* ─── Main Dashboard Page ─────────────────────────────────────── */
export default function DashboardPage() {
  const [dateFilter, setDateFilter] = useState<"today" | "7d" | "30d">("7d");
  const [insightOpen, setInsightOpen] = useState(false);
  const kpiData = kpiDataByFilter[dateFilter];

  const dateFilters = [
    { label: "오늘", value: "today" as const },
    { label: "7일", value: "7d" as const },
    { label: "30일", value: "30d" as const },
  ];

  return (
    <div className="min-h-screen" style={{ background: "var(--bg-base)", color: "var(--text-primary)" }}>

      {/* ── Top Bar ──────────────────────────────────── */}
      <header className="sticky top-0 z-30 glass-nav px-8 py-4 flex justify-between items-center" style={{ borderColor: "var(--border-faint)" }}>
        <div className="flex items-center gap-3">
          <span className="font-semibold text-white">대시보드</span>
          <span className="text-zinc-600 text-xs px-2 py-0.5 rounded-md border border-white/6 font-mono"
            style={{ background: "var(--bg-elevated)" }}>
            v1.0
          </span>
        </div>

        <div className="flex items-center gap-3">
          {/* Search */}
          <div className="relative hidden md:block">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-zinc-600" />
            <input
              className="pl-9 pr-12 py-2 rounded-lg text-xs text-white placeholder:text-zinc-600
                border border-white/7 focus:outline-none focus:border-white/20 transition-all w-52"
              style={{ background: "var(--bg-elevated)" }}
              placeholder="검색... (⌘K)"
              readOnly
            />
            <kbd className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-zinc-600 border border-white/10 rounded px-1 font-mono">⌘K</kbd>
          </div>

          {/* Date filter */}
          <div className="flex items-center gap-0.5 p-1 rounded-lg border border-white/7"
            style={{ background: "var(--bg-elevated)" }}>
            {dateFilters.map((f) => (
              <button key={f.value}
                onClick={() => setDateFilter(f.value)}
                className={`px-3 py-1.5 text-xs font-medium rounded-md transition-all ${
                  dateFilter === f.value
                    ? "bg-white text-black shadow-sm"
                    : "text-zinc-500 hover:text-zinc-200"
                }`}>
                {f.label}
              </button>
            ))}
          </div>

          {/* AI CTA */}
          <button
            onClick={() => setInsightOpen(true)}
            className="flex items-center gap-2 text-xs font-semibold px-4 py-2 rounded-lg border border-white/12 text-white
              hover:bg-white/8 transition-all shimmer-btn relative"
            style={{ background: "var(--bg-elevated)" }}>
            <Brain className="w-3.5 h-3.5" />
            AI 인사이트
            <span className="absolute -top-1.5 -right-1.5 w-4 h-4 rounded-full bg-red-500 text-white text-xs flex items-center justify-center font-bold">
              {insights.length}
            </span>
          </button>

          {/* Download */}
          <button
            onClick={() => toast.success("리포트 생성 완료 (데모)")}
            className="w-9 h-9 rounded-lg border border-white/7 flex items-center justify-center text-zinc-500 hover:text-white hover:border-white/15 transition-all"
            style={{ background: "var(--bg-elevated)" }}>
            <Download className="w-4 h-4" />
          </button>
        </div>
      </header>

      {/* ── Content ──────────────────────────────────── */}
      <div className="px-8 py-8 max-w-7xl mx-auto space-y-6">

        {/* KPI grid */}
        <div className="grid grid-cols-1 md:grid-cols-6 gap-3">
          {/* Big ROAS card */}
          {(() => {
            const roas = kpiData.roas;
            return (
              <KpiCard
                label={roas.label}
                value={roas.value}
                change={roas.change}
                isCpa={false}
                glowColor="rgba(3,199,90,0.3)"
                index={0}
                isBig
              />
            );
          })()}

          {/* Small KPI cards */}
          {[
            { key: "totalSpend", isCpa: false, glow: "rgba(227,116,0,0.3)" },
            { key: "totalConversions", isCpa: false, glow: "rgba(24,119,242,0.3)" },
            { key: "cpa", isCpa: true, glow: "rgba(255,255,255,0.15)" },
            { key: "ctr", isCpa: false, glow: "rgba(227,116,0,0.2)" },
            { key: "totalClicks", isCpa: false, glow: "rgba(24,119,242,0.2)" },
          ].map((cfg, i) => {
            const data = kpiData[cfg.key as keyof typeof kpiData];
            const change = data?.change ?? 0;
            return (
              <KpiCard
                key={cfg.key}
                label={data?.label ?? cfg.key}
                value={data?.value ?? "—"}
                change={change}
                isCpa={cfg.isCpa}
                glowColor={cfg.glow}
                index={i + 1}
              />
            );
          })}
        </div>

        {/* Main grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">

          {/* Chart — 2/3 */}
          <motion.div
            initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4, duration: 0.5 }}
            className="md:col-span-2 rounded-2xl border border-white/7 p-7"
            style={{ background: "var(--bg-elevated)", borderColor: "var(--border-subtle)" }}>
            <div className="flex justify-between items-start mb-7">
              <div>
                <h4 className="font-bold text-white mb-1">채널 성과 분석</h4>
                <p className="text-zinc-500 text-xs">지난 기간 클릭 + 전환 추이</p>
              </div>
              <div className="flex gap-1.5">
                {["Daily", "Weekly", "Monthly"].map((t, i) => (
                  <button key={t}
                    className={`px-3 py-1.5 text-xs font-medium rounded-lg border transition-all ${
                      i === 0
                        ? "border-white/20 text-white bg-white/8"
                        : "border-white/7 text-zinc-500 hover:text-zinc-200 hover:border-white/15"
                    }`}>
                    {t}
                  </button>
                ))}
              </div>
            </div>

            <ResponsiveContainer width="100%" height={220}>
              <LineChart data={chartData}>
                <defs>
                  <linearGradient id="ga4g" x1="0" x2="0" y1="0" y2="1">
                    <stop offset="0%" stopColor="#E37400" stopOpacity="0.2" />
                    <stop offset="100%" stopColor="#E37400" stopOpacity="0" />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="2 4" stroke="rgba(255,255,255,0.04)" vertical={false} />
                <XAxis dataKey="date" tick={{ fontSize: 10, fill: "#71717a" }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 10, fill: "#71717a" }} axisLine={false} tickLine={false} width={32} />
                <Tooltip content={<ChartTooltip />} cursor={{ stroke: "rgba(255,255,255,0.08)", strokeWidth: 1 }} />
                <Line type="monotone" dataKey="ga4" stroke="#E37400" strokeWidth={2} dot={false} name="GA4" />
                <Line type="monotone" dataKey="meta" stroke="#1877F2" strokeWidth={2} dot={false} name="메타" />
                <Line type="monotone" dataKey="naver" stroke="#03C75A" strokeWidth={2} dot={false} name="네이버SA" />
              </LineChart>
            </ResponsiveContainer>

            {/* Summary row */}
            <div className="mt-6 grid grid-cols-4 gap-4 border-t pt-5" style={{ borderColor: "var(--border-subtle)" }}>
              {[
                { label: "평균 CTR", val: "3.2%" },
                { label: "총 클릭", val: "42.8K" },
                { label: "전환율", val: "4.1%" },
                { label: "ROAS", val: "3.8x" },
              ].map((s) => (
                <div key={s.label}>
                  <span className="text-xs text-zinc-600 font-mono uppercase block mb-1">{s.label}</span>
                  <p className="font-bold text-white font-mono text-sm">{s.val}</p>
                </div>
              ))}
            </div>
          </motion.div>

          {/* Pie chart — 1/3 */}
          <motion.div
            initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5, duration: 0.5 }}
            className="rounded-2xl border border-white/7 p-7 flex flex-col"
            style={{ background: "var(--bg-elevated)", borderColor: "var(--border-subtle)" }}>
            <h4 className="font-bold text-white mb-1">채널 점유율</h4>
            <p className="text-zinc-500 text-xs mb-4">트래픽 채널별 분포</p>

            <div className="flex-1 flex items-center justify-center">
              <ResponsiveContainer width="100%" height={180}>
                <PieChart>
                  <Pie data={pieData} cx="50%" cy="50%" innerRadius={50} outerRadius={78}
                    paddingAngle={3} dataKey="value" strokeWidth={0}>
                    {pieData.map((entry, i) => (
                      <Cell key={i} fill={entry.color} opacity={1 - i * 0.15} />
                    ))}
                  </Pie>
                  <Legend
                    iconType="circle" iconSize={7}
                    formatter={(v) => <span style={{ color: "#a1a1aa", fontSize: 11 }}>{v}</span>}
                  />
                  <Tooltip
                    formatter={(v) => [`${v}%`, ""]}
                    contentStyle={{ background: "var(--bg-elevated)", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 12, fontSize: 12 }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>

            {/* AI micro-insight */}
            <div className="mt-4 p-3.5 rounded-xl border-l-2 border-zinc-600"
              style={{ background: "rgba(255,255,255,0.04)" }}>
              <div className="flex items-center gap-1.5 mb-1">
                <Sparkles className="w-3 h-3 text-zinc-500" />
                <span className="text-xs font-semibold text-zinc-500 uppercase tracking-wider">AI 요약</span>
              </div>
              <p className="text-xs text-zinc-400 leading-relaxed italic">
                "네이버SA CTR 지난주 대비 12% 하락.<br />키워드 입찰가 점검 권장."
              </p>
            </div>
          </motion.div>
        </div>

        {/* Bottom grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Channel performance table */}
          <motion.div
            initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6, duration: 0.5 }}
            className="rounded-2xl border border-white/7 p-7"
            style={{ background: "var(--bg-elevated)", borderColor: "var(--border-subtle)" }}>
            <h4 className="font-bold text-white mb-6">채널별 성과</h4>
            <div className="space-y-1">
              {/* Header */}
              <div className="grid grid-cols-5 gap-2 px-3 pb-2 border-b" style={{ borderColor: "var(--border-subtle)" }}>
                {["채널", "광고비", "ROAS", "클릭", "전환"].map((h) => (
                  <span key={h} className="text-xs font-mono uppercase text-zinc-600 tracking-wider">{h}</span>
                ))}
              </div>
              {channelPerformance.map((ch, i) => (
                <motion.div
                  key={ch.channel}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.7 + i * 0.08 }}
                  className="grid grid-cols-5 gap-2 px-3 py-3 rounded-lg hover:bg-white/4 transition-colors group cursor-default">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full shrink-0" style={{ background: channelColors[ch.channel] }} />
                    <span className="text-xs font-semibold text-zinc-300 group-hover:text-white transition-colors truncate">
                      {ch.label}
                    </span>
                  </div>
                  {[ch.spend, ch.roas, ch.clicks, ch.conversions].map((v, j) => (
                    <span key={j} className="text-xs text-zinc-400 font-mono group-hover:text-zinc-200 transition-colors">{v}</span>
                  ))}
                </motion.div>
              ))}
            </div>
          </motion.div>

          {/* Recent activity */}
          <motion.div
            initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.7, duration: 0.5 }}
            className="rounded-2xl border border-white/7 p-7"
            style={{ background: "var(--bg-elevated)", borderColor: "var(--border-subtle)" }}>
            <div className="flex items-center justify-between mb-6">
              <h4 className="font-bold text-white">최근 활동</h4>
              <button className="text-xs text-zinc-500 hover:text-zinc-300 transition-colors flex items-center gap-1">
                전체 보기 <ChevronRight className="w-3 h-3" />
              </button>
            </div>

            <div className="space-y-1">
              {[
                { name: "GA4 — 자연 검색", id: "CH_GA4_001", amount: "+2,840", status: "active", color: "#E37400" },
                { name: "메타 광고 — FB+IG", id: "CH_META_001", amount: "+1,920", status: "active", color: "#1877F2" },
                { name: "네이버SA", id: "CH_NAVER_001", amount: "+980", status: "pending", color: "#03C75A" },
              ].map((t, i) => (
                <motion.div
                  key={t.id}
                  initial={{ opacity: 0, x: 10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.8 + i * 0.08 }}
                  className="flex items-center justify-between py-3 px-3 rounded-lg hover:bg-white/4 transition-colors cursor-default group">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-xl flex items-center justify-center shrink-0"
                      style={{ background: `${t.color}15` }}>
                      <div className="w-2.5 h-2.5 rounded-full" style={{ background: t.color }} />
                    </div>
                    <div>
                      <p className="text-xs font-semibold text-zinc-200 group-hover:text-white transition-colors">{t.name}</p>
                      <p className="text-xs text-zinc-600 font-mono mt-0.5">{t.id}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-xs font-bold text-white font-mono">{t.amount}</p>
                    <p className={`text-xs font-bold uppercase mt-0.5 ${t.status === "active" ? "text-green-400" : "text-zinc-500"}`}>
                      {t.status === "active" ? "Active" : "Pending"}
                    </p>
                  </div>
                </motion.div>
              ))}
            </div>

            {/* Generate report card */}
            <div className="mt-4 p-4 rounded-xl border border-white/7 relative overflow-hidden group cursor-pointer hover:border-white/15 transition-all"
              style={{ background: "rgba(255,255,255,0.03)" }}
              onClick={() => toast.success("리포트 생성 완료 (데모)")}>
              <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity"
                style={{ background: "linear-gradient(135deg, rgba(255,255,255,0.03), transparent)" }} />
              <p className="text-sm font-bold text-white mb-1 relative z-10">AI 리포트 생성</p>
              <p className="text-xs text-zinc-500 relative z-10 leading-relaxed">
                사용자 행동 패턴과 매출 예측이 담긴 PDF 리포트를 생성합니다.
              </p>
              <button className="mt-3 flex items-center gap-1.5 text-xs font-semibold text-zinc-300 hover:text-white transition-colors relative z-10 group/btn">
                <Download className="w-3.5 h-3.5" />
                리포트 생성
                <ChevronRight className="w-3 h-3 transition-transform group-hover/btn:translate-x-0.5" />
              </button>
            </div>
          </motion.div>
        </div>
      </div>

      {/* AI Insight Drawer */}
      <InsightDrawer open={insightOpen} onClose={() => setInsightOpen(false)} />
    </div>
  );
}
