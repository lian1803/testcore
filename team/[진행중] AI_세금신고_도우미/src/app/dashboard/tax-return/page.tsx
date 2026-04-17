"use client";

import { useState } from "react";
import { HeaderBar } from "@/components/layout/HeaderBar";
import { TaxReturnForm } from "@/components/tax-return/TaxReturnForm";
import { TaxReturnPreview } from "@/components/tax-return/TaxReturnPreview";
import { DownloadButtons } from "@/components/tax-return/DownloadButtons";
import { LoadingSpinner } from "@/components/common/LoadingSpinner";
import { ErrorMessage } from "@/components/common/ErrorMessage";
import { useCreateTaxReturn } from "@/hooks/use-tax-return";
import { MOCK_TAX_RETURN } from "@/lib/mock-data";
import { AlertTriangle } from "lucide-react";

// BUG FIX: 402 무료 한도 초과 에러 미처리 → 업그레이드 안내로 분기
// BUG FIX: onError에서 mock fallback으로 에러를 숨기던 패턴 제거

type PageState = "form" | "generating" | "preview" | "error";

export default function TaxReturnPage() {
  const [pageState, setPageState] = useState<PageState>("form");
  const [taxReturn, setTaxReturn] = useState<typeof MOCK_TAX_RETURN | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isUsageLimitError, setIsUsageLimitError] = useState(false);
  const { mutate: createTaxReturn, isPending } = useCreateTaxReturn();

  const handleSubmit = (data: { totalIncome: number; otherIncome: number; taxYear: number }) => {
    setPageState("generating");
    setErrorMessage(null);
    setIsUsageLimitError(false);
    createTaxReturn(data, {
      onSuccess: (result) => {
        setTaxReturn(result);
        setPageState("preview");
      },
      onError: (err: Error) => {
        // BUG FIX: 무료 플랜 한도 초과(402) 메시지 감지 후 업그레이드 안내 표시
        const msg = err.message ?? "";
        if (msg.includes("한도 초과") || msg.includes("UsageLimit") || msg.includes("402")) {
          setIsUsageLimitError(true);
        }
        setErrorMessage(msg || "신고서 생성 중 오류가 발생했습니다.");
        setPageState("error");
      },
    });
  };

  return (
    <div className="flex flex-col h-full">
      <HeaderBar title="신고서 생성" />

      <div className="flex-1 p-4 sm:p-6">
        {/* 법적 고지 배너 */}
        <div className="mb-6 p-4 bg-[#FEF3C7]/60 border border-[#F59E0B]/40 rounded-xl flex gap-3">
          <AlertTriangle className="h-5 w-5 text-[#F59E0B] flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-[#92400E]">신고 준비 도구 안내</p>
            <p className="text-xs text-[#92400E]/80 mt-1">
              생성되는 신고서는 참고용 초안입니다. 최종 신고는 반드시 홈택스(hometax.go.kr)에서
              직접 하셔야 합니다. 세무사법상 세무 대리 행위가 아닙니다.
            </p>
          </div>
        </div>

        {pageState === "form" && (
          <div className="max-w-lg mx-auto">
            <TaxReturnForm onSubmit={handleSubmit} loading={isPending} />
          </div>
        )}

        {pageState === "generating" && (
          <div className="flex flex-col items-center justify-center h-64 gap-4">
            <LoadingSpinner size="lg" />
            <div className="text-center">
              <p className="text-base font-semibold text-[#1A202C]">신고서를 생성하고 있어요</p>
              <p className="text-sm text-[#718096] mt-1">최대 30초 소요됩니다...</p>
            </div>
            <div className="flex gap-1.5">
              {[0, 1, 2].map((i) => (
                <div key={i} className="w-2 h-2 rounded-full bg-[#1E3A5F] animate-bounce" style={{ animationDelay: `${i * 0.15}s` }} />
              ))}
            </div>
          </div>
        )}

        {pageState === "error" && (
          <div className="max-w-lg mx-auto space-y-4">
            {isUsageLimitError ? (
              <div className="p-6 bg-white rounded-xl border border-[#E2E8F0] shadow-sm text-center space-y-4">
                <p className="text-base font-semibold text-[#1A202C]">무료 플랜 한도 초과</p>
                <p className="text-sm text-[#718096]">
                  무료 플랜은 연 1회 신고서 생성이 가능합니다. 프리미엄으로 업그레이드하면 무제한으로 사용할 수 있습니다.
                </p>
                <a
                  href="/dashboard/settings"
                  className="inline-block px-6 py-2.5 bg-[#1E3A5F] text-white rounded-xl text-sm font-medium hover:bg-[#2D5F8A] transition-colors"
                >
                  프리미엄 업그레이드
                </a>
                <div>
                  <button onClick={() => setPageState("form")} className="text-sm text-[#718096] hover:underline">
                    돌아가기
                  </button>
                </div>
              </div>
            ) : (
              <ErrorMessage
                title="신고서 생성 실패"
                message={errorMessage ?? "일시적인 오류가 발생했습니다."}
                onRetry={() => setPageState("form")}
              />
            )}
          </div>
        )}

        {pageState === "preview" && taxReturn && (
          <div className="max-w-2xl mx-auto space-y-6">
            <TaxReturnPreview data={taxReturn} />
            <DownloadButtons taxReturnId={taxReturn.id} />
            <div className="text-center">
              <button
                onClick={() => setPageState("form")}
                className="text-sm text-[#718096] hover:text-[#1E3A5F] hover:underline"
              >
                다시 계산하기
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
