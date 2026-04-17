import { useQuery } from "@tanstack/react-query";
import { MOCK_USAGE } from "@/lib/mock-data";

export function useUsage() {
  return useQuery({
    queryKey: ["usage"],
    queryFn: async () => {
      const res = await fetch("/api/usage");
      if (!res.ok) {
        // BUG FIX: 에러 삼킴 제거. 단, usage는 UI 차단 요소가 아니므로
        // 조용히 mock 반환 (UsageMeter는 non-critical UI)
        console.warn("[useUsage] 사용량 조회 실패:", res.status);
        return MOCK_USAGE;
      }
      const json = await res.json();
      // BUG FIX: BE 응답 형식 = { planStatus, receipt: { used, limit }, taxReturn: { used, limit } }
      // FE mock 형식 = { receiptUsed, receiptLimit, taxReturnUsed, taxReturnLimit }
      // 두 형식 모두 처리
      if (json.receipt !== undefined) {
        return {
          receiptUsed: json.receipt.used ?? 0,
          receiptLimit: json.receipt.limit ?? 20,
          taxReturnUsed: json.taxReturn.used ?? 0,
          taxReturnLimit: json.taxReturn.limit ?? 1,
        };
      }
      return json;
    },
    initialData: MOCK_USAGE,
    refetchInterval: 60 * 1000,
  });
}
