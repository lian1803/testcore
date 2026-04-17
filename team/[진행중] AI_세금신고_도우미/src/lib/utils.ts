import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

/** shadcn/ui 표준 cn 유틸 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/** 금액을 한국 원화 형식으로 포맷 (예: 1,234,567원) */
export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat("ko-KR").format(amount) + "원";
}

/** 금액을 만원 단위로 포맷 (차트용, 예: 123만) */
export function formatCurrencyShort(amount: number): string {
  if (amount >= 100000000) {
    return (amount / 100000000).toFixed(1) + "억";
  }
  if (amount >= 10000) {
    return Math.floor(amount / 10000) + "만";
  }
  return amount.toLocaleString("ko-KR");
}

/** 날짜를 한국 형식으로 포맷 (예: 2025.01.15) */
export function formatDate(date: Date | string): string {
  const d = typeof date === "string" ? new Date(date) : date;
  return d.toLocaleDateString("ko-KR", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).replace(/\. /g, ".").replace(/\.$/, "");
}

/** 날짜를 상대 시간으로 포맷 (예: 3일 전) */
export function formatRelativeDate(date: Date | string): string {
  const d = typeof date === "string" ? new Date(date) : date;
  const now = new Date();
  const diffMs = now.getTime() - d.getTime();
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffDays === 0) return "오늘";
  if (diffDays === 1) return "어제";
  if (diffDays < 7) return `${diffDays}일 전`;
  if (diffDays < 30) return `${Math.floor(diffDays / 7)}주 전`;
  if (diffDays < 365) return `${Math.floor(diffDays / 30)}개월 전`;
  return `${Math.floor(diffDays / 365)}년 전`;
}

/** 퍼센트 변화 계산 */
export function calcPercentChange(current: number, previous: number): number {
  if (previous === 0) return 0;
  return Math.round(((current - previous) / previous) * 100);
}

/** 종합소득세 간이 계산 (참고용 — 실제 신고는 홈택스 사용) */
export function estimateIncomeTax(taxBase: number): number {
  // 2024 기준 종합소득세율 (6단계 누진세율)
  if (taxBase <= 14000000) return Math.floor(taxBase * 0.06);
  if (taxBase <= 50000000) return Math.floor(840000 + (taxBase - 14000000) * 0.15);
  if (taxBase <= 88000000) return Math.floor(6240000 + (taxBase - 50000000) * 0.24);
  if (taxBase <= 150000000) return Math.floor(15360000 + (taxBase - 88000000) * 0.35);
  if (taxBase <= 300000000) return Math.floor(37060000 + (taxBase - 150000000) * 0.38);
  if (taxBase <= 500000000) return Math.floor(94060000 + (taxBase - 300000000) * 0.40);
  return Math.floor(174060000 + (taxBase - 500000000) * 0.42);
}

/** 카테고리 한국어 레이블 */
export const CATEGORY_LABELS: Record<string, string> = {
  OFFICE_SUPPLIES: "사무용품",
  COMMUNICATION: "통신비",
  TRANSPORTATION: "교통비",
  MEAL: "식비",
  EDUCATION: "교육비",
  EQUIPMENT: "장비/소프트웨어",
  RENT: "임차료",
  INSURANCE: "보험료",
  ADVERTISING: "광고/마케팅",
  PROFESSIONAL_FEE: "전문가 수수료",
  OTHER: "기타",
};

/** 카테고리 뱃지 클래스 */
export const CATEGORY_BADGE_CLASSES: Record<string, string> = {
  MEAL: "badge-meal",
  TRANSPORTATION: "badge-transportation",
  COMMUNICATION: "badge-communication",
  OFFICE_SUPPLIES: "badge-office",
  EDUCATION: "badge-education",
  EQUIPMENT: "badge-other",
  RENT: "badge-other",
  INSURANCE: "badge-other",
  ADVERTISING: "badge-other",
  PROFESSIONAL_FEE: "badge-other",
  OTHER: "badge-other",
};

/** 과세유형 레이블 */
export const TAX_TYPE_LABELS: Record<string, string> = {
  GENERAL: "일반과세자",
  SIMPLIFIED: "간이과세자",
  TAX_FREE: "면세사업자",
  INCOME_ONLY: "개인 (사업자등록 없음)",
};

/** 업종 목록 */
export const BUSINESS_TYPES = [
  { code: "940909", label: "프리랜서 (소프트웨어 개발)", description: "소프트웨어 개발, IT 서비스, 앱 개발" },
  { code: "921501", label: "유튜버/크리에이터", description: "동영상 콘텐츠 제작, 방송" },
  { code: "721401", label: "디자이너", description: "그래픽, UI/UX, 영상 디자인" },
  { code: "859001", label: "강사/튜터", description: "온라인/오프라인 강의, 컨설팅" },
  { code: "493200", label: "배달라이더", description: "음식 배달, 퀵서비스" },
  { code: "472101", label: "소매업", description: "온라인/오프라인 제품 판매" },
  { code: "960901", label: "서비스업 (기타)", description: "개인 서비스, 용역 제공" },
  { code: "741100", label: "작가/번역가", description: "글쓰기, 번역, 저작권" },
  { code: "731200", label: "사진작가", description: "사진 촬영, 편집" },
  { code: "900001", label: "기타 프리랜서", description: "위 항목에 해당하지 않는 경우" },
] as const;
