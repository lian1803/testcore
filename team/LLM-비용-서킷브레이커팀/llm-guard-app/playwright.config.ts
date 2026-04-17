import { defineConfig, devices } from '@playwright/test';

const BASE_URL = process.env.MONITOR_URL || 'https://llm-guard-app.lian1803.workers.dev';

export default defineConfig({
  testDir: './e2e',
  timeout: 30_000,
  retries: 1,
  reporter: [['list'], ['json', { outputFile: 'e2e/results.json' }]],
  use: {
    baseURL: BASE_URL,
    extraHTTPHeaders: {
      'Accept': 'text/html,application/json',
    },
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
});
