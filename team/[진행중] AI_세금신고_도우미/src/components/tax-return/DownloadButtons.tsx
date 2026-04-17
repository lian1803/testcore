"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { FileDown, ExternalLink, List } from "lucide-react";
import { useDownloadTaxReturn } from "@/hooks/use-tax-return";

interface DownloadButtonsProps {
  taxReturnId: string;
}

const HOMETAX_GUIDE_STEPS = [
  "홈택스(hometax.go.kr) 접속 후 로그인",
  "상단 메뉴 '신고/납부' > '종합소득세' 클릭",
  "신고서 선택 > '일반신고서' 또는 '간편신고서' 선택",
  "수입금액 및 경비를 다운로드한 초안의 수치로 입력",
  "공제 항목 확인 후 신고서 제출",
  "납부세액 확인 후 납부 또는 환급 신청",
];

export function DownloadButtons({ taxReturnId }: DownloadButtonsProps) {
  const [guideOpen, setGuideOpen] = useState(false);
  const { mutate: download, isPending } = useDownloadTaxReturn();

  return (
    <>
      <div className="bg-white rounded-xl border border-[#E2E8F0] shadow-sm p-6">
        <h3 className="text-base font-semibold text-[#1A202C] mb-4">신고서 다운로드</h3>
        <div className="flex flex-col sm:flex-row gap-3 mb-4">
          <Button
            variant="default"
            className="flex-1 gap-2"
            onClick={() => download({ id: taxReturnId, format: "pdf" })}
            loading={isPending}
          >
            <FileDown className="h-4 w-4" />
            PDF 다운로드
          </Button>
          <Button
            variant="outline"
            className="flex-1 gap-2"
            onClick={() => download({ id: taxReturnId, format: "excel" })}
            loading={isPending}
          >
            <FileDown className="h-4 w-4" />
            Excel 다운로드
          </Button>
        </div>

        <div className="border-t border-[#E2E8F0] pt-4">
          <Button
            variant="ghost"
            className="w-full gap-2 text-[#1E3A5F]"
            onClick={() => setGuideOpen(true)}
          >
            <List className="h-4 w-4" />
            홈택스 직접 입력 가이드 보기
          </Button>
        </div>
      </div>

      <Dialog open={guideOpen} onOpenChange={setGuideOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>홈택스 직접 입력 가이드</DialogTitle>
            <DialogDescription>
              다운로드한 신고서 초안을 참고해 홈택스에서 직접 입력하세요.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-3 my-2">
            {HOMETAX_GUIDE_STEPS.map((step, i) => (
              <div key={i} className="flex gap-3">
                <div className="w-6 h-6 rounded-full bg-[#1E3A5F] text-white text-xs font-bold flex items-center justify-center flex-shrink-0">
                  {i + 1}
                </div>
                <p className="text-sm text-[#1A202C] pt-0.5">{step}</p>
              </div>
            ))}
          </div>

          <div className="p-3 bg-[#FEF3C7]/50 border border-[#F59E0B]/30 rounded-xl text-xs text-[#92400E]">
            본 서비스는 신고 준비 도구입니다. 실제 신고는 홈택스에서 직접 하셔야 하며,
            최종 세액 책임은 납세자 본인에게 있습니다.
          </div>

          <a
            href="https://www.hometax.go.kr"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center justify-center gap-2 w-full py-2.5 px-4 bg-[#1E3A5F] text-white rounded-xl text-sm font-medium hover:bg-[#2D5F8A] transition-colors"
          >
            홈택스 바로가기
            <ExternalLink className="h-4 w-4" />
          </a>
        </DialogContent>
      </Dialog>
    </>
  );
}
