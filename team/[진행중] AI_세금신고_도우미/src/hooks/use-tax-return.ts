import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { MOCK_TAX_RETURN } from "@/lib/mock-data";

export function useTaxReturn(id?: string) {
  return useQuery({
    queryKey: ["tax-return", id],
    queryFn: async () => {
      if (!id) return null;
      const res = await fetch(`/api/tax-return/${id}`);
      if (!res.ok) {
        // BUG FIX: 에러를 삼키지 않고 throw — mock 반환은 실제 오류를 숨김
        const err = await res.json().catch(() => ({}));
        throw new Error(err?.detail ?? "신고서 조회에 실패했습니다.");
      }
      const json = await res.json();
      return json.data ?? json;
    },
    enabled: !!id,
  });
}

export function useCreateTaxReturn() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: { totalIncome: number; otherIncome: number; taxYear: number }) => {
      const res = await fetch("/api/tax-return", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        // BUG FIX: 402 무료 플랜 한도 초과 에러를 명시적으로 throw
        // 호출자(page.tsx)의 onError에서 업그레이드 모달로 연결해야 함
        throw new Error(err?.detail ?? "신고서 생성에 실패했습니다.");
      }
      const json = await res.json();
      return json.data ?? json;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tax-return"] });
      queryClient.invalidateQueries({ queryKey: ["usage"] });
    },
  });
}

export function useDownloadTaxReturn() {
  return useMutation({
    mutationFn: async ({ id, format }: { id: string; format: "pdf" | "excel" }) => {
      const res = await fetch(`/api/tax-return/${id}/download?format=${format}`);
      if (!res.ok) throw new Error("다운로드에 실패했습니다");
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      // BUG FIX: BE 명세에서 다운로드 파일명은 "tax-return-{year}-draft.pdf/xlsx"
      // 신고서 id만으로는 연도를 알 수 없어 일단 id 기반 유지, draft 명시 추가
      a.download = `tax-return-draft-${id}.${format === "pdf" ? "pdf" : "xlsx"}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    },
  });
}
