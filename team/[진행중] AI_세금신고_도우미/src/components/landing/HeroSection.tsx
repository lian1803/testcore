import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ArrowRight, Camera, CheckCircle } from "lucide-react";

export function HeroSection() {
  return (
    <section className="min-h-[600px] bg-[#1E3A5F] flex items-center pt-16">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-20 w-full">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          <div className="text-white">
            <div className="inline-flex items-center gap-2 bg-white/10 rounded-full px-4 py-1.5 text-sm text-white/80 mb-6">
              <CheckCircle className="h-4 w-4 text-[#22C55E]" />
              OCR 정확도 97% · 처리 시간 10초
            </div>

            <h1 className="text-4xl md:text-5xl font-bold leading-tight mb-6 text-white">
              영수증 찍으면<br />세금신고 끝
            </h1>

            <p className="text-lg text-white/70 mb-8 leading-relaxed">
              AI가 경비를 자동 분류하고 종합소득세 신고서 초안을 만들어드려요.
              1인 사업자·프리랜서를 위한 절세 파트너.
            </p>

            <div className="flex flex-col sm:flex-row gap-3 mb-6">
              <Link href="/signup">
                <Button
                  variant="accent"
                  size="xl"
                  className="w-full sm:w-auto shadow-lg"
                >
                  무료로 시작하기
                  <ArrowRight className="h-5 w-5" />
                </Button>
              </Link>
            </div>

            <p className="text-sm text-white/50">
              신용카드 불필요 · 영수증 20건 무료 · 언제든 취소 가능
            </p>
          </div>

          <div className="hidden lg:flex justify-center">
            <div className="relative w-72 h-96">
              <div className="absolute inset-0 bg-white/10 rounded-3xl backdrop-blur-sm border border-white/20" />
              <div className="absolute inset-4 bg-white rounded-2xl shadow-2xl p-5 flex flex-col gap-4">
                <div className="flex items-center gap-2 text-xs text-[#718096]">
                  <Camera className="h-4 w-4 text-[#22C55E]" />
                  영수증 AI 분석 완료
                </div>
                <div className="bg-[#F8FAFC] rounded-xl p-3 space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-[#718096]">상호명</span>
                    <span className="font-medium text-[#1A202C]">스타벅스 강남점</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-[#718096]">금액</span>
                    <span className="font-medium text-[#1A202C]">18,000원</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-[#718096]">분류</span>
                    <span className="text-xs bg-[#FEF3C7] text-[#92400E] px-2 py-0.5 rounded-full font-medium">식비</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-[#718096]">날짜</span>
                    <span className="font-medium text-[#1A202C]">2025.03.15</span>
                  </div>
                </div>
                <div className="mt-auto p-3 bg-[#22C55E]/10 rounded-xl border border-[#22C55E]/20">
                  <p className="text-xs text-[#16A34A] font-medium">이 경비로 절세 예상</p>
                  <p className="text-xl font-bold text-[#22C55E]">+2,700원</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
