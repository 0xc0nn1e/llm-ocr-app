import { useState, useEffect } from "react";

// Format the four fields into a readable plain-text block for copying.
function formatResult(result) {
  return [
    `【OCR（文字起こし）】`,
    result.ocr,
    ``,
    `【内容の説明】`,
    result.description,
    ``,
    `【タグ】`,
    result.tags.join(", "),
    ``,
    `【代替テキスト（alt）】`,
    result.alt,
  ].join("\n");
}

function ResultDisplay({ result, onRegenerate, onEdit, isRegenerating }) {
  const [copied, setCopied] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  // Local draft while editing; committed to the parent on save.
  const [draft, setDraft] = useState(null);

  // Reset the draft whenever the underlying result changes (e.g. regenerate).
  useEffect(() => {
    setIsEditing(false);
    setDraft(null);
  }, [result]);

  if (!result) return null;

  const handleCopy = async () => {
    const text = formatResult(result);
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(text);
      } else {
        const textarea = document.createElement("textarea");
        textarea.value = text;
        textarea.style.position = "fixed";
        textarea.style.opacity = "0";
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand("copy");
        document.body.removeChild(textarea);
      }
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (e) {
      console.warn("Copy to clipboard failed:", e);
    }
  };

  const startEditing = () => {
    // Copy the current result into an editable draft.
    setDraft({
      ocr: result.ocr,
      description: result.description,
      tags: result.tags.join(", "),
      alt: result.alt,
    });
    setIsEditing(true);
  };

  const cancelEditing = () => {
    setIsEditing(false);
    setDraft(null);
  };

  const saveEditing = () => {
    onEdit({
      ...result,
      ocr: draft.ocr,
      description: draft.description,
      // Split the comma-separated tag input back into an array.
      tags: draft.tags
        .split(",")
        .map((t) => t.trim())
        .filter(Boolean),
      alt: draft.alt,
    });
    setIsEditing(false);
    setDraft(null);
  };

  const updateDraft = (field, value) => {
    setDraft((prev) => ({ ...prev, [field]: value }));
  };

  return (
    <div className="result">
      <div className="result-header">
        <h2 className="result-title">解析結果</h2>
        <div className="result-actions">
          {isEditing ? (
            <>
              <button className="action-button" onClick={cancelEditing}>
                キャンセル
              </button>
              <button
                className="action-button action-primary"
                onClick={saveEditing}
              >
                保存
              </button>
            </>
          ) : (
            <>
              <button
                className="action-button"
                onClick={onRegenerate}
                disabled={isRegenerating}
              >
                {isRegenerating ? "再生成中..." : "再生成"}
              </button>
              <button className="action-button" onClick={startEditing}>
                編集
              </button>
              <button className="action-button" onClick={handleCopy}>
                {copied ? "コピーしました ✓" : "結果をコピー"}
              </button>
            </>
          )}
        </div>
      </div>

      <section className="result-section">
        <h3 className="result-label">OCR（文字起こし）</h3>
        {isEditing ? (
          <textarea
            className="result-edit result-edit-mono"
            value={draft.ocr}
            onChange={(e) => updateDraft("ocr", e.target.value)}
            rows={6}
          />
        ) : (
          <pre className="result-ocr">{result.ocr}</pre>
        )}
      </section>

      <section className="result-section">
        <h3 className="result-label">内容の説明</h3>
        {isEditing ? (
          <textarea
            className="result-edit"
            value={draft.description}
            onChange={(e) => updateDraft("description", e.target.value)}
            rows={5}
          />
        ) : (
          <p className="result-text">{result.description}</p>
        )}
      </section>

      <section className="result-section">
        <h3 className="result-label">タグ</h3>
        {isEditing ? (
          <>
            <input
              className="result-edit"
              value={draft.tags}
              onChange={(e) => updateDraft("tags", e.target.value)}
            />
            <p className="edit-hint">カンマ区切りで入力してください</p>
          </>
        ) : (
          <div className="result-tags">
            {result.tags.map((tag, i) => (
              <span key={i} className="tag">
                {tag}
              </span>
            ))}
          </div>
        )}
      </section>

      <section className="result-section">
        <h3 className="result-label">代替テキスト（alt）</h3>
        {isEditing ? (
          <textarea
            className="result-edit"
            value={draft.alt}
            onChange={(e) => updateDraft("alt", e.target.value)}
            rows={3}
          />
        ) : (
          <p className="result-text">{result.alt}</p>
        )}
      </section>
    </div>
  );
}

export default ResultDisplay;