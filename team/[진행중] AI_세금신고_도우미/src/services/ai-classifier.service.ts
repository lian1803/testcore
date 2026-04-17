// ──────────────────────────────────────────────
// AI 분류 서비스 — GPT-4o
// OCR 텍스트 → 경비 카테고리 + 금액/날짜/상호명 추출
// 세법 항목 매핑: 소득세법 시행령 제55조 (필요경비 범위)
// ──────────────────────────────────────────────

export type ExpenseCategory =
  | "OFFICE_SUPPLIES"   // 사무용품비 — 소득세법 시행령 §55①8
  | "COMMUNICATION"     // 통신비 — 소득세법 시행령 §55①13
  | "TRANSPORTATION"    // 교통비(여비교통비) — 소득세법 시행령 §55①7
  | "MEAL"              // 식비/접대비 — 소득세법 §35(접대비), §55①6(복리후생비)
  | "EDUCATION"         // 교육/도서비 — 소득세법 시행령 §55①11
  | "EQUIPMENT"         // 장비/소프트웨어(감가상각 또는 즉시손금) — §55①2
  | "RENT"              // 임차료 — 소득세법 시행령 §55①3
  | "INSURANCE"         // 보험료 — 소득세법 시행령 §55①4
  | "ADVERTISING"       // 광고/마케팅비 — 소득세법 시행령 §55①15
  | "PROFESSIONAL_FEE"  // 전문가 수수료 — 소득세법 시행령 §55①14
  | "OTHER";            // 기타 — 해당 조항 불명확 시 보수적 처리

export interface ClassificationResult {
  merchantName: string;      // 상호명
  date: string | null;       // ISO 8601 날짜 (YYYY-MM-DD), 인식 불가 시 null
  amount: number | null;     // 원 단위 정수, 인식 불가 시 null
  category: ExpenseCategory;
  confidence: number;        // AI 분류 신뢰도 0~1
  classificationReason: string; // 분류 근거 (사용자에게 표시)
  lowConfidenceFields: string[]; // 신뢰도 낮은 필드 목록
  taxLawReference: string;   // 적용 세법 조항
}

const CLASSIFICATION_PROMPT = `당신은 한국 종합소득세 전문 경비 분류 AI입니다.
영수증 OCR 텍스트를 분석하여 아래 JSON 형식으로 정확하게 응답하세요.

카테고리 분류 기준 (소득세법 시행령 제55조 기반):
- OFFICE_SUPPLIES: 문구류, 복사용지, 프린터 잉크 등 사무용품 (§55①8)
- COMMUNICATION: 휴대폰 요금, 인터넷 요금, 우편 (§55①13)
- TRANSPORTATION: 택시, KTX, 버스, 주차비, 항공권 (§55①7)
- MEAL: 식당 식사, 카페, 업무 관련 식비 및 접대비 (§35, §55①6)
- EDUCATION: 강의, 도서, 세미나, 자격증 (§55①11)
- EQUIPMENT: 컴퓨터, 소프트웨어 구독, 카메라, 서버 비용 (§55①2)
- RENT: 사무실 임대료, 공유오피스, 창고 임차 (§55①3)
- INSURANCE: 사업 관련 보험료 (§55①4)
- ADVERTISING: 광고비, 홍보물, 마케팅 비용 (§55①15)
- PROFESSIONAL_FEE: 세무사, 변호사, 디자이너 외주비 (§55①14)
- OTHER: 위 항목에 해당하지 않거나 불확실한 경우

주의사항:
- 불확실한 경우 반드시 OTHER로 분류 (보수적 처리 원칙)
- 금액은 총 결제금액 기준, 부가세 포함 금액으로 기재
- 날짜는 반드시 YYYY-MM-DD 형식

응답 JSON 형식:
{
  "merchantName": "상호명",
  "date": "YYYY-MM-DD 또는 null",
  "amount": 숫자 또는 null,
  "category": "카테고리코드",
  "confidence": 0.0~1.0,
  "classificationReason": "분류 근거 설명 (한국어, 1~2문장)",
  "lowConfidenceFields": ["낮은신뢰도필드명 배열"],
  "taxLawReference": "소득세법 시행령 §55①X 또는 해당 없음"
}`;

/**
 * OCR 텍스트를 GPT-4o로 분류
 * @param ocrText - Google Vision 또는 GPT-4o Vision으로 추출한 텍스트
 * @returns ClassificationResult
 */
export async function classifyExpense(
  ocrText: string
): Promise<ClassificationResult> {
  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) {
    throw new Error("OPENAI_API_KEY 환경변수가 설정되지 않았습니다.");
  }

  const response = await fetch("https://api.openai.com/v1/chat/completions", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${apiKey}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model: "gpt-4o",
      temperature: 0.1, // 일관된 분류를 위해 낮은 온도
      max_tokens: 500,
      response_format: { type: "json_object" },
      messages: [
        { role: "system", content: CLASSIFICATION_PROMPT },
        {
          role: "user",
          content: `다음 영수증 텍스트를 분류해주세요:\n\n${ocrText}`,
        },
      ],
    }),
  });

  if (!response.ok) {
    const err = await response.text();
    throw new Error(`GPT-4o API 오류: ${response.status} ${err}`);
  }

  const data = await response.json();
  const content = data.choices?.[0]?.message?.content;

  if (!content) {
    throw new Error("GPT-4o 응답이 비어있습니다.");
  }

  const parsed = JSON.parse(content) as ClassificationResult;

  // 필드 유효성 보정
  return {
    merchantName: parsed.merchantName ?? "상호명 미확인",
    date: parsed.date && isValidDate(parsed.date) ? parsed.date : null,
    amount: parsed.amount && typeof parsed.amount === "number" && parsed.amount > 0
      ? Math.round(parsed.amount) // 원 단위 반올림
      : null,
    category: isValidCategory(parsed.category) ? parsed.category : "OTHER",
    confidence: Math.min(1, Math.max(0, parsed.confidence ?? 0.5)),
    classificationReason: parsed.classificationReason ?? "분류 근거 없음",
    lowConfidenceFields: Array.isArray(parsed.lowConfidenceFields)
      ? parsed.lowConfidenceFields
      : [],
    taxLawReference: parsed.taxLawReference ?? "해당 없음",
  };
}

function isValidDate(dateStr: string): boolean {
  return /^\d{4}-\d{2}-\d{2}$/.test(dateStr) && !isNaN(Date.parse(dateStr));
}

const VALID_CATEGORIES: ExpenseCategory[] = [
  "OFFICE_SUPPLIES",
  "COMMUNICATION",
  "TRANSPORTATION",
  "MEAL",
  "EDUCATION",
  "EQUIPMENT",
  "RENT",
  "INSURANCE",
  "ADVERTISING",
  "PROFESSIONAL_FEE",
  "OTHER",
];

function isValidCategory(cat: string): cat is ExpenseCategory {
  return VALID_CATEGORIES.includes(cat as ExpenseCategory);
}
