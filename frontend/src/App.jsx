import { useState, useEffect } from "react";
import FileUpload from "./components/FileUpload";
import FileItem from "./components/FileItem";
import AnalyzeButton from "./components/AnalyzeButton";
import { analyzeFile } from "./api";

// Generate a simple unique id for each selected file.
let nextId = 1;
const SHOW_HEALTH = import.meta.env.VITE_SHOW_HEALTH === "true";

function App() {
  const [health, setHealth] = useState({ label: "確認中...", state: "" });
  const [items, setItems] = useState([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  useEffect(() => {
    // Skip health polling entirely when the indicator is hidden.
    if (!SHOW_HEALTH) return;

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
      const delay = ok ? 180000 : 5000;
      timeoutId = setTimeout(checkHealth, delay);
    };

    checkHealth();
    return () => {
      if (timeoutId) clearTimeout(timeoutId);
    };
  }, []);

  // Add newly selected files to the list as pending items.
  const handleFilesSelect = (files) => {
    const newItems = files.map((file) => ({
      id: nextId++,
      file,
      status: "pending",
      result: null,
      error: null,
    }));
    setItems((prev) => [ ...newItems,...prev]);
  };

  const handleRemove = (id) => {
    setItems((prev) => prev.filter((item) => item.id !== id));
  };

  const handleClearAll = () => {
    setItems([]);
  };

  // Update one item by id, leaving the others untouched.
  const updateItem = (id, changes) => {
    setItems((prev) =>
      prev.map((item) => (item.id === id ? { ...item, ...changes } : item))
    );
  };

  // Analyze all pending items sequentially so one failure doesn't
  // block the rest, and to avoid hitting API rate limits.
  const handleAnalyzeAll = async () => {
    const pending = items.filter((item) => item.status === "pending").reverse();
    if (pending.length === 0) return;

    setIsAnalyzing(true);
    for (const item of pending) {
      updateItem(item.id, { status: "analyzing", error: null, result: null });
      try {
        const data = await analyzeFile(item.file);
        updateItem(item.id, { status: "done", result: data });
      } catch (e) {
        updateItem(item.id, { status: "error", error: e.message });
      }
    }
    setIsAnalyzing(false);
  };

  // Re-run analysis for a single item (LLM output varies between runs).
  const handleRegenerate = async (id) => {
    const item = items.find((i) => i.id === id);
    if (!item || isAnalyzing) return;

    updateItem(id, { status: "analyzing", error: null });
    try {
      const data = await analyzeFile(item.file);
      updateItem(id, { status: "done", result: data });
    } catch (e) {
      updateItem(id, { status: "error", error: e.message });
    }
  };

  // Apply user edits to a result (local only; not sent to the backend).
  const handleEditResult = (id, updatedResult) => {
    updateItem(id, { result: updatedResult });
  };

  const pendingCount = items.filter((i) => i.status === "pending").length;

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
          <FileUpload onFilesSelect={handleFilesSelect} />

          {items.length > 0 && (
            <>
              <div className="list-actions">
                <span className="list-count">
                  {items.length}件のファイル
                </span>
                <button
                  className="clear-button"
                  onClick={handleClearAll}
                  disabled={isAnalyzing}
                >
                  すべてクリア
                </button>
              </div>

              <div className="file-list">
                {items.map((item) => (
                  <FileItem
                    key={item.id}
                    item={item}
                    onRemove={handleRemove}
                    onRegenerate={handleRegenerate}
                    onEditResult={handleEditResult}
                  />
                ))}
              </div>

              {pendingCount > 0 && (
                <AnalyzeButton
                  onClick={handleAnalyzeAll}
                  isLoading={isAnalyzing}
                  disabled={isAnalyzing}
                  label={`${pendingCount}件を解析する`}
                />
              )}
            </>
          )}
        </div>
      </div>

      <footer className="footer">
        <span>画像OCR・説明文生成アプリ</span>
        {SHOW_HEALTH && (              // ← 呢個令佢唔顯示
          <span className="health">
            <span className={`health-dot ${health.state}`} />
            バックエンド: {health.label}
          </span>
        )}
      </footer>
    </>
  );
}

export default App;