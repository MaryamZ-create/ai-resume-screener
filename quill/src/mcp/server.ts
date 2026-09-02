import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { createServer } from "node:http";
import { randomUUID } from "node:crypto";
import { z } from "zod";

import { db } from "../db/connection.js";
import { initializeDatabase } from "../db/database.js";
import { authenticateApiKey } from "../auth/api-key-auth.js";
import {
  createPost,
  deletePost,
  getPost,
  listPosts,
  updatePost,
  publishPost,
} from "../posts/service.js";

const PORT = Number(process.env.MCP_PORT ?? 3001);

initializeDatabase(db);

function getApiKey(req: import("node:http").IncomingMessage): string | null {
  const authorization = req.headers.authorization;

  if (!authorization?.startsWith("Bearer ")) {
    return null;
  }

  return authorization.slice("Bearer ".length).trim() || null;
}

function createMcpServer(userId: number): McpServer {
  const server = new McpServer({
    name: "quill",
    version: "1.0.0",
  });

  server.tool(
    "create_post",
    "Create a new Quill blog post.",
    {
      title: z.string().min(1),
      content: z.string().min(1),
      tags: z.array(z.string()).optional(),
    },
    async ({ title, content, tags }) => {
      const post = createPost(db, userId, title, content, tags ?? []);

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(post, null, 2),
          },
        ],
      };
    }
  );

  server.tool(
    "list_posts",
    "List the authenticated user's blog posts.",
    {
      status: z.enum(["draft", "published", "scheduled"]).optional(),
      limit: z.number().int().min(1).max(100).optional(),
    },
    async ({ status, limit }) => {
      const posts = listPosts(db, userId, status, limit ?? 20);

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(posts, null, 2),
          },
        ],
      };
    }
  );

  server.tool(
    "get_post",
    "Get one of the authenticated user's blog posts.",
    {
      id: z.number().int().positive(),
    },
    async ({ id }) => {
      const post = getPost(db, userId, id);

      if (!post) {
        return {
          isError: true,
          content: [
            {
              type: "text",
              text: "Post not found.",
            },
          ],
        };
      }

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(post, null, 2),
          },
        ],
      };
    }
  );

  server.tool(
    "update_post",
    "Update one of the authenticated user's blog posts.",
    {
      id: z.number().int().positive(),
      title: z.string().optional(),
      content: z.string().optional(),
      tags: z.array(z.string()).optional(),
    },
    async ({ id, title, content, tags }) => {
      const updates: {
        title?: string;
        contentMd?: string;
        tags?: string[];
      } = {};

      if (title !== undefined) updates.title = title;
      if (content !== undefined) updates.contentMd = content;
      if (tags !== undefined) updates.tags = tags;

      const post = updatePost(db, userId, id, updates);

      if (!post) {
        return {
          isError: true,
          content: [
            {
              type: "text",
              text: "Post not found.",
            },
          ],
        };
      }

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(post, null, 2),
          },
        ],
      };
    }
  );

  server.tool(
    "delete_post",
    "Delete one of the authenticated user's blog posts.",
    {
      id: z.number().int().positive(),
    },
    async ({ id }) => {
      const deleted = deletePost(db, userId, id);

      if (!deleted) {
        return {
          isError: true,
          content: [
            {
              type: "text",
              text: "Post not found.",
            },
          ],
        };
      }

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify({ success: true }),
          },
        ],
      };
    }
  );

  server.tool(
    "publish_post",
    "Publish one of the authenticated user's blog posts.",
    {
      id: z.number().int().positive(),
    },
    async ({ id }) => {
      const post = publishPost(db, userId, id);

      if (!post) {
        return {
          isError: true,
          content: [
            {
              type: "text",
              text: "Post not found.",
            },
          ],
        };
      }

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(post, null, 2),
          },
        ],
      };
    }
  );

  return server;
}

const sessions = new Map<string, {
  server: McpServer;
  transport: StreamableHTTPServerTransport;
}>();

const httpServer = createServer(async (req, res) => {
  if (req.method === "GET" && req.url === "/health") {
    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ status: "ok" }));
    return;
  }

  if (req.url !== "/mcp") {
    res.writeHead(404, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ error: "Not found" }));
    return;
  }

  const sessionId = req.headers["mcp-session-id"];

  if (sessionId && typeof sessionId === "string") {
    const session = sessions.get(sessionId);

    if (!session) {
      res.writeHead(400, { "Content-Type": "application/json" });
      res.end(JSON.stringify({ error: "Unknown MCP session." }));
      return;
    }

    await session.transport.handleRequest(req, res);
    return;
  }

  const apiKey = getApiKey(req);

  if (!apiKey) {
    res.writeHead(401, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ error: "API key required." }));
    return;
  }

  const user = authenticateApiKey(db, apiKey);

  if (!user) {
    res.writeHead(401, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ error: "Invalid or revoked API key." }));
    return;
  }

  const server = createMcpServer(user.userId);

  const transport = new StreamableHTTPServerTransport({
    sessionIdGenerator: () => randomUUID(),
    onsessioninitialized: (newSessionId) => {
      sessions.set(newSessionId, {
        server,
        transport,
      });
    },
  });

  await server.connect(
    transport as Parameters<typeof server.connect>[0]
  );

  await transport.handleRequest(req, res);
});

httpServer.listen(PORT, () => {
  console.log(`Quill MCP server listening on port ${PORT}`);
});
