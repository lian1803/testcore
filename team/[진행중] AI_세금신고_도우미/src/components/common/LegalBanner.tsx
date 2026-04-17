import { AlertTriangle } from "lucide-react";

export function LegalBanner() {
  return (
    <div className="bg-[#FEF3C7] border-b border-[#F59E0B]/30 px-4 py-2 flex items-center gap-2">
      <AlertTriangle className="h-4 w-4 text-[#F59E0B] flex-shrink-0" />
      <p className="text-xs text-[#92400E]">
        본 서비스는 세금 신고 준비 도구로, 세무사법상 세무 대리 행위가 아닙니다.
        최종 신고 책임은 사용자 본인에게 있으며, 홈택스에서 직접 신고하셔야 합니다.
      </p>
    </div>
  );
}
