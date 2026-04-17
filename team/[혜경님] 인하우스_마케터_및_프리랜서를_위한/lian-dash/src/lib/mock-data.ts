// Mock data for Lian Dash

export const channelColors = {
  ga4: "#4285F4",
  meta: "#1877F2",
  naver: "#03C75A",
} as const;

export type Channel = keyof typeof channelColors;

export interface KPIData {
  label: string;
  value: string;
  change?: number;
  unit?: string;
}

export interface KPIDataset {
  totalSpend: KPIData;
  totalConversions: KPIData;
  roas: KPIData;
  cpa: KPIData;
  ctr: KPIData;
  totalClicks: KPIData;
}

export interface ChannelPerformance {
  channel: Channel;
  label: string;
  spend: string;
  clicks: string;
  conversions: string;
  roas: string;
  cpa: string;
}

export interface ChartDataPoint {
  date: string;
  ga4: number;
  meta: number;
  naver: number;
}

export interface Insight {
  id: string;
  severity: "danger" | "warning" | "success";
  title: string;
  description: string;
  channel: Channel;
  action: string;
}

// KPI data by filter
export const kpiDataByFilter: Record<string, KPIDataset> = {
  today: {
    totalSpend: { label: "총 광고비", value: "38만원", change: -5.2 },
    totalConversions: { label: "총 전환", value: "28건", change: 12.4 },
    roas: { label: "ROAS", value: "3.0x", change: -2.1 },
    cpa: { label: "CPA", value: "13,571원", change: 8.3 },
    ctr: { label: "CTR", value: "2.8%", change: -0.3 },
    totalClicks: { label: "총 클릭", value: "1,240", change: 3.8 },
  },
  "7d": {
    totalSpend: { label: "총 광고비", value: "265만원", change: 4.1 },
    totalConversions: { label: "총 전환", value: "196건", change: 7.2 },
    roas: { label: "ROAS", value: "3.3x", change: 5.4 },
    cpa: { label: "CPA", value: "13,520원", change: -3.2 },
    ctr: { label: "CTR", value: "3.1%", change: 0.2 },
    totalClicks: { label: "총 클릭", value: "8,680", change: 6.1 },
  },
  "30d": {
    totalSpend: { label: "총 광고비", value: "1,120만원", change: 2.8 },
    totalConversions: { label: "총 전환", value: "842건", change: 15.3 },
    roas: { label: "ROAS", value: "3.4x", change: 8.7 },
    cpa: { label: "CPA", value: "13,302원", change: -5.1 },
    ctr: { label: "CTR", value: "3.2%", change: 0.4 },
    totalClicks: { label: "총 클릭", value: "37,200", change: 11.2 },
  },
};

export const channelPerformance: ChannelPerformance[] = [
  {
    channel: "ga4",
    label: "GA4",
    spend: "110만",
    clicks: "3,500",
    conversions: "82",
    roas: "3.9x",
    cpa: "13,415원",
  },
  {
    channel: "meta",
    label: "메타",
    spend: "98만",
    clicks: "3,180",
    conversions: "71",
    roas: "3.5x",
    cpa: "13,803원",
  },
  {
    channel: "naver",
    label: "네이버SA",
    spend: "57만",
    clicks: "2,000",
    conversions: "43",
    roas: "2.8x",
    cpa: "13,256원",
  },
];

// Chart data for 7 days
const generateChartData = (): ChartDataPoint[] => {
  const data: ChartDataPoint[] = [];
  const today = new Date();

  for (let i = 6; i >= 0; i--) {
    const date = new Date(today);
    date.setDate(date.getDate() - i);
    const dateStr = `${date.getMonth() + 1}/${date.getDate()}`;

    data.push({
      date: dateStr,
      ga4: Math.floor(Math.random() * 800) + 1200,
      meta: Math.floor(Math.random() * 700) + 1000,
      naver: Math.floor(Math.random() * 500) + 600,
    });
  }

  return data;
};

export const chartData = generateChartData();

export const insights: Insight[] = [
  {
    id: "1",
    severity: "danger",
    title: "네이버SA CTR 18% 하락",
    description: "상위 3개 키워드 입찰가 점검 권장",
    channel: "naver",
    action: "키워드 입찰가 조정하기",
  },
  {
    id: "2",
    severity: "warning",
    title: "메타 CPA 목표 초과",
    description: "20~34세 여성 세그먼트 성과 저조, 타겟팅 재검토 필요",
    channel: "meta",
    action: "타겟팅 재설정하기",
  },
  {
    id: "3",
    severity: "success",
    title: "GA4 유기 전환율 +12%",
    description: "블로그 콘텐츠 기여 추정, 콘텐츠 증량 권장",
    channel: "ga4",
    action: "콘텐츠 분석 보기",
  },
];

// GA4 상세 데이터
export interface GA4Metric {
  metric: string;
  value: number;
  change: number;
  unit: string;
}

export const ga4Metrics: GA4Metric[] = [
  { metric: "Sessions", value: 12450, change: 8.2, unit: "" },
  { metric: "Users", value: 8920, change: 5.3, unit: "" },
  { metric: "Bounce Rate", value: 42.3, change: -2.1, unit: "%" },
  { metric: "Goal Completions", value: 485, change: 12.4, unit: "" },
];

export interface ChannelDetailData {
  date: string;
  sessions?: number;
  users?: number;
  bounceRate?: number;
  goalCompletions?: number;
  impressions?: number;
  clicks?: number;
  ctr?: number;
  cpc?: number;
  conversions?: number;
  spend?: number;
  roas?: number;
}

export const ga4DetailChart: ChannelDetailData[] = [
  { date: "3/27", sessions: 1200, bounceRate: 44.2, goalCompletions: 52 },
  { date: "3/28", sessions: 1450, bounceRate: 42.1, goalCompletions: 68 },
  { date: "3/29", sessions: 1680, bounceRate: 41.3, goalCompletions: 75 },
  { date: "3/30", sessions: 1520, bounceRate: 42.8, goalCompletions: 58 },
  { date: "3/31", sessions: 1890, bounceRate: 40.5, goalCompletions: 92 },
  { date: "4/1", sessions: 2100, bounceRate: 39.2, goalCompletions: 105 },
  { date: "4/2", sessions: 2340, bounceRate: 38.8, goalCompletions: 120 },
];

export const metaMetrics: GA4Metric[] = [
  { metric: "Impressions", value: 285400, change: 11.5, unit: "" },
  { metric: "Clicks", value: 18920, change: 9.2, unit: "" },
  { metric: "CTR", value: 6.6, change: -0.3, unit: "%" },
  { metric: "CPC", value: 1420, change: 3.2, unit: "원" },
  { metric: "ROAS", value: 3.8, change: 5.1, unit: "x" },
  { metric: "Spend", value: 2680000, change: 2.1, unit: "원" },
];

export const metaDetailChart: ChannelDetailData[] = [
  { date: "3/27", impressions: 38000, clicks: 2400, spend: 360000, roas: 3.5 },
  { date: "3/28", impressions: 41200, clicks: 2680, spend: 375000, roas: 3.6 },
  { date: "3/29", impressions: 43800, clicks: 2920, spend: 395000, roas: 3.7 },
  { date: "3/30", impressions: 40500, clicks: 2580, spend: 380000, roas: 3.5 },
  { date: "3/31", impressions: 45600, clicks: 3120, spend: 420000, roas: 3.9 },
  { date: "4/1", impressions: 48200, clicks: 3450, spend: 450000, roas: 4.0 },
  { date: "4/2", impressions: 50100, clicks: 3750, spend: 470000, roas: 4.1 },
];

export const naverMetrics: GA4Metric[] = [
  { metric: "Impressions", value: 156200, change: -3.2, unit: "" },
  { metric: "Clicks", value: 9240, change: -1.8, unit: "" },
  { metric: "CTR", value: 5.9, change: -0.8, unit: "%" },
  { metric: "CPC", value: 1850, change: 2.4, unit: "원" },
  { metric: "Conversions", value: 142, change: -5.1, unit: "" },
  { metric: "Spend", value: 1710000, change: 0.5, unit: "원" },
];

export const naverDetailChart: ChannelDetailData[] = [
  { date: "3/27", impressions: 21200, clicks: 1240, conversions: 22, spend: 240000 },
  { date: "3/28", impressions: 22400, clicks: 1320, conversions: 21, spend: 245000 },
  { date: "3/29", impressions: 23100, clicks: 1380, conversions: 20, spend: 252000 },
  { date: "3/30", impressions: 22800, clicks: 1350, conversions: 19, spend: 248000 },
  { date: "3/31", impressions: 22600, clicks: 1320, conversions: 20, spend: 245000 },
  { date: "4/1", impressions: 22200, clicks: 1290, conversions: 21, spend: 243000 },
  { date: "4/2", impressions: 21900, clicks: 1260, conversions: 19, spend: 240000 },
];

// 설정 페이지 데이터
export interface IntegrationInfo {
  id: string;
  name: string;
  icon: string;
  status: "connected" | "disconnected" | "mock";
  lastSync?: string;
  accountName?: string;
}

export const integrationData: IntegrationInfo[] = [
  {
    id: "ga4",
    name: "GA4",
    icon: "📊",
    status: "connected",
    lastSync: "2분 전",
    accountName: "analytics-123456.firebaseapp.com",
  },
  {
    id: "meta",
    name: "Meta (Facebook & Instagram)",
    icon: "📱",
    status: "connected",
    lastSync: "5분 전",
    accountName: "Company Ads Account",
  },
  {
    id: "naver",
    name: "Naver Search Ads",
    icon: "🔍",
    status: "mock",
    lastSync: "미연동",
    accountName: "API Key 입력 필요",
  },
];

export interface PricingPlan {
  name: string;
  price: number;
  currency: string;
  interval: "month" | "year";
  features: string[];
  recommended?: boolean;
}

export const pricingPlans: PricingPlan[] = [
  {
    name: "Starter",
    price: 29,
    currency: "$",
    interval: "month",
    features: [
      "3개 채널 연동",
      "월 10회 AI 인사이트",
      "기본 리포트",
      "7일 데이터 보관",
      "1개 워크스페이스",
    ],
  },
  {
    name: "Pro",
    price: 99,
    currency: "$",
    interval: "month",
    recommended: true,
    features: [
      "5개 채널 연동",
      "월 100회 AI 인사이트",
      "고급 리포트 + 자동 생성",
      "90일 데이터 보관",
      "5개 워크스페이스",
      "우선 지원",
    ],
  },
  {
    name: "Agency",
    price: 299,
    currency: "$",
    interval: "month",
    features: [
      "무제한 채널 연동",
      "무제한 AI 인사이트",
      "커스텀 리포트 빌더",
      "무제한 데이터 보관",
      "무제한 워크스페이스",
      "전담 계정 관리자",
      "화이트라벨 옵션",
    ],
  },
];

export interface SettingsPageData {
  user: {
    name: string;
    email: string;
    joinedAt: string;
  };
  plan: {
    name: string;
    status: "active" | "trial" | "expired";
    startDate: string;
    trialDaysRemaining?: number;
  };
  usage: {
    aiInsights: number;
    maxAiInsights: number;
    integrationsConnected: number;
    maxIntegrations: number;
  };
}

export const settingsData: SettingsPageData = {
  user: {
    name: "홍길동",
    email: "hong@company.com",
    joinedAt: "2026-03-20",
  },
  plan: {
    name: "Starter Plan",
    status: "trial",
    startDate: "2026-03-20",
    trialDaysRemaining: 11,
  },
  usage: {
    aiInsights: 3,
    maxAiInsights: 10,
    integrationsConnected: 2,
    maxIntegrations: 3,
  },
};