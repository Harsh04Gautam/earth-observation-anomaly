function StatusPanel({ apiStatus, sensorCount, error }) {
  return (
    <div className="status-panel">
      <span className={apiStatus === 'ok' ? 'api-pill online' : 'api-pill'}>
        API {apiStatus}
      </span>
      <span>{sensorCount} sensors</span>
      {error ? <span className="status-error">{error}</span> : null}
    </div>
  );
}

export default StatusPanel;
