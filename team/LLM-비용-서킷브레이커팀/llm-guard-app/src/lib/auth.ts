/**
 * 커스텀 인증 시스템 — D1 + JWT
 * Supabase Auth → 자체 구현으로 마이그레이션
 * bcryptjs → Web Crypto API (Edge Runtime 호환)
 */

import { SignJWT, jwtVerify } from 'jose';
import { d1QueryOne, d1QueryAll, d1Execute } from './d1';
import { generateRequestId, hashPassword, verifyPassword } from './utils';

const JWT_SECRET = new TextEncoder().encode(
  process.env.JWT_SECRET || 'fallback-secret-key-change-in-production'
);
const JWT_EXPIRY = 7 * 24 * 60 * 60; // 7 days

/**
 * 사용자 타입
 */
export interface User {
  id: string;
  email: string;
  plan: 'free' | 'pro' | 'team';
  stripe_customer_id: string | null;
  stripe_subscription_id: string | null;
  google_id?: string | null;
  avatar_url?: string | null;
  created_at: string;
  updated_at: string;
}

/**
 * JWT payload 타입
 */
export interface JWTPayload {
  sub: string; // user_id
  email: string;
  iat: number;
  exp: number;
}

/**
 * 회원가입
 */
export async function signup(
  email: string,
  password: string
): Promise<{ user: User; token: string }> {
  // 유효성 검사
  if (!email || !password) {
    throw new Error('Email and password are required');
  }

  if (password.length < 8) {
    throw new Error('Password must be at least 8 characters');
  }

  // 이메일 형식 검증
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    throw new Error('Invalid email format');
  }

  // 기존 사용자 확인
  const existing = await d1QueryOne<{ id: string }>(
    'SELECT id FROM users WHERE email = ?',
    [email]
  );

  if (existing) {
    throw new Error('Email already registered');
  }

  // 비밀번호 해싱 (Web Crypto API)
  const hashedPassword = await hashPassword(password);

  // 사용자 생성
  const userId = generateRequestId();
  const now = new Date().toISOString();

  try {
    // users 테이블에 삽입
    await d1Execute(
      `INSERT INTO users (id, email, password, plan, created_at, updated_at)
       VALUES (?, ?, ?, ?, ?, ?)`,
      [userId, email, hashedPassword, 'free', now, now]
    );

    // 초기 프로젝트 생성
    const projectId = generateRequestId();
    await d1Execute(
      `INSERT INTO projects (id, user_id, name, budget_usd, reset_day, is_active, created_at)
       VALUES (?, ?, ?, ?, ?, ?, ?)`,
      [projectId, userId, 'Default Project', 10.0, 1, true, now]
    );
  } catch (error) {
    console.error('[Auth] Signup error:', error);
    throw new Error('Failed to create user');
  }

  // 사용자 조회
  const user = await d1QueryOne<User>(
    'SELECT id, email, plan, stripe_customer_id, stripe_subscription_id, google_id, avatar_url, created_at, updated_at FROM users WHERE id = ?',
    [userId]
  );

  if (!user) {
    throw new Error('Failed to retrieve created user');
  }

  // JWT 생성
  const token = await createJWT({ sub: userId, email });

  return { user, token };
}

/**
 * 로그인
 */
export async function login(
  email: string,
  password: string
): Promise<{ user: User; token: string }> {
  if (!email || !password) {
    throw new Error('Email and password are required');
  }

  // 사용자 조회
  const userRow = await d1QueryOne<User & { password: string }>(
    'SELECT * FROM users WHERE email = ?',
    [email]
  );

  if (!userRow) {
    throw new Error('Invalid email or password');
  }

  // 비밀번호 검증 (Web Crypto API)
  const passwordValid = await verifyPassword(password, userRow.password);
  if (!passwordValid) {
    throw new Error('Invalid email or password');
  }

  // 민감정보 제거
  const { password: _, ...user } = userRow;

  // JWT 생성
  const token = await createJWT({ sub: user.id, email: user.email });

  return { user: user as User, token };
}

/**
 * JWT 생성
 */
export async function createJWT(payload: Omit<JWTPayload, 'iat' | 'exp'>) {
  const now = Math.floor(Date.now() / 1000);
  const jwt = await new SignJWT({
    sub: payload.sub,
    email: payload.email,
    iat: now,
    exp: now + JWT_EXPIRY,
  })
    .setProtectedHeader({ alg: 'HS256' })
    .sign(JWT_SECRET);

  return jwt;
}

/**
 * JWT 검증 및 payload 반환
 */
export async function verifyJWT(token: string): Promise<JWTPayload | null> {
  try {
    const verified = await jwtVerify(token, JWT_SECRET);
    return verified.payload as unknown as JWTPayload;
  } catch (error) {
    console.error('[Auth] JWT verification failed:', error);
    return null;
  }
}

/**
 * Request 헤더에서 JWT 추출
 * Authorization: Bearer <token>
 */
export function extractJWT(authHeader: string | null): string | null {
  if (!authHeader) return null;

  const parts = authHeader.split(' ');
  if (parts.length !== 2 || parts[0] !== 'Bearer') {
    return null;
  }

  return parts[1];
}

/**
 * 사용자 ID로 사용자 조회
 */
export async function getUserById(userId: string): Promise<User | null> {
  return d1QueryOne<User>(
    'SELECT id, email, plan, stripe_customer_id, stripe_subscription_id, google_id, avatar_url, created_at, updated_at FROM users WHERE id = ?',
    [userId]
  );
}

/**
 * 사용자 이메일로 사용자 조회
 */
export async function getUserByEmail(email: string): Promise<User | null> {
  return d1QueryOne<User>(
    'SELECT id, email, plan, stripe_customer_id, stripe_subscription_id, google_id, avatar_url, created_at, updated_at FROM users WHERE email = ?',
    [email]
  );
}

/**
 * 사용자 Google ID로 사용자 조회
 */
export async function getUserByGoogleId(googleId: string): Promise<User | null> {
  return d1QueryOne<User>(
    'SELECT id, email, plan, stripe_customer_id, stripe_subscription_id, google_id, avatar_url, created_at, updated_at FROM users WHERE google_id = ?',
    [googleId]
  );
}

/**
 * 사용자 정보 업데이트
 */
export async function updateUser(
  userId: string,
  updates: Partial<User>
): Promise<User | null> {
  const now = new Date().toISOString();

  const setClauses = [];
  const params = [];

  if ('plan' in updates) {
    setClauses.push('plan = ?');
    params.push(updates.plan);
  }

  if ('stripe_customer_id' in updates) {
    setClauses.push('stripe_customer_id = ?');
    params.push(updates.stripe_customer_id);
  }

  if ('stripe_subscription_id' in updates) {
    setClauses.push('stripe_subscription_id = ?');
    params.push(updates.stripe_subscription_id);
  }

  if (setClauses.length === 0) {
    return getUserById(userId);
  }

  setClauses.push('updated_at = ?');
  params.push(now);
  params.push(userId);

  const sql = `UPDATE users SET ${setClauses.join(', ')} WHERE id = ?`;

  try {
    await d1Execute(sql, params);
    return getUserById(userId);
  } catch (error) {
    console.error('[Auth] Update user error:', error);
    return null;
  }
}
