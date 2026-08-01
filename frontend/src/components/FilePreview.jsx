import { useEffect, useState } from "react";

function FilePreview({ file }) {
  const [previewUrl, setPreviewUrl] = useState(null);
  // Track image loading so we can show a placeholder until it's ready.
  const [isImageLoaded, setIsImageLoaded] = useState(false);

  useEffect(() => {
    setIsImageLoaded(false);

    if (!file) {
      setPreviewUrl(null);
      return;
    }

    if (file.type.startsWith("image/")) {
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
      return () => URL.revokeObjectURL(url);
    } else {
      setPreviewUrl(null);
    }
  }, [file]);

  if (!file) return null;

  const isPdf = file.type === "application/pdf";
  const isImage = file.type.startsWith("image/");

  return (
    <div className="preview">
      <div className="preview-header">
        <span className="preview-name">{file.name}</span>
        <span className="preview-size">
          {(file.size / 1024).toFixed(1)} KB
        </span>
      </div>
      <div className="preview-body">
        {isImage ? (
          <>
            {/* Placeholder shown until the image finishes loading. */}
            {!isImageLoaded && (
              <div className="preview-placeholder">
                <span className="spinner spinner-dark" />
                <span>読み込み中...</span>
              </div>
            )}
            {previewUrl && (
              <img
                src={previewUrl}
                alt="プレビュー"
                className="preview-image"
                style={{ display: isImageLoaded ? "block" : "none" }}
                onLoad={() => setTimeout(() => setIsImageLoaded(true), 1000)} 
                onError={() => setIsImageLoaded(true)}
              />
            )}
          </>
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