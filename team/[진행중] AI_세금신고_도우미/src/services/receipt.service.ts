// ──────────────────────────────────────────────
// 영수증 서비스 — OCR + AI 분류 + DB 저장
// ──────────────────────────────────────────────
import { prisma } from "@/lib/prisma";
import { runOcr } from "./ocr.service";
import { classifyExpense } from "./ai-classifier.service";
import { logUsage } from "./usage.service";
import { deleteS3Object } from "./s3.service";
import { NotFoundError, ForbiddenError } from "@/lib/errors";

/**
 * 영수증 업로드 + OCR + AI 분류 + DB 저장
 */
export async function processReceiptUpload(params: {
  userId: string;
  imageKey: string;
  deleteAfterProcessing: boolean;
}): Promise<{
  receipt: {
    id: string;
    status: string;
    ocrConfidence: number | null;
    ocrEngine: string;
  };
  expenseItem: {
    id: string;
    merchantName: string;
    amount: number | null;
    date: string | null;
    category: string;
    confidence: number;
    classificationReason: string;
    lowConfidenceFields: string[];
    taxLawReference: string;
  } | null;
}> {
  // 1. Receipt 레코드 생성 (PROCESSING 상태)
  const receipt = await prisma.receipt.create({
    data: {
      userId: params.userId,
      imageUrl: params.imageKey,
      status: "PROCESSING",
    },
    select: { id: true },
  });

  // 사용량 로그 기록
  await logUsage(params.userId, "RECEIPT_UPLOAD", { receiptId: receipt.id });

  let expenseItem = null;

  try {
    // 2. OCR 실행
    const ocrResult = await runOcr(params.imageKey);

    // 3. AI 분류 (OCR 텍스트가 충분한 경우)
    let classification = null;
    if (ocrResult.rawText.length >= 10) {
      classification = await classifyExpense(ocrResult.rawText);
    }

    // 4. Receipt 업데이트 (COMPLETED)
    await prisma.receipt.update({
      where: { id: receipt.id },
      data: {
        ocrRawText: ocrResult.rawText,
        ocrConfidence: ocrResult.confidence,
        ocrEngine: ocrResult.engine,
        status: "COMPLETED",
        processedAt: new Date(),
        // 원본 삭제 옵션
        imageDeleted: params.deleteAfterProcessing,
      },
    });

    // 5. S3 원본 삭제 (옵션)
    if (params.deleteAfterProcessing) {
      await deleteS3Object(params.imageKey).catch((err) => {
        console.error("[Receipt] S3 원본 삭제 실패:", err);
      });
    }

    // 6. ExpenseItem 자동 생성 (AI 분류 성공 시)
    if (classification && classification.amount && classification.date) {
      const now = new Date();
      const taxYear = new Date(classification.date).getFullYear();

      const created = await prisma.expenseItem.create({
        data: {
          receiptId: receipt.id,
          userId: params.userId,
          date: new Date(classification.date),
          amount: classification.amount,
          merchantName: classification.merchantName,
          category: classification.category,
          isBusinessExpense: true,
          userVerified: false, // 사용자 최종 확인 대기
          taxYear,
          memo: `[AI 분류] ${classification.classificationReason}`,
        },
        select: {
          id: true,
          merchantName: true,
          amount: true,
          date: true,
          category: true,
        },
      });

      expenseItem = {
        id: created.id,
        merchantName: created.merchantName,
        amount: created.amount,
        date: created.date.toISOString().split("T")[0],
        category: created.category,
        confidence: classification.confidence,
        classificationReason: classification.classificationReason,
        lowConfidenceFields: classification.lowConfidenceFields,
        taxLawReference: classification.taxLawReference,
      };
    }

    const updatedReceipt = await prisma.receipt.findUnique({
      where: { id: receipt.id },
      select: { id: true, status: true, ocrConfidence: true, ocrEngine: true },
    });

    return { receipt: updatedReceipt!, expenseItem };
  } catch (error) {
    // OCR/AI 실패 시 FAILED 상태로 업데이트
    await prisma.receipt.update({
      where: { id: receipt.id },
      data: { status: "FAILED", processedAt: new Date() },
    });
    throw error;
  }
}

/**
 * OCR 재처리 (실패한 영수증 재시도)
 */
export async function reprocessReceipt(
  receiptId: string,
  userId: string
): Promise<void> {
  const receipt = await prisma.receipt.findUnique({
    where: { id: receiptId },
    select: { id: true, userId: true, imageUrl: true, imageDeleted: true, status: true },
  });

  if (!receipt) throw new NotFoundError("영수증", receiptId);
  if (receipt.userId !== userId) throw new ForbiddenError();
  if (receipt.imageDeleted) {
    throw new ForbiddenError("원본 이미지가 삭제되어 재처리할 수 없습니다.");
  }

  await prisma.receipt.update({
    where: { id: receiptId },
    data: { status: "PROCESSING" },
  });

  // 비동기 처리 (실제 환경에서는 큐에 넣지만 MVP에서는 동기 처리)
  const ocrResult = await runOcr(receipt.imageUrl);
  const classification =
    ocrResult.rawText.length >= 10
      ? await classifyExpense(ocrResult.rawText)
      : null;

  await prisma.receipt.update({
    where: { id: receiptId },
    data: {
      ocrRawText: ocrResult.rawText,
      ocrConfidence: ocrResult.confidence,
      ocrEngine: ocrResult.engine,
      status: "COMPLETED",
      processedAt: new Date(),
    },
  });

  if (classification?.amount && classification?.date) {
    // 기존 ExpenseItem 업데이트 또는 신규 생성
    await prisma.expenseItem.upsert({
      where: {
        // receipt 1:1 관계 보장을 위한 findFirst 후 upsert
        id: (
          await prisma.expenseItem.findFirst({
            where: { receiptId },
            select: { id: true },
          })
        )?.id ?? "nonexistent",
      },
      update: {
        merchantName: classification.merchantName,
        amount: classification.amount,
        date: new Date(classification.date),
        category: classification.category,
        userVerified: false,
      },
      create: {
        receiptId,
        userId,
        date: new Date(classification.date),
        amount: classification.amount,
        merchantName: classification.merchantName,
        category: classification.category,
        isBusinessExpense: true,
        userVerified: false,
        taxYear: new Date(classification.date).getFullYear(),
        memo: `[AI 재분류] ${classification.classificationReason}`,
      },
    });
  }
}
