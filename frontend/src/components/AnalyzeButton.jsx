function AnalyzeButton({ onClick, isLoading, disabled }) {
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
        "解析する"
      )}
    </button>
  );
}

export default AnalyzeButton;