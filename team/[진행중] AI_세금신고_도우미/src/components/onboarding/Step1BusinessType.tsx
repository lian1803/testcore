"use client";

import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { BUSINESS_TYPES } from "@/lib/utils";

interface Step1Props {
  value: string;
  onChange: (value: string) => void;
  error?: string;
}

const BUSINESS_EXPENSE_HINTS: Record<string, string> = {
  "940909": "교통비, 통신비, 소프트웨어 구독료, 교육비, 사무용품이 주요 공제 항목입니다.",
  "921501": "장비 구매비, 소품, 편집 소프트웨어, 스튜디오 대여료가 공제됩니다.",
  "721401": "소프트웨어 구독료, 장비, 교육비, 외주 비용이 공제 항목입니다.",
  "859001": "교재, 강의 장비, 온라인 플랫폼 수수료, 교통비가 공제됩니다.",
  "493200": "오토바이 유지비, 보험료, 통신비, 배달용품이 공제됩니다.",
  "472101": "상품 구매비, 포장재, 배송비, 광고비가 공제됩니다.",
  "960901": "업무 관련 재료비, 교통비, 통신비, 교육비가 공제됩니다.",
  "741100": "자료 구매비, 소프트웨어, 교육비, 통신비가 공제됩니다.",
  "731200": "카메라 장비, 조명, 편집 소프트웨어, 스튜디오 대여료가 공제됩니다.",
  "900001": "업종에 따른 일반적 사업 경비가 공제 대상입니다.",
};

export function Step1BusinessType({ value, onChange, error }: Step1Props) {
  const selected = BUSINESS_TYPES.find((b) => b.code === value);
  const hint = value ? BUSINESS_EXPENSE_HINTS[value] : null;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-[#1A202C] mb-2">어떤 일을 하세요?</h2>
        <p className="text-[#718096] text-sm">
          업종에 맞게 공제 항목을 자동으로 설정해 드려요.
        </p>
      </div>

      <div className="space-y-2">
        <Select value={value} onValueChange={onChange}>
          <SelectTrigger error={!!error}>
            <SelectValue placeholder="업종을 선택해주세요" />
          </SelectTrigger>
          <SelectContent>
            {BUSINESS_TYPES.map((business) => (
              <SelectItem key={business.code} value={business.code}>
                {business.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        {error && <p className="text-xs text-[#EF4444]">{error}</p>}
      </div>

      {selected && hint && (
        <div className="p-4 bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl animate-fade-in">
          <p className="text-sm font-medium text-[#1A202C] mb-1">{selected.label}</p>
          <p className="text-xs text-[#718096] mb-2">{selected.description}</p>
          <div className="border-t border-[#E2E8F0] pt-2 mt-2">
            <p className="text-xs text-[#1E3A5F] font-medium mb-1">주요 공제 항목</p>
            <p className="text-xs text-[#718096]">{hint}</p>
          </div>
        </div>
      )}
    </div>
  );
}
