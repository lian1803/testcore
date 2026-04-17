"use client";

import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { AlertTriangle, FileText } from "lucide-react";
import { useAuthStore } from "@/store/auth.store";

interface TaxReturnFormProps {
  onSubmit: (data: { totalIncome: number; otherIncome: number; taxYear: number }) => void;
  loading?: boolean;
}

export function TaxReturnForm({ onSubmit, loading }: TaxReturnFormProps) {
  const user = useAuthStore((s) => s.user);
  const taxYear = user?.businessProfile?.taxYear ?? new Date().getFullYear() - 1;

  const [totalIncome, setTotalIncome] = useState("");
  const [otherIncome, setOtherIncome] = useState("");
  const [errors, setErrors] = useState<{ totalIncome?: string }>({});

  const parseAmount = (v: string) => Number(v.replace(/,/g, "")) || 0;

  const validate = () => {
    const errs: { totalIncome?: string } = {};
    if (!totalIncome || parseAmount(totalIncome) <= 0) {
      errs.totalIncome = "연간 총 매출액을 입력해주세요";
    }
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;
    onSubmit({
      totalIncome: parseAmount(totalIncome),
      otherIncome: parseAmount(otherIncome),
      taxYear,
    });
  };

  const formatInput = (value: string) => {
    const raw = value.replace(/,/g, "");
    if (!raw || isNaN(Number(raw))) return value;
    return Number(raw).toLocaleString("ko-KR");
  };

  return (
    <div className="bg-white rounded-xl border border-[#E2E8F0] shadow-sm p-6">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 rounded-xl bg-[#1E3A5F]/10 flex items-center justify-center">
          <FileText className="h-5 w-5 text-[#1E3A5F]" />
        </div>
        <div>
          <h3 className="text-lg font-semibold text-[#1A202C]">소득 정보 입력</h3>
          <p className="text-sm text-[#718096]">{taxYear}년 귀속 종합소득세 신고서</p>
        </div>
      </div>

      <div className="p-3 bg-[#FEF3C7]/50 border border-[#F59E0B]/30 rounded-xl flex gap-2 mb-6">
        <AlertTriangle className="h-4 w-4 text-[#F59E0B] flex-shrink-0 mt-0.5" />
        <p className="text-xs text-[#92400E]">
          아래 정보는 신고서 초안 계산에만 사용됩니다. 실제 신고는 홈택스에서 직접 하셔야 합니다.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="space-y-1.5">
          <Label htmlFor="totalIncome">연간 총 매출액 (원)</Label>
          <div className="relative">
            <Input
              id="totalIncome"
              value={formatInput(totalIncome)}
              onChange={(e) => setTotalIncome(e.target.value.replace(/,/g, ""))}
              placeholder="48,000,000"
              error={!!errors.totalIncome}
              className="pr-8"
            />
            <span className="absolute right-3 top-1/2 -translate-y-1/2 text-sm text-[#718096]">원</span>
          </div>
          {errors.totalIncome && <p className="text-xs text-[#EF4444]">{errors.totalIncome}</p>}
          <p className="text-xs text-[#718096]">사업 소득 (용역비, 판매 수익 등) 합계</p>
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="otherIncome">기타 소득 (원, 선택)</Label>
          <div className="relative">
            <Input
              id="otherIncome"
              value={formatInput(otherIncome)}
              onChange={(e) => setOtherIncome(e.target.value.replace(/,/g, ""))}
              placeholder="0"
              className="pr-8"
            />
            <span className="absolute right-3 top-1/2 -translate-y-1/2 text-sm text-[#718096]">원</span>
          </div>
          <p className="text-xs text-[#718096]">이자, 배당, 임대 소득 등 기타 소득</p>
        </div>

        <Button type="submit" className="w-full" size="lg" loading={loading}>
          신고서 만들기
        </Button>
      </form>
    </div>
  );
}
