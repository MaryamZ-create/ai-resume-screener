import { DatabaseSync } from "node:sqlite";

export type PostStatus = "draft" | "published" | "scheduled";

export interface Post {
  id: number;
  userId: number;
  title: string;
  slug: string;
  contentMd: string;
  tags: string[];
  status: PostStatus;
  metaTitle: string | null;
  metaDescription: string | null;
  publishedAt: string | null;
  scheduledAt: string | null;
  createdAt: string;
  updatedAt: string;
}

function mapPost(row: any): Post {
  return {
    id: row.id,
    userId: row.user_id,
    title: row.title,
    slug: row.slug,
    contentMd: row.content_md,
    tags: JSON.parse(row.tags ?? '[]'),
    status: row.status,
    metaTitle: row.meta_title,
    metaDescription: row.meta_description,
    publishedAt: row.published_at,
    scheduledAt: row.scheduled_at,
    createdAt: row.created_at,
    updatedAt: row.updated_at,
  };
}

export function createPost(
  db: DatabaseSync,
  userId: number,
  title: string,
  contentMd: string,
  tags: string[] = []
): Post {
  const cleanTitle = title.trim();
  const cleanContent = contentMd.trim();

  if (!cleanTitle) {
    throw new Error("Title is required.");
  }

  if (!cleanContent) {
    throw new Error("Content is required.");
  }

  const slug =
    cleanTitle
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-|-$/g, "") || `post-${Date.now()}`;

  const result = db
    .prepare(
      `INSERT INTO posts (user_id, title, slug, content_md, tags)
       VALUES (?, ?, ?, ?, ?)
       RETURNING *`
    )
    .get(userId, cleanTitle, slug, cleanContent, JSON.stringify(tags));

  return mapPost(result);
}

export function getPost(
  db: DatabaseSync,
  userId: number,
  postId: number
): Post | null {
  const row = db
    .prepare(
      `SELECT *
       FROM posts
       WHERE id = ? AND user_id = ?`
    )
    .get(postId, userId);

  return row ? mapPost(row) : null;
}

export function listPosts(
  db: DatabaseSync,
  userId: number,
  status?: PostStatus,
  limit = 20
): Post[] {
  const safeLimit = Math.min(Math.max(limit, 1), 100);

  const rows = status
    ? db
        .prepare(
          `SELECT *
           FROM posts
           WHERE user_id = ? AND status = ?
           ORDER BY created_at DESC
           LIMIT ?`
        )
        .all(userId, status, safeLimit)
    : db
        .prepare(
          `SELECT *
           FROM posts
           WHERE user_id = ?
           ORDER BY created_at DESC
           LIMIT ?`
        )
        .all(userId, safeLimit);

  return rows.map(mapPost);
}

export function updatePost(
  db: DatabaseSync,
  userId: number,
  postId: number,
  updates: {
    title?: string;
    contentMd?: string;
    tags?: string[];
  }
): Post | null {
  const existing = getPost(db, userId, postId);

  if (!existing) {
    return null;
  }

  const title =
    updates.title !== undefined ? updates.title.trim() : existing.title;

  const contentMd =
    updates.contentMd !== undefined
      ? updates.contentMd.trim()
      : existing.contentMd;

  if (!title) {
    throw new Error("Title cannot be empty.");
  }

  if (!contentMd) {
    throw new Error("Content cannot be empty.");
  }

  const tags = updates.tags !== undefined ? updates.tags : existing.tags;

  const slug =
    updates.title !== undefined
      ? title
          .toLowerCase()
          .replace(/[^a-z0-9]+/g, "-")
          .replace(/^-|-$/g, "") || `post-${postId}`
      : existing.slug;

  const row = db
    .prepare(
      `UPDATE posts
       SET title = ?,
           slug = ?,
           content_md = ?,
           tags = ?,
           updated_at = CURRENT_TIMESTAMP
       WHERE id = ? AND user_id = ?
       RETURNING *`
    )
    .get(title, slug, contentMd, JSON.stringify(tags), postId, userId);

  return row ? mapPost(row) : null;
}

export function deletePost(
  db: DatabaseSync,
  userId: number,
  postId: number
): boolean {
  const result = db
    .prepare(
      `DELETE FROM posts
       WHERE id = ? AND user_id = ?`
    )
    .run(postId, userId);

  return result.changes > 0;
}

export function publishPost(
  db: DatabaseSync,
  userId: number,
  postId: number
): Post | null {
  const post = getPost(db, userId, postId);

  if (!post) {
    return null;
  }

  const row = db
    .prepare(
      `UPDATE posts
       SET status = 'published',
           published_at = CURRENT_TIMESTAMP,
           scheduled_at = NULL,
           updated_at = CURRENT_TIMESTAMP
       WHERE id = ? AND user_id = ?
       RETURNING *`
    )
    .get(postId, userId);

  return row ? mapPost(row) : null;
}

export function unpublishPost(
  db: DatabaseSync,
  userId: number,
  postId: number
): Post | null {
  const post = getPost(db, userId, postId);

  if (!post) {
    return null;
  }

  const row = db
    .prepare(
      `UPDATE posts
       SET status = 'draft',
           published_at = NULL,
           scheduled_at = NULL,
           updated_at = CURRENT_TIMESTAMP
       WHERE id = ? AND user_id = ?
       RETURNING *`
    )
    .get(postId, userId);

  return row ? mapPost(row) : null;
}

export function schedulePost(
  db: DatabaseSync,
  userId: number,
  postId: number,
  publishAt: string
): Post | null {
  const post = getPost(db, userId, postId);

  if (!post) {
    return null;
  }

  if (!publishAt || Number.isNaN(Date.parse(publishAt))) {
    throw new Error("A valid publish date is required.");
  }

  const row = db
    .prepare(
      `UPDATE posts
       SET status = 'scheduled',
           scheduled_at = ?,
           published_at = NULL,
           updated_at = CURRENT_TIMESTAMP
       WHERE id = ? AND user_id = ?
       RETURNING *`
    )
    .get(publishAt, postId, userId);

  return row ? mapPost(row) : null;
}

export function manageSeo(
  db: DatabaseSync,
  userId: number,
  postId: number,
  metaTitle?: string,
  metaDescription?: string
): Post | null {
  const existing = getPost(db, userId, postId);

  if (!existing) {
    return null;
  }

  const nextMetaTitle =
    metaTitle !== undefined ? metaTitle.trim() || null : existing.metaTitle;

  const nextMetaDescription =
    metaDescription !== undefined
      ? metaDescription.trim() || null
      : existing.metaDescription;

  const row = db
    .prepare(
      `UPDATE posts
       SET meta_title = ?,
           meta_description = ?,
           updated_at = CURRENT_TIMESTAMP
       WHERE id = ? AND user_id = ?
       RETURNING *`
    )
    .get(nextMetaTitle, nextMetaDescription, postId, userId);

  return row ? mapPost(row) : null;
}

export function listPublishedPosts(
  db: DatabaseSync,
  limit = 50
): Post[] {
  const safeLimit = Math.min(Math.max(limit, 1), 100);

  const rows = db
    .prepare(
      `SELECT *
       FROM posts
       WHERE status = 'published'
       ORDER BY published_at DESC
       LIMIT ?`
    )
    .all(safeLimit);

  return rows.map(mapPost);
}

export function getAnalytics(
  db: DatabaseSync,
  userId: number,
  postId?: number,
  range = 30
) {
  const safeRange = Math.min(Math.max(range, 1), 365);

  const rows = postId
    ? db.prepare(
        `SELECT event_type, COUNT(*) AS count
         FROM analytics_events e
         JOIN posts p ON p.id = e.post_id
         WHERE p.user_id = ?
           AND p.id = ?
           AND e.occurred_at >= datetime('now', ?)
         GROUP BY event_type`
      ).all(userId, postId, `-${safeRange} days`)
    : db.prepare(
        `SELECT event_type, COUNT(*) AS count
         FROM analytics_events e
         JOIN posts p ON p.id = e.post_id
         WHERE p.user_id = ?
           AND e.occurred_at >= datetime('now', ?)
         GROUP BY event_type`
      ).all(userId, `-${safeRange} days`);

  return {
    range: safeRange,
    postId: postId ?? null,
    events: rows.map((row: any) => ({
      eventType: row.event_type,
      count: Number(row.count),
    })),
  };
}
