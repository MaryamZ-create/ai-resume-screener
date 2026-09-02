import { createServer } from "node:http";
import { db } from "./db/connection.js";
import { initializeDatabase } from "./db/database.js";
import { handleApiRequest } from "./api/router.js";

const PORT = Number(process.env.PORT ?? 3000);

initializeDatabase(db);

const server = createServer(async (req, res) => {
  if (req.method === "GET" && req.url === "/health") {
    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ status: "ok" }));
    return;
  }

  if (req.url?.startsWith("/api/")) {
    await handleApiRequest(req, res);
    return;
  }

  res.writeHead(404, { "Content-Type": "application/json" });
  res.end(JSON.stringify({ error: "Not found" }));
});

server.listen(PORT, () => {
  console.log(`Quill server listening on port ${PORT}`);
});
