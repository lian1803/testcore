// ──────────────────────────────────────────────
// OCR 서비스
// 1차: Google Cloud Vision API (한글 정확도 우수)
// 2차: GPT-4o Vision (Vision API 실패/신뢰도 < 0.7 시 폴백)
// ──────────────────────────────────────────────

export interface OcrResult {
  rawText: string;
  confidence: number; // 0~1
  engine: "GOOGLE_VISION" | "GPT4O_VISION";
}

/**
 * S3 오브젝트 키로부터 이미지 바이트를 가져와 OCR 실행
 * 1차: Google Vision API
 * 2차: GPT-4o Vision (신뢰도 < 0.7 또는 실패 시)
 */
export async function runOcr(imageKey: string): Promise<OcrResult> {
  // S3에서 이미지 URL 생성 (퍼블릭 버킷이면 직접 URL, 프라이빗이면 presigned URL 필요)
  const imageUrl = buildS3PublicUrl(imageKey);

  try {
    const googleResult = await runGoogleVision(imageUrl);
    // 신뢰도 0.7 이상이면 Google Vision 결과 사용
    if (googleResult.confidence >= 0.7 && googleResult.rawText.length > 0) {
      return googleResult;
    }
    // 신뢰도 낮으면 GPT-4o Vision 폴백
    console.log(`[OCR] Google Vision 신뢰도 낮음 (${googleResult.confidence}), GPT-4o 폴백 실행`);
    return await runGpt4oVision(imageUrl);
  } catch (googleError) {
    console.error("[OCR] Google Vision 실패:", googleError);
    // Google Vision 실패 시 GPT-4o Vision 폴백
    return await runGpt4oVision(imageUrl);
  }
}

/** Google Cloud Vision API 호출 */
async function runGoogleVision(imageUrl: string): Promise<OcrResult> {
  const apiKey = process.env.GOOGLE_VISION_API_KEY;
  if (!apiKey) {
    throw new Error("GOOGLE_VISION_API_KEY 환경변수가 설정되지 않았습니다.");
  }

  const response = await fetch(
    `https://vision.googleapis.com/v1/images:annotate?key=${apiKey}`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        requests: [
          {
            image: { source: { imageUri: imageUrl } },
            features: [
              { type: "TEXT_DETECTION", maxResults: 1 },
              { type: "DOCUMENT_TEXT_DETECTION", maxResults: 1 },
            ],
            imageContext: {
              languageHints: ["ko", "en"], // 한국어 우선
            },
          },
        ],
      }),
    }
  );

  if (!response.ok) {
    const err = await response.text();
    throw new Error(`Google Vision API 오류: ${response.status} ${err}`);
  }

  const data = await response.json();
  const annotation = data.responses?.[0]?.fullTextAnnotation;
  const textAnnotations = data.responses?.[0]?.textAnnotations;

  if (!annotation && (!textAnnotations || textAnnotations.length === 0)) {
    return { rawText: "", confidence: 0, engine: "GOOGLE_VISION" };
  }

  const rawText = annotation?.text ?? textAnnotations?.[0]?.description ?? "";

  // Google Vision은 신뢰도를 직접 제공하지 않음
  // pages.blocks.paragraphs.words.symbols의 confidence 평균으로 추정
  const pages = annotation?.pages ?? [];
  let totalConf = 0;
  let count = 0;
  for (const page of pages) {
    for (const block of page.blocks ?? []) {
      for (const para of block.paragraphs ?? []) {
        for (const word of para.words ?? []) {
          for (const symbol of word.symbols ?? []) {
            if (typeof symbol.confidence === "number") {
              totalConf += symbol.confidence;
              count++;
            }
          }
        }
      }
    }
  }

  const confidence = count > 0 ? totalConf / count : 0.85; // 신뢰도 미제공 시 기본값

  return { rawText, confidence, engine: "GOOGLE_VISION" };
}

/** GPT-4o Vision API 호출 (폴백) */
async function runGpt4oVision(imageUrl: string): Promise<OcrResult> {
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
      max_tokens: 1000,
      messages: [
        {
          role: "user",
          content: [
            {
              type: "text",
              text: `이 영수증 이미지에서 텍스트를 모두 정확하게 추출해주세요.
한국어와 영어를 모두 포함하여 읽을 수 있는 모든 텍스트를 원본 그대로 출력하세요.
JSON 형식으로 응답: {"text": "추출된 텍스트"}`,
            },
            {
              type: "image_url",
              image_url: { url: imageUrl, detail: "high" },
            },
          ],
        },
      ],
    }),
  });

  if (!response.ok) {
    const err = await response.text();
    throw new Error(`GPT-4o Vision API 오류: ${response.status} ${err}`);
  }

  const data = await response.json();
  const content = data.choices?.[0]?.message?.content ?? "";

  let rawText = content;
  try {
    const parsed = JSON.parse(content);
    rawText = parsed.text ?? content;
  } catch {
    // JSON 파싱 실패 시 원본 텍스트 사용
    rawText = content;
  }

  return {
    rawText,
    confidence: 0.82, // GPT-4o Vision은 신뢰도 미제공 → 경험적 기본값
    engine: "GPT4O_VISION",
  };
}

// BUG FIX (보안): S3 버킷이 프라이빗인 경우 public URL로 직접 접근 불가.
// Google Vision API는 공개 URL 또는 base64 인코딩 이미지를 요구.
// MVP에서는 s3.service.ts의 generatePresignedUploadUrl에서 presigned URL을 활용하거나
// 서버에서 S3 오브젝트를 직접 읽어 base64로 인코딩해야 함.
// 현재는 버킷이 퍼블릭임을 전제로 하되, 향후 프라이빗 전환 시 presigned URL로 교체 필요.
// TODO: 프라이빗 버킷으로 전환 시 s3.service.ts의 generatePresignedReadUrl() 구현 후 교체.
function buildS3PublicUrl(imageKey: string): string {
  const bucket = process.env.AWS_S3_BUCKET_NAME!;
  const region = process.env.AWS_REGION ?? "ap-northeast-2";
  return `https://${bucket}.s3.${region}.amazonaws.com/${imageKey}`;
}
