"use client";

import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { AlertCircle } from "lucide-react";

interface Step3Props {
  taxYear: string;
  onChange: (value: string) => void;
  error?: string;
}

export function Step3TaxYear({ taxYear, onChange, error }: Step3Props) {
  const currentYear = new Date().getFullYear();
  const years = [currentYear - 1, currentYear - 2, currentYear - 3].map(String);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-[#1A202C] mb-2">몇 년도 세금을 준비하시나요?</h2>
        <p className="text-[#718096] text-sm">
          신고 대상 연도를 선택하면 해당 연도 경비를 관리할 수 있습니다.
        </p>
      </div>

      <div className="space-y-2">
        <Label>신고 대상 연도</Label>
        <Select value={taxYear} onValueChange={onChange}>
          <SelectTrigger error={!!error}>
            <SelectValue placeholder="연도 선택" />
          </SelectTrigger>
          <SelectContent>
            {years.map((year) => (
              <SelectItem key={year} value={year}>
                {year}년 귀속분
                {year === String(currentYear - 1) ? " (권장)" : ""}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        {error && <p className="text-xs text-[#EF4444]">{error}</p>}
      </div>

      <div className="p-4 bg-[#FEF3C7]/40 border border-[#F59E0B]/40 rounded-xl flex gap-3">
        <AlertCircle className="h-5 w-5 text-[#F59E0B] flex-shrink-0 mt-0.5" />
        <div>
          <p className="text-sm font-medium text-[#92400E]">종합소득세 신고 기간 안내</p>
          <p className="text-xs text-[#92400E]/80 mt-1">
            매년 5월 1일 ~ 5월 31일. 성실신고확인대상자는 6월 30일까지.
            국세청 홈택스(hometax.go.kr)에서 직접 신고하세요.
          </p>
        </div>
      </div>

      <div className="p-4 bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl">
        <p className="text-xs font-medium text-[#1A202C] mb-2">이제 대시보드에서 할 수 있는 것</p>
        <ul className="text-xs text-[#718096] space-y-1">
          <li>· 영수증 촬영 업로드 → AI 자동 분류</li>
          <li>· 월별 경비 현황 차트 확인</li>
          <li>· 종합소득세 신고서 초안 PDF/Excel 다운로드</li>
          <li>· 홈택스 직접 입력 가이드 제공</li>
        </ul>
      </div>
    </div>
  );
}
