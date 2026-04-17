"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { BarChart3, TrendingUp, TrendingDown, AlertCircle } from "lucide-react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Legend,
} from "recharts";
import { naverMetrics, naverDetailChart } from "@/lib/mock-data";

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
        (e.currentTarget as HTMLElement).style.boxShadow = "0 0 24px rgba(3,199,90,0.3)";
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
export default function NaverPage() {
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
              <BarChart3 className="w-5 h-5 text-green-400" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-white">네이버 검색광고 분석</h1>
              <p className="text-xs text-zinc-500">노출, 클릭, 전환, 지출</p>
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
        {/* Beta Banner */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="rounded-xl border border-amber-500/30 bg-amber-500/10 px-5 py-4 flex items-start gap-3"
        >
          <AlertCircle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
          <div>
            <h3 className="text-sm font-semibold text-amber-100 mb-1">베타 단계</h3>
            <p className="text-xs text-amber-200">
              네이버 검색광고 API는 현재 베타 테스트 중입니다. 실제 API 연동 준비 중이며, 현재는 샘플 데이터로 기능을 확인하실 수 있습니다.
            </p>
          </div>
        </motion.div>

        {/* KPI Cards */}
        <div className="grid grid-cols-2 md:grid-cols-6 gap-3">
          {naverMetrics.map((metric, i) => (
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
              <h2 className="font-bold text-white mb-1">광고 성과</h2>
              <p className="text-zinc-500 text-xs">지난 7일 노출 및 지출 추이</p>
            </div>
          </div>

          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={naverDetailChart}>
              <CartesianGrid strokeDasharray="2 4" stroke="rgba(255,255,255,0.04)" vertical={false} />
              <XAxis dataKey="date" tick={{ fontSize: 10, fill: "#71717a" }} axisLine={false} tickLine={false} />
              <YAxis yAxisId="left" tick={{ fontSize: 10, fill: "#71717a" }} axisLine={false} tickLine={false} width={40} />
              <YAxis yAxisId="right" orientation="right" tick={{ fontSize: 10, fill: "#71717a" }} axisLine={false} tickLine={false} width={40} />
              <Tooltip content={<ChartTooltip />} cursor={{ fill: "rgba(255,255,255,0.05)" }} />
              <Legend wrapperStyle={{ paddingTop: "20px" }} />
              <Bar yAxisId="left" dataKey="impressions" fill="#03C75A" name="노출" opacity={0.8} />
              <Bar yAxisId="right" dataKey="spend" fill="#F59E0B" name="지출 (₩)" opacity={0.8} />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Keyword Performance Table */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="rounded-2xl border border-white/7 p-7"
          style={{ background: "var(--bg-elevated)" }}
        >
          <h3 className="font-bold text-white mb-6">키워드 성과</h3>

          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b" style={{ borderColor: "var(--border-subtle)" }}>
                  <th className="text-left py-3 px-4 text-[10px] font-mono uppercase text-zinc-600">키워드</th>
                  <th className="text-right py-3 px-4 text-[10px] font-mono uppercase text-zinc-600">노출</th>
                  <th className="text-right py-3 px-4 text-[10px] font-mono uppercase text-zinc-600">클릭</th>
                  <th className="text-right py-3 px-4 text-[10px] font-mono uppercase text-zinc-600">CTR</th>
                  <th className="text-right py-3 px-4 text-[10px] font-mono uppercase text-zinc-600">CPC</th>
                  <th className="text-right py-3 px-4 text-[10px] font-mono uppercase text-zinc-600">전환</th>
                </tr>
              </thead>
              <tbody>
                {[
                  { keyword: "마케팅 자동화", impressions: 28400, clicks: 1920, ctr: 6.8, cpc: 1850, conversions: 34 },
                  { keyword: "SaaS 솔루션", impressions: 24600, clicks: 1580, ctr: 6.4, cpc: 1920, conversions: 28 },
                  { keyword: "데이터 분석 툴", impressions: 22100, clicks: 1420, ctr: 6.4, cpc: 1780, conversions: 25 },
                  { keyword: "BI 플랫폼", impressions: 19800, clicks: 1210, ctr: 6.1, cpc: 1850, conversions: 21 },
                  { keyword: "대시보드 소프트웨어", impressions: 18300, clicks: 1110, ctr: 6.1, cpc: 1920, conversions: 19 },
                ].map((keyword, i) => (
                  <motion.tr
                    key={keyword.keyword}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.5 + i * 0.02 }}
                    className="border-b hover:bg-white/3 transition-colors"
                    style={{ borderColor: "var(--border-subtle)" }}
                  >
                    <td className="py-3 px-4 text-xs text-zinc-300">{keyword.keyword}</td>
                    <td className="text-right py-3 px-4 text-xs text-white font-mono">{keyword.impressions.toLocaleString()}</td>
                    <td className="text-right py-3 px-4 text-xs text-white font-mono">{keyword.clicks.toLocaleString()}</td>
                    <td className="text-right py-3 px-4 text-xs text-white font-mono">{keyword.ctr.toFixed(1)}%</td>
                    <td className="text-right py-3 px-4 text-xs text-white font-mono">₩{keyword.cpc.toLocaleString()}</td>
                    <td className="text-right py-3 px-4 text-xs text-white font-mono">{keyword.conversions}</td>
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
            { label: "총 노출", val: "156.2K" },
            { label: "총 클릭", val: "9.2K" },
            { label: "평균 CTR", val: "5.9%" },
            { label: "총 전환", val: "142" },
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
