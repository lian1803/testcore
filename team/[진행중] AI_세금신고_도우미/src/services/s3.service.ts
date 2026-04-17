// ──────────────────────────────────────────────
// S3 서비스 — presigned URL 생성, 오브젝트 삭제
// ──────────────────────────────────────────────
import crypto from "crypto";

const BUCKET = process.env.AWS_S3_BUCKET_NAME!;
const REGION = process.env.AWS_REGION ?? "ap-northeast-2";
const ACCESS_KEY = process.env.AWS_ACCESS_KEY_ID!;
const SECRET_KEY = process.env.AWS_SECRET_ACCESS_KEY!;

/**
 * S3 presigned PUT URL 생성 (클라이언트 직접 업로드용)
 * 유효 시간: 5분
 */
export async function generatePresignedUploadUrl(params: {
  userId: string;
  fileName: string;
  contentType: string;
}): Promise<{ uploadUrl: string; imageKey: string }> {
  const ext = params.fileName.split(".").pop()?.toLowerCase() ?? "jpg";
  const allowed = ["jpg", "jpeg", "png", "webp", "heic", "pdf"];
  if (!allowed.includes(ext)) {
    throw new Error(`지원하지 않는 파일 형식입니다: ${ext}`);
  }

  // S3 키: receipts/{userId}/{timestamp}-{random}.{ext}
  const imageKey = `receipts/${params.userId}/${Date.now()}-${crypto.randomBytes(8).toString("hex")}.${ext}`;
  const expiresIn = 300; // 5분

  // AWS SDK 없이 직접 presigned URL 생성 (SigV4)
  // 실제 프로덕션에서는 @aws-sdk/s3-presigned-post 사용 권장
  const uploadUrl = await createPresignedPutUrl(imageKey, params.contentType, expiresIn);

  return { uploadUrl, imageKey };
}

/**
 * S3 오브젝트 삭제 (영수증 원본 삭제 옵션)
 */
export async function deleteS3Object(imageKey: string): Promise<void> {
  const url = `https://${BUCKET}.s3.${REGION}.amazonaws.com/${imageKey}`;
  const now = new Date();
  const dateString = now.toISOString().replace(/[:-]|\.\d{3}/g, "").slice(0, 15) + "Z";
  const dateShort = dateString.slice(0, 8);

  const headers = await signRequest({
    method: "DELETE",
    url,
    dateString,
    dateShort,
    payload: "",
  });

  const response = await fetch(url, { method: "DELETE", headers });
  if (!response.ok && response.status !== 204) {
    throw new Error(`S3 삭제 실패: ${response.status} ${await response.text()}`);
  }
}

async function createPresignedPutUrl(
  key: string,
  contentType: string,
  expiresIn: number
): Promise<string> {
  const now = new Date();
  const dateString = now.toISOString().replace(/[:-]|\.\d{3}/g, "").slice(0, 15) + "Z";
  const dateShort = dateString.slice(0, 8);
  const credential = `${ACCESS_KEY}/${dateShort}/${REGION}/s3/aws4_request`;

  const queryParams = new URLSearchParams({
    "X-Amz-Algorithm": "AWS4-HMAC-SHA256",
    "X-Amz-Credential": credential,
    "X-Amz-Date": dateString,
    "X-Amz-Expires": String(expiresIn),
    "X-Amz-SignedHeaders": "content-type;host",
  });

  const host = `${BUCKET}.s3.${REGION}.amazonaws.com`;
  const canonicalRequest = [
    "PUT",
    `/${key}`,
    queryParams.toString(),
    `content-type:${contentType}\nhost:${host}\n`,
    "content-type;host",
    "UNSIGNED-PAYLOAD",
  ].join("\n");

  const stringToSign = [
    "AWS4-HMAC-SHA256",
    dateString,
    `${dateShort}/${REGION}/s3/aws4_request`,
    await sha256(canonicalRequest),
  ].join("\n");

  const signingKey = await getSigningKey(dateShort);
  const signature = await hmacHex(signingKey, stringToSign);

  queryParams.set("X-Amz-Signature", signature);

  return `https://${host}/${key}?${queryParams.toString()}`;
}

async function signRequest(params: {
  method: string;
  url: string;
  dateString: string;
  dateShort: string;
  payload: string;
}): Promise<Record<string, string>> {
  const urlObj = new URL(params.url);
  const host = urlObj.hostname;
  const payloadHash = await sha256(params.payload);

  const canonicalRequest = [
    params.method,
    urlObj.pathname,
    urlObj.search.slice(1),
    `host:${host}\nx-amz-date:${params.dateString}\n`,
    "host;x-amz-date",
    payloadHash,
  ].join("\n");

  const stringToSign = [
    "AWS4-HMAC-SHA256",
    params.dateString,
    `${params.dateShort}/${REGION}/s3/aws4_request`,
    await sha256(canonicalRequest),
  ].join("\n");

  const signingKey = await getSigningKey(params.dateShort);
  const signature = await hmacHex(signingKey, stringToSign);

  return {
    Host: host,
    "X-Amz-Date": params.dateString,
    Authorization: `AWS4-HMAC-SHA256 Credential=${ACCESS_KEY}/${params.dateShort}/${REGION}/s3/aws4_request,SignedHeaders=host;x-amz-date,Signature=${signature}`,
  };
}

async function getSigningKey(dateShort: string): Promise<ArrayBuffer> {
  const kDate = await hmac(`AWS4${SECRET_KEY}`, dateShort);
  const kRegion = await hmac(kDate, REGION);
  const kService = await hmac(kRegion, "s3");
  return hmac(kService, "aws4_request");
}

async function sha256(message: string): Promise<string> {
  const encoder = new TextEncoder();
  const data = encoder.encode(message);
  const hash = await crypto.subtle.digest("SHA-256", data);
  return Array.from(new Uint8Array(hash))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

async function hmac(
  key: string | ArrayBuffer,
  message: string
): Promise<ArrayBuffer> {
  const encoder = new TextEncoder();
  const keyData =
    typeof key === "string" ? encoder.encode(key) : new Uint8Array(key);
  const cryptoKey = await crypto.subtle.importKey(
    "raw",
    keyData,
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"]
  );
  return crypto.subtle.sign("HMAC", cryptoKey, encoder.encode(message));
}

async function hmacHex(
  key: string | ArrayBuffer,
  message: string
): Promise<string> {
  const result = await hmac(key, message);
  return Array.from(new Uint8Array(result))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}
