import { useRef, useState } from "react";

// Accepted MIME types, matching the backend's validation.
const ACCEPTED = "image/jpeg,image/png,application/pdf";

function FileUpload({ onFileSelect }) {
  const inputRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);

  // Forward the chosen file to the parent.
  const handleFile = (file) => {
    if (file) {
      onFileSelect(file);
    }
  };

  const handleInputChange = (e) => {
    handleFile(e.target.files?.[0]);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    handleFile(e.dataTransfer.files?.[0]);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  return (
    <div
      className={`upload-zone ${isDragging ? "dragging" : ""}`}
      onClick={() => inputRef.current?.click()}
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
    >
      <input
        ref={inputRef}
        type="file"
        accept={ACCEPTED}
        onChange={handleInputChange}
        hidden
      />
      <p className="upload-text">
        クリックまたはドラッグ＆ドロップでファイルを選択
      </p>
      <p className="upload-hint">対応形式: JPEG / PNG / PDF</p>
    </div>
  );
}

export default FileUpload;