import { mkdirSync } from "node:fs";
import { dirname } from "node:path";
import { DatabaseSync } from "node:sqlite";

const dbPath = process.env.DB_PATH ?? "data/quill.db";

mkdirSync(dirname(dbPath), { recursive: true });

export const db = new DatabaseSync(dbPath);

db.exec("PRAGMA foreign_keys = ON;");
