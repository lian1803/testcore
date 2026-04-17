import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Check } from "lucide-react";

const PLANS = [
  {
    name: "무료",
    price: "0원",
    period: "",
    description: "처음 시작하는 분들을 위해",
    features: ["영수증 월 20건", "신고서 연 1회", "경비 대시보드", "PDF 다운로드"],
    cta: "무료로 시작",
    href: "/signup",
    highlighted: false,
    ctaVariant: "outline" as const,
  },
  {
    name: "프리미엄",
    price: "월 9,900원",
    period: "또는 연 79,200원 (33% 할인)",
    description: "세금 신고를 제대로 준비하고 싶은 분들",
    features: [
      "영수증 무제한",
      "신고서 무제한",
      "경비 대시보드",
      "PDF + Excel 다운로드",
      "홈택스 입력 가이드",
      "우선 고객 지원",
    ],
    cta: "지금 구독하기",
    href: "/signup",
    highlighted: true,
    ctaVariant: "accent" as const,
  },
];

export function PricingSection() {
  return (
    <section className="py-20 bg-[#F8FAFC]">
      <div className="max-w-4xl mx-auto px-4 sm:px-6">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-[#1A202C] mb-4">간단하고 투명한 요금제</h2>
          <p className="text-[#718096] text-lg">숨겨진 비용 없이, 필요한 만큼만</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {PLANS.map((plan) => (
            <div
              key={plan.name}
              className={`bg-white rounded-2xl p-8 border-2 relative ${
                plan.highlighted
                  ? "border-[#22C55E] ring-2 ring-[#22C55E]/20 shadow-lg"
                  : "border-[#E2E8F0] shadow-sm"
              }`}
            >
              {plan.highlighted && (
                <div className="absolute -top-3.5 left-1/2 -translate-x-1/2">
                  <span className="bg-[#22C55E] text-white text-xs font-bold px-3 py-1 rounded-full">
                    인기
                  </span>
                </div>
              )}

              <div className="mb-6">
                <h3 className="text-xl font-bold text-[#1A202C] mb-1">{plan.name}</h3>
                <p className="text-[#718096] text-sm mb-4">{plan.description}</p>
                <div className="text-3xl font-bold text-[#1A202C]">{plan.price}</div>
                {plan.period && (
                  <p className="text-sm text-[#718096] mt-1">{plan.period}</p>
                )}
              </div>

              <ul className="space-y-3 mb-8">
                {plan.features.map((feature) => (
                  <li key={feature} className="flex items-center gap-3 text-sm text-[#1A202C]">
                    <Check className="h-4 w-4 text-[#22C55E] flex-shrink-0" />
                    {feature}
                  </li>
                ))}
              </ul>

              <Link href={plan.href}>
                <Button variant={plan.ctaVariant} className="w-full" size="lg">
                  {plan.cta}
                </Button>
              </Link>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
