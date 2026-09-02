import { DatabaseSync } from "node:sqlite";
import { verifyPassword } from "./password.js";

export interface LoginResult {
  userId: number;
  email: string;
}

export async function login(
  db: DatabaseSync,
  email: string,
  password: string
): Promise<LoginResult> {
  const normalizedEmail = email.trim().toLowerCase();

  if (!normalizedEmail) {
    throw new Error("Email is required.");
  }

  const user = db
    .prepare(
      `SELECT id, email, password_hash
       FROM users
       WHERE email = ?`
    )
    .get(normalizedEmail) as
    | {
        id: number;
        email: string;
        password_hash: string;
      }
    | undefined;

  if (!user) {
    throw new Error("Invalid email or password.");
  }

  const passwordValid = await verifyPassword(password, user.password_hash);

  if (!passwordValid) {
    throw new Error("Invalid email or password.");
  }

  return {
    userId: user.id,
    email: user.email,
  };
}
