import { IncomingMessage, ServerResponse } from "node:http";
import { db } from "../db/connection.js";
import { authenticateApiKey } from "../auth/api-key-auth.js";
import {
  createPost,
  deletePost,
  getPost,
  listPosts,
  updatePost,
  publishPost,
} from "../posts/service.js";

function sendJson(
  res: ServerResponse,
  statusCode: number,
  data: unknown
): void {
  res.writeHead(statusCode, {
    "Content-Type": "application/json",
  });

  res.end(JSON.stringify(data));
}

function getApiKey(req: IncomingMessage): string | null {
  const authorization = req.headers.authorization;

  if (!authorization?.startsWith("Bearer ")) {
    return null;
  }

  return authorization.slice("Bearer ".length).trim() || null;
}

async function readJsonBody(req: IncomingMessage): Promise<any> {
  const chunks: Buffer[] = [];

  for await (const chunk of req) {
    chunks.push(Buffer.from(chunk));
  }

  const body = Buffer.concat(chunks).toString("utf8");

  if (!body) {
    return {};
  }

  return JSON.parse(body);
}

export async function handleApiRequest(
  req: IncomingMessage,
  res: ServerResponse
): Promise<boolean> {
  if (!req.url?.startsWith("/api/")) {
    return false;
  }

  const apiKey = getApiKey(req);

  if (!apiKey) {
    sendJson(res, 401, { error: "API key required." });
    return true;
  }

  const user = authenticateApiKey(db, apiKey);

  if (!user) {
    sendJson(res, 401, { error: "Invalid or revoked API key." });
    return true;
  }

  try {
    if (req.method === "POST" && req.url === "/api/posts") {
      const body = await readJsonBody(req);

      const post = createPost(
        db,
        user.userId,
        body.title,
        body.contentMd ?? body.content,
        body.tags ?? []
      );

      sendJson(res, 201, post);
      return true;
    }

    if (req.method === "GET" && req.url === "/api/posts") {
      const posts = listPosts(db, user.userId);

      sendJson(res, 200, posts);
      return true;
    }

    const postMatch = req.url.match(/^\/api\/posts\/(\d+)$/);

    if (postMatch) {
      const postId = Number(postMatch[1]);

      if (req.method === "GET") {
        const post = getPost(db, user.userId, postId);

        if (!post) {
          sendJson(res, 404, { error: "Post not found." });
          return true;
        }

        sendJson(res, 200, post);
        return true;
      }

      if (req.method === "PATCH") {
        const body = await readJsonBody(req);

        const post = updatePost(db, user.userId, postId, {
          title: body.title,
          contentMd: body.contentMd ?? body.content,
          tags: body.tags,
        });

        if (!post) {
          sendJson(res, 404, { error: "Post not found." });
          return true;
        }

        sendJson(res, 200, post);
        return true;
      }

      if (req.method === "DELETE") {
        const deleted = deletePost(db, user.userId, postId);

        if (!deleted) {
          sendJson(res, 404, { error: "Post not found." });
          return true;
        }

        sendJson(res, 200, { success: true });
        return true;
      }
    }

    const publishMatch = req.url.match(
      /^\/api\/posts\/(\d+)\/publish$/
    );

    if (req.method === "POST" && publishMatch) {
      const postId = Number(publishMatch[1]);

      const post = publishPost(db, user.userId, postId);

      if (!post) {
        sendJson(res, 404, { error: "Post not found." });
        return true;
      }

      sendJson(res, 200, post);
      return true;
    }

    sendJson(res, 404, { error: "API endpoint not found." });
    return true;
  } catch (error) {
    console.error(error);

    sendJson(res, 400, {
      error: error instanceof Error ? error.message : "Request failed.",
    });

    return true;
  }
}
