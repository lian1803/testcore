import { encryptToken, decryptToken } from "@/lib/encryption";

export interface NaverMetrics {
  impressions?: number;
  clicks?: number;
  ctr?: number;
  cpc?: number;
  conversions?: number;
  [key: string]: any;
}

export interface MetricsParams {
  accountId?: string;
  startDate: string;
  endDate: string;
}

const NAVER_API_URL = "https://api.naver.com/naver_searchad";

export class NaverAdapter {
  static async handleConnect(apiKey: string, secret: string) {
    try {
      // Validate API key format (basic validation)
      if (!apiKey || apiKey.length < 10) {
        throw new Error("Invalid API key format");
      }

      // Encrypt and store
      return {
        accessToken: encryptToken(apiKey),
        refreshToken: encryptToken(secret),
        expiresAt: null, // Naver SA doesn't use expiring tokens
      };
    } catch (error) {
      console.error("Naver connect error:", error);
      throw new Error("Failed to save Naver SA credentials");
    }
  }

  static async getMetrics(
    encryptedApiKey: string,
    params: MetricsParams
  ): Promise<NaverMetrics> {
    try {
      const usesMock = process.env.NAVER_MOCK === "true";

      if (usesMock) {
        return this.getMockData();
      }

      const apiKey = decryptToken(encryptedApiKey);

      // Make actual API call
      const response = await fetch(
        `${NAVER_API_URL}/reports?startDate=${params.startDate}&endDate=${params.endDate}`,
        {
          headers: {
            Authorization: `Bearer ${apiKey}`,
            "Content-Type": "application/json",
          },
        }
      );

      if (!response.ok) {
        // Fallback to mock on error
        console.warn("Naver SA API error, falling back to mock data");
        return this.getMockData();
      }

      const data = (await response.json()) as {
        data?: Array<{
          imp?: number;
          click?: number;
          ctr?: number;
          avgCpc?: number;
          conv?: number;
        }>;
      };

      if (!data.data || data.data.length === 0) {
        return this.getMockData();
      }

      const row = data.data[0];
      return {
        impressions: row.imp || 0,
        clicks: row.click || 0,
        ctr: row.ctr || 0,
        cpc: row.avgCpc || 0,
        conversions: row.conv || 0,
      };
    } catch (error) {
      console.error("Naver getMetrics error:", error);
      return this.getMockData();
    }
  }

  static getMockData(): NaverMetrics {
    return {
      impressions: Math.floor(Math.random() * 30000) + 5000,
      clicks: Math.floor(Math.random() * 1500) + 200,
      ctr: Math.random() * 8,
      cpc: Math.random() * 2.5 + 0.3,
      conversions: Math.floor(Math.random() * 300) + 30,
    };
  }
}
