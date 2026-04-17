// API Response Types
export interface ApiResponse<T = unknown> {
  data?: T;
  error?: {
    code: string;
    message: string;
    requestId?: string;
  };
}

// SDK API Types
export interface SDKCheckRequest {
  model: string;
  provider: 'openai' | 'anthropic' | 'google';
  estimated_tokens: number;
  request_hash: string;
  context_count: number;
}

export interface SDKCheckResponse {
  allowed: boolean;
  current_spend_usd: number;
  budget_usd: number;
  remaining_usd: number;
  estimated_cost_usd?: number;
  reason?: 'budget_exceeded' | 'loop_detected';
}

export interface SDKReportRequest {
  model: string;
  provider: 'openai' | 'anthropic' | 'google';
  input_tokens: number;
  output_tokens: number;
  cost_usd: number;
  latency_ms: number;
  is_blocked: boolean;
  request_hash: string;
}

// Dashboard API Types
export interface Project {
  id: string;
  user_id: string;
  name: string;
  description?: string;
  budget_usd: number;
  reset_day: number;
  is_active: boolean;
  created_at: string;
}

export interface ApiKey {
  id: string;
  user_id: string;
  project_id: string;
  name: string;
  key_prefix: string;
  last_used_at?: string;
  is_active: boolean;
  created_at: string;
}

export interface UsageLog {
  id: string;
  project_id: string;
  user_id: string;
  model: string;
  provider: 'openai' | 'anthropic' | 'google';
  input_tokens: number;
  output_tokens: number;
  cost_usd: number;
  is_blocked: boolean;
  block_reason?: 'budget_exceeded' | 'loop_detected';
  request_hash?: string;
  latency_ms?: number;
  called_at: string;
}

export interface Budget {
  id: string;
  project_id: string;
  user_id: string;
  period_start: string;
  spent_usd: number;
  call_count: number;
  blocked_count: number;
  updated_at: string;
}

export interface Alert {
  id: string;
  project_id: string;
  user_id: string;
  threshold_pct: number;
  channel: 'email' | 'slack';
  slack_webhook?: string;
  is_active: boolean;
  last_fired_at?: string;
  created_at: string;
}

export interface User {
  id: string;
  email: string;
  plan: 'free' | 'pro' | 'team';
  stripe_customer_id?: string;
  stripe_subscription_id?: string;
  created_at: string;
  updated_at: string;
}

// Cost calculation types
export interface ModelPricing {
  input: number; // per 1M tokens
  output: number; // per 1M tokens
}

export interface PricingTable {
  [provider: string]: {
    [model: string]: ModelPricing;
  };
}
