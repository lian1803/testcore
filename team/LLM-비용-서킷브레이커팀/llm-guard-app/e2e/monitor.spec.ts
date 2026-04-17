import { test, expect } from '@playwright/test';

const SITE = process.env.MONITOR_URL || 'https://llm-guard-app.lian1803.workers.dev';

// ─── 1. 퍼블릭 페이지 ────────────────────────────────────────────────────────

test('홈페이지 200 응답', async ({ page }) => {
  const res = await page.goto(SITE);
  expect(res?.status()).toBe(200);
});

test('로그인 페이지 200 응답', async ({ page }) => {
  const res = await page.goto(`${SITE}/auth/login`);
  expect(res?.status()).toBe(200);
  await expect(page.locator('body')).toContainText('Sign in');
});

test('회원가입 페이지 200 응답', async ({ page }) => {
  const res = await page.goto(`${SITE}/auth/signup`);
  expect(res?.status()).toBe(200);
});

test('SDK 문서 페이지 200 응답', async ({ page }) => {
  const res = await page.goto(`${SITE}/docs`);
  expect(res?.status()).toBe(200);
});

// ─── 2. Google OAuth 리다이렉트 ───────────────────────────────────────────────

test('Google OAuth 리다이렉트 → accounts.google.com 이동', async ({ page }) => {
  // 리다이렉트 따라가되 Google 도달 시 중단
  const res = await page.goto(`${SITE}/api/auth/google`, { waitUntil: 'commit' });
  // Google로 최종 리다이렉트되어야 함
  expect(page.url()).toContain('accounts.google.com');
});

test('Google OAuth redirect_uri에 workers.dev 포함', async ({ page }) => {
  await page.goto(`${SITE}/api/auth/google`, { waitUntil: 'commit' });
  const url = new URL(page.url());
  const redirectUri = url.searchParams.get('redirect_uri') || '';
  expect(redirectUri).toContain('lian1803.workers.dev');
  expect(redirectUri).not.toContain('pages.dev'); // 이전 버그 방지
});

// ─── 3. 인증 보호 경로 ────────────────────────────────────────────────────────

test('대시보드 미인증 → 로그인 페이지로 이동', async ({ page }) => {
  await page.goto(`${SITE}/dashboard`);
  // 로그인 페이지로 리다이렉트되거나 로그인 UI가 보여야 함
  await page.waitForURL(/auth\/login/, { timeout: 10_000 });
  expect(page.url()).toContain('auth/login');
});

// ─── 4. API 엔드포인트 상태 ───────────────────────────────────────────────────

test('API /api/dashboard/projects → 401 (500 아님)', async ({ request }) => {
  const res = await request.get(`${SITE}/api/dashboard/projects`);
  expect(res.status()).toBe(401);
});

test('API /api/dashboard/api-keys → 401 (500 아님)', async ({ request }) => {
  const res = await request.get(`${SITE}/api/dashboard/api-keys`);
  expect(res.status()).toBe(401);
});

test('API /api/auth/login → 405 또는 400 (GET은 안됨)', async ({ request }) => {
  const res = await request.get(`${SITE}/api/auth/login`);
  // GET은 지원 안 함 → 405 or 400, 절대 500 아니어야 함
  expect(res.status()).not.toBe(500);
});

test('SDK /api/v1/sdk/check → 401 (키 없으면)', async ({ request }) => {
  const res = await request.post(`${SITE}/api/v1/sdk/check`, {
    data: { model: 'gpt-4', estimated_tokens: 1000 },
  });
  expect(res.status()).toBe(401);
});

// ─── 5. D1 데이터베이스 연결 확인 ─────────────────────────────────────────────

test('로그인 API → D1 연결 정상 (500 아님)', async ({ request }) => {
  const res = await request.post(`${SITE}/api/auth/login`, {
    data: { email: 'healthcheck@monitor.test', password: 'wrongpassword' },
  });
  // 잘못된 비밀번호 → 401 AUTH_ERROR. 500이면 D1 연결 문제
  expect(res.status()).toBe(401);
  const body = await res.json();
  expect(body.error?.code).toBe('AUTH_ERROR');
});
