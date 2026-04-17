import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { MOCK_RECEIPTS } from "@/lib/mock-data";
import type { MockReceipt } from "@/lib/mock-data";

export function useReceipts() {
  return useQuery({
    queryKey: ["receipts"],
    queryFn: async (): Promise<MockReceipt[]> => {
      const res = await fetch("/api/receipts");
      if (!res.ok) {
        // BUG FIX: 에러를 삼키지 않음. 401이면 세션 만료, 500이면 서버 오류.
        // initialData가 있으므로 throw해도 UI는 mock 데이터로 유지됨.
        const err = await res.json().catch(() => ({}));
        throw new Error(err?.detail ?? `영수증 목록 조회 실패 (${res.status})`);
      }
      const json = await res.json();
      // BE 응답 형식: { success: true, data: [...], pagination: {...} }
      return json.data ?? json;
    },
    initialData: MOCK_RECEIPTS,
  });
}

export function useReceipt(id: string) {
  return useQuery({
    queryKey: ["receipts", id],
    queryFn: async (): Promise<MockReceipt> => {
      const res = await fetch(`/api/receipts/${id}`);
      if (!res.ok) throw new Error("Receipt not found");
      const json = await res.json();
      return json.data ?? json;
    },
  });
}

export function useDeleteReceipt() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      const res = await fetch(`/api/receipts/${id}`, { method: "DELETE" });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err?.detail ?? "영수증 삭제에 실패했습니다.");
      }
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["receipts"] });
      queryClient.invalidateQueries({ queryKey: ["expenses"] });
    },
  });
}
