import { useEffect, useState } from "react";

function FilePreview({ file }) {
  const [previewUrl, setPreviewUrl] = useState(null);

  useEffect(() => {
    if (!file) {
      setPreviewUrl(null);
      return;
    }

    // Only create object URLs for images; PDFs show an icon instead.
    if (file.type.startsWith("image/")) {
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
      // Clean up the object URL when the file changes or unmounts.
      return () => URL.revokeObjectURL(url);
    } else {
      setPreviewUrl(null);
    }
  }, [file]);

  if (!file) return null;

  const isPdf = file.type === "application/pdf";

  return (
    <div className="preview">
      <div className="preview-header">
        <span className="preview-name">{file.name}</span>
        <span className="preview-size">
          {(file.size / 1024).toFixed(1)} KB
        </span>
      </div>
      <div className="preview-body">
        {previewUrl ? (
          <img src={previewUrl} alt="プレビュー" className="preview-image" />
        ) : isPdf ? (
          <div className="preview-pdf">
            <span className="preview-pdf-icon">PDF</span>
            <span>PDFファイルが選択されました</span>
          </div>
        ) : null}
      </div>
    </div>
  );
}

export default FilePreview;