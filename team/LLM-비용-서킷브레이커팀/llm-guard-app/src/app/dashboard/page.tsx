'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { motion } from 'framer-motion';
import { toast } from 'sonner';

interface Project {
  id: string;
  name: string;
  budget_usd: number;
  reset_day: number;
  is_active: number;
}

interface ChartDataPoint {
  time: string;
  cost: number;
}

export default function DashboardPage() {
  const [project, setProject] = useState<Project | null>(null);
  const [todayCost, setTodayCost] = useState(0);
  const [monthlyBudget, setMonthlyBudget] = useState(0);
  const [requestsBlocked, setRequestsBlocked] = useState(0);
  const [remainingBudget, setRemainingBudget] = useState(0);
  const [costData, setCostData] = useState<ChartDataPoint[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const budgetPercentage = monthlyBudget > 0 ? Math.round((todayCost / monthlyBudget) * 100) : 0;

  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        setIsLoading(true);
        setError(null);

        // 1. 프로젝트 목록 먼저 조회
        const projectsRes = await fetch('/api/dashboard/projects', { credentials: 'include' });
        if (!projectsRes.ok) {
          if (projectsRes.status === 401) {
            window.location.href = '/auth/login';
            return;
          }
          throw new Error('Failed to load projects');
        }

        const projectsData = await projectsRes.json();
        const projects: Project[] = projectsData.data || [];

        if (projects.length === 0) {
          // 프로젝트가 없는 경우 빈 상태
          setIsLoading(false);
          return;
        }

        const firstProject = projects[0];
        setProject(firstProject);

        // 2. 프로젝트 ID로 usage + chart 병렬 조회
        const [usageRes, chartRes] = await Promise.all([
          fetch(`/api/dashboard/usage?project_id=${firstProject.id}`, { credentials: 'include' }),
          fetch(`/api/dashboard/chart?project_id=${firstProject.id}&days=7`, { credentials: 'include' }),
        ]);

        if (usageRes.ok) {
          const usageJson = await usageRes.json();
          const usage = usageJson.data;
          if (usage) {
            setTodayCost(usage.spent_usd || 0);
            setMonthlyBudget(usage.budget_usd || firstProject.budget_usd);
            setRequestsBlocked(usage.blocked_count || 0);
            setRemainingBudget(usage.remaining_usd || firstProject.budget_usd);
          }
        }

        if (chartRes.ok) {
          const chartJson = await chartRes.json();
          const chartPoints: ChartDataPoint[] = (chartJson.data || []).map((d: { date: string; cost: number }) => ({
            time: d.date,
            cost: d.cost,
          }));
          setCostData(chartPoints);
        }
      } catch (err) {
        console.error('[Dashboard Load Error]', err);
        setError(err instanceof Error ? err.message : 'Failed to load dashboard data');
        toast.error('Failed to load dashboard. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };

    loadDashboardData();
  }, []);

  if (isLoading) {
    return (
      <div className="p-6 space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <Card key={i} className="bg-[#161b22] border-[#30363d]">
              <CardHeader className="pb-2">
                <div className="h-4 bg-[#30363d] rounded w-1/2 animate-pulse" />
              </CardHeader>
              <CardContent>
                <div className="h-8 bg-[#30363d] rounded mb-3 animate-pulse" />
                <div className="h-3 bg-[#30363d] rounded w-2/3 animate-pulse" />
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <Card className="bg-[#161b22] border-[#ff4444]">
          <CardContent className="pt-6">
            <p className="text-[#ff4444] mb-4">{error}</p>
            <Button
              onClick={() => window.location.reload()}
              className="bg-[#00ff88] text-[#0d1117] font-bold"
            >
              Try Again
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!project) {
    return (
      <div className="p-6">
        <Card className="bg-[#161b22] border-[#30363d]">
          <CardContent className="pt-6 text-center">
            <p className="text-[#8b949e] mb-4">No projects yet. Create your first project to get started.</p>
            <Button
              onClick={() => window.location.href = '/dashboard/projects'}
              className="bg-[#00ff88] text-[#0d1117] font-bold"
            >
              Create Project
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Project selector */}
      <div className="flex items-center gap-2 text-sm text-[#8b949e]">
        <span>Project:</span>
        <span className="text-[#e6edf3] font-medium">{project.name}</span>
        <Badge className="bg-[#00ff88]/20 text-[#00ff88] text-xs">ACTIVE</Badge>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0 }}
        >
          <Card className="bg-[#161b22] border-[#30363d]">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-[#8b949e]">
                Total Spent
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold font-mono">${todayCost.toFixed(4)}</div>
              <p className="text-xs text-[#8b949e] mt-2">This billing period</p>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.1 }}
        >
          <Card className="bg-[#161b22] border-[#30363d]">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-[#8b949e]">
                Budget Used
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold font-mono text-[#f0c040]">
                {budgetPercentage}%
              </div>
              <div className="w-full bg-[#21262d] rounded-full h-2 mt-3">
                <div
                  className={`h-full rounded-full transition-all ${
                    budgetPercentage > 80
                      ? 'bg-[#ff4444]'
                      : budgetPercentage > 50
                      ? 'bg-[#f0c040]'
                      : 'bg-[#00ff88]'
                  }`}
                  style={{ width: `${Math.min(budgetPercentage, 100)}%` }}
                />
              </div>
              <p className="text-xs text-[#6e7681] mt-2">of ${monthlyBudget} budget</p>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.2 }}
        >
          <Card className="bg-[#161b22] border-[#30363d]">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-[#8b949e]">
                Requests Blocked
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold font-mono text-[#ff4444]">
                {requestsBlocked}
              </div>
              <Badge className="mt-3 bg-[#00ff88]/20 text-[#00ff88]">
                GUARD ACTIVE
              </Badge>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.3 }}
        >
          <Card className="bg-[#161b22] border-[#30363d]">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-[#8b949e]">
                Remaining Budget
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold font-mono text-[#00ff88]">
                ${remainingBudget.toFixed(2)}
              </div>
              <p className="text-xs text-[#8b949e] mt-2">until circuit breaks</p>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Cost Over Time Chart */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.4 }}
      >
        <Card className="bg-[#161b22] border-[#30363d]">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Cost Over Time (7 days)</CardTitle>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-[#00ff88] animate-pulse" />
                <span className="text-xs text-[#8b949e]">LIVE</span>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {costData.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={costData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#30363d" />
                  <XAxis dataKey="time" stroke="#6e7681" tick={{ fontSize: 11 }} />
                  <YAxis stroke="#6e7681" tick={{ fontSize: 11 }} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#161b22',
                      border: '1px solid #30363d',
                      borderRadius: '6px',
                    }}
                    labelStyle={{ color: '#e6edf3' }}
                    formatter={(val: number) => [`$${val.toFixed(4)}`, 'Cost']}
                  />
                  <Line
                    type="monotone"
                    dataKey="cost"
                    stroke="#00ff88"
                    dot={false}
                    strokeWidth={2}
                  />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-[300px] flex items-center justify-center text-[#6e7681] text-sm">
                No usage data yet. Start using your API key to see cost trends.
              </div>
            )}
          </CardContent>
        </Card>
      </motion.div>

      {/* Quick Start */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.5 }}
      >
        <Card className="bg-[#161b22] border-[#30363d]">
          <CardHeader>
            <CardTitle>Quick Start</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-[#8b949e] mb-4">
              Get an API key from the <a href="/dashboard/keys" className="text-[#00ff88] hover:underline">API Keys</a> page and wrap your LLM calls:
            </p>
            <pre className="bg-[#0d1117] rounded-lg p-4 text-xs font-mono text-[#00ff88] overflow-x-auto">
{`import llmguard from 'llm-guard-sdk';

const guard = new LLMGuard('your-api-key');
await guard.check({ model: 'gpt-4', estimatedTokens: 2000 });
// Throws if budget exceeded — your LLM call is protected`}
            </pre>
          </CardContent>
        </Card>
      </motion.div>

      {/* Upgrade CTA */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.6 }}
        className="bg-gradient-to-r from-[#161b22] to-[#21262d] border border-[#30363d] rounded-lg p-6 flex items-center justify-between"
      >
        <div>
          <h3 className="font-bold mb-1">Unlock Advanced Features</h3>
          <p className="text-sm text-[#8b949e]">
            Get agent loop detection, Slack integration, and 10x rate limits
          </p>
        </div>
        <Button className="bg-[#00ff88] text-[#0d1117] font-bold">
          Upgrade to Pro
        </Button>
      </motion.div>
    </div>
  );
}
