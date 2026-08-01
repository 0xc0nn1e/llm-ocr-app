function AnalyzeButton({ onClick, isLoading, disabled, label = "解析する" }) {
  return (
    <button
      className="analyze-button"
      onClick={onClick}
      disabled={disabled || isLoading}
    >
      {isLoading ? (
        <span className="button-loading">
          <span className="spinner" />
          解析中...
        </span>
      ) : (
        label
      )}
    </button>
  );
}

export default AnalyzeButton;