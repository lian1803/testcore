-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================
-- 1. users (Supabase Auth 확장)
-- =============================================
CREATE TABLE IF NOT EXISTS public.users (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email TEXT NOT NULL,
  plan TEXT NOT NULL DEFAULT 'free',  -- 'free' | 'pro' | 'team'
  stripe_customer_id TEXT,
  stripe_subscription_id TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX idx_users_email ON public.users(email);

ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
CREATE POLICY users_self ON public.users
  FOR SELECT USING (id = auth.uid());
CREATE POLICY users_insert ON public.users
  FOR INSERT WITH CHECK (id = auth.uid());
CREATE POLICY users_update ON public.users
  FOR UPDATE USING (id = auth.uid()) WITH CHECK (id = auth.uid());

-- =============================================
-- 2. projects
-- =============================================
CREATE TABLE IF NOT EXISTS public.projects (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  description TEXT,
  budget_usd NUMERIC(10, 4) NOT NULL DEFAULT 10.0,
  reset_day SMALLINT NOT NULL DEFAULT 1,
  is_active BOOLEAN NOT NULL DEFAULT true,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_projects_user_id ON public.projects(user_id, created_at DESC);

ALTER TABLE public.projects ENABLE ROW LEVEL SECURITY;
CREATE POLICY projects_owner ON public.projects
  FOR ALL USING (user_id = auth.uid());

-- =============================================
-- 3. api_keys
-- =============================================
CREATE TABLE IF NOT EXISTS public.api_keys (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  project_id UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  key_hash TEXT NOT NULL UNIQUE,
  key_prefix TEXT NOT NULL,
  last_used_at TIMESTAMPTZ,
  is_active BOOLEAN NOT NULL DEFAULT true,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_api_keys_key_hash ON public.api_keys(key_hash);
CREATE INDEX idx_api_keys_project ON public.api_keys(project_id);

ALTER TABLE public.api_keys ENABLE ROW LEVEL SECURITY;
CREATE POLICY api_keys_owner ON public.api_keys
  FOR ALL USING (user_id = auth.uid());

-- =============================================
-- 4. usage_logs
-- =============================================
CREATE TABLE IF NOT EXISTS public.usage_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
  user_id UUID NOT NULL,
  model TEXT NOT NULL,
  provider TEXT NOT NULL,  -- 'openai' | 'anthropic' | 'google'
  input_tokens INTEGER NOT NULL DEFAULT 0,
  output_tokens INTEGER NOT NULL DEFAULT 0,
  cost_usd NUMERIC(10, 6) NOT NULL DEFAULT 0,
  is_blocked BOOLEAN NOT NULL DEFAULT false,
  block_reason TEXT,
  request_hash TEXT,
  latency_ms INTEGER,
  called_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_usage_logs_project_called ON public.usage_logs(project_id, called_at DESC);
CREATE INDEX idx_usage_logs_user_called ON public.usage_logs(user_id, called_at DESC);
CREATE INDEX idx_usage_logs_month ON public.usage_logs(project_id, date_trunc('month', called_at));

ALTER TABLE public.usage_logs ENABLE ROW LEVEL SECURITY;
CREATE POLICY usage_logs_owner ON public.usage_logs
  FOR ALL USING (user_id = auth.uid());

-- Realtime 활성화
ALTER PUBLICATION supabase_realtime ADD TABLE public.usage_logs;

-- =============================================
-- 5. budgets
-- =============================================
CREATE TABLE IF NOT EXISTS public.budgets (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
  user_id UUID NOT NULL,
  period_start DATE NOT NULL,
  spent_usd NUMERIC(10, 4) NOT NULL DEFAULT 0,
  call_count INTEGER NOT NULL DEFAULT 0,
  blocked_count INTEGER NOT NULL DEFAULT 0,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE(project_id, period_start)
);

CREATE INDEX idx_budgets_project_period ON public.budgets(project_id, period_start DESC);

ALTER TABLE public.budgets ENABLE ROW LEVEL SECURITY;
CREATE POLICY budgets_owner ON public.budgets
  FOR ALL USING (user_id = auth.uid());

-- =============================================
-- 6. alerts
-- =============================================
CREATE TABLE IF NOT EXISTS public.alerts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
  user_id UUID NOT NULL,
  threshold_pct SMALLINT NOT NULL,  -- 50 | 80 | 100
  channel TEXT NOT NULL,  -- 'email' | 'slack'
  slack_webhook TEXT,
  is_active BOOLEAN NOT NULL DEFAULT true,
  last_fired_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_alerts_project ON public.alerts(project_id);

ALTER TABLE public.alerts ENABLE ROW LEVEL SECURITY;
CREATE POLICY alerts_owner ON public.alerts
  FOR ALL USING (user_id = auth.uid());

-- =============================================
-- 7. stripe_events (Webhook 멱등성)
-- =============================================
CREATE TABLE IF NOT EXISTS public.stripe_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  stripe_event_id TEXT NOT NULL UNIQUE,
  type TEXT NOT NULL,
  status TEXT NOT NULL,  -- 'processing' | 'processed' | 'failed'
  error TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_stripe_events_status ON public.stripe_events(status);

-- =============================================
-- 8. Helper Functions
-- =============================================
CREATE OR REPLACE FUNCTION get_current_spend(p_project_id UUID)
RETURNS NUMERIC AS $$
  SELECT COALESCE(spent_usd, 0)
  FROM public.budgets
  WHERE project_id = p_project_id
    AND period_start = date_trunc('month', now())::date
$$ LANGUAGE sql STABLE SECURITY DEFINER;

CREATE OR REPLACE FUNCTION get_month_period_start(p_project_id UUID)
RETURNS DATE AS $$
  SELECT CASE 
    WHEN extract(day from now()) >= COALESCE((
      SELECT reset_day FROM public.projects WHERE id = p_project_id
    ), 1)
    THEN date_trunc('month', now())::date + (COALESCE((
      SELECT reset_day FROM public.projects WHERE id = p_project_id
    ), 1) - 1) * interval '1 day'::interval
    ELSE (date_trunc('month', now()) - interval '1 month')::date + (COALESCE((
      SELECT reset_day FROM public.projects WHERE id = p_project_id
    ), 1) - 1) * interval '1 day'::interval
  END
$$ LANGUAGE sql STABLE SECURITY DEFINER;

-- =============================================
-- RPC: budgets 원자적 증분 (Race Condition 방지)
-- =============================================
CREATE OR REPLACE FUNCTION increment_budget_counts(
  p_project_id UUID,
  p_period_start DATE,
  p_cost_usd NUMERIC,
  p_is_blocked BOOLEAN
) RETURNS VOID
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
  INSERT INTO public.budgets (project_id, period_start, spent_usd, call_count, blocked_count, updated_at)
  VALUES (
    p_project_id,
    p_period_start,
    p_cost_usd,
    CASE WHEN p_is_blocked THEN 0 ELSE 1 END,
    CASE WHEN p_is_blocked THEN 1 ELSE 0 END,
    now()
  )
  ON CONFLICT (project_id, period_start)
  DO UPDATE SET
    spent_usd    = budgets.spent_usd + EXCLUDED.spent_usd,
    call_count   = budgets.call_count + EXCLUDED.call_count,
    blocked_count= budgets.blocked_count + EXCLUDED.blocked_count,
    updated_at   = now();
END;
$$;
