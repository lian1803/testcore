"use client";

import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { TAX_TYPE_LABELS } from "@/lib/utils";

interface Step2Props {
  taxationType: string;
  registrationNumber: string;
  onTaxationTypeChange: (value: string) => void;
  onRegistrationNumberChange: (value: string) => void;
  error?: string;
}

const TAX_TYPE_DESCRIPTIONS: Record<string, string> = {
  GENERAL: "연 매출 8,000만원 이상이거나 일반과세자로 등록한 경우. 부가세 신고 의무 있음.",
  SIMPLIFIED: "연 매출 8,000만원 미만의 소규모 사업자. 부가세 납부 의무 간소화.",
  TAX_FREE: "의료, 교육 등 부가세가 면제되는 업종. 부가세 신고 불필요.",
  INCOME_ONLY: "사업자등록 없이 프리랜서로 활동 중. 원천징수 후 종합소득세 신고.",
};

const TAX_TYPES = ["GENERAL", "SIMPLIFIED", "TAX_FREE", "INCOME_ONLY"] as const;

export function Step2TaxationType({
  taxationType,
  registrationNumber,
  onTaxationTypeChange,
  onRegistrationNumberChange,
  error,
}: Step2Props) {
  const formatRegNum = (value: string) => {
    const digits = value.replace(/\D/g, "").slice(0, 10);
    if (digits.length <= 3) return digits;
    if (digits.length <= 5) return `${digits.slice(0, 3)}-${digits.slice(3)}`;
    return `${digits.slice(0, 3)}-${digits.slice(3, 5)}-${digits.slice(5)}`;
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-[#1A202C] mb-2">사업자 정보를 입력해주세요</h2>
        <p className="text-[#718096] text-sm">
          과세 유형에 따라 공제 항목과 계산 방식이 달라집니다.
        </p>
      </div>

      <div className="space-y-2">
        <Label className="text-sm font-semibold">과세 유형</Label>
        <RadioGroup value={taxationType} onValueChange={onTaxationTypeChange} className="space-y-3">
          {TAX_TYPES.map((type) => (
            <label
              key={type}
              className={`flex items-start gap-4 p-4 rounded-xl border-2 cursor-pointer transition-colors ${
                taxationType === type
                  ? "border-[#1E3A5F] bg-[#1E3A5F]/5"
                  : "border-[#E2E8F0] hover:border-[#2D5F8A]/40"
              }`}
            >
              <RadioGroupItem value={type} className="mt-0.5" />
              <div>
                <p className="text-sm font-medium text-[#1A202C]">{TAX_TYPE_LABELS[type]}</p>
                <p className="text-xs text-[#718096] mt-0.5">{TAX_TYPE_DESCRIPTIONS[type]}</p>
              </div>
            </label>
          ))}
        </RadioGroup>
        {error && <p className="text-xs text-[#EF4444]">{error}</p>}
      </div>

      <div className="space-y-1.5">
        <Label htmlFor="regNum">사업자등록번호 (선택)</Label>
        <Input
          id="regNum"
          placeholder="000-00-00000 (선택사항)"
          value={registrationNumber}
          onChange={(e) => onRegistrationNumberChange(formatRegNum(e.target.value))}
        />
        <p className="text-xs text-[#718096]">미입력 시 프리랜서로 처리됩니다.</p>
      </div>
    </div>
  );
}
