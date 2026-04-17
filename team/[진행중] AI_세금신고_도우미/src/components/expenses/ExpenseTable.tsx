import type { MockExpenseItem } from "@/lib/mock-data";
import { ExpenseRow } from "./ExpenseRow";
import { formatCurrency } from "@/lib/utils";

interface ExpenseTableProps {
  expenses: MockExpenseItem[];
  onDelete?: (id: string) => void;
}

export function ExpenseTable({ expenses, onDelete }: ExpenseTableProps) {
  const total = expenses.reduce((sum, e) => sum + e.amount, 0);

  return (
    <div className="bg-white rounded-xl border border-[#E2E8F0] shadow-sm overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-[#E2E8F0] bg-[#F8FAFC]">
              <th className="py-3 px-4 text-left text-xs font-semibold text-[#718096] w-28">날짜</th>
              <th className="py-3 px-4 text-left text-xs font-semibold text-[#718096]">상호명 / 메모</th>
              <th className="py-3 px-4 text-left text-xs font-semibold text-[#718096] w-28">분류</th>
              <th className="py-3 px-4 text-right text-xs font-semibold text-[#718096] w-28">금액</th>
              <th className="py-3 px-4 text-center text-xs font-semibold text-[#718096] w-16">확인</th>
              <th className="py-3 px-4 w-10" />
            </tr>
          </thead>
          <tbody>
            {expenses.map((expense) => (
              <ExpenseRow key={expense.id} expense={expense} onDelete={onDelete} />
            ))}
          </tbody>
          <tfoot>
            <tr className="border-t border-[#E2E8F0] bg-[#F8FAFC]">
              <td colSpan={3} className="py-3 px-4 text-sm font-semibold text-[#1A202C]">
                합계 ({expenses.length}건)
              </td>
              <td className="py-3 px-4 text-right text-sm font-bold text-[#1A202C]">
                {formatCurrency(total)}
              </td>
              <td colSpan={2} />
            </tr>
          </tfoot>
        </table>
      </div>
    </div>
  );
}
