import crypto from "crypto";

const ALGORITHM = "aes-256-gcm";
const DEMO_KEY = "0000000000000000000000000000000000000000000000000000000000000000";

function getKey(): string {
  const key = process.env.ENCRYPTION_KEY || DEMO_KEY;
  return key.length === 64 ? key : DEMO_KEY;
}

export function encryptToken(token: string): string {
  const iv = crypto.randomBytes(16);
  const key = Buffer.from(getKey(), "hex");
  const cipher = crypto.createCipheriv(ALGORITHM, key, iv);

  let encrypted = cipher.update(token, "utf-8", "hex");
  encrypted += cipher.final("hex");

  const authTag = cipher.getAuthTag();
  const combined = iv.toString("hex") + ":" + authTag.toString("hex") + ":" + encrypted;

  return combined;
}

export function decryptToken(encryptedData: string): string {
  try {
    const parts = encryptedData.split(":");
    if (parts.length !== 3) {
      throw new Error("Invalid encrypted data format");
    }

    const iv = Buffer.from(parts[0], "hex");
    const authTag = Buffer.from(parts[1], "hex");
    const encrypted = parts[2];
    const key = Buffer.from(getKey(), "hex");

    const decipher = crypto.createDecipheriv(ALGORITHM, key, iv);
    decipher.setAuthTag(authTag);

    let decrypted = decipher.update(encrypted, "hex", "utf-8");
    decrypted += decipher.final("utf-8");

    return decrypted;
  } catch {
    throw new Error("Failed to decrypt token");
  }
}
