import Link from "next/link";
import { FileText, CheckCircle } from "lucide-react";

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen flex">
      {/* 좌측 브랜드 영역 — 데스크탑 전용 */}
      <div className="hidden lg:flex lg:w-1/2 bg-[#1E3A5F] flex-col justify-between p-12">
        <Link href="/" className="flex items-center gap-2">
          <div className="w-9 h-9 rounded-xl bg-white/10 flex items-center justify-center">
            <FileText className="h-5 w-5 text-white" />
          </div>
          <span className="font-bold text-white text-xl">세금신고 도우미</span>
        </Link>

        <div className="space-y-8">
          <div>
            <h2 className="text-3xl font-bold text-white mb-4">
              영수증 찍으면<br />세금신고 끝
            </h2>
            <p className="text-white/60 text-lg leading-relaxed">
              AI가 경비를 자동 분류하고<br />
              종합소득세 신고서 초안을 만들어드려요.
            </p>
          </div>

          <ul className="space-y-4">
            {[
              "OCR 인식 정확도 97%",
              "처리 시간 평균 10초",
              "세무사 비용 연 40만원 절약",
              "홈택스 직접 입력 가이드 포함",
            ].map((item) => (
              <li key={item} className="flex items-center gap-3 text-white/80">
                <CheckCircle className="h-5 w-5 text-[#22C55E] flex-shrink-0" />
                <span className="text-sm">{item}</span>
              </li>
            ))}
          </ul>
        </div>

        <p className="text-white/30 text-xs">
          본 서비스는 세금 신고 준비 도구로, 세무 대리 행위가 아닙니다.
        </p>
      </div>

      {/* 우측 콘텐츠 영역 */}
      <div className="flex-1 flex items-center justify-center p-6 bg-[#F8FAFC]">
        <div className="w-full max-w-md">{children}</div>
      </div>
    </div>
  );
}
