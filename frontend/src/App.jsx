import { useState, useEffect } from "react";

function App() {
  // Backend health status, to confirm the frontend can reach the API.
  const [health, setHealth] = useState({ label: "確認中...", state: "" });

  useEffect(() => {
    // Calls /api/health via the Vite proxy (same-origin, no CORS).
    fetch("/api/health")
      .then((res) => res.json())
      .then((data) =>
        setHealth(
          data.status === "ok"
            ? { label: "接続OK", state: "ok" }
            : { label: "異常", state: "fail" }
        )
      )
      .catch(() => setHealth({ label: "接続失敗", state: "fail" }));
  }, []);

  return (
    <>
      <div className="container">
        <h1>画像OCR・説明文生成</h1>
        <p className="subtitle">
          画像やPDFをアップロードすると、マルチモーダルLLMが文字起こし（OCR）と
          内容の説明を生成します。
        </p>

        <div className="card">
          <span className="pill">Claude</span>
          <p className="placeholder">
            アップロード機能は次のステップで追加します
          </p>
        </div>
      </div>

      <footer className="footer">
        <span>画像OCR・説明文生成アプリ</span>
        <span className="health">
          <span className={`health-dot ${health.state}`} />
          バックエンド: {health.label}
        </span>
      </footer>
    </>
  );
}

export default App;