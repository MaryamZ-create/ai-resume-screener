import type { Post } from "../posts/service.js";

function escapeHtml(value: string): string {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

export function renderDashboard(email: string, posts: Post[]): string {
  const postRows =
    posts.length === 0
      ? `<p>No posts yet. Create your first post below!</p>`
      : posts
          .map(
            (post) => `
      <article>
        <h3>${escapeHtml(post.title)}</h3>
        <p>
          <strong>Status:</strong> ${escapeHtml(post.status)}
          ${post.tags.length ? ` | <strong>Tags:</strong> ${post.tags.map(escapeHtml).join(", ")}` : ""}
        </p>
        <p>${escapeHtml(post.contentMd.slice(0, 160))}${post.contentMd.length > 160 ? "..." : ""}</p>
        <p><strong>Slug:</strong> ${escapeHtml(post.slug)}</p>
        ${
          post.status === "draft"
            ? `<form method="POST" action="/dashboard/posts/${post.id}/publish">
                 <button type="submit">Publish</button>
               </form>`
            : `<form method="POST" action="/dashboard/posts/${post.id}/unpublish">
                 <button type="submit">Unpublish</button>
               </form>`
        }
        <form method="POST" action="/dashboard/posts/${post.id}/delete">
          <button type="submit">Delete</button>
        </form>
        <hr>
      </article>
    `
          )
          .join("");

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Quill Dashboard</title>
</head>
<body>
  <h1>Quill Dashboard</h1>

  <p>Welcome, ${escapeHtml(email)}</p>

  <h2>MCP Connection</h2>
  <p>Connect your IDE to Quill using the MCP server:</p>
  <pre>${escapeHtml((process.env.BASE_URL ?? "http://localhost:3001") + "/mcp")}</pre>
  <p>Use your Quill API key as a Bearer token when configuring your MCP client.</p>


  <h2>Create a Post</h2>

  <form method="POST" action="/dashboard/posts">
    <label>
      Title
      <br>
      <input type="text" name="title" required>
    </label>

    <br><br>

    <label>
      Tags
      <br>
      <input type="text" name="tags" placeholder="ai, technology, writing">
    </label>

    <br><br>

    <label>
      Content
      <br>
      <textarea name="content" rows="12" cols="70" required></textarea>
    </label>

    <br><br>

    <button type="submit">Create Post</button>
  </form>

  <h2>Your Posts</h2>

  ${postRows}
</body>
</html>`;
}
