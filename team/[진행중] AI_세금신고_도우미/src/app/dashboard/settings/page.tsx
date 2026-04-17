"use client";

import { useState } from "react";
import { HeaderBar } from "@/components/layout/HeaderBar";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useAuthStore } from "@/store/auth.store";
import { useUsage } from "@/hooks/use-usage";
import { Progress } from "@/components/ui/progress";
import { MOCK_PREMIUM_SUBSCRIPTION } from "@/lib/mock-data";
import { Check, CreditCard, Zap } from "lucide-react";

const PREMIUM_FEATURES = [
  "영수증 무제한 업로드",
  "신고서 무제한 생성",
  "PDF + Excel 다운로드",
  "홈택스 입력 가이드",
  "우선 고객 지원",
];

export default function SettingsPage() {
  const user = useAuthStore((s) => s.user);
  const { data: usage } = useUsage();
  const [checkoutLoading, setCheckoutLoading] = useState(false);
  const isPremium = user?.planStatus === "PREMIUM";

  const handleCheckout = async (plan: "monthly" | "annual") => {
    setCheckoutLoading(true);
    try {
      const res = await fetch("/api/billing/checkout", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ plan }),
      });
      const data = await res.json();
      if (data.url) window.location.href = data.url;
    } catch {
      alert("결제 연결에 실패했습니다. 잠시 후 다시 시도해주세요.");
    } finally {
      setCheckoutLoading(false);
    }
  };

  const usagePercent = usage ? Math.round((usage.receiptUsed / usage.receiptLimit) * 100) : 0;

  return (
    <div className="flex flex-col h-full">
      <HeaderBar title="설정 / 결제" />

      <div className="flex-1 p-4 sm:p-6 space-y-6 max-w-2xl">
        {/* 현재 플랜 */}
        <div className="bg-white rounded-xl border border-[#E2E8F0] shadow-sm p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-base font-semibold text-[#1A202C]">현재 플랜</h3>
            <Badge variant={isPremium ? "accent" : "secondary"}>
              {isPremium ? "프리미엄" : "무료"}
            </Badge>
          </div>

          {!isPremium && usage && (
            <div className="space-y-3">
              <div className="space-y-1.5">
                <div className="flex justify-between text-sm">
                  <span className="text-[#718096]">영수증 사용량</span>
                  <span className={`font-medium ${usagePercent >= 80 ? "text-[#EF4444]" : "text-[#1A202C]"}`}>
                    {usage.receiptUsed} / {usage.receiptLimit}건
                  </span>
                </div>
                <Progress value={usagePercent} className={usagePercent >= 80 ? "[&>div]:bg-[#EF4444]" : ""} />
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-[#718096]">신고서 생성</span>
                <span className="font-medium text-[#1A202C]">
                  {usage.taxReturnUsed} / {usage.taxReturnLimit}회
                </span>
              </div>
            </div>
          )}

          {isPremium && (
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-[#718096]">구독 갱신일</span>
                <span className="font-medium text-[#1A202C]">{MOCK_PREMIUM_SUBSCRIPTION.currentPeriodEnd}</span>
              </div>
              <div className="flex items-center gap-2">
                <CreditCard className="h-4 w-4 text-[#718096]" />
                <span className="text-sm text-[#718096]">
                  {MOCK_PREMIUM_SUBSCRIPTION.paymentMethod?.brand?.toUpperCase()} ****{MOCK_PREMIUM_SUBSCRIPTION.paymentMethod?.last4}
                </span>
              </div>
            </div>
          )}
        </div>

        {/* 업그레이드 플랜 */}
        {!isPremium && (
          <div className="bg-white rounded-xl border-2 border-[#22C55E] shadow-sm p-6">
            <div className="flex items-center gap-2 mb-4">
              <Zap className="h-5 w-5 text-[#22C55E]" />
              <h3 className="text-base font-semibold text-[#1A202C]">프리미엄으로 업그레이드</h3>
            </div>

            <ul className="space-y-2 mb-6">
              {PREMIUM_FEATURES.map((f) => (
                <li key={f} className="flex items-center gap-2 text-sm text-[#1A202C]">
                  <Check className="h-4 w-4 text-[#22C55E] flex-shrink-0" />
                  {f}
                </li>
              ))}
            </ul>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div className="border border-[#E2E8F0] rounded-xl p-4 text-center">
                <p className="text-xs text-[#718096] mb-1">월간 구독</p>
                <p className="text-2xl font-bold text-[#1A202C]">9,900원</p>
                <p className="text-xs text-[#718096]">/ 월</p>
                <Button
                  className="w-full mt-3"
                  size="sm"
                  onClick={() => handleCheckout("monthly")}
                  loading={checkoutLoading}
                >
                  월간 구독하기
                </Button>
              </div>
              <div className="border-2 border-[#22C55E] rounded-xl p-4 text-center bg-[#22C55E]/5">
                <div className="text-xs font-bold text-[#22C55E] mb-1">33% 할인</div>
                <p className="text-2xl font-bold text-[#1A202C]">79,200원</p>
                <p className="text-xs text-[#718096]">/ 연</p>
                <Button
                  variant="accent"
                  className="w-full mt-3"
                  size="sm"
                  onClick={() => handleCheckout("annual")}
                  loading={checkoutLoading}
                >
                  연간 구독하기
                </Button>
              </div>
            </div>
          </div>
        )}

        {/* 계정 정보 */}
        <div className="bg-white rounded-xl border border-[#E2E8F0] shadow-sm p-6">
          <h3 className="text-base font-semibold text-[#1A202C] mb-4">계정 정보</h3>
          <div className="space-y-3 text-sm">
            <div className="flex justify-between">
              <span className="text-[#718096]">이름</span>
              <span className="text-[#1A202C] font-medium">{user?.name}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-[#718096]">이메일</span>
              <span className="text-[#1A202C] font-medium">{user?.email}</span>
            </div>
            {user?.businessProfile && (
              <>
                <div className="flex justify-between">
                  <span className="text-[#718096]">업종</span>
                  <span className="text-[#1A202C] font-medium">{user.businessProfile.businessTypeLabel}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[#718096]">신고 연도</span>
                  <span className="text-[#1A202C] font-medium">{user.businessProfile.taxYear}년</span>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
