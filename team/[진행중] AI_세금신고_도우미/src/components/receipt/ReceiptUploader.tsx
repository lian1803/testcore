"use client";

import { useState, useRef, useCallback } from "react";
import { Upload, Camera, ImageIcon } from "lucide-react";
import { cn } from "@/lib/utils";

interface ReceiptUploaderProps {
  onFileSelected: (file: File) => void;
  disabled?: boolean;
}

export function ReceiptUploader({ onFileSelected, disabled }: ReceiptUploaderProps) {
  const [isDragOver, setIsDragOver] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFile = useCallback((file: File) => {
    if (!file.type.startsWith("image/")) return;
    onFileSelected(file);
  }, [onFileSelected]);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = () => setIsDragOver(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
  };

  return (
    <div
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onClick={() => !disabled && inputRef.current?.click()}
      className={cn(
        "relative border-2 border-dashed rounded-2xl p-12 flex flex-col items-center justify-center gap-4 cursor-pointer transition-all",
        isDragOver
          ? "border-[#1E3A5F] bg-[#1E3A5F]/5"
          : "border-[#E2E8F0] hover:border-[#2D5F8A] hover:bg-[#F8FAFC]",
        disabled && "opacity-50 cursor-not-allowed"
      )}
    >
      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        capture="environment"
        className="hidden"
        onChange={handleChange}
        disabled={disabled}
      />

      <div className={cn(
        "w-16 h-16 rounded-2xl flex items-center justify-center transition-colors",
        isDragOver ? "bg-[#1E3A5F] text-white" : "bg-[#F1F5F9] text-[#718096]"
      )}>
        <Upload className="h-8 w-8" />
      </div>

      <div className="text-center">
        <p className="text-base font-semibold text-[#1A202C] mb-1">
          {isDragOver ? "여기에 놓으세요" : "영수증 이미지를 업로드하세요"}
        </p>
        <p className="text-sm text-[#718096]">
          드래그앤드롭 또는 클릭하여 선택
        </p>
        <p className="text-xs text-[#718096] mt-1">JPG, PNG, HEIC 지원 · 최대 10MB</p>
      </div>

      <div className="flex gap-3 mt-2">
        <div className="flex items-center gap-1.5 text-xs text-[#718096] bg-white border border-[#E2E8F0] px-3 py-1.5 rounded-lg">
          <Camera className="h-3.5 w-3.5" />
          카메라 촬영
        </div>
        <div className="flex items-center gap-1.5 text-xs text-[#718096] bg-white border border-[#E2E8F0] px-3 py-1.5 rounded-lg">
          <ImageIcon className="h-3.5 w-3.5" />
          갤러리 선택
        </div>
      </div>
    </div>
  );
}
