import { Navbar } from "@/components/landing/Navbar";
import { HeroSection } from "@/components/landing/HeroSection";
import { FeatureCards } from "@/components/landing/FeatureCards";
import { TrustSection } from "@/components/landing/TrustSection";
import { PricingSection } from "@/components/landing/PricingSection";
import { Footer } from "@/components/landing/Footer";
import { MOCK_TESTIMONIALS } from "@/lib/mock-data";
import { Star } from "lucide-react";

export default function LandingPage() {
  return (
    <main className="min-h-screen">
      <Navbar />
      <HeroSection />
      <FeatureCards />
      <TrustSection />

      {/* 이용 후기 섹션 */}
      <section className="py-20 bg-white">
        <div className="max-w-6xl mx-auto px-4 sm:px-6">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-[#1A202C] mb-4">실제 사용자 후기</h2>
            <p className="text-[#718096] text-lg">세무사 없이 혼자 신고에 성공한 분들</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {MOCK_TESTIMONIALS.map((testimonial) => (
              <div key={testimonial.id} className="bg-[#F8FAFC] rounded-2xl p-6 border border-[#E2E8F0]">
                <div className="flex gap-0.5 mb-4">
                  {Array.from({ length: testimonial.rating }).map((_, i) => (
                    <Star key={i} className="h-4 w-4 fill-[#F59E0B] text-[#F59E0B]" />
                  ))}
                </div>
                <p className="text-[#1A202C] text-sm leading-relaxed mb-4">{testimonial.content}</p>
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-semibold text-sm text-[#1A202C]">{testimonial.name}</div>
                    <div className="text-xs text-[#718096]">{testimonial.role}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-xs text-[#718096]">절세 추정액</div>
                    <div className="text-sm font-bold text-[#22C55E]">
                      {testimonial.saving.toLocaleString("ko-KR")}원
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <PricingSection />
      <Footer />
    </main>
  );
}
