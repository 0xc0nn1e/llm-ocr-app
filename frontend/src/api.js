// API client for the backend. Uses same-origin /api paths (Vite proxy).

/**
 * Send a file to the analyze endpoint and return the structured result.
 * Throws an Error with a Japanese message on failure.
 */
export async function analyzeFile(file) {
  const formData = new FormData();
  formData.append("file", file);

  let res;
  try {
    res = await fetch("/api/analyze", {
      method: "POST",
      body: formData,
    });
  } catch {
    // Network-level failure (backend down, connection refused, etc.).
    throw new Error("サーバーに接続できませんでした。");
  }

  if (!res.ok) {
    // Backend returns { error: { code, message } } on failure.
    let message = "解析中にエラーが発生しました。";
    try {
      const data = await res.json();
      if (data?.error?.message) {
        message = data.error.message;
      }
    } catch {
      // Response wasn't JSON; keep the default message.
    }
    throw new Error(message);
  }

  return res.json();
}