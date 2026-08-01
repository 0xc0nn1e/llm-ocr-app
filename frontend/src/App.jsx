import { useState, useEffect } from "react";
import FileUpload from "./components/FileUpload";
import FilePreview from "./components/FilePreview";
import AnalyzeButton from "./components/AnalyzeButton";
import ResultDisplay from "./components/ResultDisplay";
import ErrorMessage from "./components/ErrorMessage";
import { analyzeFile } from "./api";

function App() {
  const [health, setHealth] = useState({ label: "確認中...", state: "" });
  const [selectedFile, setSelectedFile] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

useEffect(() => {
  let timeoutId = null;

  const checkHealth = async () => {
    let ok = false;
    try {
      const res = await fetch("/api/health");
      const data = await res.json();
      ok = data.status === "ok";
      setHealth(
        ok
          ? { label: "接続OK", state: "ok" }
          : { label: "異常", state: "fail" }
      );
    } catch {
      setHealth({ label: "接続失敗", state: "fail" });
    }
    // Reschedule based on current state:
    // - connected: check occasionally (3 min) just to confirm it's alive
    // - disconnected: retry quickly (5 s) to recover fast
    const delay = ok ? 180000 : 5000;
    timeoutId = setTimeout(checkHealth, delay);
  };

  checkHealth(); // Check immediately on mount.

  return () => {
    if (timeoutId) clearTimeout(timeoutId);
  };
}, []);

  // When a new file is selected, reset previous result/error.
  const handleFileSelect = (file) => {
    setSelectedFile(file);
    setResult(null);
    setError(null);
  };

  const handleAnalyze = async () => {
    if (!selectedFile) return;
    setIsLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await analyzeFile(selectedFile);
      setResult(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setIsLoading(false);
    }
  };

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
          <FileUpload onFileSelect={handleFileSelect} />
          <FilePreview file={selectedFile} />

          {selectedFile && (
            <AnalyzeButton
              onClick={handleAnalyze}
              isLoading={isLoading}
              disabled={!selectedFile}
            />
          )}

          <ErrorMessage message={error} />
          <ResultDisplay result={result} />
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