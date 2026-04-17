import { TrendingUp, TrendingDown, Receipt, PiggyBank, DollarSign, FileText } from "lucide-react";
import type { MockKpiData } from "@/lib/mock-data";
import { formatCurrency } from "@/lib/utils";

interface KpiCardsProps {
  kpi: MockKpiData;
  receiptCount: number;
}

export function KpiCards({ kpi, receiptCount }: KpiCardsProps) {
  const cards = [
    {
      label: "총 경비",
      value: formatCurrency(kpi.totalExpense),
      change: kpi.totalExpensePrevMonthChange,
      icon: DollarSign,
      accent: false,
    },
    {
      label: "예상 세액",
      value: formatCurrency(kpi.estimatedTax),
      change: kpi.estimatedTaxPrevMonthChange,
      icon: FileText,
      accent: false,
      valueClass: "text-[#EF4444]",
    },
    {
      label: "영수증 수",
      value: `${receiptCount}건`,
      change: kpi.receiptCountPrevMonthChange,
      icon: Receipt,
      accent: false,
    },
    {
      label: "절세 예상액",
      value: formatCurrency(kpi.estimatedSaving),
      change: kpi.estimatedSavingPrevMonthChange,
      icon: PiggyBank,
      accent: true,
    },
  ];

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map((card) => {
        const Icon = card.icon;
        const isPositiveChange = card.change > 0;
        return (
          <div
            key={card.label}
            className={`bg-white rounded-xl p-6 shadow-sm border ${
              card.accent
                ? "border-l-4 border-l-[#22C55E] border-[#E2E8F0]"
                : "border-[#E2E8F0]"
            }`}
          >
            <div className="flex items-center justify-between mb-3">
              <span className="text-sm text-[#718096]">{card.label}</span>
              <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${card.accent ? "bg-[#22C55E]/10" : "bg-[#F1F5F9]"}`}>
                <Icon className={`h-4 w-4 ${card.accent ? "text-[#22C55E]" : "text-[#718096]"}`} />
              </div>
            </div>
            <div className={`text-2xl font-bold ${card.valueClass || (card.accent ? "text-[#22C55E]" : "text-[#1A202C]")}`}>
              {card.value}
            </div>
            {card.change !== 0 && (
              <div className={`flex items-center gap-1 mt-1 text-xs ${isPositiveChange ? "text-[#22C55E]" : "text-[#EF4444]"}`}>
                {isPositiveChange ? (
                  <TrendingUp className="h-3 w-3" />
                ) : (
                  <TrendingDown className="h-3 w-3" />
                )}
                <span>전월 대비 {Math.abs(card.change)}%</span>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
