const TRUST_STATS = [
  { value: "97%", label: "OCR 인식 정확도", sub: "Google Vision + GPT-4o 하이브리드" },
  { value: "10초", label: "평균 처리 시간", sub: "영수증 업로드 → AI 분류 완료" },
  { value: "40만원", label: "세무사 비용 절약", sub: "연간 평균 절감액 (무료 플랜 기준)" },
];

export function TrustSection() {
  return (
    <section className="py-20 bg-[#1E3A5F]">
      <div className="max-w-6xl mx-auto px-4 sm:px-6">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-white mb-4">검증된 성능, 신뢰할 수 있는 도구</h2>
          <p className="text-white/60 text-lg">수치로 증명하는 AI 세금 신고 준비 도구</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {TRUST_STATS.map((stat) => (
            <div key={stat.label} className="text-center">
              <div className="text-4xl font-bold text-[#22C55E] mb-2">{stat.value}</div>
              <div className="text-white font-semibold text-lg mb-1">{stat.label}</div>
              <div className="text-white/50 text-sm">{stat.sub}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
