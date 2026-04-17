"use client";

import type { MockExpenseItem } from "@/lib/mock-data";
import { formatCurrency, formatDate, CATEGORY_LABELS } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { CheckCircle2, Circle, Trash2 } from "lucide-react";

const CATEGORY_VARIANTS: Record<string, "meal" | "transportation" | "communication" | "office" | "education" | "other"> = {
  MEAL: "meal",
  TRANSPORTATION: "transportation",
  COMMUNICATION: "communication",
  OFFICE_SUPPLIES: "office",
  EDUCATION: "education",
};

interface ExpenseRowProps {
  expense: MockExpenseItem;
  onDelete?: (id: string) => void;
}

export function ExpenseRow({ expense, onDelete }: ExpenseRowProps) {
  return (
    <tr className="border-b border-[#E2E8F0] hover:bg-[#F8FAFC] transition-colors">
      <td className="py-3 px-4">
        <span className="text-sm text-[#1A202C]">{formatDate(expense.date)}</span>
      </td>
      <td className="py-3 px-4">
        <div>
          <p className="text-sm font-medium text-[#1A202C]">{expense.merchantName}</p>
          {expense.memo && (
            <p className="text-xs text-[#718096] mt-0.5">{expense.memo}</p>
          )}
        </div>
      </td>
      <td className="py-3 px-4">
        <Badge variant={CATEGORY_VARIANTS[expense.category] ?? "other"}>
          {CATEGORY_LABELS[expense.category] ?? expense.category}
        </Badge>
      </td>
      <td className="py-3 px-4 text-right">
        <span className="text-sm font-semibold text-[#1A202C]">{formatCurrency(expense.amount)}</span>
      </td>
      <td className="py-3 px-4 text-center">
        <div className="flex items-center justify-center">
          {expense.userVerified ? (
            <CheckCircle2 className="h-4 w-4 text-[#22C55E]" />
          ) : (
            <Circle className="h-4 w-4 text-[#E2E8F0]" />
          )}
        </div>
      </td>
      <td className="py-3 px-4">
        {onDelete && (
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8 text-[#718096] hover:text-[#EF4444]"
            onClick={() => onDelete(expense.id)}
          >
            <Trash2 className="h-3.5 w-3.5" />
          </Button>
        )}
      </td>
    </tr>
  );
}
