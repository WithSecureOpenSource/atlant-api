import React, { useState, useRef, useId } from "react";
import ScanResults from "./ScanResults";
import { buildURL } from "./Common";

export default function ScanFileForm(props) {
  const fileRef = useRef(null);
  const [inProgress, setInProgress] = useState(false);
  const [response, setResponse] = useState(null);

  async function scanFile(file) {
    const formData = new FormData();
    formData.append("file", file);
    const response = await fetch(buildURL("/analysis/file/content/"), {
      method: "POST",
      body: formData,
    });
    return await response.json();
  }

  async function handleSubmit(event) {
    event.preventDefault();
    const files = fileRef.current.files;
    if (files.length > 0) {
      setInProgress(true);
      try {
        setResponse(await scanFile(files[0]));
      } finally {
        setInProgress(false);
      }
    }
  }

  const inputId = useId();

  return (
    <form onSubmit={handleSubmit}>
      <div className="input-group input-group-lg">
        <input type="file" className="form-control" ref={fileRef}></input>
        <button className="btn btn-primary" disabled={inProgress}>
          {inProgress && (
            <span className="spinner-border spinner-border-sm"></span>
          )}
          Scan
        </button>
      </div>
      <ScanResults results={response} />
    </form>
  );
}
