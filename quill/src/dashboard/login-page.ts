export function renderLoginPage(error = ""): string {
  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Login — Quill</title>
</head>
<body>
  <h1>Quill</h1>
  <h2>Login</h2>
  ${error ? `<p>${error}</p>` : ""}
  <form method="POST" action="/login">
    <label>
      Email
      <input type="email" name="email" required>
    </label>
    <br><br>
    <label>
      Password
      <input type="password" name="password" required>
    </label>
    <br><br>
    <button type="submit">Login</button>
  </form>
</body>
</html>`;
}
