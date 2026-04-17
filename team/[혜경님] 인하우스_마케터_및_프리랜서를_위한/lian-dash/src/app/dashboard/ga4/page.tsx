"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { BarChart3, TrendingUp, TrendingDown } from "lucide-react";
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer,
} from "recharts";
import { ga4Metrics, ga4DetailChart } from "@/lib/mock-data";

/* ─── Custom Tooltip ─────────────────────────────────── */
const ChartTooltip = ({ active, payload, label }: { active?: boolean; payload?: any[]; label?: string }) => {
  if (!active || !payload?.length) return null;
  return (
    <div
      className="rounded-xl border border-white/10 px-4 py-3 shadow-2xl"
      style={{ background: "var(--bg-elevated)", minWidth: 140 }}
    >
      <p className="text-[10px] text-zinc-500 font-mono uppercase mb-2">{label}</p>
      {payload.map((p: any) => (
        <div key={p.dataKey} className="flex items-center gap-2 text-xs mb-1">
          <div className="w-2 h-2 rounded-full" style={{ background: p.color }} />
          <span className="text-zinc-400">{p.name}</span>
          <span className="ml-auto font-bold text-white font-mono">{p.value.toLocaleString()}</span>
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
  const formattedValue = typeof value === "number" && value > 999
    ? (value / 1000).toFixed(1) + "K"
    : value.toLocaleString();

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.06 }}
      className="kpi-card p-5 cursor-default group"
      onMouseEnter={(e) => {
        (e.currentTarget as HTMLElement).style.boxShadow = "0 0 24px rgba(59,130,246,0.3)";
      }}
      onMouseLeave={(e) => {
        (e.currentTarget as HTMLElement).style.boxShadow = "";
      }}
      style={{ borderRadius: "12px" }}
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
export default function GA4Page() {
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
              <BarChart3 className="w-5 h-5 text-orange-400" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-white">GA4 분석</h1>
              <p className="text-xs text-zinc-500">세션, 사용자, 이탈율, 목표 달성</p>
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
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {ga4Metrics.map((metric, i) => (
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
              <h2 className="font-bold text-white mb-1">세션 추이</h2>
              <p className="text-zinc-500 text-xs">지난 7일 일일 세션</p>
            </div>
          </div>

          <ResponsiveContainer width="100%" height={250}>
            <AreaChart data={ga4DetailChart}>
              <defs>
                <linearGradient id="sessionsGradient" x1="0" x2="0" y1="0" y2="1">
                  <stop offset="0%" stopColor="#3b82f6" stopOpacity="0.2" />
                  <stop offset="100%" stopColor="#3b82f6" stopOpacity="0" />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="2 4" stroke="rgba(255,255,255,0.04)" vertical={false} />
              <XAxis dataKey="date" tick={{ fontSize: 10, fill: "#71717a" }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 10, fill: "#71717a" }} axisLine={false} tickLine={false} width={40} />
              <Tooltip content={<ChartTooltip />} cursor={{ stroke: "rgba(255,255,255,0.08)", strokeWidth: 1 }} />
              <Area type="monotone" dataKey="sessions" stroke="#3b82f6" strokeWidth={2} fill="url(#sessionsGradient)" name="Sessions" />
            </AreaChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Data Table */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="rounded-2xl border border-white/7 p-7"
          style={{ background: "var(--bg-elevated)" }}
        >
          <h3 className="font-bold text-white mb-6">일일 세부 데이터</h3>

          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b" style={{ borderColor: "var(--border-subtle)" }}>
                  <th className="text-left py-3 px-4 text-[10px] font-mono uppercase text-zinc-600">날짜</th>
                  <th className="text-right py-3 px-4 text-[10px] font-mono uppercase text-zinc-600">세션</th>
                  <th className="text-right py-3 px-4 text-[10px] font-mono uppercase text-zinc-600">이탈율</th>
                  <th className="text-right py-3 px-4 text-[10px] font-mono uppercase text-zinc-600">목표 완료</th>
                </tr>
              </thead>
              <tbody>
                {ga4DetailChart.map((row, i) => (
                  <motion.tr
                    key={row.date}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.5 + i * 0.02 }}
                    className="border-b hover:bg-white/3 transition-colors"
                    style={{ borderColor: "var(--border-subtle)" }}
                  >
                    <td className="py-3 px-4 text-xs text-zinc-300 font-mono">{row.date}</td>
                    <td className="text-right py-3 px-4 text-xs text-white font-mono">{row.sessions?.toLocaleString()}</td>
                    <td className="text-right py-3 px-4 text-xs text-white font-mono">{row.bounceRate?.toFixed(1)}%</td>
                    <td className="text-right py-3 px-4 text-xs text-white font-mono">{row.goalCompletions}</td>
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
            { label: "평균 세션", val: "1,806" },
            { label: "최고 세션", val: "2,340" },
            { label: "평균 이탈율", val: "41.2%" },
            { label: "총 목표 완료", val: "590" },
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
