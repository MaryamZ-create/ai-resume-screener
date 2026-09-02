import { createHmac } from "node:crypto";

const SESSION_TTL_MS = 1000 * 60 * 60 * 24 * 7;

function getSessionSecret(): string {
  const secret = process.env.SESSION_SECRET;

  if (!secret) {
    throw new Error("SESSION_SECRET is not configured.");
  }

  return secret;
}

export interface SessionData {
  userId: number;
  email: string;
  expiresAt: number;
}

export function createSession(userId: number, email: string): string {
  const expiresAt = Date.now() + SESSION_TTL_MS;
  const payload = `${userId}:${email}:${expiresAt}`;

  const signature = createHmac("sha256", getSessionSecret())
    .update(payload)
    .digest("hex");

  return `${Buffer.from(payload).toString("base64url")}.${signature}`;
}

export function verifySession(token: string): SessionData | null {
  const [encodedPayload, signature] = token.split(".");

  if (!encodedPayload || !signature) {
    return null;
  }

  const payload = Buffer.from(encodedPayload, "base64url").toString("utf8");
  const expectedSignature = createHmac("sha256", getSessionSecret())
    .update(payload)
    .digest("hex");

  if (signature.length !== expectedSignature.length) {
    return null;
  }

  const signatureMatches = signature === expectedSignature;

  if (!signatureMatches) {
    return null;
  }

  const [userIdText, email, expiresAtText] = payload.split(":");
  const userId = Number(userIdText);
  const expiresAt = Number(expiresAtText);

  if (!Number.isInteger(userId) || !email || !Number.isFinite(expiresAt)) {
    return null;
  }

  if (Date.now() >= expiresAt) {
    return null;
  }

  return {
    userId,
    email,
    expiresAt,
  };
}
