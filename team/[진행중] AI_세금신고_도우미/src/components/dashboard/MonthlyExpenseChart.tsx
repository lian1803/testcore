"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import type { MockMonthlyData } from "@/lib/mock-data";
import { formatCurrencyShort } from "@/lib/utils";

const COLORS = {
  MEAL: "#F59E0B",
  TRANSPORTATION: "#3B82F6",
  COMMUNICATION: "#8B5CF6",
  OFFICE_SUPPLIES: "#22C55E",
  EDUCATION: "#EF4444",
  OTHER: "#94A3B8",
};

const LABELS: Record<string, string> = {
  MEAL: "식비",
  TRANSPORTATION: "교통비",
  COMMUNICATION: "통신비",
  OFFICE_SUPPLIES: "사무용품",
  EDUCATION: "교육비",
  OTHER: "기타",
};

interface MonthlyExpenseChartProps {
  data: MockMonthlyData[];
}

const CustomTooltip = ({ active, payload, label }: { active?: boolean; payload?: Array<{ name: string; value: number; fill: string }>; label?: string }) => {
  if (!active || !payload || !payload.length) return null;
  const total = payload.reduce((sum, p) => sum + p.value, 0);
  return (
    <div className="bg-white border border-[#E2E8F0] rounded-xl p-3 shadow-lg min-w-[140px]">
      <p className="text-sm font-semibold text-[#1A202C] mb-2">{label}</p>
      {payload.filter(p => p.value > 0).map((p) => (
        <div key={p.name} className="flex justify-between gap-4 text-xs">
          <span style={{ color: p.fill }}>{LABELS[p.name] || p.name}</span>
          <span className="text-[#1A202C]">{formatCurrencyShort(p.value)}</span>
        </div>
      ))}
      {total > 0 && (
        <div className="border-t border-[#E2E8F0] mt-2 pt-2 flex justify-between text-xs font-semibold">
          <span className="text-[#718096]">합계</span>
          <span className="text-[#1A202C]">{formatCurrencyShort(total)}</span>
        </div>
      )}
    </div>
  );
};

export function MonthlyExpenseChart({ data }: MonthlyExpenseChartProps) {
  return (
    <div className="bg-white rounded-xl border border-[#E2E8F0] shadow-sm p-6">
      <h3 className="text-lg font-semibold text-[#1A202C] mb-6">월별 경비 현황</h3>
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={data} margin={{ top: 0, right: 0, left: -10, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" vertical={false} />
          <XAxis
            dataKey="month"
            tick={{ fontSize: 12, fill: "#718096" }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            tickFormatter={formatCurrencyShort}
            tick={{ fontSize: 12, fill: "#718096" }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend
            wrapperStyle={{ paddingTop: "16px", fontSize: "12px" }}
            formatter={(value) => LABELS[value] || value}
          />
          {Object.entries(COLORS).map(([key, color]) => (
            <Bar key={key} dataKey={key} stackId="a" fill={color} radius={key === "OTHER" ? [4, 4, 0, 0] : [0, 0, 0, 0]} />
          ))}
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
