import Link from "next/link";
import { FileText } from "lucide-react";

export function Footer() {
  return (
    <footer className="bg-[#1A202C] text-white py-12">
      <div className="max-w-6xl mx-auto px-4 sm:px-6">
        <div className="flex flex-col md:flex-row justify-between gap-8 mb-8">
          <div>
            <div className="flex items-center gap-2 mb-3">
              <div className="w-7 h-7 rounded-lg bg-[#1E3A5F] flex items-center justify-center">
                <FileText className="h-3.5 w-3.5 text-white" />
              </div>
              <span className="font-bold text-white">세금신고 도우미</span>
            </div>
            <p className="text-white/50 text-sm max-w-xs leading-relaxed">
              1인 사업자·프리랜서를 위한 AI 세금 신고 준비 도구.
              세무 대리 행위가 아닙니다.
            </p>
          </div>

          <div className="grid grid-cols-2 gap-8">
            <div>
              <h4 className="font-semibold text-white mb-3 text-sm">서비스</h4>
              <ul className="space-y-2 text-sm text-white/50">
                <li><Link href="/signup" className="hover:text-white transition-colors">무료 시작하기</Link></li>
                <li><Link href="/login" className="hover:text-white transition-colors">로그인</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold text-white mb-3 text-sm">법적 고지</h4>
              <ul className="space-y-2 text-sm text-white/50">
                <li><span>이용약관</span></li>
                <li><span>개인정보처리방침</span></li>
              </ul>
            </div>
          </div>
        </div>

        <div className="border-t border-white/10 pt-6">
          <p className="text-white/30 text-xs text-center">
            본 서비스는 세금 신고 준비 도구로, 세무사법상 세무 대리 행위가 아닙니다.
            최종 신고 책임은 사용자 본인에게 있습니다.
          </p>
        </div>
      </div>
    </footer>
  );
}
