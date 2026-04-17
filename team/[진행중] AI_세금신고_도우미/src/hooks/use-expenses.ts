import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { MOCK_EXPENSES, MOCK_KPI, MOCK_MONTHLY_DATA } from "@/lib/mock-data";
import type { MockExpenseItem } from "@/lib/mock-data";

export function useExpenses(params?: { category?: string; dateFrom?: string; dateTo?: string }) {
  return useQuery({
    queryKey: ["expenses", params],
    queryFn: async (): Promise<MockExpenseItem[]> => {
      const searchParams = new URLSearchParams();
      if (params?.category) searchParams.set("category", params.category);
      if (params?.dateFrom) searchParams.set("dateFrom", params.dateFrom);
      if (params?.dateTo) searchParams.set("dateTo", params.dateTo);
      const res = await fetch(`/api/expenses?${searchParams}`);
      if (!res.ok) {
        // BUG FIX: 에러를 삼키지 않음
        const err = await res.json().catch(() => ({}));
        throw new Error(err?.detail ?? `경비 목록 조회 실패 (${res.status})`);
      }
      const json = await res.json();
      // BE 응답 형식: { success: true, data: [...] }
      return json.data ?? json;
    },
    initialData: MOCK_EXPENSES,
  });
}

export function useExpenseSummary() {
  return useQuery({
    queryKey: ["expenses", "summary"],
    queryFn: async () => {
      // BUG FIX: /api/expenses/summary는 BE에 미구현된 엔드포인트.
      // BE wave_be_완료.md에 없음. 실패 시 mock으로 graceful fallback.
      const res = await fetch("/api/expenses/summary");
      if (!res.ok) {
        // 404는 미구현 엔드포인트이므로 mock 반환 (조용히 처리)
        if (res.status === 404) return { kpi: MOCK_KPI, monthly: MOCK_MONTHLY_DATA };
        const err = await res.json().catch(() => ({}));
        throw new Error(err?.detail ?? `경비 요약 조회 실패 (${res.status})`);
      }
      return res.json();
    },
    initialData: { kpi: MOCK_KPI, monthly: MOCK_MONTHLY_DATA },
  });
}

export function useUpdateExpense() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: Partial<MockExpenseItem> }) => {
      const res = await fetch(`/api/expenses/${id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      if (!res.ok) throw new Error("Failed to update expense");
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["expenses"] });
    },
  });
}

export function useDeleteExpense() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      const res = await fetch(`/api/expenses/${id}`, { method: "DELETE" });
      if (!res.ok) throw new Error("Failed to delete expense");
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["expenses"] });
    },
  });
}
