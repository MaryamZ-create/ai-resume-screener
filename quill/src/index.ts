import { createServer } from "node:http";
import { db } from "./db/connection.js";
import { initializeDatabase } from "./db/database.js";
import { handleApiRequest } from "./api/router.js";
import { renderDashboard } from "./dashboard/page.js";
import { renderLoginPage } from "./dashboard/login-page.js";
import { login } from "./auth/login.js";
import { createSession, verifySession } from "./auth/session.js";
import { createPost, listPosts, listPublishedPosts, publishPost, deletePost, unpublishPost } from "./posts/service.js";

const PORT = Number(process.env.PORT ?? 3000);

initializeDatabase(db);

async function readBody(
  req: import("node:http").IncomingMessage
): Promise<string> {
  const chunks: Buffer[] = [];

  for await (const chunk of req) {
    chunks.push(Buffer.from(chunk));
  }

  return Buffer.concat(chunks).toString("utf8");
}

function getSessionToken(
  req: import("node:http").IncomingMessage
): string | null {
  const cookieHeader = req.headers.cookie;

  if (!cookieHeader) {
    return null;
  }

  const cookies = cookieHeader.split(";");

  for (const cookie of cookies) {
    const [name, ...valueParts] = cookie.trim().split("=");

    if (name === "quill_session") {
      return valueParts.join("=") || null;
    }
  }

  return null;
}

const server = createServer(async (req, res) => {
  if (req.method === "GET" && req.url === "/health") {
    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ status: "ok" }));
    return;
  }

  if (req.method === "GET" && req.url === "/login") {
    res.writeHead(200, {
      "Content-Type": "text/html; charset=utf-8",
    });
    res.end(renderLoginPage());
    return;
  }

  if (req.method === "POST" && req.url === "/login") {
    try {
      const body = await readBody(req);
      const form = new URLSearchParams(body);

      const email = form.get("email") ?? "";
      const password = form.get("password") ?? "";

      const result = await login(db, email, password);
      const sessionToken = createSession(result.userId, result.email);

      res.writeHead(302, {
        Location: "/dashboard",
        "Set-Cookie": `quill_session=${sessionToken}; HttpOnly; Path=/; SameSite=Lax; Max-Age=604800`,
      });
      res.end();
    } catch {
      res.writeHead(401, {
        "Content-Type": "text/html; charset=utf-8",
      });
      res.end(renderLoginPage("Invalid email or password."));
    }

    return;
  }

  if (req.method === "POST" && req.url === "/dashboard/posts") {
    const sessionToken = getSessionToken(req);
    const session = sessionToken ? verifySession(sessionToken) : null;

    if (!session) {
      res.writeHead(302, { Location: "/login" });
      res.end();
      return;
    }

    try {
      const body = await readBody(req);
      const form = new URLSearchParams(body);

      const title = form.get("title") ?? "";
      const content = form.get("content") ?? "";
      const tags = (form.get("tags") ?? "")
        .split(",")
        .map((tag) => tag.trim())
        .filter(Boolean);

      createPost(db, session.userId, title, content, tags);

      res.writeHead(302, {
        Location: "/dashboard",
      });
      res.end();
    } catch {
      res.writeHead(400, {
        "Content-Type": "text/html; charset=utf-8",
      });
      res.end("Could not create post.");
    }

    return;
  }

  if (req.method === "POST" && req.url?.match(/^\/dashboard\/posts\/\d+\/delete$/)) {
    const sessionToken = getSessionToken(req);
    const session = sessionToken ? verifySession(sessionToken) : null;

    if (!session) {
      res.writeHead(302, { Location: "/login" });
      res.end();
      return;
    }

    const postId = Number(req.url.split("/")[3]);

    const deleted = deletePost(db, session.userId, postId);

    if (!deleted) {
      res.writeHead(404, {
        "Content-Type": "text/plain; charset=utf-8",
      });
      res.end("Post not found.");
      return;
    }

    res.writeHead(302, {
      Location: "/dashboard",
    });
    res.end();
    return;
  }

  if (req.method === "POST" && req.url?.match(/^\/dashboard\/posts\/\d+\/delete$/)) {
    const sessionToken = getSessionToken(req);
    const session = sessionToken ? verifySession(sessionToken) : null;

    if (!session) {
      res.writeHead(302, { Location: "/login" });
      res.end();
      return;
    }

    const postId = Number(req.url.split("/")[3]);
    const deleted = deletePost(db, session.userId, postId);

    if (!deleted) {
      res.writeHead(404, { "Content-Type": "text/plain; charset=utf-8" });
      res.end("Post not found.");
      return;
    }

    res.writeHead(302, { Location: "/dashboard" });
    res.end();
    return;
  }

  if (req.method === "POST" && req.url?.match(/^\/dashboard\/posts\/\d+\/unpublish$/)) {
    const sessionToken = getSessionToken(req);
    const session = sessionToken ? verifySession(sessionToken) : null;

    if (!session) {
      res.writeHead(302, { Location: "/login" });
      res.end();
      return;
    }

    const postId = Number(req.url.split("/")[3]);

    const post = unpublishPost(db, session.userId, postId);

    if (!post) {
      res.writeHead(404, {
        "Content-Type": "text/plain; charset=utf-8",
      });
      res.end("Post not found.");
      return;
    }

    res.writeHead(302, {
      Location: "/dashboard",
    });
    res.end();
    return;
  }

  if (req.method === "POST" && req.url?.match(/^\/dashboard\/posts\/\d+\/publish$/)) {
    const sessionToken = getSessionToken(req);
    const session = sessionToken ? verifySession(sessionToken) : null;

    if (!session) {
      res.writeHead(302, { Location: "/login" });
      res.end();
      return;
    }

    const postId = Number(req.url.split("/")[3]);

    const post = publishPost(db, session.userId, postId);

    if (!post) {
      res.writeHead(404, {
        "Content-Type": "text/plain; charset=utf-8",
      });
      res.end("Post not found.");
      return;
    }

    res.writeHead(302, {
      Location: "/dashboard",
    });
    res.end();
    return;
  }

  if (req.method === "GET" && req.url === "/blog") {
    const posts = listPublishedPosts(db);
    const items = posts.map(
      (post) => `<article>
        <h2>${post.title}</h2>
        <p>${post.contentMd.slice(0, 300)}</p>
        <p><strong>Tags:</strong> ${post.tags.join(", ")}</p>
        <hr>
      </article>`
    ).join("");

    const html = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Quill Blog</title>
</head>
<body>
  <h1>Quill Blog</h1>
  ${posts.length ? items : "<p>No published posts yet.</p>"}
</body>
</html>`;

    res.writeHead(200, {
      "Content-Type": "text/html; charset=utf-8",
    });
    res.end(html);
    return;
  }

  if (req.method === "GET" && req.url === "/dashboard") {
    const sessionToken = getSessionToken(req);
    const session = sessionToken ? verifySession(sessionToken) : null;

    if (!session) {
      res.writeHead(302, {
        Location: "/login",
      });
      res.end();
      return;
    }

    res.writeHead(200, {
      "Content-Type": "text/html; charset=utf-8",
    });
    const posts = listPosts(db, session.userId);
    res.end(renderDashboard(session.email, posts));
    return;
  }

  if (req.url?.startsWith("/api/")) {
    await handleApiRequest(req, res);
    return;
  }

  res.writeHead(404, {
    "Content-Type": "application/json",
  });
  res.end(JSON.stringify({ error: "Not found" }));
});

server.listen(PORT, () => {
  console.log(`Quill server listening on port ${PORT}`);
});
