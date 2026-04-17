import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

// C-3: timing attack 방지용 더미 해시 (Web Crypto API 기반)
export const DUMMY_HASH = 'pbkdf2:100000:' + 'a'.repeat(64) + ':' + 'a'.repeat(64);

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * API Key 생성 (lg_ 접두어 포함 — Web Crypto API)
 */
export function generateApiKey(): { key: string; prefix: string } {
  const randomArray = crypto.getRandomValues(new Uint8Array(24));
  const randomBytes = Array.from(randomArray).map(b => b.toString(16).padStart(2, '0')).join('');
  const key = `lg_${randomBytes}`;
  // 앞 8자만 노출 (lg_ + 8자)
  const prefix = key.substring(0, 13); // lg_ + 8자

  return { key, prefix };
}

/**
 * 비밀번호 해싱 (PBKDF2 — Web Crypto API)
 */
export async function hashPassword(password: string): Promise<string> {
  const encoder = new TextEncoder();
  const salt = crypto.getRandomValues(new Uint8Array(16));
  const keyMaterial = await crypto.subtle.importKey(
    'raw',
    encoder.encode(password),
    'PBKDF2',
    false,
    ['deriveBits']
  );
  const bits = await crypto.subtle.deriveBits(
    { name: 'PBKDF2', salt, iterations: 100000, hash: 'SHA-256' },
    keyMaterial,
    256
  );
  const hashArray = Array.from(new Uint8Array(bits));
  const saltArray = Array.from(salt);
  const saltHex = saltArray.map(b => b.toString(16).padStart(2, '0')).join('');
  const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
  return `pbkdf2:100000:${saltHex}:${hashHex}`;
}

/**
 * 비밀번호 검증 (PBKDF2 — Web Crypto API)
 */
export async function verifyPassword(password: string, stored: string): Promise<boolean> {
  try {
    const [algorithm, iterations, saltHex, storedHashHex] = stored.split(':');
    if (algorithm !== 'pbkdf2' || !iterations || !saltHex || !storedHashHex) {
      return false;
    }

    const salt = new Uint8Array(saltHex.match(/.{2}/g)!.map(b => parseInt(b, 16)));
    const encoder = new TextEncoder();
    const keyMaterial = await crypto.subtle.importKey(
      'raw',
      encoder.encode(password),
      'PBKDF2',
      false,
      ['deriveBits']
    );
    const bits = await crypto.subtle.deriveBits(
      { name: 'PBKDF2', salt, iterations: parseInt(iterations), hash: 'SHA-256' },
      keyMaterial,
      256
    );
    const newHashArray = Array.from(new Uint8Array(bits));
    const newHashHex = newHashArray.map(b => b.toString(16).padStart(2, '0')).join('');
    return constantTimeCompare(newHashHex, storedHashHex);
  } catch (error) {
    console.error('[Auth] Password verification error:', error);
    return false;
  }
}

/**
 * API Key 해싱 (PBKDF2 — Web Crypto API)
 */
export async function hashApiKey(key: string): Promise<string> {
  return hashPassword(key);
}

/**
 * API Key 검증 (상수 시간 비교)
 */
export async function verifyApiKey(plain: string, hash: string): Promise<boolean> {
  return verifyPassword(plain, hash);
}

/**
 * 요청 메시지 해시 (루프 감지용 — Web Crypto API)
 */
export async function computeMessageHash(messages: unknown[]): Promise<string> {
  const content = JSON.stringify(messages);
  const encoder = new TextEncoder();
  const data = encoder.encode(content);
  const hashBuffer = await crypto.subtle.digest('SHA-256', data);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
}

/**
 * 요청 ID 생성 (추적용)
 */
export function generateRequestId(): string {
  return crypto.randomUUID();
}

/**
 * 현재 월의 시작일 계산 (reset_day 기준)
 */
export function getMonthPeriodStart(resetDay: number = 1, now: Date = new Date()): Date {
  const year = now.getFullYear();
  const month = now.getMonth();
  const currentDay = now.getDate();

  if (currentDay >= resetDay) {
    // 현재 월이 reset_day를 지났음
    return new Date(year, month, resetDay);
  } else {
    // 지난 달 reset_day부터 시작
    return new Date(year, month - 1, resetDay);
  }
}

/**
 * 다음 월의 시작일 계산
 */
export function getNextMonthPeriodStart(resetDay: number = 1, now: Date = new Date()): Date {
  const year = now.getFullYear();
  const month = now.getMonth();
  const currentDay = now.getDate();

  if (currentDay >= resetDay) {
    // 다음 달의 reset_day
    return new Date(year, month + 1, resetDay);
  } else {
    // 현재 달의 reset_day
    return new Date(year, month, resetDay);
  }
}

/**
 * 에러 응답 생성
 */
export function createErrorResponse(
  code: string,
  message: string,
  requestId: string,
  status: number = 400
): { error: { code: string; message: string; requestId: string }; status: number } {
  return {
    error: {
      code,
      message,
      requestId,
    },
    status,
  };
}

/**
 * HMAC-SHA256 기반 타이밍 어택 방지 비교
 */
export function constantTimeCompare(a: string, b: string): boolean {
  if (a.length !== b.length) return false;

  let result = 0;
  for (let i = 0; i < a.length; i++) {
    result |= a.charCodeAt(i) ^ b.charCodeAt(i);
  }

  return result === 0;
}

/**
 * ISO 날짜 문자열 반환 (UTC)
 */
export function now(): string {
  return new Date().toISOString();
}

/**
 * 지정한 일수를 더한 미래 날짜 반환
 */
export function addDays(date: Date, days: number): Date {
  const result = new Date(date);
  result.setDate(result.getDate() + days);
  return result;
}
