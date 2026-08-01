function ResultDisplay({ result }) {
  if (!result) return null;

  return (
    <div className="result">
      <h2 className="result-title">解析結果</h2>

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