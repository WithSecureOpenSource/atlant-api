import React, { useState, useId } from "react";
import ScanResults from "./ScanResults";

export default function ScanForm({ label, placeholder, onSubmit, validate }) {
  const [value, setValue] = useState("");
  const [inProgress, setInProgress] = useState(false);
  const [response, setResponse] = useState(null);

  const valid = validate(value);

  async function handleSubmit(event) {
    event.preventDefault();
    setInProgress(true);
    try {
      setResponse(await onSubmit(value));
    } finally {
      setInProgress(false);
    }
  }

  const inputId = useId();

  return (
    <form onSubmit={handleSubmit}>
      <div className="input-group input-group-lg">
        <label className="input-group-text" htmlFor={inputId}>
          {label}
        </label>
        <input
          type="text"
          id={inputId}
          className="form-control"
          value={value}
          onChange={(event) => setValue(event.target.value)}
          placeholder={placeholder}
        ></input>
        <button className="btn btn-primary" disabled={!valid || inProgress}>
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
