"use client";

import { useState, useMemo } from "react";
import { HeaderBar } from "@/components/layout/HeaderBar";
import { ExpenseTable } from "@/components/expenses/ExpenseTable";
import { ExpenseFilters } from "@/components/expenses/ExpenseFilters";
import { ConfirmDialog } from "@/components/common/ConfirmDialog";
import { EmptyState } from "@/components/common/EmptyState";
import { LoadingSpinner } from "@/components/common/LoadingSpinner";
import { useExpenses, useDeleteExpense } from "@/hooks/use-expenses";
import { List } from "lucide-react";

interface Filters {
  category: string;
  dateFrom: string;
  dateTo: string;
}

const DEFAULT_FILTERS: Filters = { category: "", dateFrom: "", dateTo: "" };

export default function ExpensesPage() {
  const { data: expenses, isLoading } = useExpenses();
  const { mutate: deleteExpense } = useDeleteExpense();
  const [filters, setFilters] = useState<Filters>(DEFAULT_FILTERS);
  const [deleteTarget, setDeleteTarget] = useState<string | null>(null);

  const filtered = useMemo(() => {
    if (!expenses) return [];
    return expenses.filter((e) => {
      if (filters.category && e.category !== filters.category) return false;
      if (filters.dateFrom && e.date < filters.dateFrom) return false;
      if (filters.dateTo && e.date > filters.dateTo) return false;
      return true;
    });
  }, [expenses, filters]);

  return (
    <div className="flex flex-col h-full">
      <HeaderBar title="경비 목록" />

      <div className="flex-1 p-4 sm:p-6 space-y-4">
        <ExpenseFilters
          filters={filters}
          onChange={setFilters}
          onReset={() => setFilters(DEFAULT_FILTERS)}
        />

        {isLoading ? (
          <div className="flex items-center justify-center h-48">
            <LoadingSpinner size="lg" label="경비 목록을 불러오는 중..." />
          </div>
        ) : filtered.length === 0 ? (
          <EmptyState
            icon={List}
            title="경비 내역이 없습니다"
            description="영수증을 업로드하면 AI가 자동으로 경비를 분류합니다."
            cta={{ label: "영수증 추가하기", href: "/dashboard/receipts" }}
          />
        ) : (
          <ExpenseTable
            expenses={filtered}
            onDelete={(id) => setDeleteTarget(id)}
          />
        )}
      </div>

      <ConfirmDialog
        open={!!deleteTarget}
        onOpenChange={(open) => !open && setDeleteTarget(null)}
        title="경비 삭제"
        description="이 경비 항목을 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다."
        confirmLabel="삭제"
        onConfirm={() => {
          if (deleteTarget) deleteExpense(deleteTarget);
          setDeleteTarget(null);
        }}
        destructive
      />
    </div>
  );
}
