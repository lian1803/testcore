"use client";

import { motion } from "framer-motion";
import { CreditCard, ArrowUpRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { pricingPlans, settingsData } from "@/lib/mock-data";
import { toast } from "sonner";

/* ─── Current Plan Card ──────────────────────────────– */
function CurrentPlanCard() {
  const handlePortal = () => {
    toast.success("Stripe 결제 관리 페이지가 열립니다.");
    // window.open("https://billing.stripe.com/...", "_blank");
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="rounded-xl border border-white/7 p-8"
      style={{ background: "var(--bg-elevated)" }}
    >
      <div className="mb-6">
        <h2 className="text-lg font-bold text-white mb-1">현재 플랜</h2>
        <p className="text-xs text-zinc-500">구독 정보 및 사용량</p>
      </div>

      <div className="mb-8">
        <div className="flex items-baseline gap-2 mb-6">
          <span className="text-4xl font-bold text-white">{settingsData.plan.name}</span>
          <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
            settingsData.plan.status === "trial"
              ? "bg-amber-500/10 text-amber-400"
              : settingsData.plan.status === "active"
              ? "bg-green-500/10 text-green-400"
              : "bg-red-500/10 text-red-400"
          }`}>
            {settingsData.plan.status === "trial"
              ? `${settingsData.plan.trialDaysRemaining}일 남음`
              : settingsData.plan.status === "active"
              ? "활성"
              : "만료됨"}
          </span>
        </div>

        {/* Usage Bars */}
        <div className="space-y-6">
          <div>
            <div className="flex justify-between mb-2">
              <span className="text-xs text-zinc-400">AI 인사이트</span>
              <span className="text-xs font-semibold text-white">
                {settingsData.usage.aiInsights} / {settingsData.usage.maxAiInsights}
              </span>
            </div>
            <Progress value={(settingsData.usage.aiInsights / settingsData.usage.maxAiInsights) * 100} className="h-2" />
          </div>

          <div>
            <div className="flex justify-between mb-2">
              <span className="text-xs text-zinc-400">채널 연동</span>
              <span className="text-xs font-semibold text-white">
                {settingsData.usage.integrationsConnected} / {settingsData.usage.maxIntegrations}
              </span>
            </div>
            <Progress
              value={(settingsData.usage.integrationsConnected / settingsData.usage.maxIntegrations) * 100}
              className="h-2"
            />
          </div>
        </div>
      </div>

      {/* CTA Buttons */}
      <div className="flex gap-3">
        <Button
          onClick={handlePortal}
          className="flex-1 bg-blue-600 hover:bg-blue-700"
        >
          <CreditCard className="w-4 h-4 mr-2" />
          결제 관리
        </Button>
        <Button
          variant="outline"
          className="flex-1"
        >
          <ArrowUpRight className="w-4 h-4 mr-2" />
          플랜 업그레이드
        </Button>
      </div>
    </motion.div>
  );
}

/* ─── Pricing Table ──────────────────────────────────– */
function PricingTable() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.1 }}
    >
      <h3 className="text-lg font-bold text-white mb-6">플랜 비교</h3>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b" style={{ borderColor: "var(--border-subtle)" }}>
              <th className="text-left py-4 px-6 text-xs font-mono uppercase text-zinc-600">기능</th>
              {pricingPlans.map((plan) => (
                <th key={plan.name} className="text-center py-4 px-6 text-xs font-mono uppercase text-zinc-600">
                  {plan.name}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {[
              { feature: "채널 연동", starter: "3개", pro: "5개", agency: "무제한" },
              { feature: "월 AI 인사이트", starter: "10회", pro: "100회", agency: "무제한" },
              { feature: "데이터 보관", starter: "7일", pro: "90일", agency: "무제한" },
              { feature: "워크스페이스", starter: "1개", pro: "5개", agency: "무제한" },
              { feature: "리포트 생성", starter: "기본", pro: "고급 + 자동", agency: "커스텀" },
              { feature: "고객 지원", starter: "이메일", pro: "우선 지원", agency: "전담 관리자" },
            ].map((row) => (
              <tr key={row.feature} className="border-b" style={{ borderColor: "var(--border-subtle)" }}>
                <td className="py-4 px-6 text-xs text-zinc-300 font-medium">{row.feature}</td>
                <td className="py-4 px-6 text-center text-xs text-zinc-400">{row.starter}</td>
                <td className="py-4 px-6 text-center text-xs text-zinc-400">{row.pro}</td>
                <td className="py-4 px-6 text-center text-xs text-zinc-400">{row.agency}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </motion.div>
  );
}

/* ─── Page ───────────────────────────────────────────– */
export default function BillingPage() {
  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white mb-2">결제 및 구독</h1>
        <p className="text-sm text-zinc-500">플랜을 관리하고 구독 정보를 확인합니다.</p>
      </div>

      {/* Current Plan */}
      <CurrentPlanCard />

      {/* Pricing Comparison */}
      <PricingTable />

      {/* FAQ */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="rounded-xl border border-white/7 p-6"
        style={{ background: "var(--bg-elevated)" }}
      >
        <h3 className="text-sm font-bold text-white mb-4">자주 묻는 질문</h3>
        <div className="space-y-4">
          {[
            {
              q: "언제든 플랜을 변경할 수 있나요?",
              a: "네, 언제든 플랜을 업그레이드하거나 다운그레이드할 수 있습니다. 변경사항은 즉시 반영됩니다.",
            },
            {
              q: "구독을 취소하면 데이터는 어떻게 되나요?",
              a: "구독 취소 후에도 30일간 데이터가 보관됩니다. 그 이후 자동으로 삭제됩니다.",
            },
            {
              q: "청구 주기는 어떻게 되나요?",
              a: "모든 플랜은 월간 청구입니다. 월초 1일에 청구되며, 언제든 취소 가능합니다.",
            },
          ].map((faq, i) => (
            <div key={i}>
              <h4 className="text-xs font-semibold text-white mb-1">{faq.q}</h4>
              <p className="text-xs text-zinc-400">{faq.a}</p>
            </div>
          ))}
        </div>
      </motion.div>
    </div>
  );
}
