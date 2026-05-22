import { useState } from 'react';
import { uploadSensorCsv } from '../api/eoApi.js';

const INITIAL_FORM = {
  latitude: '',
  longitude: '',
  name: '',
};

function UploadPanel({ onUploaded }) {
  const [form, setForm] = useState(INITIAL_FORM);
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState('');
  const [isUploading, setIsUploading] = useState(false);

  function updateField(event) {
    setForm((current) => ({
      ...current,
      [event.target.name]: event.target.value,
    }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    if (!file) {
      setStatus('Choose a CSV file first.');
      return;
    }

    setIsUploading(true);
    setStatus('');

    try {
      const upload = await uploadSensorCsv({
        file,
        latitude: form.latitude,
        longitude: form.longitude,
        name: form.name.trim(),
      });
      setForm(INITIAL_FORM);
      setFile(null);
      event.target.reset();
      setStatus(`Uploaded ${upload.source_file}`);
      onUploaded(upload);
    } catch (err) {
      setStatus(err.message);
    } finally {
      setIsUploading(false);
    }
  }

  return (
    <section className="upload-panel">
      <div className="panel-heading">
        <h2>Upload sensor CSV</h2>
        <p>Add a file and its map coordinates.</p>
      </div>

      <form onSubmit={handleSubmit}>
        <label>
          <span>CSV file</span>
          <input
            type="file"
            accept=".csv,text/csv"
            onChange={(event) => setFile(event.target.files?.[0] ?? null)}
            required
          />
        </label>

        <div className="coordinate-row">
          <label>
            <span>Latitude</span>
            <input
              name="latitude"
              type="number"
              min="-90"
              max="90"
              step="0.000001"
              value={form.latitude}
              onChange={updateField}
              required
            />
          </label>
          <label>
            <span>Longitude</span>
            <input
              name="longitude"
              type="number"
              min="-180"
              max="180"
              step="0.000001"
              value={form.longitude}
              onChange={updateField}
              required
            />
          </label>
        </div>

        <label>
          <span>Display name</span>
          <input
            name="name"
            type="text"
            value={form.name}
            onChange={updateField}
            placeholder="Optional"
          />
        </label>

        <button type="submit" disabled={isUploading}>
          {isUploading ? 'Uploading...' : 'Upload'}
        </button>
      </form>

      {status ? <p className="upload-status">{status}</p> : null}
    </section>
  );
}

export default UploadPanel;
