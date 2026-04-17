import { formatCurrency } from "@/lib/utils";
import type { MOCK_TAX_RETURN } from "@/lib/mock-data";

type TaxReturnData = typeof MOCK_TAX_RETURN;

interface TaxReturnPreviewProps {
  data: TaxReturnData;
}

export function TaxReturnPreview({ data }: TaxReturnPreviewProps) {
  const rows = [
    { label: "총 수입금액", value: data.totalIncome, bold: false },
    { label: "총 경비 합계", value: data.totalExpense, bold: false, color: "text-[#EF4444]" },
    { label: "기본공제", value: data.standardDeduction, bold: false, color: "text-[#EF4444]" },
    { label: "과세 표준", value: data.taxBase, bold: true },
    { label: "예상 세액", value: data.estimatedTax, bold: true, color: "text-[#EF4444]" },
    { label: "절세 예상액", value: data.estimatedSaving, bold: true, color: "text-[#22C55E]" },
  ];

  return (
    <div className="bg-white rounded-xl border border-[#E2E8F0] shadow-sm overflow-hidden">
      <div className="px-6 py-4 border-b border-[#E2E8F0] bg-[#F8FAFC]">
        <h3 className="text-base font-semibold text-[#1A202C]">{data.taxYear}년 귀속 종합소득세 신고서 초안</h3>
        <p className="text-xs text-[#718096] mt-0.5">참고용 — 실제 세액과 다를 수 있습니다</p>
      </div>

      <div className="divide-y divide-[#E2E8F0]">
        {rows.map((row) => (
          <div key={row.label} className={`flex justify-between px-6 py-3 ${row.bold ? "bg-[#F8FAFC]" : ""}`}>
            <span className={`text-sm ${row.bold ? "font-semibold text-[#1A202C]" : "text-[#718096]"}`}>
              {row.label}
            </span>
            <span className={`text-sm font-${row.bold ? "bold" : "medium"} ${row.color || "text-[#1A202C]"}`}>
              {formatCurrency(row.value)}
            </span>
          </div>
        ))}
      </div>

      <div className="px-6 py-4 border-t border-[#E2E8F0]">
        <h4 className="text-sm font-semibold text-[#1A202C] mb-3">경비 항목별 내역</h4>
        <div className="space-y-2">
          {data.categoryBreakdown.map((item) => (
            <div key={item.category} className="flex justify-between text-sm">
              <span className="text-[#718096]">{item.label}</span>
              <span className="text-[#1A202C] font-medium">{formatCurrency(item.amount)}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
