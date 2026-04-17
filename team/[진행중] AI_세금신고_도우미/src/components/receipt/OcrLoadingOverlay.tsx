"use client";

import { useEffect, useState } from "react";
import { LoadingSpinner } from "@/components/common/LoadingSpinner";

const OCR_STAGES = [
  "이미지 업로드 중...",
  "이미지 분석 중...",
  "텍스트 인식 중...",
  "AI 카테고리 분류 중...",
  "결과 정리 중...",
];

interface OcrLoadingOverlayProps {
  imagePreviewUrl: string | null;
}

export function OcrLoadingOverlay({ imagePreviewUrl }: OcrLoadingOverlayProps) {
  const [stageIndex, setStageIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setStageIndex((prev) => Math.min(prev + 1, OCR_STAGES.length - 1));
    }, 1800);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="relative rounded-2xl overflow-hidden border border-[#E2E8F0] bg-[#1A202C]">
      {imagePreviewUrl && (
        <img
          src={imagePreviewUrl}
          alt="영수증 미리보기"
          className="w-full h-64 object-cover opacity-30"
        />
      )}
      {!imagePreviewUrl && <div className="w-full h-64 bg-gray-800" />}

      {/* 스캔 라인 */}
      <div className="scan-overlay absolute inset-0 pointer-events-none" />

      {/* 오버레이 */}
      <div className="absolute inset-0 flex flex-col items-center justify-center gap-4">
        <LoadingSpinner size="lg" className="text-white [&>svg]:text-white" />
        <div className="text-center">
          <p className="text-white font-semibold text-base">{OCR_STAGES[stageIndex]}</p>
          <p className="text-white/50 text-xs mt-1">최대 10초 소요됩니다</p>
        </div>
        <div className="flex gap-1.5 mt-2">
          {OCR_STAGES.map((_, i) => (
            <div
              key={i}
              className={`h-1.5 rounded-full transition-all duration-300 ${
                i <= stageIndex ? "w-6 bg-[#22C55E]" : "w-2 bg-white/30"
              }`}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
