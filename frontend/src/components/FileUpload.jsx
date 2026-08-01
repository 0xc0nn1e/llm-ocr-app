import { useRef, useState } from "react";

// Accepted MIME types, matching the backend's validation.
const ACCEPTED = "image/jpeg,image/png,application/pdf";

function FileUpload({ onFilesSelect }) {
  const inputRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);

  // Forward all chosen files to the parent.
  const handleFiles = (fileList) => {
    const files = Array.from(fileList || []);
    if (files.length > 0) {
      onFilesSelect(files);
    }
  };
  const handleInputChange = (e) => {
    handleFiles(e.target.files);
    // Reset so selecting the same file again still fires onChange.
    e.target.value = "";
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    handleFiles(e.dataTransfer.files);
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
        multiple
        hidden
      />
      <p className="upload-text">
        クリックまたはドラッグ＆ドロップでファイルを選択
      </p>
      <p className="upload-hint">
        対応形式: JPEG / PNG / PDF（複数選択可）
      </p>
    </div>
  );
}

export default FileUpload;