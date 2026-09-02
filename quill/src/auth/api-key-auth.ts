import { DatabaseSync } from "node:sqlite";
import { hashApiKey } from "./api-key.js";

export interface AuthenticatedUser {
  userId: number;
  email: string;
}

export function authenticateApiKey(
  db: DatabaseSync,
  apiKey: string
): AuthenticatedUser | null {
  const normalizedKey = apiKey.trim();

  if (!normalizedKey) {
    return null;
  }

  const keyHash = hashApiKey(normalizedKey);

  const user = db
    .prepare(
      `SELECT users.id, users.email
       FROM api_keys
       JOIN users ON users.id = api_keys.user_id
       WHERE api_keys.key_hash = ?
         AND api_keys.revoked_at IS NULL`
    )
    .get(keyHash) as
    | {
        id: number;
        email: string;
      }
    | undefined;

  if (!user) {
    return null;
  }

  return {
    userId: user.id,
    email: user.email,
  };
}
