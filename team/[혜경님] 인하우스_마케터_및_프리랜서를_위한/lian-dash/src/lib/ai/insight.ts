import OpenAI from "openai";

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

export interface InsightResponse {
  insights: Array<{
    title: string;
    description: string;
    priority: "high" | "medium" | "low";
    metric: string;
  }>;
  inputTokens: number;
  outputTokens: number;
}

export async function generateInsight(
  ga4Data: Record<string, any>,
  metaData: Record<string, any>,
  naverData: Record<string, any>
): Promise<InsightResponse> {
  const prompt = `You are a digital marketing expert AI. Based on the following analytics data from the past 7 days, provide 3 actionable recommendations for improvement.

GA4 Data:
- Sessions: ${ga4Data?.sessions || 0}
- Users: ${ga4Data?.users || 0}
- Bounce Rate: ${ga4Data?.bounceRate?.toFixed(2) || 0}%
- Goal Completions: ${ga4Data?.goalCompletions || 0}

Meta (Facebook/Instagram) Ads Data:
- Impressions: ${metaData?.impressions || 0}
- Clicks: ${metaData?.clicks || 0}
- CTR: ${metaData?.ctr?.toFixed(2) || 0}%
- CPC: $${metaData?.cpc?.toFixed(2) || 0}
- Spend: $${metaData?.spend?.toFixed(2) || 0}
- ROAS: ${metaData?.roas?.toFixed(2) || 0}

Naver Search Ads Data:
- Impressions: ${naverData?.impressions || 0}
- Clicks: ${naverData?.clicks || 0}
- CTR: ${naverData?.ctr?.toFixed(2) || 0}%
- CPC: ${naverData?.cpc?.toFixed(2) || 0}
- Conversions: ${naverData?.conversions || 0}

Respond ONLY with valid JSON in this exact format:
{
  "insights": [
    {
      "title": "specific improvement area",
      "description": "detailed explanation with numbers and suggestions",
      "priority": "high|medium|low",
      "metric": "which metric should improve"
    }
  ]
}`;

  const response = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [
      {
        role: "user",
        content: prompt,
      },
    ],
    max_tokens: 800,
    temperature: 0.7,
  });

  const content = response.choices[0]?.message?.content || "{}";

  try {
    const parsed = JSON.parse(content);
    return {
      insights: parsed.insights || [],
      inputTokens: response.usage?.prompt_tokens || 0,
      outputTokens: response.usage?.completion_tokens || 0,
    };
  } catch {
    // Fallback if JSON parsing fails
    return {
      insights: [
        {
          title: "Unable to parse insights",
          description: content,
          priority: "low",
          metric: "general",
        },
      ],
      inputTokens: response.usage?.prompt_tokens || 0,
      outputTokens: response.usage?.completion_tokens || 0,
    };
  }
}
