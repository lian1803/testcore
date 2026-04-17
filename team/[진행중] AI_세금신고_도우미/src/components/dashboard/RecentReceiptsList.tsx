import Link from "next/link";
import type { MockReceipt } from "@/lib/mock-data";
import { formatCurrency, formatRelativeDate, CATEGORY_LABELS } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { ArrowRight, ImageIcon } from "lucide-react";

const CATEGORY_VARIANTS: Record<string, "meal" | "transportation" | "communication" | "office" | "education" | "other"> = {
  MEAL: "meal",
  TRANSPORTATION: "transportation",
  COMMUNICATION: "communication",
  OFFICE_SUPPLIES: "office",
  EDUCATION: "education",
};

interface RecentReceiptsListProps {
  receipts: MockReceipt[];
}

export function RecentReceiptsList({ receipts }: RecentReceiptsListProps) {
  const recent = receipts.slice(0, 5);

  return (
    <div className="bg-white rounded-xl border border-[#E2E8F0] shadow-sm p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-[#1A202C]">최근 영수증</h3>
        <Link href="/dashboard/receipts" className="text-sm text-[#1E3A5F] hover:underline flex items-center gap-1">
          전체 보기 <ArrowRight className="h-3.5 w-3.5" />
        </Link>
      </div>

      <div className="space-y-3">
        {recent.map((receipt) => (
          <div key={receipt.id} className="flex items-center gap-3 p-3 rounded-xl hover:bg-[#F8FAFC] transition-colors">
            <div className="w-10 h-10 rounded-lg bg-[#F1F5F9] flex items-center justify-center flex-shrink-0">
              <ImageIcon className="h-5 w-5 text-[#718096]" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-[#1A202C] truncate">{receipt.merchantName}</p>
              <p className="text-xs text-[#718096]">{formatRelativeDate(receipt.date)}</p>
            </div>
            <Badge variant={CATEGORY_VARIANTS[receipt.category] ?? "other"} className="flex-shrink-0">
              {CATEGORY_LABELS[receipt.category] ?? receipt.category}
            </Badge>
            <div className="text-sm font-semibold text-[#1A202C] flex-shrink-0">
              {formatCurrency(receipt.amount)}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
