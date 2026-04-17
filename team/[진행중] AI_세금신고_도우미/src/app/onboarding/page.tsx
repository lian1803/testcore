import { OnboardingWizard } from "@/components/onboarding/OnboardingWizard";
import { FileText } from "lucide-react";
import Link from "next/link";

export default function OnboardingPage() {
  return (
    <div className="min-h-screen bg-[#F8FAFC] flex flex-col items-center justify-center p-6">
      <Link href="/" className="flex items-center gap-2 mb-8">
        <div className="w-9 h-9 rounded-xl bg-[#1E3A5F] flex items-center justify-center">
          <FileText className="h-5 w-5 text-white" />
        </div>
        <span className="font-bold text-[#1E3A5F] text-xl">세금신고 도우미</span>
      </Link>
      <OnboardingWizard />
    </div>
  );
}
