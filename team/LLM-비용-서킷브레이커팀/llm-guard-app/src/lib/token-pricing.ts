import type { PricingTable } from '@/types';

// 2026-04-08 기준 공식 가격
// 단위: per 1M tokens (입력/출력)
export const PRICING: PricingTable = {
  openai: {
    'gpt-4o': { input: 2.5, output: 10.0 },
    'gpt-4o-mini': { input: 0.15, output: 0.6 },
    'o1': { input: 15.0, output: 60.0 },
    'o3-mini': { input: 1.1, output: 4.4 },
    'gpt-4-turbo': { input: 10.0, output: 30.0 },
    'gpt-3.5-turbo': { input: 0.5, output: 1.5 },
  },
  anthropic: {
    'claude-3-5-sonnet-20241022': { input: 3.0, output: 15.0 },
    'claude-3-5-haiku-20241022': { input: 0.8, output: 4.0 },
    'claude-opus-4-5': { input: 15.0, output: 75.0 },
    'claude-3-sonnet-20240229': { input: 3.0, output: 15.0 },
  },
  google: {
    'gemini-2.0-flash': { input: 0.1, output: 0.4 },
    'gemini-2.5-pro': { input: 1.25, output: 10.0 },
    'gemini-1.5-pro': { input: 1.25, output: 10.0 },
    'gemini-1.5-flash': { input: 0.075, output: 0.3 },
  },
};

/**
 * 주어진 모델/공급자에 대해 비용 계산
 * @param provider - 'openai' | 'anthropic' | 'google'
 * @param model - 모델 이름
 * @param inputTokens - 입력 토큰 수
 * @param outputTokens - 출력 토큰 수
 * @returns USD 단위 비용
 */
export function calculateCost(
  provider: string,
  model: string,
  inputTokens: number,
  outputTokens: number
): number {
  const providerPricing = PRICING[provider as keyof PricingTable];
  if (!providerPricing) {
    // 알 수 없는 공급자 — 0 처리 (과금 미스보다 차단 미스가 낫다)
    return 0.0;
  }

  const modelPricing = providerPricing[model];
  if (!modelPricing) {
    // 알 수 없는 모델 — 0 처리
    return 0.0;
  }

  const inputCost = (inputTokens * modelPricing.input) / 1_000_000;
  const outputCost = (outputTokens * modelPricing.output) / 1_000_000;

  return inputCost + outputCost;
}

/**
 * 모델의 가격 정보 조회
 */
export function getModelPricing(provider: string, model: string) {
  return PRICING[provider as keyof PricingTable]?.[model] || null;
}

/**
 * 지원하는 모든 모델 목록
 */
export function getSupportedModels(provider?: string): string[] {
  if (provider) {
    return Object.keys(PRICING[provider as keyof PricingTable] || {});
  }

  const allModels: string[] = [];
  for (const providerModels of Object.values(PRICING)) {
    allModels.push(...Object.keys(providerModels));
  }
  return [...new Set(allModels)];
}
