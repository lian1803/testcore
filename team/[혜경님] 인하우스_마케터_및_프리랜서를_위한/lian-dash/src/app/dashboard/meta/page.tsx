"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { BarChart3, TrendingUp, TrendingDown } from "lucide-react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Legend,
} from "recharts";
import { metaMetrics, metaDetailChart } from "@/lib/mock-data";

/* ─── Custom Tooltip ─────────────────────────────────── */
const ChartTooltip = ({ active, payload, label }: { active?: boolean; payload?: any[]; label?: string }) => {
  if (!active || !payload?.length) return null;
  return (
    <div
      className="rounded-xl border border-white/10 px-4 py-3 shadow-2xl"
      style={{ background: "var(--bg-elevated)", minWidth: 160 }}
    >
      <p className="text-[10px] text-zinc-500 font-mono uppercase mb-2">{label}</p>
      {payload.map((p: any) => (
        <div key={p.dataKey} className="flex items-center gap-2 text-xs mb-1">
          <div className="w-2 h-2 rounded-full" style={{ background: p.color }} />
          <span className="text-zinc-400">{p.name}</span>
          <span className="ml-auto font-bold text-white font-mono">
            {p.dataKey === "spend" ? `₩${p.value.toLocaleString()}` : p.value.toLocaleString()}
          </span>
        </div>
      ))}
    </div>
  );
};

/* ─── KPI Card ───────────────────────────────────────── */
function MetricCard({
  label,
  value,
  change,
  unit,
  index,
}: {
  label: string;
  value: number;
  change: number;
  unit: string;
  index: number;
}) {
  const isPositive = change > 0;
  const formattedValue = typeof value === "number" && value > 999999
    ? (value / 1000000).toFixed(1) + "M"
    : typeof value === "number" && value > 999
      ? (value / 1000).toFixed(1) + "K"
      : value.toLocaleString();

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.06 }}
      className="kpi-card p-5 cursor-default group"
      onMouseEnter={(e) => {
        (e.currentTarget as HTMLElement).style.boxShadow = "0 0 24px rgba(24,119,242,0.3)";
      }}
      onMouseLeave={(e) => {
        (e.currentTarget as HTMLElement).style.boxShadow = "";
      }}
    >
      <p className="text-[10px] uppercase tracking-widest text-zinc-500 font-mono mb-3">{label}</p>
      <div className="flex items-baseline gap-2">
        <span className="text-2xl font-bold text-white font-mono">{formattedValue}</span>
        {unit && <span className="text-xs text-zinc-500">{unit}</span>}
      </div>
      {change !== 0 && (
        <div className={`text-xs font-bold flex items-center gap-0.5 mt-2 ${isPositive ? "text-green-400" : "text-red-400"}`}>
          {isPositive ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
          {Math.abs(change).toFixed(1)}%
        </div>
      )}
    </motion.div>
  );
}

/* ─── Page ───────────────────────────────────────────── */
export default function MetaPage() {
  const [timeRange, setTimeRange] = useState("7d");

  const timeRanges = [
    { label: "7일", value: "7d" },
    { label: "30일", value: "30d" },
    { label: "90일", value: "90d" },
  ];

  return (
    <div className="min-h-screen" style={{ background: "var(--bg-base)", color: "var(--text-primary)" }}>
      {/* ── Header ──────────────────────────────────── */}
      <header className="sticky top-0 z-20 glass-nav px-8 py-5 border-b" style={{ borderColor: "var(--border-subtle)" }}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-white/8 flex items-center justify-center">
              <BarChart3 className="w-5 h-5 text-blue-400" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-white">메타 광고 분석</h1>
              <p className="text-xs text-zinc-500">노출, 클릭, ROAS, 지출</p>
            </div>
          </div>

          {/* Time Range */}
          <div className="flex items-center gap-1 p-1 rounded-lg border border-white/7" style={{ background: "var(--bg-elevated)" }}>
            {timeRanges.map((range) => (
              <button
                key={range.value}
                onClick={() => setTimeRange(range.value)}
                className={`px-3 py-1.5 text-xs font-medium rounded-md transition-all ${
                  timeRange === range.value
                    ? "bg-white text-black shadow-sm"
                    : "text-zinc-500 hover:text-zinc-200"
                }`}
              >
                {range.label}
              </button>
            ))}
          </div>
        </div>
      </header>

      {/* ── Content ────────────────────────────────── */}
      <div className="px-8 py-8 max-w-7xl mx-auto space-y-6">
        {/* KPI Cards */}
        <div className="grid grid-cols-2 md:grid-cols-6 gap-3">
          {metaMetrics.map((metric, i) => (
            <MetricCard
              key={metric.metric}
              label={metric.metric}
              value={metric.value}
              change={metric.change}
              unit={metric.unit}
              index={i}
            />
          ))}
        </div>

        {/* Chart */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="rounded-2xl border border-white/7 p-7"
          style={{ background: "var(--bg-elevated)" }}
        >
          <div className="flex justify-between items-center mb-6">
            <div>
              <h2 className="font-bold text-white mb-1">캠페인별 성과</h2>
              <p className="text-zinc-500 text-xs">지난 7일 노출 및 지출 추이</p>
            </div>
          </div>

          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={metaDetailChart}>
              <CartesianGrid strokeDasharray="2 4" stroke="rgba(255,255,255,0.04)" vertical={false} />
              <XAxis dataKey="date" tick={{ fontSize: 10, fill: "#71717a" }} axisLine={false} tickLine={false} />
              <YAxis yAxisId="left" tick={{ fontSize: 10, fill: "#71717a" }} axisLine={false} tickLine={false} width={40} />
              <YAxis yAxisId="right" orientation="right" tick={{ fontSize: 10, fill: "#71717a" }} axisLine={false} tickLine={false} width={40} />
              <Tooltip content={<ChartTooltip />} cursor={{ fill: "rgba(255,255,255,0.05)" }} />
              <Legend wrapperStyle={{ paddingTop: "20px" }} />
              <Bar yAxisId="left" dataKey="impressions" fill="#1877F2" name="노출" opacity={0.8} />
              <Bar yAxisId="right" dataKey="spend" fill="#F59E0B" name="지출 (₩)" opacity={0.8} />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Campaign Performance Table */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="rounded-2xl border border-white/7 p-7"
          style={{ background: "var(--bg-elevated)" }}
        >
          <h3 className="font-bold text-white mb-6">캠페인 목록</h3>

          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b" style={{ borderColor: "var(--border-subtle)" }}>
                  <th className="text-left py-3 px-4 text-[10px] font-mono uppercase text-zinc-600">캠페인명</th>
                  <th className="text-right py-3 px-4 text-[10px] font-mono uppercase text-zinc-600">노출</th>
                  <th className="text-right py-3 px-4 text-[10px] font-mono uppercase text-zinc-600">클릭</th>
                  <th className="text-right py-3 px-4 text-[10px] font-mono uppercase text-zinc-600">CTR</th>
                  <th className="text-right py-3 px-4 text-[10px] font-mono uppercase text-zinc-600">지출</th>
                  <th className="text-right py-3 px-4 text-[10px] font-mono uppercase text-zinc-600">ROAS</th>
                </tr>
              </thead>
              <tbody>
                {[
                  { name: "Summer Sale 2026", impressions: 125400, clicks: 8230, ctr: 6.6, spend: 850000, roas: 4.2 },
                  { name: "New Product Launch", impressions: 98600, clicks: 6450, ctr: 6.5, spend: 720000, roas: 3.9 },
                  { name: "Brand Awareness Q2", impressions: 61400, clicks: 4240, ctr: 6.9, spend: 610000, roas: 3.5 },
                  { name: "Newsletter Signup", impressions: 45800, clicks: 3180, ctr: 6.9, spend: 380000, roas: 3.2 },
                  { name: "Retargeting Campaign", impressions: 78200, clicks: 5820, ctr: 7.4, spend: 520000, roas: 4.5 },
                ].map((campaign, i) => (
                  <motion.tr
                    key={campaign.name}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.5 + i * 0.02 }}
                    className="border-b hover:bg-white/3 transition-colors"
                    style={{ borderColor: "var(--border-subtle)" }}
                  >
                    <td className="py-3 px-4 text-xs text-zinc-300">{campaign.name}</td>
                    <td className="text-right py-3 px-4 text-xs text-white font-mono">{campaign.impressions.toLocaleString()}</td>
                    <td className="text-right py-3 px-4 text-xs text-white font-mono">{campaign.clicks.toLocaleString()}</td>
                    <td className="text-right py-3 px-4 text-xs text-white font-mono">{campaign.ctr.toFixed(1)}%</td>
                    <td className="text-right py-3 px-4 text-xs text-white font-mono">₩{campaign.spend.toLocaleString()}</td>
                    <td className="text-right py-3 px-4 text-xs text-white font-mono">{campaign.roas.toFixed(1)}x</td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>
        </motion.div>

        {/* Summary */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="grid grid-cols-1 md:grid-cols-4 gap-4"
        >
          {[
            { label: "총 노출", val: "285.4K" },
            { label: "총 클릭", val: "18.9K" },
            { label: "평균 CTR", val: "6.6%" },
            { label: "평균 ROAS", val: "3.8x" },
          ].map((s) => (
            <div key={s.label} className="rounded-xl border border-white/7 p-4" style={{ background: "var(--bg-surface)" }}>
              <span className="text-[9px] text-zinc-600 font-mono uppercase block mb-2">{s.label}</span>
              <p className="font-bold text-white font-mono text-lg">{s.val}</p>
            </div>
          ))}
        </motion.div>
      </div>
    </div>
  );
}
