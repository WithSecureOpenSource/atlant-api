import React from "react";
import ScanForm from "./ScanForm";
import { buildURL } from "./Common";

export default function ScanHashForm(props) {
  const validate = (value) => new RegExp("^[0-9a-f]{40}$").test(value);

  async function handleSubmit(value) {
    const response = await fetch(
      buildURL("/analysis/file/sha1/", encodeURIComponent(value)),
      {
        method: "POST",
      }
    );
    return await response.json();
  }

  return (
    <ScanForm
      label="SHA1 to Scan"
      placeholder="SHA1 Hash"
      onSubmit={handleSubmit}
      validate={validate}
    />
  );
}
