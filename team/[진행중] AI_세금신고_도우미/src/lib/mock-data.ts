/**
 * Mock 데이터 — 모든 화면 개발용
 * 실제 API 연결 시 이 파일의 데이터를 대체하면 됩니다.
 */

// ────────────────────────────────────────────
// 타입 정의
// ────────────────────────────────────────────

export type PlanStatus = "FREE" | "PREMIUM" | "EXPIRED";
export type TaxationType = "GENERAL" | "SIMPLIFIED" | "TAX_FREE" | "INCOME_ONLY";
export type ReceiptStatus = "PENDING" | "PROCESSING" | "COMPLETED" | "FAILED" | "MANUAL";
export type ExpenseCategory =
  | "OFFICE_SUPPLIES"
  | "COMMUNICATION"
  | "TRANSPORTATION"
  | "MEAL"
  | "EDUCATION"
  | "EQUIPMENT"
  | "RENT"
  | "INSURANCE"
  | "ADVERTISING"
  | "PROFESSIONAL_FEE"
  | "OTHER";

export interface MockUser {
  id: string;
  name: string;
  email: string;
  planStatus: PlanStatus;
  image: string | null;
  businessProfile: MockBusinessProfile | null;
}

export interface MockBusinessProfile {
  businessType: string;
  businessTypeLabel: string;
  taxationType: TaxationType;
  registrationNumber: string | null;
  taxYear: number;
}

export interface MockReceipt {
  id: string;
  imageUrl: string;
  merchantName: string;
  amount: number;
  date: string;
  category: ExpenseCategory;
  status: ReceiptStatus;
  ocrConfidence: number;
  uploadedAt: string;
}

export interface MockExpenseItem {
  id: string;
  receiptId: string | null;
  date: string;
  amount: number;
  merchantName: string;
  category: ExpenseCategory;
  isBusinessExpense: boolean;
  userVerified: boolean;
  memo: string | null;
  taxYear: number;
}

export interface MockKpiData {
  totalExpense: number;
  totalExpensePrevMonthChange: number;
  estimatedTax: number;
  estimatedTaxPrevMonthChange: number;
  receiptCount: number;
  receiptCountPrevMonthChange: number;
  estimatedSaving: number;
  estimatedSavingPrevMonthChange: number;
}

export interface MockMonthlyData {
  month: string;
  total: number;
  MEAL: number;
  TRANSPORTATION: number;
  COMMUNICATION: number;
  OFFICE_SUPPLIES: number;
  EDUCATION: number;
  OTHER: number;
}

// ────────────────────────────────────────────
// Mock 사용자
// ────────────────────────────────────────────

export const MOCK_USER: MockUser = {
  id: "user_001",
  name: "김민준",
  email: "minjun.kim@example.com",
  planStatus: "FREE",
  image: null,
  businessProfile: {
    businessType: "940909",
    businessTypeLabel: "프리랜서 (소프트웨어 개발)",
    taxationType: "INCOME_ONLY",
    registrationNumber: null,
    taxYear: 2025,
  },
};

export const MOCK_PREMIUM_USER: MockUser = {
  ...MOCK_USER,
  id: "user_002",
  name: "이서연",
  email: "seoyeon.lee@example.com",
  planStatus: "PREMIUM",
};

// ────────────────────────────────────────────
// Mock 사용량
// ────────────────────────────────────────────

export const MOCK_USAGE = {
  receiptUsed: 12,
  receiptLimit: 20,
  taxReturnUsed: 0,
  taxReturnLimit: 1,
};

// ────────────────────────────────────────────
// Mock 영수증
// ────────────────────────────────────────────

export const MOCK_RECEIPTS: MockReceipt[] = [
  {
    id: "receipt_001",
    imageUrl: "/mock/receipt1.jpg",
    merchantName: "스타벅스 강남점",
    amount: 18000,
    date: "2025-03-15",
    category: "MEAL",
    status: "COMPLETED",
    ocrConfidence: 0.97,
    uploadedAt: "2025-03-15T10:30:00Z",
  },
  {
    id: "receipt_002",
    imageUrl: "/mock/receipt2.jpg",
    merchantName: "쿠팡 (사무용품)",
    amount: 45000,
    date: "2025-03-12",
    category: "OFFICE_SUPPLIES",
    status: "COMPLETED",
    ocrConfidence: 0.92,
    uploadedAt: "2025-03-12T14:20:00Z",
  },
  {
    id: "receipt_003",
    imageUrl: "/mock/receipt3.jpg",
    merchantName: "SK텔레콤",
    amount: 89000,
    date: "2025-03-05",
    category: "COMMUNICATION",
    status: "COMPLETED",
    ocrConfidence: 0.99,
    uploadedAt: "2025-03-05T09:00:00Z",
  },
  {
    id: "receipt_004",
    imageUrl: "/mock/receipt4.jpg",
    merchantName: "카카오T (택시)",
    amount: 12500,
    date: "2025-03-18",
    category: "TRANSPORTATION",
    status: "COMPLETED",
    ocrConfidence: 0.95,
    uploadedAt: "2025-03-18T19:15:00Z",
  },
  {
    id: "receipt_005",
    imageUrl: "/mock/receipt5.jpg",
    merchantName: "인프런 (강의)",
    amount: 99000,
    date: "2025-03-10",
    category: "EDUCATION",
    status: "COMPLETED",
    ocrConfidence: 0.88,
    uploadedAt: "2025-03-10T11:00:00Z",
  },
  {
    id: "receipt_006",
    imageUrl: "/mock/receipt6.jpg",
    merchantName: "네이버클라우드",
    amount: 150000,
    date: "2025-03-01",
    category: "EQUIPMENT",
    status: "COMPLETED",
    ocrConfidence: 0.91,
    uploadedAt: "2025-03-01T08:00:00Z",
  },
  {
    id: "receipt_007",
    imageUrl: "/mock/receipt7.jpg",
    merchantName: "한국철도공사",
    amount: 35000,
    date: "2025-02-28",
    category: "TRANSPORTATION",
    status: "COMPLETED",
    ocrConfidence: 0.96,
    uploadedAt: "2025-02-28T07:30:00Z",
  },
  {
    id: "receipt_008",
    imageUrl: "/mock/receipt8.jpg",
    merchantName: "교보문고",
    amount: 28000,
    date: "2025-02-25",
    category: "EDUCATION",
    status: "COMPLETED",
    ocrConfidence: 0.94,
    uploadedAt: "2025-02-25T16:00:00Z",
  },
];

// ────────────────────────────────────────────
// Mock 경비 항목
// ────────────────────────────────────────────

export const MOCK_EXPENSES: MockExpenseItem[] = [
  {
    id: "exp_001",
    receiptId: "receipt_001",
    date: "2025-03-15",
    amount: 18000,
    merchantName: "스타벅스 강남점",
    category: "MEAL",
    isBusinessExpense: true,
    userVerified: true,
    memo: "클라이언트 미팅",
    taxYear: 2025,
  },
  {
    id: "exp_002",
    receiptId: "receipt_002",
    date: "2025-03-12",
    amount: 45000,
    merchantName: "쿠팡 (사무용품)",
    category: "OFFICE_SUPPLIES",
    isBusinessExpense: true,
    userVerified: true,
    memo: null,
    taxYear: 2025,
  },
  {
    id: "exp_003",
    receiptId: "receipt_003",
    date: "2025-03-05",
    amount: 89000,
    merchantName: "SK텔레콤",
    category: "COMMUNICATION",
    isBusinessExpense: true,
    userVerified: true,
    memo: "업무용 핸드폰 요금",
    taxYear: 2025,
  },
  {
    id: "exp_004",
    receiptId: "receipt_004",
    date: "2025-03-18",
    amount: 12500,
    merchantName: "카카오T (택시)",
    category: "TRANSPORTATION",
    isBusinessExpense: true,
    userVerified: false,
    memo: null,
    taxYear: 2025,
  },
  {
    id: "exp_005",
    receiptId: "receipt_005",
    date: "2025-03-10",
    amount: 99000,
    merchantName: "인프런 (강의)",
    category: "EDUCATION",
    isBusinessExpense: true,
    userVerified: true,
    memo: "React 고급 강의",
    taxYear: 2025,
  },
  {
    id: "exp_006",
    receiptId: "receipt_006",
    date: "2025-03-01",
    amount: 150000,
    merchantName: "네이버클라우드",
    category: "EQUIPMENT",
    isBusinessExpense: true,
    userVerified: true,
    memo: "서버 호스팅 비용",
    taxYear: 2025,
  },
  {
    id: "exp_007",
    receiptId: "receipt_007",
    date: "2025-02-28",
    amount: 35000,
    merchantName: "한국철도공사",
    category: "TRANSPORTATION",
    isBusinessExpense: true,
    userVerified: true,
    memo: "출장 KTX",
    taxYear: 2025,
  },
  {
    id: "exp_008",
    receiptId: "receipt_008",
    date: "2025-02-25",
    amount: 28000,
    merchantName: "교보문고",
    category: "EDUCATION",
    isBusinessExpense: true,
    userVerified: true,
    memo: null,
    taxYear: 2025,
  },
  {
    id: "exp_009",
    receiptId: null,
    date: "2025-02-20",
    amount: 200000,
    merchantName: "사무실 임차료 (2월분 일부)",
    category: "RENT",
    isBusinessExpense: true,
    userVerified: true,
    memo: "공유 오피스 이용료",
    taxYear: 2025,
  },
  {
    id: "exp_010",
    receiptId: null,
    date: "2025-01-31",
    amount: 120000,
    merchantName: "Adobe Creative Cloud",
    category: "EQUIPMENT",
    isBusinessExpense: true,
    userVerified: true,
    memo: "연간 구독 1/12",
    taxYear: 2025,
  },
];

// ────────────────────────────────────────────
// Mock KPI 데이터
// ────────────────────────────────────────────

export const MOCK_KPI: MockKpiData = {
  totalExpense: 796500,
  totalExpensePrevMonthChange: 12,
  estimatedTax: 185000,
  estimatedTaxPrevMonthChange: -8,
  receiptCount: 12,
  receiptCountPrevMonthChange: 4,
  estimatedSaving: 238950,
  estimatedSavingPrevMonthChange: 15,
};

// ────────────────────────────────────────────
// Mock 월별 경비 차트 데이터
// ────────────────────────────────────────────

export const MOCK_MONTHLY_DATA: MockMonthlyData[] = [
  { month: "1월", total: 520000, MEAL: 80000, TRANSPORTATION: 60000, COMMUNICATION: 89000, OFFICE_SUPPLIES: 45000, EDUCATION: 120000, OTHER: 126000 },
  { month: "2월", total: 683000, MEAL: 95000, TRANSPORTATION: 98000, COMMUNICATION: 89000, OFFICE_SUPPLIES: 71000, EDUCATION: 148000, OTHER: 182000 },
  { month: "3월", total: 796500, MEAL: 18000, TRANSPORTATION: 47500, COMMUNICATION: 89000, OFFICE_SUPPLIES: 45000, EDUCATION: 99000, OTHER: 498000 },
  { month: "4월", total: 0, MEAL: 0, TRANSPORTATION: 0, COMMUNICATION: 0, OFFICE_SUPPLIES: 0, EDUCATION: 0, OTHER: 0 },
  { month: "5월", total: 0, MEAL: 0, TRANSPORTATION: 0, COMMUNICATION: 0, OFFICE_SUPPLIES: 0, EDUCATION: 0, OTHER: 0 },
  { month: "6월", total: 0, MEAL: 0, TRANSPORTATION: 0, COMMUNICATION: 0, OFFICE_SUPPLIES: 0, EDUCATION: 0, OTHER: 0 },
  { month: "7월", total: 0, MEAL: 0, TRANSPORTATION: 0, COMMUNICATION: 0, OFFICE_SUPPLIES: 0, EDUCATION: 0, OTHER: 0 },
  { month: "8월", total: 0, MEAL: 0, TRANSPORTATION: 0, COMMUNICATION: 0, OFFICE_SUPPLIES: 0, EDUCATION: 0, OTHER: 0 },
  { month: "9월", total: 0, MEAL: 0, TRANSPORTATION: 0, COMMUNICATION: 0, OFFICE_SUPPLIES: 0, EDUCATION: 0, OTHER: 0 },
  { month: "10월", total: 0, MEAL: 0, TRANSPORTATION: 0, COMMUNICATION: 0, OFFICE_SUPPLIES: 0, EDUCATION: 0, OTHER: 0 },
  { month: "11월", total: 0, MEAL: 0, TRANSPORTATION: 0, COMMUNICATION: 0, OFFICE_SUPPLIES: 0, EDUCATION: 0, OTHER: 0 },
  { month: "12월", total: 0, MEAL: 0, TRANSPORTATION: 0, COMMUNICATION: 0, OFFICE_SUPPLIES: 0, EDUCATION: 0, OTHER: 0 },
];

// ────────────────────────────────────────────
// Mock 신고서 데이터
// ────────────────────────────────────────────

export const MOCK_TAX_RETURN = {
  id: "taxreturn_001",
  taxYear: 2025,
  totalIncome: 48000000,
  totalExpense: 7965000,
  standardDeduction: 1500000,
  taxBase: 38535000,
  estimatedTax: 4890250,
  estimatedSaving: 1969000,
  status: "DRAFT" as const,
  categoryBreakdown: [
    { category: "MEAL", label: "식비", amount: 193000 },
    { category: "TRANSPORTATION", label: "교통비", amount: 205500 },
    { category: "COMMUNICATION", label: "통신비", amount: 267000 },
    { category: "OFFICE_SUPPLIES", label: "사무용품", amount: 161000 },
    { category: "EDUCATION", label: "교육비", amount: 367000 },
    { category: "EQUIPMENT", label: "장비/소프트웨어", amount: 270000 },
    { category: "RENT", label: "임차료", amount: 200000 },
    { category: "OTHER", label: "기타", amount: 6302000 },
  ],
};

// ────────────────────────────────────────────
// Mock 구독 정보
// ────────────────────────────────────────────

export const MOCK_SUBSCRIPTION = {
  planStatus: "FREE" as PlanStatus,
  currentPeriodEnd: null,
  cancelAtPeriodEnd: false,
  paymentMethod: null,
};

export const MOCK_PREMIUM_SUBSCRIPTION = {
  planStatus: "PREMIUM" as PlanStatus,
  currentPeriodEnd: "2025-05-31",
  cancelAtPeriodEnd: false,
  paymentMethod: {
    brand: "visa",
    last4: "4242",
  },
};

// ────────────────────────────────────────────
// Mock OCR 결과 (영수증 업로드 후 반환값)
// ────────────────────────────────────────────

export const MOCK_OCR_RESULT = {
  merchantName: "스타벅스 강남역점",
  date: "2025-03-20",
  amount: 15500,
  category: "MEAL" as ExpenseCategory,
  confidence: 0.94,
  lowConfidenceFields: ["date"],
  classificationReason: "상호명 '스타벅스' 기반으로 식비(업무용)으로 분류됨",
};

// ────────────────────────────────────────────
// Mock 이용 후기
// ────────────────────────────────────────────

export const MOCK_TESTIMONIALS = [
  {
    id: "t1",
    name: "박현우",
    role: "프리랜서 개발자",
    content: "영수증 정리에 매달 2시간씩 썼는데, 이제 5분이면 끝나요. 종소세 신고서까지 자동으로 만들어줘서 세무사 비용 절약됐어요.",
    rating: 5,
    saving: 320000,
  },
  {
    id: "t2",
    name: "이지영",
    role: "유튜버",
    content: "카메라 장비, 소품 구매 영수증을 일일이 엑셀에 입력했는데 이제는 사진 찍으면 끝! OCR 정확도가 정말 높아요.",
    rating: 5,
    saving: 480000,
  },
  {
    id: "t3",
    name: "김서준",
    role: "온라인 강사",
    content: "세금 신고가 무서웠는데, AI가 공제 항목 설명도 해줘서 처음으로 혼자 신고해봤어요. 홈택스 가이드도 친절하게 나와 있어요.",
    rating: 5,
    saving: 195000,
  },
];
