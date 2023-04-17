import React from "react";
import ScanForm from "./ScanForm";
import { buildURL } from "./Common";

export default function ScanURLForm(props) {
  const validate = (value) => value != "";

  async function handleSubmit(value) {
    const response = await fetch(
      buildURL("/analysis/url/", encodeURIComponent(value)),
      {
        method: "POST",
      }
    );
    return await response.json();
  }

  return (
    <ScanForm
      label="URL to Scan"
      placeholder="URL"
      onSubmit={handleSubmit}
      validate={validate}
    />
  );
}
