"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Brain, Sparkles, ChevronRight, Loader } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { settingsData } from "@/lib/mock-data";
import { toast } from "sonner";

/* ─── Types ──────────────────────────────────────────── */
interface InsightItem {
  id: string;
  title: string;
  description: string;
  actions: string[];
  priority: "high" | "medium" | "low";
  generatedAt: string;
}

/* ─── Mock generated insights ────────────────────────── */
const mockGeneratedInsights: InsightItem[] = [
  {
    id: "gen-1",
    title: "메타 광고 ROAS 개선 기회",
    description: "지난 7일 대비 CPC 23% 상승. 광고 소재 교체 권장.",
    priority: "high",
    generatedAt: new Date().toISOString(),
    actions: [
      "오래된 크리에이티브(7일 이상) 교체",
      "고성과 오디언스 lookalike 확장",
      "저성과 키워드 CPC 상한 낮추기",
    ],
  },
  {
    id: "gen-2",
    title: "GA4 세션 트렌드 긍정적 신호",
    description: "신규 유입 채널 3개 발견, 콘텐츠 마케팅 효과 상승.",
    priority: "medium",
    generatedAt: new Date(Date.now() - 86400000).toISOString(),
    actions: [
      "상위 3개 콘텐츠 성과 분석",
      "유사 콘텐츠 추가 제작 계획",
      "고성과 채널 마케팅 예산 증액",
    ],
  },
];

const recentInsights: InsightItem[] = [
  {
    id: "recent-1",
    title: "네이버SA 입찰가 최적화 필요",
    description: "평균 CTR 18% 하락, 상위 키워드 경쟁 강화 감지.",
    priority: "high",
    generatedAt: new Date(Date.now() - 172800000).toISOString(),
    actions: ["키워드 입찰가 재조정", "제외 키워드 추가", "예산 재분배"],
  },
  {
    id: "recent-2",
    title: "크로스 채널 성과 비교",
    description: "메타의 ROAS가 다른 채널 대비 27% 우수. 예산 재배분 기회.",
    priority: "medium",
    generatedAt: new Date(Date.now() - 259200000).toISOString(),
    actions: ["메타 예산 10% 증액", "저성과 채널 검토", "A/B 테스트 설계"],
  },
];

/* ─── Usage Bar ──────────────────────────────────────── */
function UsageBar() {
  const used = settingsData.usage.aiInsights;
  const max = settingsData.usage.maxAiInsights;
  const percentage = (used / max) * 100;

  return (
    <div className="mb-8">
      <div className="flex items-center justify-between mb-3">
        <div>
          <h2 className="text-sm font-semibold text-white">이번달 AI 인사이트 사용</h2>
          <p className="text-xs text-zinc-500 mt-0.5">월 한도 내에서 인사이트 생성 가능</p>
        </div>
        <span className="text-lg font-bold text-white">{used} / {max}</span>
      </div>
      <Progress value={percentage} className="h-2" />
      {used >= max && (
        <p className="text-xs text-red-400 mt-2">한도 도달. 플랜 업그레이드 필요</p>
      )}
    </div>
  );
}

/* ─── Insight Card ───────────────────────────────────── */
function InsightCard({ insight }: { insight: InsightItem; isGenerated?: boolean }) {
  const priorityColor = {
    high: "from-red-500/20 to-orange-500/10",
    medium: "from-yellow-500/20 to-orange-500/10",
    low: "from-blue-500/20 to-cyan-500/10",
  }[insight.priority];

  const priorityLabel = {
    high: "높음",
    medium: "중간",
    low: "낮음",
  }[insight.priority];

  const priorityBgColor = {
    high: "bg-red-500/10",
    medium: "bg-yellow-500/10",
    low: "bg-blue-500/10",
  }[insight.priority];

  const priorityTextColor = {
    high: "text-red-400",
    medium: "text-yellow-400",
    low: "text-blue-400",
  }[insight.priority];

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`p-6 rounded-xl border border-white/7 bg-gradient-to-br ${priorityColor} backdrop-blur-sm`}
      style={{ background: "var(--bg-elevated)" }}
    >
      <div className="flex items-start justify-between gap-4 mb-4">
        <div className="flex items-start gap-3 flex-1">
          <div className="w-8 h-8 rounded-lg bg-white/8 flex items-center justify-center shrink-0 mt-0.5">
            <Sparkles className="w-4 h-4 text-purple-400" />
          </div>
          <div className="flex-1 min-w-0">
            <h3 className="text-sm font-semibold text-white leading-snug">{insight.title}</h3>
            <p className="text-xs text-zinc-400 mt-1">{insight.description}</p>
          </div>
        </div>
        <div className={`px-2 py-1 rounded-lg ${priorityBgColor} shrink-0`}>
          <span className={`text-xs font-semibold ${priorityTextColor}`}>{priorityLabel}</span>
        </div>
      </div>

      {/* Actions */}
      <div className="space-y-2 mb-4">
        {insight.actions.map((action, i) => (
          <div key={i} className="flex items-center gap-2 pl-11 text-xs text-zinc-300">
            <div className="w-1.5 h-1.5 rounded-full bg-white/20" />
            {action}
          </div>
        ))}
      </div>

      {/* Timestamp + CTA */}
      <div className="flex items-center justify-between pt-3 border-t border-white/5">
        <p className="text-[10px] text-zinc-600 font-mono">
          {new Date(insight.generatedAt).toLocaleDateString("ko-KR", {
            month: "short",
            day: "numeric",
            hour: "2-digit",
            minute: "2-digit",
          })}
        </p>
        <button className="flex items-center gap-1 text-xs text-zinc-400 hover:text-white transition-colors">
          자세히 보기 <ChevronRight className="w-3 h-3" />
        </button>
      </div>
    </motion.div>
  );
}

/* ─── Page ───────────────────────────────────────────── */
export default function InsightsPage() {
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedInsights, setGeneratedInsights] = useState<InsightItem[]>([]);
  const [showHistory, setShowHistory] = useState(false);

  const canGenerate = settingsData.usage.aiInsights < settingsData.usage.maxAiInsights;

  const handleGenerateInsight = async () => {
    if (!canGenerate) {
      toast.error("월 한도를 초과했습니다. 플랜을 업그레이드해주세요.");
      return;
    }

    setIsGenerating(true);
    // Mock API call with 2 second delay
    await new Promise((resolve) => setTimeout(resolve, 2000));
    setIsGenerating(false);

    setGeneratedInsights([...mockGeneratedInsights, ...generatedInsights]);
    toast.success("인사이트 생성 완료!");
  };

  return (
    <div className="min-h-screen" style={{ background: "var(--bg-base)", color: "var(--text-primary)" }}>
      {/* ── Header ──────────────────────────────────── */}
      <header className="sticky top-0 z-20 glass-nav px-8 py-5 border-b" style={{ borderColor: "var(--border-subtle)" }}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-white/8 flex items-center justify-center">
              <Brain className="w-5 h-5 text-purple-400" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-white">AI 인사이트</h1>
              <p className="text-xs text-zinc-500">데이터 기반 자동 분석</p>
            </div>
          </div>
        </div>
      </header>

      {/* ── Content ────────────────────────────────── */}
      <div className="px-8 py-8 max-w-4xl mx-auto">
        {/* Usage Bar */}
        <UsageBar />

        {/* Generate Button */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="mb-8"
        >
          <Button
            onClick={handleGenerateInsight}
            disabled={isGenerating || !canGenerate}
            className="w-full h-12 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white font-semibold rounded-lg flex items-center justify-center gap-2"
          >
            {isGenerating ? (
              <>
                <Loader className="w-4 h-4 animate-spin" />
                AI 분석 중... (약 2초)
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                새 인사이트 생성하기
              </>
            )}
          </Button>
        </motion.div>

        {/* Generated Insights */}
        {generatedInsights.length > 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mb-10"
          >
            <h2 className="text-base font-bold text-white mb-4">최근 생성된 인사이트</h2>
            <div className="space-y-4">
              <AnimatePresence>
                {generatedInsights.map((insight) => (
                  <InsightCard key={insight.id} insight={insight} isGenerated />
                ))}
              </AnimatePresence>
            </div>
          </motion.div>
        )}

        {/* Toggle History */}
        <div className="mb-8">
          <button
            onClick={() => setShowHistory(!showHistory)}
            className="flex items-center gap-2 text-sm font-semibold text-white hover:text-zinc-300 transition-colors"
          >
            <span>{showHistory ? "숨기기" : "이전 인사이트 보기"}</span>
            <ChevronRight className={`w-4 h-4 transition-transform ${showHistory ? "rotate-90" : ""}`} />
          </button>
        </div>

        {/* History */}
        <AnimatePresence>
          {showHistory && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              className="space-y-4"
            >
              <h3 className="text-sm font-bold text-white">최근 30일</h3>
              {recentInsights.map((insight) => (
                <InsightCard key={insight.id} insight={insight} />
              ))}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Empty State */}
        {generatedInsights.length === 0 && !showHistory && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="text-center py-12"
          >
            <div className="w-16 h-16 rounded-full bg-white/5 flex items-center justify-center mx-auto mb-4">
              <Brain className="w-8 h-8 text-zinc-600" />
            </div>
            <h3 className="text-sm font-semibold text-white mb-1">인사이트 생성 준비 완료</h3>
            <p className="text-xs text-zinc-500">
              위의 버튼을 클릭하여 첫 인사이트를 생성해보세요.
            </p>
          </motion.div>
        )}
      </div>
    </div>
  );
}
