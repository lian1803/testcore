import { Camera, Tag, FileDown } from "lucide-react";

const FEATURES = [
  {
    icon: Camera,
    title: "OCR 자동 인식",
    description: "영수증 사진 한 장으로 날짜·금액·상호명 자동 추출, 정확도 97%",
    iconBg: "bg-blue-50",
    iconColor: "text-[#1E3A5F]",
  },
  {
    icon: Tag,
    title: "AI 자동 분류",
    description: "GPT-4o가 업종에 맞게 경비 항목 자동 분류. 오분류 시 한 번에 수정",
    iconBg: "bg-green-50",
    iconColor: "text-[#22C55E]",
  },
  {
    icon: FileDown,
    title: "신고서 초안 생성",
    description: "종합소득세 신고서 PDF/Excel 자동 생성. 홈택스 직접 입력 가이드 포함",
    iconBg: "bg-orange-50",
    iconColor: "text-[#F59E0B]",
  },
];

export function FeatureCards() {
  return (
    <section className="py-20 bg-[#F8FAFC]">
      <div className="max-w-6xl mx-auto px-4 sm:px-6">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-[#1A202C] mb-4">
            세금 신고, 이렇게 쉬워집니다
          </h2>
          <p className="text-lg text-[#718096]">
            영수증 촬영 한 번으로 시작하는 스마트 세금 준비
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {FEATURES.map((feature) => {
            const Icon = feature.icon;
            return (
              <div
                key={feature.title}
                className="bg-white rounded-2xl p-8 shadow-sm border border-[#E2E8F0] hover:shadow-md transition-shadow"
              >
                <div className={`w-12 h-12 ${feature.iconBg} rounded-xl flex items-center justify-center mb-6`}>
                  <Icon className={`h-6 w-6 ${feature.iconColor}`} />
                </div>
                <h3 className="text-xl font-semibold text-[#1A202C] mb-3">{feature.title}</h3>
                <p className="text-[#718096] leading-relaxed">{feature.description}</p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
