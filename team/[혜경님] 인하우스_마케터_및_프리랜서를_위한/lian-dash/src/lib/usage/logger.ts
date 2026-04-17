import { prisma } from "@/lib/prisma";
import { UsageLogType, ChannelType } from "@prisma/client";

export interface LogUsageParams {
  userId: string;
  workspaceId: string;
  logType: UsageLogType;
  integrationId?: string;
  channel?: ChannelType;
  apiCalls?: number;
  tokensUsed?: number;
  inputTokens?: number;
  outputTokens?: number;
}

export async function logUsage(params: LogUsageParams): Promise<void> {
  try {
    // Calculate cost estimate for OpenAI
    let costEstimate: number | undefined;

    if (params.logType === "AI_INSIGHT" && params.inputTokens && params.outputTokens) {
      // GPT-4o pricing (as of 2026): $0.005/1K input, $0.015/1K output
      costEstimate =
        (params.inputTokens / 1000) * 0.005 +
        (params.outputTokens / 1000) * 0.015;
    }

    await prisma.usageLog.create({
      data: {
        userId: params.userId,
        workspaceId: params.workspaceId,
        integrationId: params.integrationId,
        logType: params.logType,
        channel: params.channel,
        apiCalls: params.apiCalls || 1,
        tokensUsed: params.tokensUsed,
        costEstimate,
      },
    });
  } catch (error) {
    console.error("Failed to log usage:", error);
    // Don't throw - usage logging should not break the main flow
  }
}

export async function getMonthlyUsage(userId: string, workspaceId: string) {
  const now = new Date();
  const monthStart = new Date(now.getFullYear(), now.getMonth(), 1);

  const [totalApiCalls, totalTokens, totalCost, byChannel] = await Promise.all([
    prisma.usageLog.aggregate({
      where: {
        userId,
        workspaceId,
        createdAt: { gte: monthStart },
        logType: "CHANNEL_API_CALL",
      },
      _sum: { apiCalls: true },
    }),
    prisma.usageLog.aggregate({
      where: {
        userId,
        workspaceId,
        createdAt: { gte: monthStart },
        logType: "AI_INSIGHT",
      },
      _sum: { tokensUsed: true },
    }),
    prisma.usageLog.aggregate({
      where: {
        userId,
        workspaceId,
        createdAt: { gte: monthStart },
      },
      _sum: { costEstimate: true },
    }),
    prisma.usageLog.groupBy({
      by: ["channel"],
      where: {
        userId,
        workspaceId,
        createdAt: { gte: monthStart },
      },
      _sum: { apiCalls: true },
    }),
  ]);

  return {
    period: { start: monthStart, end: now },
    totalApiCalls: totalApiCalls._sum.apiCalls || 0,
    totalAiTokens: totalTokens._sum.tokensUsed || 0,
    estimatedCost: totalCost._sum.costEstimate || 0,
    byChannel: byChannel.reduce(
      (acc, item) => {
        if (item.channel) {
          acc[item.channel] = item._sum.apiCalls || 0;
        }
        return acc;
      },
      {} as Record<string, number>
    ),
  };
}
