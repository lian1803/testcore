"use client";

import { Progress } from "@/components/ui/progress";
import { useUsage } from "@/hooks/use-usage";
import { useAuthStore } from "@/store/auth.store";
import Link from "next/link";

export function UsageMeter() {
  const { data: usage } = useUsage();
  const user = useAuthStore((s) => s.user);
  const isPremium = user?.planStatus === "PREMIUM";

  if (isPremium) {
    return (
      <div className="px-3 py-2 mx-3 rounded-xl bg-[#22C55E]/10 border border-[#22C55E]/20">
        <p className="text-xs font-medium text-[#16A34A]">프리미엄 구독 중</p>
        <p className="text-xs text-[#16A34A]/70">영수증 무제한 · 신고서 무제한</p>
      </div>
    );
  }

  const percent = usage ? Math.round((usage.receiptUsed / usage.receiptLimit) * 100) : 0;
  const isNearLimit = percent >= 80;

  return (
    <div className="px-3 py-3 mx-3 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0]">
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs font-medium text-[#1A202C]">영수증 사용량</span>
        <span className={`text-xs font-bold ${isNearLimit ? "text-[#EF4444]" : "text-[#718096]"}`}>
          {usage?.receiptUsed}/{usage?.receiptLimit}건
        </span>
      </div>
      <Progress value={percent} className={isNearLimit ? "[&>div]:bg-[#EF4444]" : ""} />
      {isNearLimit && (
        <Link href="/dashboard/settings" className="text-xs text-[#1E3A5F] hover:underline mt-1.5 block">
          업그레이드하면 무제한으로 사용 가능
        </Link>
      )}
    </div>
  );
}
