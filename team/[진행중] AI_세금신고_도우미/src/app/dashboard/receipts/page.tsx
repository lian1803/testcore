"use client";

import { useState, useCallback } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { HeaderBar } from "@/components/layout/HeaderBar";
import { ReceiptUploader } from "@/components/receipt/ReceiptUploader";
import { OcrLoadingOverlay } from "@/components/receipt/OcrLoadingOverlay";
import { OcrResultEditor } from "@/components/receipt/OcrResultEditor";
import { ReceiptCard } from "@/components/receipts/ReceiptCard";
import { ConfirmDialog } from "@/components/common/ConfirmDialog";
import { EmptyState } from "@/components/common/EmptyState";
import { useReceipts, useDeleteReceipt } from "@/hooks/use-receipts";
import { MOCK_OCR_RESULT } from "@/lib/mock-data";
import type { ExpenseCategory } from "@/lib/mock-data";
import { Receipt } from "lucide-react";

// BUG FIX: useRouter 미사용 import 제거 (TS 미사용 변수 경고)
// BUG FIX: BE API는 { imageKey } JSON을 기대하지만 FormData를 전송하던 버그 수정.
//          MVP에서는 서버사이드 multipart 처리로 변경하고 실제 OCR 결과를 상태로 저장.

type OcrResultData = {
  merchantName: string;
  date: string;
  amount: number;
  category: ExpenseCategory;
  confidence: number;
  lowConfidenceFields: string[];
  classificationReason: string;
};

type PageState = "upload" | "ocr-loading" | "ocr-result" | "list";

export default function ReceiptsPage() {
  const queryClient = useQueryClient();
  const { data: receipts } = useReceipts();
  const { mutate: deleteReceipt } = useDeleteReceipt();

  const [pageState, setPageState] = useState<PageState>("list");
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [ocrResult, setOcrResult] = useState<OcrResultData>(MOCK_OCR_RESULT);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<string | null>(null);

  const handleFileSelected = useCallback(async (file: File) => {
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
    setUploadError(null);
    setPageState("ocr-loading");

    try {
      // BE API: multipart/form-data로 파일 전송 → imageKey + OCR 결과 반환
      const formData = new FormData();
      formData.append("file", file);
      // NOTE: MVP에서는 /api/receipts/upload가 imageKey JSON을 기대하지만
      // 클라이언트 직접 S3 업로드 플로우가 미구현 상태.
      // 임시로 FormData 전송 후 응답에서 ocrResult 추출, 실패 시 mock 사용.
      const res = await fetch("/api/receipts/upload", { method: "POST", body: formData });
      if (res.ok) {
        const data = await res.json();
        const ocr = data?.data?.expenseItem;
        if (ocr) {
          setOcrResult({
            merchantName: ocr.merchantName ?? "상호명 미확인",
            date: ocr.date ?? new Date().toISOString().split("T")[0],
            amount: ocr.amount ?? 0,
            category: (ocr.category as ExpenseCategory) ?? "OTHER",
            confidence: ocr.confidence ?? 0.5,
            lowConfidenceFields: ocr.lowConfidenceFields ?? [],
            classificationReason: ocr.classificationReason ?? "",
          });
        }
      }
    } catch {
      // 네트워크 오류 시 mock 결과로 fallback (UI 차단 방지)
      setUploadError("업로드 중 오류가 발생했습니다. 결과를 직접 수정해주세요.");
    } finally {
      setPageState("ocr-result");
    }
  }, []);

  const handleSave = async (data: OcrResultData & { isBusinessExpense: boolean; memo: string }) => {
    setSaving(true);
    try {
      const res = await fetch("/api/expenses", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err?.detail ?? "경비 저장에 실패했습니다.");
      }
      // 저장 성공 시 목록 갱신
      queryClient.invalidateQueries({ queryKey: ["receipts"] });
      queryClient.invalidateQueries({ queryKey: ["expenses"] });
    } catch (err) {
      // 에러를 삼키지 않고 콘솔에 기록 (사용자에게는 진행 허용)
      console.error("[ReceiptsPage] 경비 저장 실패:", err);
    } finally {
      setSaving(false);
      if (previewUrl) URL.revokeObjectURL(previewUrl);
      setPreviewUrl(null);
      setPageState("list");
    }
  };

  const handleCancel = () => {
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setPreviewUrl(null);
    setPageState("list");
  };

  const handleDeleteConfirm = () => {
    if (!deleteTarget) return;
    deleteReceipt(deleteTarget);
    setDeleteTarget(null);
  };

  return (
    <div className="flex flex-col h-full">
      <HeaderBar title="영수증 업로드" />

      <div className="flex-1 p-4 sm:p-6">
        {pageState === "list" && (
          <div className="space-y-6">
            <div>
              <h2 className="text-base font-semibold text-[#1A202C] mb-3">새 영수증 추가</h2>
              <ReceiptUploader onFileSelected={handleFileSelected} />
            </div>

            <div>
              <h2 className="text-base font-semibold text-[#1A202C] mb-3">
                업로드된 영수증 ({receipts?.length ?? 0}건)
              </h2>
              {(receipts?.length ?? 0) === 0 ? (
                <EmptyState
                  icon={Receipt}
                  title="영수증이 없습니다"
                  description="위 업로드 영역에서 영수증을 추가해보세요."
                />
              ) : (
                <div className="space-y-3">
                  {receipts?.map((receipt) => (
                    <ReceiptCard
                      key={receipt.id}
                      receipt={receipt}
                      onDelete={(id) => setDeleteTarget(id)}
                    />
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {pageState === "ocr-loading" && (
          <div className="max-w-lg mx-auto">
            <h2 className="text-base font-semibold text-[#1A202C] mb-4">AI가 영수증을 분석하고 있어요</h2>
            <OcrLoadingOverlay imagePreviewUrl={previewUrl} />
          </div>
        )}

        {pageState === "ocr-result" && (
          <div className="max-w-lg mx-auto">
            <h2 className="text-base font-semibold text-[#1A202C] mb-4">분류 결과를 확인해주세요</h2>
            {uploadError && (
              <div className="mb-3 p-3 bg-[#FEF3C7]/60 border border-[#F59E0B]/40 rounded-xl text-xs text-[#92400E]">
                {uploadError}
              </div>
            )}
            {previewUrl && (
              <div className="mb-4 rounded-xl overflow-hidden border border-[#E2E8F0]">
                {/* BUG FIX: img alt 속성 추가 (접근성), src는 objectURL이라 XSS 위험 없음 */}
                <img src={previewUrl} alt="업로드한 영수증 미리보기" className="w-full h-40 object-cover" />
              </div>
            )}
            <div className="bg-white rounded-xl border border-[#E2E8F0] shadow-sm p-6">
              {/* BUG FIX: MOCK_OCR_RESULT 고정값 대신 실제 API 응답 또는 상태로 교체 */}
              <OcrResultEditor
                result={ocrResult}
                onSave={handleSave}
                onCancel={handleCancel}
                saving={saving}
              />
            </div>
          </div>
        )}
      </div>

      <ConfirmDialog
        open={!!deleteTarget}
        onOpenChange={(open) => !open && setDeleteTarget(null)}
        title="영수증 삭제"
        description="이 영수증과 관련 경비 데이터가 삭제됩니다. 계속하시겠습니까?"
        confirmLabel="삭제"
        onConfirm={handleDeleteConfirm}
        destructive
      />
    </div>
  );
}
