import { DatabaseSync } from "node:sqlite";
import { hashPassword } from "./password.js";
import { generateApiKey, hashApiKey } from "./api-key.js";

export interface SignupResult {
  userId: number;
  email: string;
  apiKey: string;
}

export async function signup(
  db: DatabaseSync,
  email: string,
  password: string
): Promise<SignupResult> {
  const normalizedEmail = email.trim().toLowerCase();

  if (!normalizedEmail) {
    throw new Error("Email is required.");
  }

  if (password.length < 8) {
    throw new Error("Password must be at least 8 characters.");
  }

  const passwordHash = await hashPassword(password);
  const apiKey = generateApiKey();
  const apiKeyHash = hashApiKey(apiKey);

  db.exec("BEGIN");

  try {
    const userResult = db
      .prepare(
        `INSERT INTO users (email, password_hash)
         VALUES (?, ?)
         RETURNING id`
      )
      .get(normalizedEmail, passwordHash) as { id: number };

    db.prepare(
      `INSERT INTO api_keys (user_id, key_hash)
       VALUES (?, ?)`
    ).run(userResult.id, apiKeyHash);

    db.exec("COMMIT");

    return {
      userId: userResult.id,
      email: normalizedEmail,
      apiKey,
    };
  } catch (error) {
    db.exec("ROLLBACK");
    throw error;
  }
}
