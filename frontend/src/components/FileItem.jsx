import FilePreview from "./FilePreview";
import ResultDisplay from "./ResultDisplay";
import ErrorMessage from "./ErrorMessage";

// Status label shown next to each file.
const STATUS_LABEL = {
  pending: "待機中",
  analyzing: "解析中...",
  done: "完了",
  error: "エラー",
};

function FileItem({ item, onRemove }) {
  return (
    <div className="file-item">
      <div className="file-item-header">
        <span className={`file-status file-status-${item.status}`}>
          {STATUS_LABEL[item.status]}
        </span>
        <button
          className="remove-button"
          onClick={() => onRemove(item.id)}
          disabled={item.status === "analyzing"}
          aria-label="削除"
        >
          ×
        </button>
      </div>

      <FilePreview file={item.file} />

      {item.status === "analyzing" && (
        <div className="item-loading">
          <span className="spinner spinner-dark" />
          <span>解析中...</span>
        </div>
      )}

      <ErrorMessage message={item.error} />
      <ResultDisplay result={item.result} />
    </div>
  );
}

export default FileItem;