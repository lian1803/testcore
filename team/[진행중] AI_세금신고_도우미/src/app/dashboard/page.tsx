"use client";

import Link from "next/link";
import { HeaderBar } from "@/components/layout/HeaderBar";
import { KpiCards } from "@/components/dashboard/KpiCards";
import { MonthlyExpenseChart } from "@/components/dashboard/MonthlyExpenseChart";
import { RecentReceiptsList } from "@/components/dashboard/RecentReceiptsList";
import { EmptyState } from "@/components/common/EmptyState";
import { Button } from "@/components/ui/button";
import { useExpenseSummary } from "@/hooks/use-expenses";
import { useReceipts } from "@/hooks/use-receipts";
import { LoadingSpinner } from "@/components/common/LoadingSpinner";
import { Plus, Receipt } from "lucide-react";

export default function DashboardPage() {
  const { data: summary, isLoading: summaryLoading } = useExpenseSummary();
  const { data: receipts, isLoading: receiptsLoading } = useReceipts();

  const isLoading = summaryLoading || receiptsLoading;

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <LoadingSpinner size="lg" label="데이터를 불러오는 중..." />
      </div>
    );
  }

  const hasData = (receipts?.length ?? 0) > 0;

  return (
    <div className="flex flex-col h-full">
      <HeaderBar
        title="대시보드"
        actions={
          <Link href="/dashboard/receipts">
            <Button variant="accent" size="sm" className="gap-2">
              <Plus className="h-4 w-4" />
              영수증 추가
            </Button>
          </Link>
        }
      />

      <div className="flex-1 p-4 sm:p-6 space-y-6">
        {!hasData ? (
          <EmptyState
            icon={Receipt}
            title="첫 영수증을 추가해보세요"
            description="영수증을 업로드하면 AI가 자동으로 경비를 분류하고 절세 예상액을 계산해 드려요."
            cta={{ label: "영수증 추가하기", href: "/dashboard/receipts" }}
          />
        ) : (
          <>
            <KpiCards
              kpi={summary!.kpi}
              receiptCount={receipts?.length ?? 0}
            />

            <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
              <div className="xl:col-span-2">
                <MonthlyExpenseChart data={summary!.monthly} />
              </div>
              <div>
                <RecentReceiptsList receipts={receipts ?? []} />
              </div>
            </div>
          </>
        )}
      </div>

      {/* 모바일 FAB */}
      <Link
        href="/dashboard/receipts"
        className="fixed bottom-6 right-6 lg:hidden w-14 h-14 bg-[#22C55E] rounded-full flex items-center justify-center shadow-lg hover:bg-[#16A34A] transition-colors z-10"
      >
        <Plus className="h-6 w-6 text-white" />
      </Link>
    </div>
  );
}
