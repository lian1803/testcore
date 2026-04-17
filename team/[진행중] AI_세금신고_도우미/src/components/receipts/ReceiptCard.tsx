"use client";

import type { MockReceipt } from "@/lib/mock-data";
import { formatCurrency, formatDate, CATEGORY_LABELS } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Trash2, ImageIcon, CheckCircle2, AlertCircle } from "lucide-react";

const CATEGORY_VARIANTS: Record<string, "meal" | "transportation" | "communication" | "office" | "education" | "other"> = {
  MEAL: "meal",
  TRANSPORTATION: "transportation",
  COMMUNICATION: "communication",
  OFFICE_SUPPLIES: "office",
  EDUCATION: "education",
};

interface ReceiptCardProps {
  receipt: MockReceipt;
  onDelete?: (id: string) => void;
}

export function ReceiptCard({ receipt, onDelete }: ReceiptCardProps) {
  const isLowConfidence = receipt.ocrConfidence < 0.9;

  return (
    <div className="bg-white rounded-xl border border-[#E2E8F0] shadow-sm p-4 flex items-center gap-4 hover:shadow-md transition-shadow">
      <div className="w-12 h-12 rounded-xl bg-[#F1F5F9] flex items-center justify-center flex-shrink-0">
        <ImageIcon className="h-6 w-6 text-[#718096]" />
      </div>

      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <p className="text-sm font-medium text-[#1A202C] truncate">{receipt.merchantName}</p>
          {isLowConfidence ? (
            <AlertCircle className="h-3.5 w-3.5 text-[#F59E0B] flex-shrink-0" />
          ) : (
            <CheckCircle2 className="h-3.5 w-3.5 text-[#22C55E] flex-shrink-0" />
          )}
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-xs text-[#718096]">{formatDate(receipt.date)}</span>
          <Badge variant={CATEGORY_VARIANTS[receipt.category] ?? "other"}>
            {CATEGORY_LABELS[receipt.category] ?? receipt.category}
          </Badge>
        </div>
      </div>

      <div className="text-right flex-shrink-0">
        <p className="text-sm font-bold text-[#1A202C]">{formatCurrency(receipt.amount)}</p>
        <p className="text-xs text-[#718096]">신뢰도 {Math.round(receipt.ocrConfidence * 100)}%</p>
      </div>

      {onDelete && (
        <Button
          variant="ghost"
          size="icon"
          className="text-[#718096] hover:text-[#EF4444] flex-shrink-0"
          onClick={() => onDelete(receipt.id)}
        >
          <Trash2 className="h-4 w-4" />
        </Button>
      )}
    </div>
  );
}
