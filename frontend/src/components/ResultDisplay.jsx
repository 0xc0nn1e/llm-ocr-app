import { useState } from "react";

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

function ResultDisplay({ result }) {
  const [copied, setCopied] = useState(false);

  if (!result) return null;

const handleCopy = async () => {
  const text = formatResult(result);

  try {
    if (navigator.clipboard && window.isSecureContext) {
      // Modern Clipboard API (requires HTTPS or localhost).
      await navigator.clipboard.writeText(text);
    } else {
      // Fallback for non-secure contexts (e.g. accessing via LAN IP over HTTP).
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
    setTimeout(() => setCopied(false), 3000);
  } catch {
    console.warn("Copy to clipboard failed:", e);
  }
};

  return (
    <div className="result">
      <div className="result-header">
        <h2 className="result-title">解析結果</h2>
        <button className="copy-button" onClick={handleCopy}>
          {copied ? "コピーしました ✓" : "結果をコピー"}
        </button>
      </div>

      <section className="result-section">
        <h3 className="result-label">OCR（文字起こし）</h3>
        <pre className="result-ocr">{result.ocr}</pre>
      </section>

      <section className="result-section">
        <h3 className="result-label">内容の説明</h3>
        <p className="result-text">{result.description}</p>
      </section>

      <section className="result-section">
        <h3 className="result-label">タグ</h3>
        <div className="result-tags">
          {result.tags.map((tag, i) => (
            <span key={i} className="tag">
              {tag}
            </span>
          ))}
        </div>
      </section>

      <section className="result-section">
        <h3 className="result-label">代替テキスト（alt）</h3>
        <p className="result-text">{result.alt}</p>
      </section>
    </div>
  );
}

export default ResultDisplay;