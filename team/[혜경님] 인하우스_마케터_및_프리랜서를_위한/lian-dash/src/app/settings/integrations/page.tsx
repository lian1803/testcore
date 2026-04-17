"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Plug, RotateCcw, Loader } from "lucide-react";
import { Button } from "@/components/ui/button";
import { integrationData } from "@/lib/mock-data";
import { toast } from "sonner";

/* ─── Integration Card ───────────────────────────────– */
function IntegrationCard({ integration }: { integration: typeof integrationData[0] }) {
  const [isLoading, setIsLoading] = useState(false);
  const [isConnected, setIsConnected] = useState(integration.status !== "disconnected");

  const statusColors = {
    connected: "bg-green-500/10 text-green-400 border-green-500/20",
    disconnected: "bg-zinc-500/10 text-zinc-400 border-zinc-500/20",
    mock: "bg-amber-500/10 text-amber-400 border-amber-500/20",
  };

  const statusLabel = {
    connected: "연결됨",
    disconnected: "미연결",
    mock: "샘플 데이터",
  }[integration.status];

  const handleConnect = async () => {
    setIsLoading(true);
    await new Promise((resolve) => setTimeout(resolve, 1500));
    setIsLoading(false);
    setIsConnected(true);
    toast.success(`${integration.name} 연동 완료`);
  };

  const handleDisconnect = async () => {
    setIsLoading(true);
    await new Promise((resolve) => setTimeout(resolve, 1000));
    setIsLoading(false);
    setIsConnected(false);
    toast.success(`${integration.name} 연동 해제됨`);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="rounded-xl border border-white/7 p-6"
      style={{ background: "var(--bg-elevated)" }}
    >
      <div className="flex items-start justify-between gap-4 mb-4">
        <div className="flex items-start gap-4 flex-1">
          <div className="text-3xl">{integration.icon}</div>
          <div className="flex-1 min-w-0">
            <h3 className="text-sm font-semibold text-white mb-1">{integration.name}</h3>
            <p className="text-xs text-zinc-500 truncate">{integration.accountName}</p>
          </div>
        </div>
        <div className={`px-3 py-1 rounded-full text-xs font-semibold border ${statusColors[integration.status]}`}>
          {statusLabel}
        </div>
      </div>

      {/* Sync info */}
      {isConnected && (
        <div className="mb-4 p-3 rounded-lg bg-white/5 border border-white/5">
          <p className="text-[10px] text-zinc-600 font-mono uppercase tracking-wider mb-1">마지막 동기화</p>
          <p className="text-xs text-zinc-400">{integration.lastSync}</p>
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-2">
        {isConnected ? (
          <>
            <Button
              onClick={handleDisconnect}
              disabled={isLoading}
              variant="outline"
              size="sm"
              className="flex-1"
            >
              {isLoading ? (
                <>
                  <Loader className="w-3 h-3 animate-spin mr-1" />
                  처리 중...
                </>
              ) : (
                "연동 해제"
              )}
            </Button>
            <Button
              onClick={handleConnect}
              disabled={isLoading}
              size="sm"
              className="flex-1 bg-blue-600 hover:bg-blue-700"
            >
              {isLoading ? (
                <>
                  <Loader className="w-3 h-3 animate-spin mr-1" />
                  재동기화 중...
                </>
              ) : (
                <>
                  <RotateCcw className="w-3 h-3 mr-1" />
                  재동기화
                </>
              )}
            </Button>
          </>
        ) : (
          <Button
            onClick={handleConnect}
            disabled={isLoading}
            className="w-full bg-blue-600 hover:bg-blue-700"
          >
            {isLoading ? (
              <>
                <Loader className="w-3 h-3 animate-spin mr-1" />
                연결 중...
              </>
            ) : (
              <>
                <Plug className="w-3 h-3 mr-1" />
                연결하기
              </>
            )}
          </Button>
        )}
      </div>
    </motion.div>
  );
}

/* ─── Page ───────────────────────────────────────────── */
export default function IntegrationsPage() {
  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white mb-2">채널 연동 설정</h1>
        <p className="text-sm text-zinc-500">연결된 마케팅 채널을 관리하고 데이터 동기화를 제어합니다.</p>
      </div>

      {/* Integration List */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {integrationData.map((integration) => (
          <IntegrationCard key={integration.id} integration={integration} />
        ))}
      </div>

      {/* Info Box */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="rounded-xl border border-blue-500/30 bg-blue-500/10 px-6 py-4"
      >
        <h3 className="text-sm font-semibold text-blue-100 mb-2">팁</h3>
        <ul className="text-xs text-blue-200 space-y-1 list-disc list-inside">
          <li>연동을 해제해도 이전 데이터는 계속 보관됩니다.</li>
          <li>각 채널은 하루에 최대 1회씩 자동으로 동기화됩니다.</li>
          <li>실시간 데이터는 각 채널의 대시보드에서 확인하세요.</li>
        </ul>
      </motion.div>
    </div>
  );
}
